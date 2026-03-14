"""Shared helpers for API route modules."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def error_response(
    *, status_code: int, error_code: str, message: str, details: dict[str, Any] | None = None
) -> JSONResponse:
    payload: dict[str, Any] = {"error_code": error_code, "message": message}
    if details:
        payload["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def extraction_observability_disabled_response() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "extraction_observability_disabled",
            "hint": "Set VET_RECORDS_EXTRACTION_OBS=1 and restart backend",
        },
    )


def log_event(
    *,
    event_type: str,
    document_id: str | None,
    run_id: str | None = None,
    error_code: str | None = None,
    failure_reason: str | None = None,
    access_type: str | None = None,
    count_returned: int | None = None,
) -> None:
    payload: dict[str, Any] = {
        "event_type": event_type,
        "document_id": document_id,
        "run_id": run_id,
        "step_name": None,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if error_code:
        payload["error_code"] = error_code
    if failure_reason:
        payload["failure_reason"] = failure_reason
    if access_type:
        payload["access_type"] = access_type
    if count_returned is not None:
        payload["count_returned"] = count_returned
    logger.info(json.dumps(payload))


def _request_content_length(request: Request) -> int | None:
    content_length = request.headers.get("content-length")
    if content_length is None:
        return None
    try:
        return int(content_length)
    except ValueError:
        return None
