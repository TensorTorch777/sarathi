"""Feedback domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Feedback:
    """User feedback on an assistant message."""

    id: UUID
    user_id: UUID
    message_id: UUID
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime
