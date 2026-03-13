from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.domain.models import (
    Document,
    DocumentWithLatestRun,
    ProcessingRunDetail,
    ProcessingRunSummary,
    StepArtifact,
)
from backend.app.domain.status import DocumentStatusView, derive_document_status, map_status_label
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage


def get_document(*, document_id: str, repository: DocumentRepository) -> Document | None:
    """Retrieve document metadata for status visibility.

    Args:
        document_id: Unique identifier for the document.
        repository: Persistence port used to fetch the document.

    Returns:
        The document metadata, or None when not found.
    """

    return repository.get(document_id)


@dataclass(frozen=True, slots=True)
class DocumentStatusDetails:
    """Document status details derived from the latest processing run."""

    document: Document
    latest_run: ProcessingRunSummary | None
    status_view: DocumentStatusView


@dataclass(frozen=True, slots=True)
class DocumentOriginalLocation:
    """Resolved location and metadata for an original stored document file."""

    document: Document
    file_path: Path
    exists: bool


def get_document_status_details(
    *, document_id: str, repository: DocumentRepository
) -> DocumentStatusDetails | None:
    """Return document metadata with derived status details.

    Args:
        document_id: Unique identifier for the document.
        repository: Persistence port used to fetch document and run summaries.

    Returns:
        Document status details or None when the document does not exist.
    """

    document = repository.get(document_id)
    if document is None:
        return None

    latest_run = repository.get_latest_run(document_id)
    status_view = derive_document_status(latest_run)
    return DocumentStatusDetails(document=document, latest_run=latest_run, status_view=status_view)


def get_document_original_location(
    *, document_id: str, repository: DocumentRepository, storage: FileStorage
) -> DocumentOriginalLocation | None:
    """Resolve the stored location for an original uploaded document.

    Args:
        document_id: Unique identifier for the document.
        repository: Persistence port used to fetch document metadata.
        storage: File storage adapter used to resolve file locations.

    Returns:
        The resolved file location and metadata, or None when the document is missing.
    """

    document = repository.get(document_id)
    if document is None:
        return None

    return DocumentOriginalLocation(
        document=document,
        file_path=storage.resolve(storage_path=document.storage_path),
        exists=storage.exists(storage_path=document.storage_path),
    )


@dataclass(frozen=True, slots=True)
class ProcessingStepHistory:
    """Single step row for document processing history."""

    step_name: str
    step_status: str
    attempt: int
    started_at: str | None
    ended_at: str | None
    error_code: str | None


@dataclass(frozen=True, slots=True)
class ProcessingRunHistory:
    """Run row for document processing history."""

    run_id: str
    state: str
    failure_type: str | None
    started_at: str | None
    completed_at: str | None
    steps: list[ProcessingStepHistory]


@dataclass(frozen=True, slots=True)
class ProcessingHistory:
    """Document processing history response model for API adapters."""

    document_id: str
    runs: list[ProcessingRunHistory]


def get_processing_history(
    *, document_id: str, repository: DocumentRepository
) -> ProcessingHistory | None:
    """Return chronological processing history for a document.

    Args:
        document_id: Unique identifier for the document.
        repository: Persistence port used to fetch runs and artifacts.

    Returns:
        Processing history when the document exists; otherwise None.
    """

    if repository.get(document_id) is None:
        return None

    run_rows = repository.list_processing_runs(document_id=document_id)
    runs = [_to_processing_run_history(run, repository) for run in run_rows]
    return ProcessingHistory(document_id=document_id, runs=runs)


def _to_processing_run_history(
    run: ProcessingRunDetail, repository: DocumentRepository
) -> ProcessingRunHistory:
    return ProcessingRunHistory(
        run_id=run.run_id,
        state=run.state.value,
        failure_type=run.failure_type,
        started_at=run.started_at,
        completed_at=run.completed_at,
        steps=[
            _to_processing_step_history(step)
            for step in repository.list_step_artifacts(run_id=run.run_id)
        ],
    )


def _to_processing_step_history(step: StepArtifact) -> ProcessingStepHistory:
    return ProcessingStepHistory(
        step_name=step.step_name.value,
        step_status=step.step_status.value,
        attempt=step.attempt,
        started_at=step.started_at,
        ended_at=step.ended_at,
        error_code=step.error_code,
    )


@dataclass(frozen=True, slots=True)
class DocumentListItem:
    """Document list entry with derived status metadata."""

    document_id: str
    original_filename: str
    created_at: str
    status: str
    status_label: str
    failure_type: str | None
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


@dataclass(frozen=True, slots=True)
class DocumentListResult:
    """Paginated document list result."""

    items: list[DocumentListItem]
    limit: int
    offset: int
    total: int


def list_documents(
    *,
    repository: DocumentRepository,
    limit: int,
    offset: int,
) -> DocumentListResult:
    """List documents with derived status for list views.

    Args:
        repository: Persistence port used to fetch documents and run summaries.
        limit: Maximum number of documents to return.
        offset: Pagination offset.

    Returns:
        Paginated list of document entries with derived status.
    """

    rows = repository.list_documents(limit=limit, offset=offset)
    total = repository.count_documents()
    items = [_to_list_item(row=row) for row in rows]
    return DocumentListResult(items=items, limit=limit, offset=offset, total=total)


def _to_list_item(*, row: DocumentWithLatestRun) -> DocumentListItem:
    status_view = derive_document_status(row.latest_run)
    return DocumentListItem(
        document_id=row.document.document_id,
        original_filename=row.document.original_filename,
        created_at=row.document.created_at,
        status=status_view.status.value,
        status_label=map_status_label(status_view.status),
        failure_type=status_view.failure_type,
        review_status=row.document.review_status.value,
        reviewed_at=row.document.reviewed_at,
        reviewed_by=row.document.reviewed_by,
    )
