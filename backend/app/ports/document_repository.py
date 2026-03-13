"""Document repository ports.

This module keeps backwards compatibility via `DocumentRepository` while
splitting aggregate contracts into dedicated protocols.
"""

from __future__ import annotations

from typing import Protocol

from backend.app.domain.models import (
    Document,
    DocumentWithLatestRun,
    ProcessingStatus,
)
from backend.app.ports.calibration_repository import CalibrationRepository
from backend.app.ports.run_repository import RunRepository


class DocumentCrudRepository(Protocol):
    """Persistence contract for document metadata and list views."""

    def create(self, document: Document, status: ProcessingStatus) -> None:
        """Persist a new document and its initial status history entry."""

    def get(self, document_id: str) -> Document | None:
        """Return a document by id, if it exists."""

    def list_documents(self, *, limit: int, offset: int) -> list[DocumentWithLatestRun]:
        """Return documents with their latest processing run summaries."""

    def count_documents(self) -> int:
        """Return total number of documents."""

    def update_review_status(
        self,
        *,
        document_id: str,
        review_status: str,
        updated_at: str,
        reviewed_at: str | None,
        reviewed_by: str | None,
        reviewed_run_id: str | None,
    ) -> Document | None:
        """Update review metadata and return the updated document."""


class DocumentRepository(
    DocumentCrudRepository,
    RunRepository,
    CalibrationRepository,
    Protocol,
):
    """Backward-compatible aggregate repository contract."""
