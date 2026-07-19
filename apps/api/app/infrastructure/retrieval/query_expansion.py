"""Gita-aware query expansion (rule-based + optional local LLM paraphrase)."""

from app.core.config import Settings
from app.core.logging import get_logger
from app.infrastructure.llm.ollama import OllamaClient

logger = get_logger(__name__)

_GITA_SYNONYMS: dict[str, list[str]] = {
    "anxiety": ["fear", "restlessness", "worry", "agitated mind", "arjuna despair"],
    "fear": ["anxiety", "cowardice", "trembling", "BG 11 fear vision"],
    "duty": ["dharma", "svadharma", "obligation", "righteous action"],
    "dharma": ["duty", "righteousness", "svadharma", "sacred duty"],
    "karma": ["action", "work", "karma yoga", "nishkama karma"],
    "detachment": ["non-attachment", "renunciation of fruits", "nishkama", "equanimity"],
    "anger": ["wrath", "krodha", "passion", "rajas"],
    "grief": ["sorrow", "shoka", "lamentation", "mourning"],
    "confusion": ["delusion", "moha", "doubt", "indecision"],
    "peace": ["shanti", "equanimity", "calm mind", "steadfast wisdom"],
    "devotion": ["bhakti", "love of god", "surrender", "worship"],
    "knowledge": ["jnana", "wisdom", "discrimination", "viveka"],
    "ego": ["ahankara", "pride", "selfishness", "false identity"],
    "death": ["mortality", "soul immortal", "atman", "rebirth"],
    "focus": ["concentration", "one-pointedness", "steady mind", "sthita prajna"],
}


class GitaQueryExpander:
    """Expand queries with Gita lexicon; optionally paraphrase via local Gemma."""

    def __init__(self, settings: Settings, llm: OllamaClient | None = None) -> None:
        self._settings = settings
        self._llm = llm

    async def expand(self, query: str) -> list[str]:
        """Return deduplicated query variants including the original."""
        normalized = " ".join(query.strip().split())
        if not normalized:
            return []

        expansions = [normalized]
        lower = normalized.lower()

        for key, values in _GITA_SYNONYMS.items():
            if key in lower:
                expansions.append(f"{normalized} {' '.join(values[:3])}")
                expansions.extend(values[:2])

        if self._llm is not None:
            try:
                llm_variants = await self._llm_paraphrases(normalized)
                expansions.extend(llm_variants)
            except Exception as exc:  # noqa: BLE001
                logger.warning("query_expansion_llm_failed", error=str(exc))

        seen: set[str] = set()
        ordered: list[str] = []
        for item in expansions:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                ordered.append(item.strip())
        return ordered

    async def _llm_paraphrases(self, query: str) -> list[str]:
        assert self._llm is not None
        content = await self._llm.complete(
            system=(
                "You expand search queries for a Bhagavad Gita retrieval system. "
                "Return 2 short paraphrases, one per line. No numbering."
            ),
            user=query,
            temperature=0.2,
        )
        return [line.strip(" -•\t") for line in content.splitlines() if line.strip()]
