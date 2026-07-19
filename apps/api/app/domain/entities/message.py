"""Message domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import MessageRole


@dataclass(slots=True)
class Message:
    """A single message within a conversation."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    updated_at: datetime
