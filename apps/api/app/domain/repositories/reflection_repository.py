"""Reflection repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Reflection


class ReflectionRepository(Protocol):
    """Persistence port for reflections."""

    async def get_by_id(self, reflection_id: UUID) -> Reflection | None:
        """Fetch a reflection by identifier."""
        ...

    async def list_by_journal(
        self,
        journal_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Reflection]:
        """List reflections for a journal entry, newest first."""
        ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Reflection]:
        """List reflections for a user, newest first."""
        ...

    async def add(self, reflection: Reflection) -> Reflection:
        """Persist a new reflection."""
        ...

    async def delete(self, reflection_id: UUID) -> bool:
        """Delete a reflection by identifier."""
        ...
