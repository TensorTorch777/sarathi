"""JWT access and refresh token helpers."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt

from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.domain.enums import TokenType, UserRole


@dataclass(slots=True, frozen=True)
class TokenPayload:
    """Validated claims extracted from a JWT."""

    sub: UUID
    role: UserRole
    token_type: TokenType
    jti: str
    exp: datetime


@dataclass(slots=True, frozen=True)
class IssuedToken:
    """A newly issued JWT and its metadata."""

    token: str
    jti: str
    expires_at: datetime


def _encode(settings: Settings, claims: dict[str, Any]) -> str:
    """Encode claims into a signed JWT."""
    return jwt.encode(
        claims,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(
    *,
    user_id: UUID,
    role: UserRole,
    settings: Settings,
) -> IssuedToken:
    """Create a short-lived access token."""
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    jti = str(uuid4())
    token = _encode(
        settings,
        {
            "sub": str(user_id),
            "role": role.value,
            "type": TokenType.ACCESS.value,
            "jti": jti,
            "iat": now,
            "exp": expires_at,
        },
    )
    return IssuedToken(token=token, jti=jti, expires_at=expires_at)


def create_refresh_token(
    *,
    user_id: UUID,
    role: UserRole,
    settings: Settings,
) -> IssuedToken:
    """Create a long-lived refresh token."""
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    jti = str(uuid4())
    token = _encode(
        settings,
        {
            "sub": str(user_id),
            "role": role.value,
            "type": TokenType.REFRESH.value,
            "jti": jti,
            "iat": now,
            "exp": expires_at,
        },
    )
    return IssuedToken(token=token, jti=jti, expires_at=expires_at)


def decode_token(token: str, *, settings: Settings, expected_type: TokenType) -> TokenPayload:
    """Decode and validate a JWT, enforcing the expected token type."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if token_type != expected_type.value:
        raise UnauthorizedError("Invalid token type")

    try:
        sub = UUID(str(payload["sub"]))
        role = UserRole(str(payload["role"]))
        jti = str(payload["jti"])
        exp = datetime.fromtimestamp(int(payload["exp"]), tz=UTC)
    except (KeyError, ValueError, TypeError) as exc:
        raise UnauthorizedError("Malformed token payload") from exc

    return TokenPayload(
        sub=sub,
        role=role,
        token_type=expected_type,
        jti=jti,
        exp=exp,
    )
