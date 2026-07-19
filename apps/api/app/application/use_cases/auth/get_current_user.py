"""Resolve the authenticated user profile."""

from uuid import UUID

from app.application.dto import AuthenticatedUser
from app.application.use_cases.auth.mappers import to_authenticated_user
from app.core.errors import UnauthorizedError
from app.domain.repositories import UserRepository


class GetCurrentUserUseCase:
    """Load the current user by id from an authenticated context."""

    def __init__(self, *, users: UserRepository) -> None:
        self._users = users

    async def execute(self, user_id: UUID) -> AuthenticatedUser:
        """Return the public profile for an active user."""
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is inactive or not found")
        return to_authenticated_user(user)
