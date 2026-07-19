"""Shared token issuance helpers for auth use cases."""

from datetime import UTC, datetime

from app.application.dto import TokenPair
from app.application.ports import TokenStorePort
from app.core.config import Settings
from app.core.security import create_access_token, create_refresh_token
from app.domain.entities import User


async def issue_token_pair(
    *,
    user: User,
    settings: Settings,
    token_store: TokenStorePort,
) -> TokenPair:
    """Create access/refresh tokens and persist the refresh token."""
    access = create_access_token(user_id=user.id, role=user.role, settings=settings)
    refresh = create_refresh_token(user_id=user.id, role=user.role, settings=settings)
    await token_store.store_refresh_token(
        jti=refresh.jti,
        user_id=user.id,
        expires_at=refresh.expires_at,
    )
    expires_in = max(int((access.expires_at - datetime.now(UTC)).total_seconds()), 0)
    return TokenPair(
        access_token=access.token,
        refresh_token=refresh.token,
        token_type="bearer",
        expires_in=expires_in,
        access_jti=access.jti,
        refresh_jti=refresh.jti,
        access_expires_at=access.expires_at,
        refresh_expires_at=refresh.expires_at,
    )
