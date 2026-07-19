"""Provenance for a KnowledgeNode (edition, license, checksum)."""

from dataclasses import dataclass


@dataclass(slots=True)
class Provenance:
    """Where a knowledge unit came from and under what rights."""

    source: str
    edition: str
    publisher: str | None = None
    translator: str | None = None
    license: str | None = None
    checksum: str | None = None
