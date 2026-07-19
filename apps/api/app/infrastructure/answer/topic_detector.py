"""Topic detection for Bhagavad Gita themes."""

import re

from app.core.config import Settings
from app.core.logging import get_logger
from app.infrastructure.llm.ollama import OllamaClient

logger = get_logger(__name__)

_TOPIC_LEXICON: dict[str, tuple[str, ...]] = {
    "karma": ("karma", "action", "work", "fruits of action", "results"),
    "duty": ("duty", "obligation", "responsibility", "svadharma"),
    "dharma": ("dharma", "righteous", "righteousness", "moral"),
    "detachment": ("detach", "detachment", "non-attachment", "renounce", "nishkama"),
    "devotion": ("devotion", "bhakti", "surrender", "worship", "pray"),
    "mind": ("mind", "thoughts", "meditation", "focus", "concentration"),
    "wisdom": ("wisdom", "knowledge", "jnana", "understanding", "truth"),
    "equanimity": ("equanimity", "balance", "steady", "even-minded"),
    "compassion": ("compassion", "kindness", "friend", "love all"),
    "liberation": ("liberation", "moksha", "freedom", "release"),
    "anger": ("anger management", "temper", "rage control"),
    "self": ("self", "identity", "ego", "who am i", "atman"),
}


class LexiconTopicDetector:
    """Rule-based topic detector with optional local LLM refinement."""

    def __init__(self, settings: Settings, llm: OllamaClient | None = None) -> None:
        self._settings = settings
        self._llm = llm

    async def detect(self, message: str) -> list[str]:
        """Detect Gita topics relevant to the user message."""
        text = message.lower()
        found = [
            slug
            for slug, cues in _TOPIC_LEXICON.items()
            if any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in cues)
        ]

        if self._llm is not None and not found:
            try:
                found = await self._llm_detect(message)
            except Exception as exc:  # noqa: BLE001
                logger.warning("topic_llm_detect_failed", error=str(exc))

        return sorted(set(found))

    async def _llm_detect(self, message: str) -> list[str]:
        assert self._llm is not None
        allowed = ", ".join(_TOPIC_LEXICON)
        content = await self._llm.complete(
            system=(
                "Classify Bhagavad Gita topics in the user message. "
                f"Choose zero or more from: {allowed}. "
                "Reply with comma-separated slugs only."
            ),
            user=message,
            temperature=0.0,
        )
        normalized = content.strip().lower()
        if not normalized or normalized in {"none", "n/a"}:
            return []
        allowed_set = set(_TOPIC_LEXICON)
        return [part.strip() for part in normalized.split(",") if part.strip() in allowed_set]
