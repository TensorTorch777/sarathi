"""Journal repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Journal


class JournalRepository(Protocol):
    """Persistence port for journal entries."""

    async def get_by_id(self, journal_id: UUID) -> Journal | None:
        """Fetch a journal entry by identifier."""
        ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Journal]:
        """List journal entries for a user, newest first."""
        ...

    async def add(self, journal: Journal) -> Journal:
        """Persist a new journal entry."""
        ...

    async def update(self, journal: Journal) -> Journal:
        """Persist changes to an existing journal entry."""
        ...

    async def delete(self, journal_id: UUID) -> bool:
        """Delete a journal entry by identifier."""
        ...
