"""User domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import AuthProvider, UserRole


@dataclass(slots=True)
class User:
    """Authenticated application user."""

    id: UUID
    email: str
    hashed_password: str | None
    display_name: str | None
    is_active: bool
    role: UserRole
    auth_provider: AuthProvider
    oauth_subject: str | None
    locale: str | None
    created_at: datetime
    updated_at: datetime
