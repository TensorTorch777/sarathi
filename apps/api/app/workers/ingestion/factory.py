"""Wire a scaffold IngestionPipeline with in-memory stores (no chat DI)."""

from __future__ import annotations

from app.application.ports.knowledge import KnowledgeVectorStore
from app.application.ports.retrieval import EmbedderPort
from app.workers.ingestion.pipeline import IngestionPipeline
from app.workers.ingestion.stores.memory import (
    InMemoryCorpusManifestRepository,
    InMemoryKnowledgeNodeRepository,
    InMemoryWisdomGraphRepository,
    NullKnowledgeVectorStore,
)


def build_ingestion_pipeline(
    *,
    embedder: EmbedderPort | None = None,
    vector_store: KnowledgeVectorStore | None = None,
) -> IngestionPipeline:
    """
    Construct a pipeline safe for dry-runs and unit tests.

    Production wiring (SQLAlchemy + Qdrant ``knowledge_nodes``) lands later;
    this factory does not register chat routes or replace legacy Verse ingest.
    """
    return IngestionPipeline(
        nodes=InMemoryKnowledgeNodeRepository(),
        manifests=InMemoryCorpusManifestRepository(),
        graph=InMemoryWisdomGraphRepository(),
        embedder=embedder,
        vector_store=vector_store or NullKnowledgeVectorStore(),
    )
