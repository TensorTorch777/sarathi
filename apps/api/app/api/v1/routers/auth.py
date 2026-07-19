"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.v1.deps import (
    LoginUserUseCaseDep,
    LogoutUserUseCaseDep,
    PasswordResetUseCaseDep,
    RefreshTokensUseCaseDep,
    RegisterUserUseCaseDep,
)
from app.api.v1.schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.dto import LoginCommand, RegisterCommand
from app.core.errors import NotImplementedAppError, UnauthorizedError

router = APIRouter(prefix="/auth")
_bearer = HTTPBearer(auto_error=False)


def _to_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        locale=user.locale,
        is_active=user.is_active,
    )


def _to_token_response(tokens) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCaseDep,
) -> AuthResponse:
    """Create a local account and return tokens."""
    user, tokens = await use_case.execute(
        RegisterCommand(
            email=str(body.email),
            password=body.password,
            display_name=body.display_name,
        ),
    )
    return AuthResponse(user=_to_user_response(user), tokens=_to_token_response(tokens))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
)
async def login(
    body: LoginRequest,
    use_case: LoginUserUseCaseDep,
) -> AuthResponse:
    """Authenticate with email and password."""
    user, tokens = await use_case.execute(
        LoginCommand(email=str(body.email), password=body.password),
    )
    return AuthResponse(user=_to_user_response(user), tokens=_to_token_response(tokens))


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
)
async def logout(
    use_case: LogoutUserUseCaseDep,
    body: LogoutRequest | None = None,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ] = None,
) -> MessageResponse:
    """Revoke the current access token and optional refresh token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing bearer token")
    refresh_token = body.refresh_token if body is not None else None
    await use_case.execute(
        access_token=credentials.credentials,
        refresh_token=refresh_token,
    )
    return MessageResponse(message="Logged out")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
)
async def refresh(
    body: RefreshRequest,
    use_case: RefreshTokensUseCaseDep,
) -> TokenResponse:
    """Rotate refresh token and issue a new access token."""
    tokens = await use_case.execute(body.refresh_token)
    return _to_token_response(tokens)


@router.post(
    "/password-reset",
    response_model=PasswordResetResponse,
    summary="Request password reset (placeholder)",
)
async def password_reset(
    body: PasswordResetRequest,
    use_case: PasswordResetUseCaseDep,
) -> PasswordResetResponse:
    """Placeholder password-reset endpoint (no email sent yet)."""
    result = await use_case.execute(str(body.email))
    return PasswordResetResponse(**result)


@router.get(
    "/oauth/{provider}/authorize",
    summary="OAuth authorize (placeholder)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def oauth_authorize(provider: str) -> None:
    """OAuth-ready placeholder for provider authorization redirects."""
    raise NotImplementedAppError(
        f"OAuth provider '{provider}' is not configured yet",
        details={"provider": provider},
    )


@router.get(
    "/oauth/{provider}/callback",
    summary="OAuth callback (placeholder)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def oauth_callback(provider: str, code: str | None = None, state: str | None = None) -> None:
    """OAuth-ready placeholder for provider callbacks."""
    raise NotImplementedAppError(
        f"OAuth callback for '{provider}' is not implemented yet",
        details={"provider": provider, "code": code, "state": state},
    )
