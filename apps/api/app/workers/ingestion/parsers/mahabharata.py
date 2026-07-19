"""Mahabharata parser stub — register when corpus is ready."""

from __future__ import annotations

from app.workers.ingestion.errors import IngestStageError
from app.workers.ingestion.models import RawKnowledgeRecord


class MahabharataParser:
    """Placeholder for future Mahabharata imports (parva / adhyaya / verse)."""

    scripture = "mahabharata"

    async def parse(self, source: str | bytes) -> list[RawKnowledgeRecord]:
        """Not implemented — architecture hook only."""
        raise IngestStageError(
            "parse",
            "MahabharataParser is a stub; provide a corpus adapter before ingest.",
        )
