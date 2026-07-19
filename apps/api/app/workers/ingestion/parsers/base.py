"""Scripture parser protocol — one adapter per future corpus."""

from __future__ import annotations

from typing import Protocol

from app.workers.ingestion.models import RawKnowledgeRecord


class ScriptureParser(Protocol):
    """
    Parse a scripture source into raw knowledge records.

    Implement per corpus (Gita, Upanishads, Ramayana, Mahabharata) without
    changing the pipeline core.
    """

    scripture: str

    async def parse(self, source: str | bytes) -> list[RawKnowledgeRecord]:
        """Parse file path, URI, or in-memory payload into raw records."""
        ...
