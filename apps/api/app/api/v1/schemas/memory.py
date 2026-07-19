"""Memory API schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.memory_kind import MemoryKind


class MemoryItemResponse(BaseModel):
    """Serialized memory item."""

    id: UUID
    kind: MemoryKind
    title: str | None
    content: str
    source_id: UUID | None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MemoryCreateRequest(BaseModel):
    """Create a free-form memory note."""

    kind: MemoryKind = MemoryKind.NOTE
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1, max_length=8000)
    source_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryRecallRequest(BaseModel):
    """Semantic recall against the user's vector memory."""

    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)
    kinds: list[MemoryKind] | None = None


class RecalledMemoryResponse(BaseModel):
    """One recalled memory hit."""

    memory_id: UUID
    kind: MemoryKind
    title: str | None
    content: str
    score: float
    source_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CareerGoalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=4000)
    status: str = Field(default="active", pattern="^(active|paused|achieved)$")


class CareerGoalResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    memory_item_id: UUID | None
    created_at: datetime
    updated_at: datetime


class FavoriteVerseCreateRequest(BaseModel):
    verse_id: UUID
    note: str | None = Field(default=None, max_length=2000)


class FavoriteVerseResponse(BaseModel):
    id: UUID
    verse_id: UUID
    note: str | None
    memory_item_id: UUID | None
    citation: str | None = None
    translation: str | None = None
    created_at: datetime


class JournalCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1, max_length=12000)
    mood_note: str | None = Field(default=None, max_length=255)


class JournalResponse(BaseModel):
    id: UUID
    title: str | None
    content: str
    mood_note: str | None
    created_at: datetime
    updated_at: datetime


class ReflectionCreateRequest(BaseModel):
    journal_id: UUID
    content: str = Field(min_length=1, max_length=8000)
    verse_id: UUID | None = None


class ReflectionResponse(BaseModel):
    id: UUID
    journal_id: UUID
    verse_id: UUID | None
    content: str
    created_at: datetime


class ConversationSummaryRequest(BaseModel):
    """Persist a conversation summary into vector memory."""

    conversation_id: UUID | None = None
    title: str | None = Field(default=None, max_length=255)
    summary: str = Field(min_length=1, max_length=8000)
    messages_preview: list[str] = Field(default_factory=list, max_length=40)
