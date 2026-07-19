"""Startup and shutdown lifecycle for the FastAPI app."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.cache import dispose_redis, init_redis
from app.infrastructure.db.session import dispose_engine, init_engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down shared resources."""
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.log_json)
    init_engine(settings.database_url)
    await init_redis(settings.redis_url)
    logger.info(
        "application_started",
        app=settings.app_name,
        env=settings.app_env,
        version=settings.app_version,
    )
    if settings.voice_enabled and settings.voice_warmup_on_startup:
        try:
            from app.infrastructure.voice.piper_tts import get_piper_tts
            from app.infrastructure.voice.whisper_stt import get_whisper_stt

            await get_whisper_stt().warmup()
            await get_piper_tts().warmup()
            logger.info("voice_services_warmed")
        except Exception as exc:  # noqa: BLE001
            logger.warning("voice_warmup_failed", error=str(exc))
    try:
        yield
    finally:
        await dispose_redis()
        await dispose_engine()
        logger.info("application_stopped")
