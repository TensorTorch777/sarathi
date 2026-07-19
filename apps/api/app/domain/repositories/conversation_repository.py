"""Conversation repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Conversation


class ConversationRepository(Protocol):
    """Persistence port for conversations."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Fetch a conversation by identifier."""
        ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
    ) -> list[Conversation]:
        """List conversations for a user, newest first."""
        ...

    async def add(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation."""
        ...

    async def update(self, conversation: Conversation) -> Conversation:
        """Persist changes to an existing conversation."""
        ...

    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation by identifier."""
        ...
