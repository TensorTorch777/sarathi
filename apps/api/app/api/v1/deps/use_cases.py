"""Use-case factories for dependency injection."""

from typing import Annotated

from fastapi import Depends

from app.api.v1.deps.auth import TokenStoreDep, UserRepoDep
from app.application.use_cases.auth import (
    GetCurrentUserUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokensUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
)
from app.application.use_cases.answer import GenerateAnswerUseCase
from app.application.use_cases.health import CheckHealthUseCase
from app.application.use_cases.retrieval import RetrieveVersesUseCase
from app.core.di.providers import DbSessionDep, SettingsDep
from app.infrastructure.answer.factory import build_generate_answer_use_case
from app.infrastructure.retrieval import build_retrieve_verses_use_case


async def get_check_health_use_case(session: DbSessionDep) -> CheckHealthUseCase:
    """Build the health-check use case for the current request."""
    return CheckHealthUseCase(session=session)


async def get_register_user_use_case(
    users: UserRepoDep,
    token_store: TokenStoreDep,
    settings: SettingsDep,
) -> RegisterUserUseCase:
    """Build the registration use case."""
    return RegisterUserUseCase(users=users, token_store=token_store, settings=settings)


async def get_login_user_use_case(
    users: UserRepoDep,
    token_store: TokenStoreDep,
    settings: SettingsDep,
) -> LoginUserUseCase:
    """Build the login use case."""
    return LoginUserUseCase(users=users, token_store=token_store, settings=settings)


async def get_logout_user_use_case(
    token_store: TokenStoreDep,
    settings: SettingsDep,
) -> LogoutUserUseCase:
    """Build the logout use case."""
    return LogoutUserUseCase(token_store=token_store, settings=settings)


async def get_refresh_tokens_use_case(
    users: UserRepoDep,
    token_store: TokenStoreDep,
    settings: SettingsDep,
) -> RefreshTokensUseCase:
    """Build the token refresh use case."""
    return RefreshTokensUseCase(users=users, token_store=token_store, settings=settings)


async def get_current_user_use_case(users: UserRepoDep) -> GetCurrentUserUseCase:
    """Build the current-user use case."""
    return GetCurrentUserUseCase(users=users)


async def get_password_reset_use_case(users: UserRepoDep) -> RequestPasswordResetUseCase:
    """Build the password-reset placeholder use case."""
    return RequestPasswordResetUseCase(users=users)


async def get_retrieve_verses_use_case(
    session: DbSessionDep,
    settings: SettingsDep,
) -> RetrieveVersesUseCase:
    """Build the hybrid RAG retrieval use case."""
    return await build_retrieve_verses_use_case(session=session, settings=settings)


async def get_generate_answer_use_case(
    session: DbSessionDep,
    settings: SettingsDep,
) -> GenerateAnswerUseCase:
    """Build the full grounded answer pipeline use case."""
    return await build_generate_answer_use_case(session=session, settings=settings)


CheckHealthUseCaseDep = Annotated[CheckHealthUseCase, Depends(get_check_health_use_case)]
RegisterUserUseCaseDep = Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)]
LoginUserUseCaseDep = Annotated[LoginUserUseCase, Depends(get_login_user_use_case)]
LogoutUserUseCaseDep = Annotated[LogoutUserUseCase, Depends(get_logout_user_use_case)]
RefreshTokensUseCaseDep = Annotated[RefreshTokensUseCase, Depends(get_refresh_tokens_use_case)]
GetCurrentUserUseCaseDep = Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)]
PasswordResetUseCaseDep = Annotated[
    RequestPasswordResetUseCase,
    Depends(get_password_reset_use_case),
]
RetrieveVersesUseCaseDep = Annotated[RetrieveVersesUseCase, Depends(get_retrieve_verses_use_case)]
GenerateAnswerUseCaseDep = Annotated[GenerateAnswerUseCase, Depends(get_generate_answer_use_case)]
