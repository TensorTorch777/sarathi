"""CorpusManifest — reproducible description of an ingested scripture edition."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class CorpusManifest:
    """
    Build record for one scripture edition import.

    Enables reproducing every knowledge-base build (checksum, parser, embeddings).
    """

    id: UUID
    scripture: str
    edition: str
    version: str
    language: str
    parser_version: str
    embedding_version: str
    total_nodes: int
    checksum: str
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    publisher: str | None = None
    translator: str | None = None
    license: str | None = None
    source: str | None = None
    node_type_counts: dict[str, int] = field(default_factory=dict)
    notes: str | None = None
