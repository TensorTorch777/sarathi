"""Async engine and session factory lifecycle."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(database_url: str | None = None) -> AsyncEngine:
    """Create (or recreate) the global async engine and session factory."""
    global _engine, _session_factory

    settings = get_settings()
    url = database_url or settings.database_url

    _engine = create_async_engine(
        url,
        echo=settings.app_debug and not settings.is_production,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    return _engine


def get_engine() -> AsyncEngine:
    """Return the initialized async engine."""
    if _engine is None:
        return init_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the initialized session factory."""
    if _session_factory is None:
        init_engine()
    assert _session_factory is not None
    return _session_factory


async def dispose_engine() -> None:
    """Dispose the async engine and clear globals."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
