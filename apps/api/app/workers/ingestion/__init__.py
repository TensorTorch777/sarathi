"""
Sarathi Knowledge Base — ingestion architecture.

Transforms scriptures into versioned ``KnowledgeNode`` records (verse is one
node type), with provenance, split metadata, CorpusManifest reproducibility,
and Wisdom Graph edges.

Pipeline: Parse → Validate → Normalize → Metadata → Embed → Postgres → Qdrant

One Qdrant collection (``knowledge_nodes``) with payload filters.
Lives beside the legacy ``Verse`` model; chat/RAG are not wired yet.
"""

from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.factory import build_ingestion_pipeline
from app.workers.ingestion.pipeline import IngestionPipeline
from app.workers.ingestion.stages.persist_qdrant import KNOWLEDGE_QDRANT_COLLECTION

__all__ = [
    "IngestRunContext",
    "IngestionPipeline",
    "build_ingestion_pipeline",
    "KNOWLEDGE_QDRANT_COLLECTION",
]
