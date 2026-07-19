"""Logout by revoking access and refresh tokens."""

from app.application.ports import TokenStorePort
from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.core.security import decode_token
from app.domain.enums import TokenType


class LogoutUserUseCase:
    """Revoke the current session tokens."""

    def __init__(self, *, token_store: TokenStorePort, settings: Settings) -> None:
        self._token_store = token_store
        self._settings = settings

    async def execute(self, *, access_token: str, refresh_token: str | None) -> None:
        """Denylist the access token and revoke the refresh token when provided."""
        access_payload = decode_token(
            access_token,
            settings=self._settings,
            expected_type=TokenType.ACCESS,
        )
        await self._token_store.denylist_access_token(
            jti=access_payload.jti,
            expires_at=access_payload.exp,
        )

        if refresh_token:
            try:
                refresh_payload = decode_token(
                    refresh_token,
                    settings=self._settings,
                    expected_type=TokenType.REFRESH,
                )
            except UnauthorizedError:
                return
            await self._token_store.revoke_refresh_token(refresh_payload.jti)
