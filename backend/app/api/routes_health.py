"""Health-related API routes."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Response

from backend.app.api.schemas import HealthResponse
from backend.app.infra import database
from backend.app.settings import get_settings

router = APIRouter(tags=["Health"])


def _build_dependency_health() -> HealthResponse:
    """Build health payload with dependency checks for DB and storage."""

    overall = "healthy"
    database_status = "ok"
    storage_status = "ok"

    try:
        db_path = database.get_database_path()
        with database.get_connection() as conn:
            conn.execute("SELECT 1")
        _ = db_path
    except Exception as exc:  # pragma: no cover - exercised by tests with stubs
        _ = exc
        database_status = "error"
        overall = "degraded"

    try:
        storage_path = Path(get_settings().vet_records_storage_path)
        if storage_path.exists() and os.access(storage_path, os.W_OK):
            storage_status = "ok"
        else:
            storage_status = "error"
            overall = "degraded"
    except Exception as exc:  # pragma: no cover - exercised by tests with stubs
        _ = exc
        storage_status = "error"
        overall = "degraded"

    return HealthResponse(
        status=overall,
        database=database_status,
        storage=storage_status,
    )


@router.get("/health/live", summary="Liveness probe")
def liveness() -> dict[str, str]:
    """Trivial liveness probe that only checks process responsiveness."""

    return {"status": "alive"}


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Compatibility readiness check",
    description=(
        "Compatibility endpoint that retains historical /health behavior while "
        "exposing readiness semantics. Use /health/live for liveness probes and "
        "/health/ready for readiness probes."
    ),
)
def health(response: Response) -> HealthResponse:
    """Compatibility health endpoint that behaves like readiness."""

    payload = _build_dependency_health()
    response.status_code = 200 if payload.status == "healthy" else 503
    return payload


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Readiness probe",
    description="Check that backend dependencies are functional.",
)
def readiness(response: Response) -> HealthResponse:
    """Readiness probe that checks dependency accessibility."""

    payload = _build_dependency_health()
    response.status_code = 200 if payload.status == "healthy" else 503
    return payload
