"""Split metadata planes for KnowledgeNode (avoid one opaque JSON blob)."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class IngestionMetadata:
    """Pipeline / reproducibility facts (not used for retrieval ranking)."""

    parser_version: str | None = None
    source_path: str | None = None
    content_checksum: str | None = None
    batch_id: str | None = None
    imported_at: datetime | None = None
    embedding_model: str | None = None
    embedding_version: str | None = None
    extra: dict[str, str | int | float | bool | None] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalMetadata:
    """Signals that will later power filters and hybrid retrieval."""

    topics: list[str] = field(default_factory=list)
    emotions: list[str] = field(default_factory=list)
    virtues: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    life_domains: list[str] = field(default_factory=list)
    user_intents: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EditorialMetadata:
    """Human / editorial quality and approval trail."""

    verified_by: str | None = None
    editor: str | None = None
    revision: str | None = None
    approved: bool = False
    quality_score: float | None = None
    retrieval_confidence: float | None = None
    metadata_confidence: float | None = None
    notes: str | None = None
    extra: dict[str, str | int | float | bool | None] = field(default_factory=dict)
