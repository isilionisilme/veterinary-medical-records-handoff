"""FastAPI dependency functions for route handlers."""

from __future__ import annotations

from fastapi import Request

from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage


def get_repository(request: Request) -> DocumentRepository:
    """Return the document repository from application state."""
    return request.app.state.document_repository  # type: ignore[no-any-return]


def get_storage(request: Request) -> FileStorage:
    """Return the file storage from application state."""
    return request.app.state.file_storage  # type: ignore[no-any-return]
