"""Long-term memory item domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums.memory_kind import MemoryKind


@dataclass(slots=True)
class MemoryItem:
    """A user memory fact indexed in Postgres + Qdrant."""

    id: UUID
    user_id: UUID
    kind: MemoryKind
    content: str
    title: str | None = None
    source_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    qdrant_point_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def embed_text(self) -> str:
        """Text used for dense embedding."""
        if self.title:
            return f"{self.kind.value}: {self.title}\n{self.content}"
        return f"{self.kind.value}: {self.content}"
