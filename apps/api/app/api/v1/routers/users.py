"""Users API routes."""

from fastapi import APIRouter

from app.api.v1.deps import AdminUserDep, CurrentUserDep, GetCurrentUserUseCaseDep
from app.api.v1.schemas import UserResponse

router = APIRouter(prefix="/users")


def _to_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        locale=user.locale,
        is_active=user.is_active,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current user",
)
async def get_me(
    current_user: CurrentUserDep,
    use_case: GetCurrentUserUseCaseDep,
) -> UserResponse:
    """Return the authenticated user's profile."""
    profile = await use_case.execute(current_user.id)
    return _to_user_response(profile)


@router.get(
    "/admin/ping",
    response_model=UserResponse,
    summary="Admin RBAC check",
)
async def admin_ping(admin_user: AdminUserDep) -> UserResponse:
    """Admin-only ping demonstrating role-based access control."""
    return _to_user_response(admin_user)
