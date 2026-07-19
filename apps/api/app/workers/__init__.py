"""Background workers — knowledge ingestion and future jobs."""

from app.workers.ingestion import IngestionPipeline, build_ingestion_pipeline

__all__ = ["IngestionPipeline", "build_ingestion_pipeline"]
