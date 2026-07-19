"""Run context for a single corpus ingestion job."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class IngestRunContext:
    """
    Configuration and bookkeeping for one ingest run.

    Targets one scripture edition; produces a CorpusManifest at the end.
    """

    scripture: str
    edition: str
    language: str
    parser_version: str
    embedding_version: str
    source: str
    publisher: str | None = None
    translator: str | None = None
    license: str | None = None
    edition_version: str = "1.0.0"
    dry_run: bool = False
    skip_qdrant: bool = False
    skip_embeddings: bool = False
    batch_id: str = field(default_factory=lambda: str(uuid4()))
    run_id: UUID = field(default_factory=uuid4)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    # citation_key -> node_id (filled during normalize/persist for related resolve)
    corpus_index: dict[str, UUID] = field(default_factory=dict)

    @property
    def provenance_edition(self) -> str:
        """Edition slug used on every node."""
        return self.edition
