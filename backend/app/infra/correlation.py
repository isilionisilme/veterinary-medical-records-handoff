"""Request correlation ID propagation via contextvars."""

from __future__ import annotations

import contextvars
import logging
import uuid

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def get_request_id() -> str:
    """Return the current request correlation ID."""
    return request_id_var.get()


def generate_request_id() -> str:
    """Generate a new UUID4 correlation ID."""
    return uuid.uuid4().hex[:16]


class CorrelationIdFilter(logging.Filter):
    """Inject request_id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()  # type: ignore[attr-defined]
        return True
