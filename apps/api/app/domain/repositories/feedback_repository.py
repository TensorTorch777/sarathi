"""Feedback repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Feedback


class FeedbackRepository(Protocol):
    """Persistence port for message feedback."""

    async def get_by_id(self, feedback_id: UUID) -> Feedback | None:
        """Fetch feedback by identifier."""
        ...

    async def get_by_user_and_message(self, user_id: UUID, message_id: UUID) -> Feedback | None:
        """Fetch feedback submitted by a user for a specific message."""
        ...

    async def list_by_message(self, message_id: UUID) -> list[Feedback]:
        """List all feedback for a message."""
        ...

    async def add(self, feedback: Feedback) -> Feedback:
        """Persist new feedback."""
        ...

    async def update(self, feedback: Feedback) -> Feedback:
        """Persist changes to existing feedback."""
        ...
