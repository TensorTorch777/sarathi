"""Product-alpha answer path: editorially-driven conversation engine."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.application.dto.answer import AnswerCitation, GenerateAnswerQuery, GenerateAnswerResult
from app.application.dto.retrieval import RankedVerse
from app.conversation.conversation_engine import ConversationEngine
from app.conversation.session_store import ConversationSessionStore
from app.evaluation.response_evaluator import ResponseEvaluator


class ConversationalAnswerUseCase:
    """
    Adapter: ConversationEngine → GenerateAnswerResult for /chat/ask.

    Does not call the LLM. Builds answers from approved editorial content.
    Attaches evaluation (developer diagnostics) without changing the user answer.
    """

    def __init__(
        self,
        *,
        engine: ConversationEngine | None = None,
        session_store: ConversationSessionStore | None = None,
        evaluator: ResponseEvaluator | None = None,
    ) -> None:
        self._engine = engine or ConversationEngine(session_store=session_store)
        self._evaluator = evaluator or ResponseEvaluator()

    async def execute(self, request: GenerateAnswerQuery) -> GenerateAnswerResult:
        message = request.message.strip()
        if not message:
            return GenerateAnswerResult(
                answer="Please share what is on your mind, and I will look to the Gita with you.",
                emotions=(),
                topics=(),
                rewritten_query="",
                verses=(),
                citations=(),
                stages={"error": "empty_message", "engine": "conversation"},
            )

        result = self._engine.handle(
            message,
            conversation_id=request.conversation_id,
            top_k=request.top_k,
            write_debug=True,
        )

        evaluation = self._evaluator.evaluate(
            answer=result.answer,
            intent=result.intent,
            family_id=result.family_id,
            response_level=result.response_level.value,
            confidence=result.confidence,
            verse_ids=list(result.verse_ids),
            debug=result.debug,
            alternatives=list(result.verse_ids[1:5]),
        )

        pairs: list[tuple[str, str]] = []
        if result.verse_ids and result.citations:
            pairs = list(zip(result.verse_ids, result.citations, strict=False))
        elif result.citations:
            pairs = [(_citation_to_node(cid), cid) for cid in result.citations]

        verses = tuple(
            RankedVerse(
                verse_id=uuid4(),  # editorial path does not require DB UUIDs
                citation=cid,
                chapter=_chapter(nid),
                verse_number=_verse_num(nid),
                sanskrit="",
                translation="",
                transliteration=None,
                commentary=None,
                topics=[],
                emotions=[],
                bm25_score=0.0,
                dense_score=0.0,
                rrf_score=0.0,
                rerank_score=result.confidence,
                compressed_context="",
                verified=True,
            )
            for nid, cid in pairs
        )

        citations = tuple(
            AnswerCitation(
                citation=v.citation,
                chapter=v.chapter,
                verse_number=v.verse_number,
                verse_id=v.verse_id,
                translation=v.translation,
            )
            for v in verses
        )

        return GenerateAnswerResult(
            answer=result.answer,
            emotions=(),
            topics=(),
            rewritten_query=message,
            verses=verses,
            citations=citations,
            stages={
                "engine": "conversation_v0.7.0-product-alpha",
                "conversation_id": str(result.session_id),
                "intent": result.intent,
                "response_level": result.response_level.value,
                "state": result.state.value,
                "family_id": result.family_id,
                "confidence": result.confidence,
                "followup_asked": result.followup_asked,
                "safety_ok": result.safety_ok,
                "debug": result.debug,
                "evaluation": evaluation.to_dict(),
            },
        )


def _chapter(node_id: str) -> int:
    parts = node_id.split("_")
    return int(parts[1]) if len(parts) == 3 else 0


def _verse_num(node_id: str) -> int:
    parts = node_id.split("_")
    return int(parts[2]) if len(parts) == 3 else 0


def _parse_citation(citation: str) -> tuple[int, int]:
    # "BG 2.47"
    text = citation.upper().replace("BG", "").strip()
    if "." in text:
        a, b = text.split(".", 1)
        return int(a), int(b)
    return 0, 0


def _citation_to_node(citation: str) -> str:
    chapter, verse = _parse_citation(citation)
    return f"bg_{chapter}_{verse}"
