"""KnowledgeNode — scripture verses and future non-verse wisdom units."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.entities.knowledge_metadata import (
    EditorialMetadata,
    IngestionMetadata,
    RetrievalMetadata,
)
from app.domain.entities.provenance import Provenance
from app.domain.enums.embedding_status import EmbeddingStatus
from app.domain.enums.node_type import NodeType
from app.domain.enums.validation_status import ValidationStatus


@dataclass(slots=True)
class KnowledgeNode:
    """
    One searchable unit in the Sarathi knowledge base.

    A Bhagavad Gita verse is ``NodeType.VERSE``. Later nodes may be concepts,
    summaries, characters, events, or commentary — without redesigning ingest.
    Lives beside the legacy ``Verse`` entity used by live chat (no cutover yet).
    """

    id: UUID
    node_type: NodeType
    scripture: str
    title: str | None
    # Structural locator (scripture-agnostic). Examples:
    #   {"chapter": 2, "verse": 47}
    #   {"kanda": "ayodhya", "sarga": 1, "verse": 12}
    locator: dict[str, Any]
    language: str
    # Text planes (verse-shaped nodes use all; concepts may use translation only)
    sanskrit: str | None
    transliteration: str | None
    translation: str | None
    commentary: str | None
    body: str | None
    provenance: Provenance
    ingestion_metadata: IngestionMetadata
    retrieval_metadata: RetrievalMetadata
    editorial_metadata: EditorialMetadata
    embedding_version: str | None
    qdrant_point_id: str | None
    validation_status: ValidationStatus
    embedding_status: EmbeddingStatus
    created_at: datetime
    updated_at: datetime
    # Denormalized convenience for Gita-shaped verses (optional)
    chapter: int | None = None
    verse_number: int | None = None
    related_node_ids: list[UUID] = field(default_factory=list)

    @property
    def citation(self) -> str:
        """Human citation when chapter/verse are present; else scripture+title."""
        if self.chapter is not None and self.verse_number is not None:
            prefix = {
                "bhagavad_gita": "BG",
            }.get(self.scripture, self.scripture.upper()[:4])
            return f"{prefix} {self.chapter}.{self.verse_number}"
        if self.title:
            return f"{self.scripture}:{self.title}"
        return f"{self.scripture}:{self.id}"

    @property
    def searchable_text(self) -> str:
        """Text used for embedding and sparse indexing."""
        parts: list[str] = []
        if self.title:
            parts.append(self.title)
        if self.translation:
            parts.append(self.translation)
        if self.transliteration:
            parts.append(self.transliteration)
        if self.commentary:
            parts.append(self.commentary)
        if self.body:
            parts.append(self.body)
        if self.sanskrit:
            parts.append(self.sanskrit)
        return "\n".join(parts)
