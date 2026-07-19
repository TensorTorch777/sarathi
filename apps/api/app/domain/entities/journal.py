"""Journal domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Journal:
    """Private user journal entry."""

    id: UUID
    user_id: UUID
    title: str | None
    content: str
    mood_note: str | None
    created_at: datetime
    updated_at: datetime
