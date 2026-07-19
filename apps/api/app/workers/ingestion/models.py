"""Pydantic models flowing through the ingestion pipeline."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.embedding_status import EmbeddingStatus
from app.domain.enums.node_type import NodeType
from app.domain.enums.validation_status import ValidationStatus


class RawKnowledgeRecord(BaseModel):
    """Parser output before validation / normalization."""

    node_type: NodeType = NodeType.VERSE
    scripture: str | None = None
    title: str | None = None
    locator: dict[str, Any] = Field(default_factory=dict)
    chapter: int | None = None
    verse_number: int | None = None
    language: str | None = None
    sanskrit: str | None = None
    transliteration: str | None = None
    translation: str | None = None
    commentary: str | None = None
    body: str | None = None
    # Optional pre-seeded retrieval hints from source files
    topics: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    virtues: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    life_domains: list[str] = Field(default_factory=list)
    user_intents: list[str] = Field(default_factory=list)
    related_citations: list[str] = Field(default_factory=list)
    source_path: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class NormalizedKnowledgeRecord(BaseModel):
    """Validated + normalized record ready for metadata / embed / persist."""

    node_type: NodeType
    scripture: str
    title: str | None = None
    locator: dict[str, Any]
    citation_key: str
    chapter: int | None = None
    verse_number: int | None = None
    language: str
    sanskrit: str | None = None
    transliteration: str | None = None
    translation: str | None = None
    commentary: str | None = None
    body: str | None = None
    content_checksum: str
    topics: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    virtues: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    life_domains: list[str] = Field(default_factory=list)
    user_intents: list[str] = Field(default_factory=list)
    related_citations: list[str] = Field(default_factory=list)
    source_path: str | None = None
    validation_status: ValidationStatus = ValidationStatus.VALID


class IndexedKnowledgeRecord(BaseModel):
    """Fully prepared record including embedding vector and statuses."""

    node_id: UUID
    normalized: NormalizedKnowledgeRecord
    embedding_version: str
    vector: list[float] | None = None
    qdrant_point_id: str | None = None
    embedding_status: EmbeddingStatus = EmbeddingStatus.PENDING
    related_node_ids: list[UUID] = Field(default_factory=list)
    quality_score: float | None = None
    retrieval_confidence: float | None = None
    metadata_confidence: float | None = None


class IngestPipelineResult(BaseModel):
    """Summary of one pipeline run."""

    run_id: UUID
    scripture: str
    edition: str
    parsed: int
    validated: int
    rejected: int
    indexed: int
    edges_proposed: int
    manifest_id: UUID | None = None
    checksum: str | None = None
    finished_at: datetime
    errors: list[str] = Field(default_factory=list)
