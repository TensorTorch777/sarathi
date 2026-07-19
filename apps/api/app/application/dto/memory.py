"""Memory application DTOs."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.domain.enums.memory_kind import MemoryKind


@dataclass(slots=True, frozen=True)
class RecalledMemory:
    """A memory hit returned from vector recall."""

    memory_id: UUID
    kind: MemoryKind
    title: str | None
    content: str
    score: float
    source_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class UpsertMemoryCommand:
    """Create or update a memory item and re-index vectors."""

    user_id: UUID
    kind: MemoryKind
    content: str
    title: str | None = None
    source_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
