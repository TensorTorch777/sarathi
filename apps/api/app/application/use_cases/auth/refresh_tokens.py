"""Rotate refresh tokens and issue a new access token."""

from app.application.dto import TokenPair
from app.application.ports import TokenStorePort
from app.application.use_cases.auth.token_service import issue_token_pair
from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.core.security import decode_token
from app.domain.enums import TokenType
from app.domain.repositories import UserRepository


class RefreshTokensUseCase:
    """Exchange a valid refresh token for a new token pair."""

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

    async def execute(self, refresh_token: str) -> TokenPair:
        """Validate, revoke, and rotate the refresh token."""
        payload = decode_token(
            refresh_token,
            settings=self._settings,
            expected_type=TokenType.REFRESH,
        )
        stored_user_id = await self._token_store.get_refresh_user_id(payload.jti)
        if stored_user_id is None or stored_user_id != payload.sub:
            raise UnauthorizedError("Refresh token is revoked or unknown")

        user = await self._users.get_by_id(payload.sub)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is inactive or not found")

        await self._token_store.revoke_refresh_token(payload.jti)
        return await issue_token_pair(
            user=user,
            settings=self._settings,
            token_store=self._token_store,
        )
