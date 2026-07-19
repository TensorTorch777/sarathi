"""Query rewrite stage for retrieval."""

from app.core.config import Settings
from app.core.logging import get_logger
from app.infrastructure.llm.ollama import OllamaClient

logger = get_logger(__name__)


class GitaQueryRewriter:
    """Rewrite a user message into a concise retrieval query."""

    def __init__(self, settings: Settings, llm: OllamaClient | None = None) -> None:
        self._settings = settings
        self._llm = llm

    async def rewrite(
        self,
        message: str,
        *,
        emotions: list[str],
        topics: list[str],
    ) -> str:
        """Produce a single rewritten query biased by emotion and topic."""
        cleaned = " ".join(message.strip().split())
        if not cleaned:
            return ""

        if self._llm is not None:
            try:
                rewritten = await self._llm_rewrite(cleaned, emotions=emotions, topics=topics)
                if rewritten:
                    return rewritten
            except Exception as exc:  # noqa: BLE001
                logger.warning("query_rewrite_llm_failed", error=str(exc))

        parts = [cleaned]
        if emotions:
            parts.append("emotions: " + ", ".join(emotions))
        if topics:
            parts.append("topics: " + ", ".join(topics))
        parts.append("Bhagavad Gita guidance")
        return " | ".join(parts)

    async def _llm_rewrite(
        self,
        message: str,
        *,
        emotions: list[str],
        topics: list[str],
    ) -> str:
        assert self._llm is not None
        return await self._llm.complete(
            system=(
                "Rewrite the user message as one short search query for retrieving "
                "Bhagavad Gita verses. Keep spiritual intent. No questions to the user. "
                "Return only the rewritten query."
            ),
            user=(
                f"Message: {message}\n"
                f"Emotions: {', '.join(emotions) or 'none'}\n"
                f"Topics: {', '.join(topics) or 'none'}"
            ),
            temperature=0.2,
        )
