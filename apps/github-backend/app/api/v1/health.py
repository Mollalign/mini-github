"""Liveness & readiness probes."""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.common.responses import HealthResponse
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_sessionmaker

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Liveness probe")
async def liveness() -> HealthResponse:
    """Check if the FastAPI application process is up and running."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version="0.1.0",
        db=True, 
    )


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
async def readiness(response: Response) -> HealthResponse:
    """Verify that backend operational dependencies are accepting network requests."""
    settings = get_settings()
    db_ok = False

    try:
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001 — readiness must not raise raw exceptions
        logger.error("readiness_probe_database_failed", error=str(exc))
        db_ok = False

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        environment=settings.environment,
        version="0.1.0",
        db=db_ok,
    )
