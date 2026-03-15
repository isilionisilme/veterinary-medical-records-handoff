"""Processing-related API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.app.api.schemas import (
    ProcessingRunResponse,
    RawTextArtifactResponse,
)
from backend.app.application.documents import get_document
from backend.app.application.processing import enqueue_processing_run
from backend.app.config import processing_enabled
from backend.app.domain.models import ProcessingRunState
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from .deps import get_repository, get_storage
from .route_constants import DOCUMENT_NOT_FOUND_MSG, DocumentIdPath, RunIdPath
from .routes_common import error_response, log_event

router = APIRouter(tags=["Processing"])


@router.post(
    "/documents/{document_id}/reprocess",
    response_model=ProcessingRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new processing run",
    description="Create a new processing run for the document (append-only).",
    responses={404: {"description": "Document not found (NOT_FOUND)."}},
)
def reprocess_document(
    document_id: DocumentIdPath,
    repository: DocumentRepository = Depends(get_repository),
) -> ProcessingRunResponse | JSONResponse:
    """Create a new queued processing run for an existing document."""

    if get_document(document_id=document_id, repository=repository) is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=DOCUMENT_NOT_FOUND_MSG,
        )

    if not processing_enabled():
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message="Processing is disabled.",
        )

    run = enqueue_processing_run(document_id=document_id, repository=repository)
    log_event(
        event_type="REPROCESS_REQUESTED",
        document_id=document_id,
        run_id=run.run_id,
    )
    return ProcessingRunResponse(
        run_id=run.run_id,
        state=run.state.value,
        created_at=run.created_at,
    )


@router.get(
    "/runs/{run_id}/artifacts/raw-text",
    response_model=RawTextArtifactResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve raw extracted text",
    description="Return raw extracted text for a processing run.",
    responses={
        404: {"description": "Run not found (NOT_FOUND)."},
        409: {"description": "Raw text not ready or not available (CONFLICT)."},
        410: {"description": "Raw text artifact missing (ARTIFACT_MISSING)."},
    },
)
def get_raw_text_artifact(
    run_id: RunIdPath,
    repository: DocumentRepository = Depends(get_repository),
    storage: FileStorage = Depends(get_storage),
) -> RawTextArtifactResponse | JSONResponse:
    """Return extracted raw text for a processing run."""
    run = repository.get_run(run_id)
    if run is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Processing run not found.",
        )

    if run.state in {ProcessingRunState.QUEUED, ProcessingRunState.RUNNING}:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message="Raw text is not ready yet.",
            details={"reason": "RAW_TEXT_NOT_READY"},
        )

    if run.state in {ProcessingRunState.FAILED, ProcessingRunState.TIMED_OUT}:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message="Raw text is not available for this run.",
            details={"reason": "RAW_TEXT_NOT_AVAILABLE"},
        )

    if not storage.exists_raw_text(document_id=run.document_id, run_id=run.run_id):
        return error_response(
            status_code=status.HTTP_410_GONE,
            error_code="ARTIFACT_MISSING",
            message="Raw text artifact is missing.",
        )

    try:
        text = storage.resolve_raw_text(document_id=run.document_id, run_id=run.run_id).read_text(
            encoding="utf-8"
        )
    except Exception as exc:  # pragma: no cover - defensive
        log_event(
            event_type="RAW_TEXT_ACCESS_FAILED",
            document_id=run.document_id,
            run_id=run.run_id,
            failure_reason=str(exc),
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while accessing raw text.",
        )

    log_event(
        event_type="RAW_TEXT_ACCESSED",
        document_id=run.document_id,
        run_id=run.run_id,
    )

    return RawTextArtifactResponse(
        run_id=run.run_id,
        artifact_type="RAW_TEXT",
        content_type="text/plain",
        text=text,
    )
