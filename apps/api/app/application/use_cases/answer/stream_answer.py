"""Streaming answer pipeline for voice / low-latency chat."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.application.dto.answer import GenerateAnswerQuery
from app.application.dto.retrieval import RetrievalFilters, RetrieveVersesQuery
from app.application.use_cases.answer.generate_answer import GenerateAnswerUseCase
from app.core.config import get_settings
from app.core.logging import get_logger
from app.infrastructure.answer.emotion_detector import LexiconEmotionDetector
from app.infrastructure.answer.topic_detector import LexiconTopicDetector

logger = get_logger(__name__)


class StreamAnswerUseCase:
    """Run retrieval once, then stream the LLM answer token-by-token."""

    def __init__(self, base: GenerateAnswerUseCase) -> None:
        self._base = base

    async def execute(self, request: GenerateAnswerQuery) -> AsyncIterator[dict[str, Any]]:
        """Yield meta, text deltas, then a final verified payload."""
        message = request.message.strip()
        if not message:
            yield {
                "type": "done",
                "answer": (
                    "Please share what is on your mind, and I will look to the Gita with you."
                ),
                "emotions": [],
                "topics": [],
                "rewritten_query": "",
                "citations": [],
                "verses": [],
            }
            return

        settings = get_settings()
        if request.voice_fast:
            emotions = await LexiconEmotionDetector(settings, llm=None).detect(message)
            topics = await LexiconTopicDetector(settings, llm=None).detect(message)
            rewritten = message
        else:
            emotions = await self._base._emotion_detector.detect(message)
            topics = await self._base._topic_detector.detect(message)
            rewritten = await self._base._query_rewriter.rewrite(
                message,
                emotions=emotions,
                topics=topics,
            )

        retrieval = await self._base._retrieve_verses.execute(
            RetrieveVersesQuery(
                query=rewritten or message,
                filters=RetrievalFilters(
                    emotions=tuple(emotions),
                    topics=tuple(topics),
                ),
                top_k=request.top_k,
                expand_query=not request.voice_fast,
            ),
        )
        verses = list(retrieval.verses)
        if not verses and (emotions or topics):
            retrieval = await self._base._retrieve_verses.execute(
                RetrieveVersesQuery(
                    query=rewritten or message,
                    top_k=request.top_k,
                    expand_query=not request.voice_fast,
                ),
            )
            verses = list(retrieval.verses)

        memories = await self._base._recall_for_user(request, message)

        prompt = self._base._prompt_builder.build(
            message=message,
            emotions=emotions,
            topics=topics,
            verses=verses,
            memories=memories,
        )

        yield {
            "type": "meta",
            "emotions": emotions,
            "topics": topics,
            "rewritten_query": rewritten,
            "verses": [_verse_payload(v) for v in verses],
            "memories": [
                {
                    "memory_id": str(m.memory_id),
                    "kind": m.kind.value,
                    "title": m.title,
                    "content": m.content,
                    "score": m.score,
                }
                for m in memories
            ],
        }

        raw_parts: list[str] = []
        async for delta in self._base._generator.generate_stream(prompt):
            raw_parts.append(delta)
            yield {"type": "delta", "text": delta}

        raw_answer = "".join(raw_parts).strip()
        cleaned_answer, citations, removed = self._base._citation_verifier.verify(
            raw_answer,
            verses,
        )

        logger.info(
            "stream_answer_completed",
            emotions=emotions,
            topics=topics,
            citations=len(citations),
            removed=removed,
            voice_fast=request.voice_fast,
        )

        yield {
            "type": "done",
            "answer": cleaned_answer,
            "emotions": emotions,
            "topics": topics,
            "rewritten_query": rewritten,
            "citations": [
                {
                    "citation": c.citation,
                    "chapter": c.chapter,
                    "verse_number": c.verse_number,
                    "verse_id": str(c.verse_id),
                    "translation": c.translation,
                }
                for c in citations
            ],
            "verses": [_verse_payload(v) for v in verses],
        }


def _verse_payload(v: Any) -> dict[str, Any]:
    return {
        "verse_id": str(v.verse_id),
        "citation": v.citation,
        "chapter": v.chapter,
        "verse_number": v.verse_number,
        "sanskrit": v.sanskrit,
        "translation": v.translation,
        "transliteration": v.transliteration,
        "topics": list(v.topics),
        "emotions": list(v.emotions),
        "verified": v.verified,
    }
