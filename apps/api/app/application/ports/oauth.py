"""OAuth provider port — architecture ready for future social login."""

from dataclasses import dataclass
from typing import Protocol

from app.domain.enums import AuthProvider


@dataclass(slots=True, frozen=True)
class OAuthUserInfo:
    """Normalized identity payload returned by an OAuth provider."""

    provider: AuthProvider
    subject: str
    email: str
    display_name: str | None
    email_verified: bool


class OAuthProviderPort(Protocol):
    """Outbound port for OAuth authorization-code flows."""

    provider: AuthProvider

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        """Build the provider authorize URL."""
        ...

    async def exchange_code(self, *, code: str, redirect_uri: str) -> OAuthUserInfo:
        """Exchange an authorization code for normalized user info."""
        ...
