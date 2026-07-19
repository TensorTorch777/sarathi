"""Verse domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Verse:
    """A grounded Bhagavad Gita verse."""

    id: UUID
    chapter: int
    verse_number: int
    sanskrit: str
    transliteration: str | None
    translation: str
    translation_source: str | None
    commentary: str | None
    qdrant_point_id: str | None
    created_at: datetime
    updated_at: datetime
    topics: list[str] = field(default_factory=list)
    emotions: list[str] = field(default_factory=list)

    @property
    def citation(self) -> str:
        """Canonical citation label, e.g. BG 2.47."""
        return f"BG {self.chapter}.{self.verse_number}"

    @property
    def searchable_text(self) -> str:
        """Text used for sparse retrieval and reranking."""
        parts = [self.translation]
        if self.transliteration:
            parts.append(self.transliteration)
        if self.commentary:
            parts.append(self.commentary)
        return "\n".join(parts)
