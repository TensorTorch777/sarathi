"""Password hashing and verification using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext password matches the stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
