"""User repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import User


class UserRepository(Protocol):
    """Persistence port for users."""

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by identifier."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by unique email address."""
        ...

    async def get_by_oauth_subject(
        self,
        auth_provider: str,
        oauth_subject: str,
    ) -> User | None:
        """Fetch a user by OAuth provider subject (future social login)."""
        ...

    async def add(self, user: User) -> User:
        """Persist a new user."""
        ...

    async def update(self, user: User) -> User:
        """Persist changes to an existing user."""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by identifier."""
        ...
