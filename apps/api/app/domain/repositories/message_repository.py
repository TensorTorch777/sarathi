"""Message repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Message


class MessageRepository(Protocol):
    """Persistence port for messages."""

    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Fetch a message by identifier."""
        ...

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Message]:
        """List messages in a conversation, oldest first."""
        ...

    async def add(self, message: Message) -> Message:
        """Persist a new message."""
        ...

    async def delete(self, message_id: UUID) -> bool:
        """Delete a message by identifier."""
        ...
