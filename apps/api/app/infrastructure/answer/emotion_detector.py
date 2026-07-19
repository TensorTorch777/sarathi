"""Emotion detection from user messages."""

import re

from app.core.config import Settings
from app.core.logging import get_logger
from app.infrastructure.llm.ollama import OllamaClient

logger = get_logger(__name__)

_EMOTION_LEXICON: dict[str, tuple[str, ...]] = {
    "anxiety": ("anxious", "anxiety", "worried", "worry", "nervous", "restless", "panic"),
    "fear": ("afraid", "fear", "scared", "terrified", "frightened"),
    "grief": ("grief", "sorrow", "sad", "sadness", "mourning", "loss", "heartbroken"),
    "anger": ("anger", "angry", "rage", "furious", "irritated", "wrath"),
    "confusion": ("confused", "confusion", "lost", "uncertain", "doubt", "indecisive"),
    "hopelessness": ("hopeless", "despair", "worthless", "give up", "no point"),
    "peace": ("peace", "calm", "serene", "content", "at ease"),
    "guilt": ("guilt", "guilty", "ashamed", "shame", "regret"),
}


class LexiconEmotionDetector:
    """Rule-based emotion detector with optional local LLM refinement."""

    def __init__(self, settings: Settings, llm: OllamaClient | None = None) -> None:
        self._settings = settings
        self._llm = llm

    async def detect(self, message: str) -> list[str]:
        """Detect emotions present in the user message."""
        text = message.lower()
        found = [
            slug
            for slug, cues in _EMOTION_LEXICON.items()
            if any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in cues)
        ]

        if self._llm is not None and not found:
            try:
                found = await self._llm_detect(message)
            except Exception as exc:  # noqa: BLE001
                logger.warning("emotion_llm_detect_failed", error=str(exc))

        return sorted(set(found))

    async def _llm_detect(self, message: str) -> list[str]:
        assert self._llm is not None
        allowed = ", ".join(_EMOTION_LEXICON)
        content = await self._llm.complete(
            system=(
                "Classify emotions in the user message for a Bhagavad Gita assistant. "
                f"Choose zero or more from: {allowed}. "
                "Reply with comma-separated slugs only."
            ),
            user=message,
            temperature=0.0,
        )
        normalized = content.strip().lower()
        if not normalized or normalized in {"none", "n/a"}:
            return []
        allowed_set = set(_EMOTION_LEXICON)
        return [part.strip() for part in normalized.split(",") if part.strip() in allowed_set]
