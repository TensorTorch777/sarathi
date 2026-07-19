"""Upsert long-term memory into Postgres + Qdrant."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.application.dto.memory import UpsertMemoryCommand
from app.domain.entities.memory_item import MemoryItem
from app.domain.repositories.memory_repository import MemoryRepository
from app.infrastructure.vector.memory_store import QdrantMemoryStore


class EmbedderPort(Protocol):
    """Minimal embedder surface used by memory indexing."""

    async def embed(self, text: str) -> list[float]: ...


class IndexMemoryUseCase:
    """Write a memory fact and keep the vector index in sync."""

    def __init__(
        self,
        *,
        memories: MemoryRepository,
        store: QdrantMemoryStore,
        embedder: EmbedderPort,
    ) -> None:
        self._memories = memories
        self._store = store
        self._embedder = embedder

    async def execute(self, command: UpsertMemoryCommand) -> MemoryItem:
        """Create or update by (user, kind, source_id) when source is set."""
        await self._store.ensure_collection()
        now = datetime.now(UTC)

        existing = None
        if command.source_id is not None:
            existing = await self._memories.get_by_source(
                command.user_id,
                command.kind,
                command.source_id,
            )

        if existing is None:
            item = MemoryItem(
                id=uuid4(),
                user_id=command.user_id,
                kind=command.kind,
                title=command.title,
                content=command.content.strip(),
                source_id=command.source_id,
                metadata=dict(command.metadata),
                qdrant_point_id=None,
                created_at=now,
                updated_at=now,
            )
            item = await self._memories.add(item)
        else:
            existing.title = command.title
            existing.content = command.content.strip()
            existing.metadata = dict(command.metadata)
            existing.updated_at = now
            item = await self._memories.update(existing)

        vector = await self._embedder.embed(item.embed_text)
        point_id = await self._store.upsert(item, vector)
        await self._memories.update_qdrant_point_id(item.id, point_id)
        item.qdrant_point_id = point_id
        return item
