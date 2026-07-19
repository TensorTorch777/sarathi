"""Auth use-case mapping helpers."""

from app.application.dto import AuthenticatedUser
from app.domain.entities import User


def to_authenticated_user(user: User) -> AuthenticatedUser:
    """Map a domain user to a public authenticated profile DTO."""
    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        locale=user.locale,
        is_active=user.is_active,
    )
