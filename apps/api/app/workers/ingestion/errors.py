"""Ingestion pipeline errors."""


class IngestError(Exception):
    """Base error for knowledge-base ingestion."""


class IngestStageError(IngestError):
    """A pipeline stage failed for one or more records."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(f"[{stage}] {message}")


class ValidationFailedError(IngestError):
    """Record failed structural validation."""

    def __init__(self, message: str, *, record_id: str | None = None) -> None:
        self.record_id = record_id
        super().__init__(message)
