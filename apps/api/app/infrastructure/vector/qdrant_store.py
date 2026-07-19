"""Qdrant vector store client for Gita verse embeddings."""

from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm

from app.application.dto.retrieval import RetrievalFilters
from app.core.config import Settings
from app.domain.entities import Verse
from app.infrastructure.retrieval.filters import build_qdrant_filter


class QdrantDenseRetriever:
    """Dense retrieval and upserts against a Qdrant collection."""

    def __init__(
        self,
        settings: Settings,
        client: AsyncQdrantClient | None = None,
        *,
        vector_size: int | None = None,
    ) -> None:
        self._settings = settings
        self._collection = settings.qdrant_collection
        self._vector_size = vector_size or settings.embedding_dimensions
        self._client = client or AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    async def ensure_collection(self) -> None:
        """Create the verses collection when missing or wrong vector size."""
        exists = await self._client.collection_exists(self._collection)
        if exists:
            info = await self._client.get_collection(self._collection)
            current_size = _collection_vector_size(info)
            if current_size == self._vector_size:
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
            ("chapter", qm.PayloadSchemaType.INTEGER),
            ("verse_number", qm.PayloadSchemaType.INTEGER),
            ("topics", qm.PayloadSchemaType.KEYWORD),
            ("emotions", qm.PayloadSchemaType.KEYWORD),
            ("translation_source", qm.PayloadSchemaType.KEYWORD),
            ("verse_id", qm.PayloadSchemaType.KEYWORD),
        ):
            await self._client.create_payload_index(
                collection_name=self._collection,
                field_name=field_name,
                field_schema=schema,
            )

    async def search(
        self,
        query_vector: list[float],
        *,
        filters: RetrievalFilters,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """ANN search with metadata / emotion / topic payload filters."""
        query_filter = None
        raw = build_qdrant_filter(filters)
        if raw is not None:
            query_filter = qm.Filter.model_validate(raw)

        results = await self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        ranked: list[tuple[UUID, float]] = []
        for point in results.points:
            payload = point.payload or {}
            verse_id_raw = payload.get("verse_id")
            if verse_id_raw is None:
                continue
            ranked.append((UUID(str(verse_id_raw)), float(point.score or 0.0)))
        return ranked

    async def upsert_verse(self, verse: Verse, vector: list[float]) -> str:
        """Upsert one verse embedding and return the point id."""
        point_id = verse.qdrant_point_id or str(verse.id)
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                qm.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "verse_id": str(verse.id),
                        "chapter": verse.chapter,
                        "verse_number": verse.verse_number,
                        "citation": verse.citation,
                        "topics": [t.lower() for t in verse.topics],
                        "emotions": [e.lower() for e in verse.emotions],
                        "translation_source": verse.translation_source,
                        "translation": verse.translation,
                    },
                ),
            ],
        )
        return point_id


class InMemoryDenseRetriever:
    """In-memory dense retriever for tests without Qdrant."""

    def __init__(self) -> None:
        self._points: dict[UUID, tuple[list[float], Verse]] = {}

    async def search(
        self,
        query_vector: list[float],
        *,
        filters: RetrievalFilters,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        from app.infrastructure.retrieval.filters import verse_matches_filters

        scored: list[tuple[UUID, float]] = []
        for verse_id, (vector, verse) in self._points.items():
            if not verse_matches_filters(verse, filters):
                continue
            score = _cosine(query_vector, vector)
            scored.append((verse_id, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    async def upsert_verse(self, verse: Verse, vector: list[float]) -> str:
        self._points[verse.id] = (vector, verse)
        return str(verse.id)


def _collection_vector_size(info: object) -> int | None:
    """Extract dense vector size from a Qdrant collection info object."""
    config = getattr(info, "config", None)
    params = getattr(config, "params", None)
    vectors = getattr(params, "vectors", None)
    if vectors is None:
        return None
    size = getattr(vectors, "size", None)
    if isinstance(size, int):
        return size
    if isinstance(vectors, dict):
        # Named vectors — use the first entry's size when present.
        for value in vectors.values():
            named_size = getattr(value, "size", None)
            if isinstance(named_size, int):
                return named_size
            if isinstance(value, dict) and isinstance(value.get("size"), int):
                return int(value["size"])
    return None


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
