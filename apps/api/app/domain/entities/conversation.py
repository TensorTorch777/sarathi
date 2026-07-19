"""Conversation domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Conversation:
    """A chat session between a user and Sarathi AI."""

    id: UUID
    user_id: UUID
    title: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
