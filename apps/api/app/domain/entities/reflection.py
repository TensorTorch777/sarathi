"""Reflection domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Reflection:
    """Grounded reflection tied to a journal entry."""

    id: UUID
    journal_id: UUID
    user_id: UUID
    verse_id: UUID | None
    content: str
    created_at: datetime
    updated_at: datetime
