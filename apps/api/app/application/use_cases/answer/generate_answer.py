"""End-to-end Sarathi answer pipeline.

User → Emotion → Topic → Query Rewrite → Hybrid Search → Rerank
    → Prompt Builder → GPT → Citation Verification → Answer
"""

from app.application.dto.answer import GenerateAnswerQuery, GenerateAnswerResult
from app.application.dto.memory import RecalledMemory
from app.application.dto.retrieval import RetrievalFilters, RetrieveVersesQuery
from app.application.ports.answer import (
    AnswerCitationVerifierPort,
    AnswerGeneratorPort,
    EmotionDetectorPort,
    PromptBuilderPort,
    QueryRewriterPort,
    TopicDetectorPort,
)
from app.application.use_cases.memory import RecallMemoryUseCase
from app.application.use_cases.retrieval import RetrieveVersesUseCase
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenerateAnswerUseCase:
    """Orchestrate the full grounded answer pipeline in stage order."""

    def __init__(
        self,
        *,
        emotion_detector: EmotionDetectorPort,
        topic_detector: TopicDetectorPort,
        query_rewriter: QueryRewriterPort,
        retrieve_verses: RetrieveVersesUseCase,
        prompt_builder: PromptBuilderPort,
        generator: AnswerGeneratorPort,
        citation_verifier: AnswerCitationVerifierPort,
        recall_memory: RecallMemoryUseCase | None = None,
        memory_top_k: int = 6,
    ) -> None:
        self._emotion_detector = emotion_detector
        self._topic_detector = topic_detector
        self._query_rewriter = query_rewriter
        self._retrieve_verses = retrieve_verses
        self._prompt_builder = prompt_builder
        self._generator = generator
        self._citation_verifier = citation_verifier
        self._recall_memory = recall_memory
        self._memory_top_k = memory_top_k

    async def execute(self, request: GenerateAnswerQuery) -> GenerateAnswerResult:
        """Run every stage and return a citation-verified answer."""
        message = request.message.strip()
        if not message:
            return GenerateAnswerResult(
                answer="Please share what is on your mind, and I will look to the Gita with you.",
                emotions=(),
                topics=(),
                rewritten_query="",
                verses=(),
                citations=(),
                stages={"error": "empty_message"},
            )

        # 1) Emotion
        emotions = await self._emotion_detector.detect(message)

        # 2) Topic
        topics = await self._topic_detector.detect(message)

        # 3) Query Rewrite
        rewritten = await self._query_rewriter.rewrite(
            message,
            emotions=emotions,
            topics=topics,
        )

        # 4–5) Hybrid Search + Rerank (RetrieveVersesUseCase)
        retrieval = await self._retrieve_verses.execute(
            RetrieveVersesQuery(
                query=rewritten or message,
                filters=RetrievalFilters(
                    emotions=tuple(emotions),
                    topics=tuple(topics),
                ),
                top_k=request.top_k,
                expand_query=True,
            ),
        )
        verses = list(retrieval.verses)

        # Soft retry without filters if emotion/topic filtering emptied the pool.
        if not verses and (emotions or topics):
            logger.info("answer_retrieval_retry_without_filters")
            retrieval = await self._retrieve_verses.execute(
                RetrieveVersesQuery(
                    query=rewritten or message,
                    top_k=request.top_k,
                    expand_query=True,
                ),
            )
            verses = list(retrieval.verses)

        # 5b) Long-term vector memory recall (user-scoped)
        memories = await self._recall_for_user(request, message)

        # 6) Prompt Builder
        prompt = self._prompt_builder.build(
            message=message,
            emotions=emotions,
            topics=topics,
            verses=verses,
            memories=memories,
        )

        # 7) GPT
        raw_answer = await self._generator.generate(prompt)

        # 8) Citation Verification → Answer
        cleaned_answer, citations, removed = self._citation_verifier.verify(raw_answer, verses)

        logger.info(
            "answer_pipeline_completed",
            emotions=emotions,
            topics=topics,
            verse_count=len(verses),
            citations=len(citations),
            removed_citations=removed,
            memories=len(memories),
        )

        return GenerateAnswerResult(
            answer=cleaned_answer,
            emotions=tuple(emotions),
            topics=tuple(topics),
            rewritten_query=rewritten,
            verses=tuple(verses),
            citations=tuple(citations),
            stages={
                "emotion": emotions,
                "topic": topics,
                "query_rewrite": rewritten,
                "hybrid_search": retrieval.stages,
                "memory_recall": [
                    {"kind": m.kind.value, "title": m.title, "score": m.score}
                    for m in memories
                ],
                "rerank": "completed_in_retrieval",
                "prompt_builder": "completed",
                "gpt": "completed",
                "citation_verification": {
                    "kept": [c.citation for c in citations],
                    "removed": removed,
                },
            },
        )

    async def _recall_for_user(
        self,
        request: GenerateAnswerQuery,
        message: str,
    ) -> list[RecalledMemory]:
        if self._recall_memory is None or request.user_id is None:
            return []
        try:
            return await self._recall_memory.execute(
                user_id=request.user_id,
                query=message,
                top_k=self._memory_top_k,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_recall_failed", error=str(exc))
            return []
