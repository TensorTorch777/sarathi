"""Editorial lifecycle for Sarathi Intelligence enrichments."""

from enum import StrEnum


class EditorialStatus(StrEnum):
    """
    generated → reviewed → approved → locked

    generated: AI / first draft
    reviewed:  human checked (edits optional)
    approved:  ready for production use
    locked:    no automatic changes; explicit review required to edit
    """

    GENERATED = "generated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    LOCKED = "locked"


# Legacy alias used in early Chapter 2 drafts
LEGACY_DRAFT = "draft"


def normalize_status(value: str | None) -> EditorialStatus:
    """Map legacy 'draft' to generated; validate others."""
    if value is None or value == LEGACY_DRAFT:
        return EditorialStatus.GENERATED
    return EditorialStatus(value)
