"""Authenticate a local user with email and password."""

from app.application.dto import AuthenticatedUser, LoginCommand, TokenPair
from app.application.ports import TokenStorePort
from app.application.use_cases.auth.mappers import to_authenticated_user
from app.application.use_cases.auth.token_service import issue_token_pair
from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.core.security import verify_password
from app.domain.enums import AuthProvider
from app.domain.repositories import UserRepository


class LoginUserUseCase:
    """Validate credentials and issue tokens."""

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

    async def execute(self, command: LoginCommand) -> tuple[AuthenticatedUser, TokenPair]:
        """Login with local credentials."""
        email = command.email.strip().lower()
        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise UnauthorizedError("Invalid email or password")

        if user.auth_provider != AuthProvider.LOCAL or user.hashed_password is None:
            raise UnauthorizedError("This account uses social login")

        if not verify_password(command.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        tokens = await issue_token_pair(
            user=user,
            settings=self._settings,
            token_store=self._token_store,
        )
        return to_authenticated_user(user), tokens
