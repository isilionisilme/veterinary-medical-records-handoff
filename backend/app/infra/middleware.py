"""ASGI middleware stack."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.app.infra.correlation import (
    generate_request_id,
    request_id_var,
)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Set X-Request-ID on every request and propagate via contextvars."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        incoming_id = request.headers.get("x-request-id", "")
        req_id = incoming_id if incoming_id else generate_request_id()
        token = request_id_var.set(req_id)
        try:
            try:
                response = await call_next(request)
            except Exception:
                response = JSONResponse(
                    status_code=500,
                    content={
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "message": "Internal Server Error",
                    },
                )

            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_var.reset(token)
