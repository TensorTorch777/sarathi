"""Qdrant vector store for per-user long-term memory."""

from __future__ import annotations

from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm

from app.core.config import Settings
from app.domain.entities.memory_item import MemoryItem
from app.domain.enums.memory_kind import MemoryKind


class QdrantMemoryStore:
    """Dense memory index scoped by user_id in payload filters."""

    def __init__(
        self,
        settings: Settings,
        client: AsyncQdrantClient | None = None,
        *,
        vector_size: int | None = None,
    ) -> None:
        self._settings = settings
        self._collection = settings.memory_qdrant_collection
        self._vector_size = vector_size or settings.embedding_dimensions
        self._client = client or AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    async def ensure_collection(self) -> None:
        """Create the memory collection when missing or wrong dimensionality."""
        exists = await self._client.collection_exists(self._collection)
        if exists:
            info = await self._client.get_collection(self._collection)
            size = getattr(getattr(getattr(info, "config", None), "params", None), "vectors", None)
            current = getattr(size, "size", None)
            if current == self._vector_size:
                return
            await self._client.delete_collection(self._collection)

        await self._client.create_collection(
            collection_name=self._collection,
            vectors_config=qm.VectorParams(
                size=self._vector_size,
                distance=qm.Distance.COSINE,
            ),
        )
        for field_name, schema in (
            ("user_id", qm.PayloadSchemaType.KEYWORD),
            ("kind", qm.PayloadSchemaType.KEYWORD),
            ("memory_id", qm.PayloadSchemaType.KEYWORD),
            ("source_id", qm.PayloadSchemaType.KEYWORD),
        ):
            await self._client.create_payload_index(
                collection_name=self._collection,
                field_name=field_name,
                field_schema=schema,
            )

    async def upsert(self, item: MemoryItem, vector: list[float]) -> str:
        """Upsert one memory embedding; return point id."""
        point_id = item.qdrant_point_id or str(item.id)
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                qm.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "memory_id": str(item.id),
                        "user_id": str(item.user_id),
                        "kind": item.kind.value,
                        "title": item.title,
                        "content": item.content,
                        "source_id": str(item.source_id) if item.source_id else None,
                        "metadata": item.metadata,
                    },
                ),
            ],
        )
        return point_id

    async def delete(self, point_id: str) -> None:
        """Remove a memory point."""
        await self._client.delete(
            collection_name=self._collection,
            points_selector=qm.PointIdsList(points=[point_id]),
        )

    async def search(
        self,
        *,
        user_id: UUID,
        query_vector: list[float],
        top_k: int = 6,
        kinds: list[MemoryKind] | None = None,
    ) -> list[tuple[UUID, float, dict]]:
        """ANN search restricted to one user's memories."""
        must: list[qm.FieldCondition] = [
            qm.FieldCondition(
                key="user_id",
                match=qm.MatchValue(value=str(user_id)),
            ),
        ]
        if kinds:
            must.append(
                qm.FieldCondition(
                    key="kind",
                    match=qm.MatchAny(any=[k.value for k in kinds]),
                ),
            )

        results = await self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            query_filter=qm.Filter(must=must),
            limit=top_k,
            with_payload=True,
        )

        ranked: list[tuple[UUID, float, dict]] = []
        for point in results.points:
            payload = point.payload or {}
            memory_id = payload.get("memory_id")
            if memory_id is None:
                continue
            ranked.append((UUID(str(memory_id)), float(point.score or 0.0), dict(payload)))
        return ranked
