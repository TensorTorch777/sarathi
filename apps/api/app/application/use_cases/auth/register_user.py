"""Register a local user account."""

from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto import AuthenticatedUser, RegisterCommand, TokenPair
from app.application.ports import TokenStorePort
from app.application.use_cases.auth.mappers import to_authenticated_user
from app.application.use_cases.auth.token_service import issue_token_pair
from app.core.config import Settings
from app.core.errors import ConflictError, ValidationAppError
from app.core.security import hash_password
from app.domain.entities import User
from app.domain.enums import AuthProvider, UserRole
from app.domain.repositories import UserRepository


class RegisterUserUseCase:
    """Create a local user and return an authenticated token pair."""

    def __init__(
        self,
        *,
        users: UserRepository,
        token_store: TokenStorePort,
        settings: Settings,
    ) -> None:
        self._users = users
        self._token_store = token_store
        self._settings = settings

    async def execute(self, command: RegisterCommand) -> tuple[AuthenticatedUser, TokenPair]:
        """Register a user if the email is available."""
        email = command.email.strip().lower()
        if len(command.password) < 8:
            raise ValidationAppError("Password must be at least 8 characters")

        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ConflictError("A user with this email already exists")

        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hash_password(command.password),
            display_name=command.display_name,
            is_active=True,
            role=UserRole.USER,
            auth_provider=AuthProvider.LOCAL,
            oauth_subject=None,
            locale=None,
            created_at=now,
            updated_at=now,
        )
        created = await self._users.add(user)
        tokens = await issue_token_pair(
            user=created,
            settings=self._settings,
            token_store=self._token_store,
        )
        return to_authenticated_user(created), tokens
