"""Favorite verse domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class FavoriteVerse:
    """A Gita verse the user has marked as personally meaningful."""

    id: UUID
    user_id: UUID
    verse_id: UUID
    note: str | None
    memory_item_id: UUID | None
    created_at: datetime
    updated_at: datetime
