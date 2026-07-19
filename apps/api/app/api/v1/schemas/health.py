"""Health endpoint schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """HTTP response for health checks."""

    status: str = Field(description="Overall health status: ok or degraded")
    checks: dict[str, str] = Field(description="Per-dependency status map")
