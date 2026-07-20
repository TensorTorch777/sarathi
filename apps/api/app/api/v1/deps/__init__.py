"""Route-level dependency wiring."""

from app.api.v1.deps.auth import (
    AdminUserDep,
    CurrentUserDep,
    TokenPayloadDep,
    TokenStoreDep,
    UserRepoDep,
    require_roles,
)
from app.api.v1.deps.use_cases import (
    CheckHealthUseCaseDep,
    ConversationalAnswerUseCaseDep,
    GenerateAnswerUseCaseDep,
    GetCurrentUserUseCaseDep,
    LoginUserUseCaseDep,
    LogoutUserUseCaseDep,
    PasswordResetUseCaseDep,
    RefreshTokensUseCaseDep,
    RegisterUserUseCaseDep,
    RetrieveVersesUseCaseDep,
)

__all__ = [
    "AdminUserDep",
    "CheckHealthUseCaseDep",
    "ConversationalAnswerUseCaseDep",
    "CurrentUserDep",
    "GenerateAnswerUseCaseDep",
    "GetCurrentUserUseCaseDep",
    "LoginUserUseCaseDep",
    "LogoutUserUseCaseDep",
    "PasswordResetUseCaseDep",
    "RefreshTokensUseCaseDep",
    "RegisterUserUseCaseDep",
    "RetrieveVersesUseCaseDep",
    "TokenPayloadDep",
    "TokenStoreDep",
    "UserRepoDep",
    "require_roles",
]
