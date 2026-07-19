"""Embedding lifecycle for knowledge nodes."""

from enum import StrEnum


class EmbeddingStatus(StrEnum):
    """Whether a dense vector exists for the active embedding version."""

    PENDING = "pending"
    INDEXED = "indexed"
    STALE = "stale"
    FAILED = "failed"
    SKIPPED = "skipped"
