"""FastAPI dependency providers (composition root helpers)."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports import TokenStorePort
from app.core.config import Settings, get_settings
from app.infrastructure.auth import RedisTokenStore
from app.infrastructure.cache import get_redis
from app.infrastructure.db.session import get_session_factory


async def get_settings_dep() -> Settings:
    """Provide application settings."""
    return get_settings()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped SQLAlchemy async session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_token_store() -> TokenStorePort:
    """Provide the Redis-backed token store."""
    return RedisTokenStore(get_redis())


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenStoreDep = Annotated[TokenStorePort, Depends(get_token_store)]
