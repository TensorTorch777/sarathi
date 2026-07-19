"""Stub OAuth provider implementing the port for future wiring."""

from app.application.ports import OAuthUserInfo
from app.core.errors import NotImplementedAppError
from app.domain.enums import AuthProvider


class StubOAuthProvider:
    """Placeholder OAuth provider until real social login is configured."""

    def __init__(self, provider: AuthProvider) -> None:
        self.provider = provider

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        """Raise until a real provider is configured."""
        raise NotImplementedAppError(
            f"OAuth provider '{self.provider.value}' is not configured",
            details={"state": state, "redirect_uri": redirect_uri},
        )

    async def exchange_code(self, *, code: str, redirect_uri: str) -> OAuthUserInfo:
        """Raise until a real provider is configured."""
        raise NotImplementedAppError(
            f"OAuth provider '{self.provider.value}' is not configured",
            details={"code": code, "redirect_uri": redirect_uri},
        )
