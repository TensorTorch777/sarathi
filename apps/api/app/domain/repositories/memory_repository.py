"""Memory item persistence port."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.memory_item import MemoryItem
from app.domain.enums.memory_kind import MemoryKind


class MemoryRepository(Protocol):
    """CRUD for long-term memory items."""

    async def get_by_id(self, memory_id: UUID) -> MemoryItem | None: ...

    async def get_by_source(
        self,
        user_id: UUID,
        kind: MemoryKind,
        source_id: UUID,
    ) -> MemoryItem | None: ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        kind: MemoryKind | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryItem]: ...

    async def add(self, item: MemoryItem) -> MemoryItem: ...

    async def update(self, item: MemoryItem) -> MemoryItem: ...

    async def delete(self, memory_id: UUID) -> bool: ...

    async def update_qdrant_point_id(self, memory_id: UUID, point_id: str) -> None: ...
