"""User role enumeration for RBAC."""

from enum import StrEnum


class UserRole(StrEnum):
    """Application roles used for authorization checks."""

    USER = "user"
    ADMIN = "admin"
