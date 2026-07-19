"""Map between User ORM models and domain entities."""

from app.domain.entities import User
from app.domain.enums import AuthProvider, UserRole
from app.infrastructure.db.models import User as UserModel


def to_domain(model: UserModel) -> User:
    """Convert an ORM user to a domain entity."""
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        display_name=model.display_name,
        is_active=model.is_active,
        role=UserRole(model.role),
        auth_provider=AuthProvider(model.auth_provider),
        oauth_subject=model.oauth_subject,
        locale=model.locale,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_domain(model: UserModel, entity: User) -> UserModel:
    """Copy mutable domain fields onto an ORM user instance."""
    model.email = entity.email
    model.hashed_password = entity.hashed_password
    model.display_name = entity.display_name
    model.is_active = entity.is_active
    model.role = entity.role.value
    model.auth_provider = entity.auth_provider.value
    model.oauth_subject = entity.oauth_subject
    model.locale = entity.locale
    return model
