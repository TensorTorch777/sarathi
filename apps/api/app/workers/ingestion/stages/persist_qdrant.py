"""Index KnowledgeNodes into one Qdrant collection with payload filters."""

from __future__ import annotations

from app.application.ports.knowledge import KnowledgeVectorStore
from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.enums.embedding_status import EmbeddingStatus
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import IndexedKnowledgeRecord


# Single collection for all scriptures / node types (filter via payload).
KNOWLEDGE_QDRANT_COLLECTION = "knowledge_nodes"


class PersistQdrantStage:
    """
    Upsert vectors keyed by ``{node_id}:{embedding_version}``.

    Changing translation or embed model creates a new point; old points remain.
    """

    def __init__(self, store: KnowledgeVectorStore | None = None) -> None:
        self._store = store

    async def run(
        self,
        nodes: list[KnowledgeNode],
        indexed: list[IndexedKnowledgeRecord],
        context: IngestRunContext,
    ) -> int:
        """Return number of points written."""
        if context.skip_qdrant or context.dry_run or self._store is None:
            return 0

        await self._store.ensure_collection()
        vectors = {item.node_id: item for item in indexed}
        written = 0
        for node in nodes:
            item = vectors.get(node.id)
            if item is None or item.vector is None:
                continue
            point_id = await self._store.upsert_node(node, item.vector)
            node.qdrant_point_id = point_id
            node.embedding_status = EmbeddingStatus.INDEXED
            written += 1
        return written
