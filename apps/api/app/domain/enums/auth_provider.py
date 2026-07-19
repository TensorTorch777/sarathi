"""Authentication provider enumeration (local + OAuth-ready)."""

from enum import StrEnum


class AuthProvider(StrEnum):
    """Identity provider used to authenticate a user."""

    LOCAL = "local"
    GOOGLE = "google"
    APPLE = "apple"
    GITHUB = "github"
