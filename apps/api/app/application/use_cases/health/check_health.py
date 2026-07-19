"""Health check use case — reports process liveness and dependency readiness."""

from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(slots=True)
class HealthStatus:
    """Aggregated health report for the API process and dependencies."""

    status: str
    checks: dict[str, str] = field(default_factory=dict)


class CheckHealthUseCase:
    """Determine API health without business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> HealthStatus:
        """Return overall status and per-dependency checks."""
        checks: dict[str, str] = {"api": "ok"}

        try:
            await self._session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"

        overall = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
        return HealthStatus(status=overall, checks=checks)
