"""Recall relevant long-term memories via vector search."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.application.dto.memory import RecalledMemory
from app.domain.enums.memory_kind import MemoryKind
from app.domain.repositories.memory_repository import MemoryRepository
from app.infrastructure.vector.memory_store import QdrantMemoryStore


class EmbedderPort(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class RecallMemoryUseCase:
    """Embed a query and retrieve the user's closest memories."""

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

    async def execute(
        self,
        *,
        user_id: UUID,
        query: str,
        top_k: int = 6,
        kinds: list[MemoryKind] | None = None,
    ) -> list[RecalledMemory]:
        """Return ranked memories for prompt grounding (never invents verses)."""
        text = query.strip()
        if not text:
            return []

        await self._store.ensure_collection()
        vector = await self._embedder.embed(text)
        hits = await self._store.search(
            user_id=user_id,
            query_vector=vector,
            top_k=top_k,
            kinds=kinds,
        )

        recalled: list[RecalledMemory] = []
        for memory_id, score, payload in hits:
            item = await self._memories.get_by_id(memory_id)
            if item is None:
                # Fall back to payload if Postgres row was deleted out of band.
                kind_raw = str(payload.get("kind") or MemoryKind.NOTE.value)
                source_raw = payload.get("source_id")
                recalled.append(
                    RecalledMemory(
                        memory_id=memory_id,
                        kind=MemoryKind(kind_raw),
                        title=payload.get("title"),
                        content=str(payload.get("content") or ""),
                        score=score,
                        source_id=UUID(str(source_raw)) if source_raw else None,
                        metadata=dict(payload.get("metadata") or {}),
                    ),
                )
                continue
            recalled.append(
                RecalledMemory(
                    memory_id=item.id,
                    kind=item.kind,
                    title=item.title,
                    content=item.content,
                    score=score,
                    source_id=item.source_id,
                    metadata=dict(item.metadata),
                ),
            )
        return recalled
