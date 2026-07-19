"""JWT token type claims."""

from enum import StrEnum


class TokenType(StrEnum):
    """Distinguishes access tokens from refresh tokens."""

    ACCESS = "access"
    REFRESH = "refresh"
