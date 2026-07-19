"""Scaffold persistence adapters for knowledge ingestion."""

from app.workers.ingestion.stores.memory import (
    InMemoryCorpusManifestRepository,
    InMemoryKnowledgeNodeRepository,
    InMemoryWisdomGraphRepository,
    NullKnowledgeVectorStore,
)

__all__ = [
    "InMemoryKnowledgeNodeRepository",
    "InMemoryCorpusManifestRepository",
    "InMemoryWisdomGraphRepository",
    "NullKnowledgeVectorStore",
]
