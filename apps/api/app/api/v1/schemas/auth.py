"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.api.v1.schemas.users import UserResponse


class RegisterRequest(BaseModel):
    """Local registration payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    """Local login payload."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh-token rotation payload."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Optional refresh token to revoke on logout."""

    refresh_token: str | None = None


class PasswordResetRequest(BaseModel):
    """Password-reset request payload (placeholder)."""

    email: EmailStr


class TokenResponse(BaseModel):
    """Bearer token pair returned by auth endpoints."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Authenticated session response including user profile."""

    user: UserResponse
    tokens: TokenResponse


class PasswordResetResponse(BaseModel):
    """Neutral acknowledgement for password-reset placeholder."""

    status: str
    message: str


class MessageResponse(BaseModel):
    """Simple status message."""

    message: str
