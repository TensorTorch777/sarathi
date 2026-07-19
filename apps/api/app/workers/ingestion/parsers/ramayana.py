"""Ramayana parser stub — register when corpus is ready."""

from __future__ import annotations

from app.workers.ingestion.errors import IngestStageError
from app.workers.ingestion.models import RawKnowledgeRecord


class RamayanaParser:
    """Placeholder for future Ramayana imports (kanda / sarga / verse)."""

    scripture = "ramayana"

    async def parse(self, source: str | bytes) -> list[RawKnowledgeRecord]:
        """Not implemented — architecture hook only."""
        raise IngestStageError(
            "parse",
            "RamayanaParser is a stub; provide a corpus adapter before ingest.",
        )
