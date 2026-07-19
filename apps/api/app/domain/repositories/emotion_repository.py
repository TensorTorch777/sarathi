"""Emotion repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Emotion


class EmotionRepository(Protocol):
    """Persistence port for emotion taxonomy labels."""

    async def get_by_id(self, emotion_id: UUID) -> Emotion | None:
        """Fetch an emotion by identifier."""
        ...

    async def get_by_slug(self, slug: str) -> Emotion | None:
        """Fetch an emotion by unique slug."""
        ...

    async def list_all(self) -> list[Emotion]:
        """List all emotion labels."""
        ...

    async def add(self, emotion: Emotion) -> Emotion:
        """Persist a new emotion label."""
        ...
