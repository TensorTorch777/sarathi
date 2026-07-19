"""Persistence port for CorpusManifest."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.corpus_manifest import CorpusManifest


class CorpusManifestRepository(Protocol):
    """Store reproducible ingest build records."""

    async def create(self, manifest: CorpusManifest) -> CorpusManifest:
        """Persist a new manifest row."""
        ...

    async def get_by_id(self, manifest_id: UUID) -> CorpusManifest | None:
        """Load by id."""
        ...

    async def get_latest(self, scripture: str, edition: str) -> CorpusManifest | None:
        """Most recent successful import for scripture+edition."""
        ...
