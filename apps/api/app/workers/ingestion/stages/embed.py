"""Generate dense embeddings without overwriting prior embedding versions."""

from __future__ import annotations

from app.application.ports.retrieval import EmbedderPort
from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.enums.embedding_status import EmbeddingStatus
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import IndexedKnowledgeRecord, NormalizedKnowledgeRecord
from app.workers.ingestion.versioning import qdrant_point_id


class EmbedStage:
    """Embed searchable text; stamp embedding_version on each node."""

    def __init__(self, embedder: EmbedderPort | None = None) -> None:
        self._embedder = embedder

    async def run(
        self,
        nodes: list[KnowledgeNode],
        normalized: list[NormalizedKnowledgeRecord],
        context: IngestRunContext,
    ) -> list[IndexedKnowledgeRecord]:
        """Produce IndexedKnowledgeRecord list (vectors optional when skipped)."""
        if len(nodes) != len(normalized):
            raise ValueError("embed stage requires aligned nodes and normalized records")

        indexed: list[IndexedKnowledgeRecord] = []

        if context.skip_embeddings or self._embedder is None:
            for node, record in zip(nodes, normalized, strict=True):
                node.embedding_status = EmbeddingStatus.SKIPPED
                node.ingestion_metadata.embedding_version = context.embedding_version
                indexed.append(
                    IndexedKnowledgeRecord(
                        node_id=node.id,
                        normalized=record,
                        embedding_version=context.embedding_version,
                        vector=None,
                        embedding_status=EmbeddingStatus.SKIPPED,
                        related_node_ids=list(node.related_node_ids),
                        quality_score=node.editorial_metadata.quality_score,
                        retrieval_confidence=node.editorial_metadata.retrieval_confidence,
                        metadata_confidence=node.editorial_metadata.metadata_confidence,
                    )
                )
            return indexed

        texts = [node.searchable_text for node in nodes]
        vectors = await self._embedder.embed_documents(texts)
        for node, record, vector in zip(nodes, normalized, vectors, strict=True):
            point_id = qdrant_point_id(str(node.id), context.embedding_version)
            node.embedding_version = context.embedding_version
            node.qdrant_point_id = point_id
            node.embedding_status = EmbeddingStatus.INDEXED
            node.ingestion_metadata.embedding_model = getattr(
                self._embedder,
                "model_name",
                None,
            )
            node.ingestion_metadata.embedding_version = context.embedding_version
            indexed.append(
                IndexedKnowledgeRecord(
                    node_id=node.id,
                    normalized=record,
                    embedding_version=context.embedding_version,
                    vector=vector,
                    qdrant_point_id=point_id,
                    embedding_status=EmbeddingStatus.INDEXED,
                    related_node_ids=list(node.related_node_ids),
                    quality_score=node.editorial_metadata.quality_score,
                    retrieval_confidence=node.editorial_metadata.retrieval_confidence,
                    metadata_confidence=node.editorial_metadata.metadata_confidence,
                )
            )
        return indexed
