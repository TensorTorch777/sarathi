"""Validation lifecycle for ingested knowledge nodes."""

from enum import StrEnum


class ValidationStatus(StrEnum):
    """Whether a node passed structural and content validation."""

    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
