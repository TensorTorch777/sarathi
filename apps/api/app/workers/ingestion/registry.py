"""Register scripture parsers and default classifier bundles."""

from __future__ import annotations

from app.workers.ingestion.classifiers import (
    NullEmotionClassifier,
    NullIntentClassifier,
    NullKeywordExtractor,
    NullLifeDomainClassifier,
    NullTopicClassifier,
    NullVirtueClassifier,
    NullWisdomGraphBuilder,
)
from app.workers.ingestion.classifiers.related import CitationRelatedVerseResolver
from app.workers.ingestion.parsers import (
    BhagavadGitaParser,
    MahabharataParser,
    RamayanaParser,
    ScriptureParser,
    UpanishadParser,
)


class ParserRegistry:
    """Map scripture slug → parser instance."""

    def __init__(self) -> None:
        self._parsers: dict[str, ScriptureParser] = {}

    def register(self, parser: ScriptureParser) -> None:
        self._parsers[parser.scripture] = parser

    def get(self, scripture: str) -> ScriptureParser:
        key = scripture.strip().lower()
        try:
            return self._parsers[key]
        except KeyError as exc:
            known = ", ".join(sorted(self._parsers)) or "(none)"
            raise KeyError(f"No parser for scripture={key!r}. Registered: {known}") from exc

    def scriptures(self) -> list[str]:
        return sorted(self._parsers)


def default_parser_registry() -> ParserRegistry:
    """Built-in adapters (Gita active; others stubs)."""
    registry = ParserRegistry()
    for parser in (
        BhagavadGitaParser(),
        UpanishadParser(),
        RamayanaParser(),
        MahabharataParser(),
    ):
        registry.register(parser)
    return registry


def default_classifiers() -> dict[str, object]:
    """Swappable Null / citation classifiers (no LLM prompts)."""
    return {
        "topics": NullTopicClassifier(),
        "emotions": NullEmotionClassifier(),
        "keywords": NullKeywordExtractor(),
        "virtues": NullVirtueClassifier(),
        "life_domains": NullLifeDomainClassifier(),
        "intents": NullIntentClassifier(),
        "related": CitationRelatedVerseResolver(),
        "wisdom_graph": NullWisdomGraphBuilder(),
    }
