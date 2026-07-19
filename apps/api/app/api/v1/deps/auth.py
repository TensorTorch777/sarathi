"""Authentication and authorization dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.ports import TokenStorePort
from app.core.di.providers import DbSessionDep, SettingsDep, get_token_store
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import TokenPayload, decode_token
from app.domain.entities import User
from app.domain.enums import TokenType, UserRole
from app.domain.repositories import UserRepository
from app.infrastructure.db.repositories import SqlAlchemyUserRepository

_bearer = HTTPBearer(auto_error=False)


async def get_user_repository(session: DbSessionDep) -> UserRepository:
    """Provide the user repository for the current request."""
    return SqlAlchemyUserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
TokenStoreDep = Annotated[TokenStorePort, Depends(get_token_store)]


async def get_token_payload(
    settings: SettingsDep,
    token_store: TokenStoreDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
) -> TokenPayload:
    """Extract and validate a bearer access token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing bearer token")

    payload = decode_token(
        credentials.credentials,
        settings=settings,
        expected_type=TokenType.ACCESS,
    )
    if await token_store.is_access_token_denylisted(payload.jti):
        raise UnauthorizedError("Token has been revoked")
    return payload


TokenPayloadDep = Annotated[TokenPayload, Depends(get_token_payload)]


async def get_current_user(
    payload: TokenPayloadDep,
    users: UserRepoDep,
) -> User:
    """Load the authenticated domain user."""
    user = await users.get_by_id(payload.sub)
    if user is None or not user.is_active:
        raise UnauthorizedError("User is inactive or not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Dependency factory enforcing role-based access control."""

    async def _checker(user: CurrentUserDep) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient permissions")
        return user

    return _checker


AdminUserDep = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
