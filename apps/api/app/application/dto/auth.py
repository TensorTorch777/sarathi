"""Authentication application DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import UserRole


@dataclass(slots=True, frozen=True)
class RegisterCommand:
    """Input for local user registration."""

    email: str
    password: str
    display_name: str | None = None


@dataclass(slots=True, frozen=True)
class LoginCommand:
    """Input for local login."""

    email: str
    password: str


@dataclass(slots=True, frozen=True)
class TokenPair:
    """Issued access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    access_jti: str
    refresh_jti: str
    access_expires_at: datetime
    refresh_expires_at: datetime


@dataclass(slots=True, frozen=True)
class AuthenticatedUser:
    """Public user profile for API responses."""

    id: UUID
    email: str
    display_name: str | None
    role: UserRole
    locale: str | None
    is_active: bool
