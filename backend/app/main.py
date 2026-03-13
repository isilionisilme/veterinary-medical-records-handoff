"""FastAPI application factory and composition root.

This module wires the HTTP API layer to application services and infrastructure
adapters. It is intentionally lightweight: routes remain thin adapters and
business logic lives in the application/domain layers.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from http import HTTPStatus
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.routes import MAX_UPLOAD_SIZE as ROUTE_MAX_UPLOAD_SIZE
from backend.app.api.routes import router as api_router
from backend.app.application.processing import processing_scheduler
from backend.app.config import (
    auth_token,
    confidence_policy_explicit_config_diagnostics,
    processing_enabled,
)
from backend.app.infra import database
from backend.app.infra.correlation import get_request_id
from backend.app.infra.file_storage import LocalFileStorage
from backend.app.infra.middleware import CorrelationIdMiddleware
from backend.app.infra.rate_limiter import limiter
from backend.app.infra.scheduler_lifecycle import SchedulerLifecycle
from backend.app.infra.sqlite_document_repository import SqliteDocumentRepository
from backend.app.logging_config import configure_logging
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage
from backend.app.settings import clear_settings_cache, get_settings

logger = logging.getLogger(__name__)
startup_logger = logging.getLogger("uvicorn.error")
_DEV_ENV_MARKERS = {"dev", "development", "local"}


def _is_dev_runtime() -> bool:
    clear_settings_cache()
    settings = get_settings()
    env_name = (settings.env or settings.app_env or settings.vet_records_env or "").strip().lower()
    if env_name in _DEV_ENV_MARKERS:
        return True
    uvicorn_reload = (settings.uvicorn_reload or "").strip().lower()
    if uvicorn_reload in {"1", "true", "yes", "on"}:
        return True
    if "--reload" in sys.argv:
        return True
    return False


def _load_backend_dotenv_for_dev(
    *, dotenv_path: Path | None = None, dev_runtime: bool | None = None
) -> bool:
    target_path = dotenv_path or (Path(__file__).resolve().parents[1] / ".env")
    is_dev = _is_dev_runtime() if dev_runtime is None else dev_runtime
    if not is_dev:
        startup_logger.debug(
            "backend .env auto-load skipped (non-dev runtime) path=%s", target_path
        )
        return False
    if not target_path.exists():
        startup_logger.info("backend .env not found for dev auto-load path=%s", target_path)
        return False
    loaded = load_dotenv(dotenv_path=target_path, override=False)
    clear_settings_cache()
    startup_logger.info(
        "backend .env auto-load path=%s loaded=%s",
        target_path,
        loaded,
    )
    return loaded


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    This function is the composition root for the backend service. It wires the
    API router, configures the document repository adapter, and ensures the
    database schema exists at startup.

    Returns:
        The configured FastAPI application instance.

    Side Effects:
        - Ensures the SQLite schema exists on application startup.
        - Sets `app.state.document_repository` for request handlers.
        - Re-exports `MAX_UPLOAD_SIZE` for compatibility with existing imports.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """FastAPI lifespan handler used to perform startup initialization."""

        configure_logging(settings.log_level)
        database.ensure_schema()
        repository = cast(DocumentRepository, app.state.document_repository)
        storage = cast(FileStorage, app.state.file_storage)
        (
            is_policy_configured,
            policy_reason,
            policy_missing_keys,
            policy_invalid_keys,
        ) = confidence_policy_explicit_config_diagnostics()
        startup_logger.info(
            "confidence_policy startup status configured=%s reason=%s "
            "missing_keys=%s invalid_keys=%s",
            is_policy_configured,
            policy_reason,
            policy_missing_keys,
            policy_invalid_keys,
        )
        recovered = repository.recover_orphaned_runs(completed_at=_now_iso())
        if recovered:
            logger.info("Recovered %s orphaned runs", recovered)
        app.state.scheduler = SchedulerLifecycle(scheduler_fn=processing_scheduler)
        if processing_enabled():
            await app.state.scheduler.start(repository=repository, storage=storage)
        yield
        await app.state.scheduler.stop()

    settings = get_settings()

    app = FastAPI(
        title="Veterinary Medical Records API",
        description=(
            "API for registering veterinary medical record documents and tracking their "
            "processing lifecycle (Release 0: metadata only)."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        try:
            http_status = HTTPStatus(exc.status_code)
            error_code = http_status.name
            default_message = http_status.phrase
        except ValueError:
            error_code = "HTTP_ERROR"
            default_message = "HTTP error"

        message = str(exc.detail) if isinstance(exc.detail, str) else default_message
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": error_code,
                "message": message,
                "request_id": get_request_id(),
            },
        )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    cors_origins = _get_cors_origins()
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type"],
        )
    app.state.document_repository = SqliteDocumentRepository()
    app.state.file_storage = LocalFileStorage()
    app.state.settings = settings
    app.state.auth_token = auth_token()

    @app.middleware("http")
    async def _optional_api_auth_middleware(request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        configured_token = app.state.auth_token
        if not configured_token:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        scheme, _, credentials = auth_header.partition(" ")
        if scheme.lower() != "bearer" or credentials != configured_token:
            return JSONResponse(
                status_code=401,
                content={
                    "error_code": "UNAUTHORIZED",
                    "message": "Missing or invalid bearer token.",
                    "request_id": get_request_id(),
                },
            )

        return await call_next(request)

    app.add_middleware(CorrelationIdMiddleware)

    global MAX_UPLOAD_SIZE
    MAX_UPLOAD_SIZE = ROUTE_MAX_UPLOAD_SIZE  # re-export for compatibility
    app.include_router(api_router)
    app.include_router(api_router, prefix="/api")

    @app.get("/version", summary="Release metadata")
    def version() -> dict[str, str]:
        metadata = app.state.settings
        return {
            "version": metadata.app_version,
            "commit": metadata.git_commit,
            "build_date": metadata.build_date,
        }

    return app


def _get_cors_origins() -> list[str]:
    """Return the configured list of CORS origins for local development.

    Uses the comma-separated `VET_RECORDS_CORS_ORIGINS` environment variable.
    Defaults to the local Vite dev server origins when unset.
    """

    raw = get_settings().vet_records_cors_origins
    if raw is None:
        default_origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:80",
            "http://127.0.0.1:80",
        ]
        for port in (5173, 15173, 25173, 35173):
            default_origins.extend(
                [
                    f"http://localhost:{port}",
                    f"http://127.0.0.1:{port}",
                ]
            )
        return default_origins
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins


_load_backend_dotenv_for_dev()
app = create_app()
