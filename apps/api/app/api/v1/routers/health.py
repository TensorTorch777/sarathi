"""Health check routes."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.api.v1.deps import CheckHealthUseCaseDep
from app.api.v1.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns process liveness and dependency readiness.",
)
async def health(use_case: CheckHealthUseCaseDep) -> JSONResponse:
    """Execute the health-check use case and map status to HTTP codes."""
    result = await use_case.execute()
    payload = HealthResponse(status=result.status, checks=result.checks)
    http_status = (
        status.HTTP_200_OK if result.status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=http_status, content=payload.model_dump())
