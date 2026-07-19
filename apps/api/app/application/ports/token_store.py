"""Token store port for refresh tokens and access-token denylist."""

from datetime import datetime
from typing import Protocol
from uuid import UUID


class TokenStorePort(Protocol):
    """Outbound port for revocable token state (typically Redis)."""

    async def store_refresh_token(
        self,
        *,
        jti: str,
        user_id: UUID,
        expires_at: datetime,
    ) -> None:
        """Persist an active refresh token until expiry."""
        ...

    async def get_refresh_user_id(self, jti: str) -> UUID | None:
        """Return the user id for an active refresh token, if present."""
        ...

    async def revoke_refresh_token(self, jti: str) -> None:
        """Revoke a refresh token immediately."""
        ...

    async def revoke_all_refresh_tokens_for_user(self, user_id: UUID) -> None:
        """Revoke every refresh token belonging to a user."""
        ...

    async def denylist_access_token(self, *, jti: str, expires_at: datetime) -> None:
        """Add an access-token jti to the denylist until it expires."""
        ...

    async def is_access_token_denylisted(self, jti: str) -> bool:
        """Return True if the access-token jti has been revoked."""
        ...
