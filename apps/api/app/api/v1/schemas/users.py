"""User API schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import UserRole


class UserResponse(BaseModel):
    """Public user profile."""

    id: UUID
    email: EmailStr
    display_name: str | None
    role: UserRole
    locale: str | None
    is_active: bool


class UpdateProfileRequest(BaseModel):
    """Optional profile update fields for /users/me."""

    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, max_length=16)
