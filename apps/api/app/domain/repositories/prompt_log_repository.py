"""PromptLog repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import PromptLog


class PromptLogRepository(Protocol):
    """Persistence port for LLM prompt audit logs."""

    async def get_by_id(self, prompt_log_id: UUID) -> PromptLog | None:
        """Fetch a prompt log by identifier."""
        ...

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PromptLog]:
        """List prompt logs for a conversation, newest first."""
        ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PromptLog]:
        """List prompt logs for a user, newest first."""
        ...

    async def add(self, prompt_log: PromptLog) -> PromptLog:
        """Append a new prompt log entry."""
        ...
