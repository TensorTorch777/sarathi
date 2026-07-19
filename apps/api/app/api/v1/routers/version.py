"""Version metadata routes."""

from fastapi import APIRouter

from app.api.v1.schemas import VersionResponse
from app.core.di.providers import SettingsDep

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Application version",
    description="Returns build and environment metadata.",
)
async def version(settings: SettingsDep) -> VersionResponse:
    """Return the configured application version."""
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        api="v1",
    )
