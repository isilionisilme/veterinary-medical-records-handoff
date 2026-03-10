"""Review-related API routes."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Path, Request, status
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.api.schemas import (
    ActiveInterpretationReviewResponse,
    DocumentReviewResponse,
    ErrorResponse,
    InterpretationEditRequest,
    InterpretationEditResponse,
    LatestCompletedRunReviewResponse,
    RawTextArtifactAvailabilityResponse,
    ReviewStatusToggleResponse,
    VisitScopingMetricsResponse,
)
from backend.app.application.document_service import (
    apply_interpretation_edits,
    get_document,
    get_document_review,
    mark_document_reviewed,
    reopen_document_review,
)
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from .review_debug import (
    build_visit_debug_sections,
    build_visit_scoping_metrics,
    render_visit_debug_html,
)
from .routes_common import error_response, log_event

router = APIRouter(tags=["Review"])
UUID_PATH_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
DocumentIdPath = Annotated[str, Path(..., pattern=UUID_PATH_PATTERN)]
RunIdPath = Annotated[str, Path(..., pattern=UUID_PATH_PATTERN)]


def _resolve_review_context(
    *,
    document_id: str,
    repository: DocumentRepository,
    storage: FileStorage,
) -> tuple[object | None, str | None] | JSONResponse:
    review = get_document_review(
        document_id=document_id,
        repository=repository,
        storage=storage,
    )
    if review is None or review.review is None:
        reason = (review.unavailable_reason if review is not None else None) or "NO_COMPLETED_RUN"
        message = (
            "Review is not available until a completed run exists."
            if reason == "NO_COMPLETED_RUN"
            else "Review interpretation is not available for the latest completed run."
        )
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details={"reason": reason},
        )

    raw_text: str | None = None
    run_id = review.review.latest_completed_run.run_id
    if storage.exists_raw_text(document_id=document_id, run_id=run_id):
        try:
            raw_text = storage.resolve_raw_text(document_id=document_id, run_id=run_id).read_text(
                encoding="utf-8"
            )
        except OSError:
            raw_text = None
    return review.review, raw_text


@router.get(
    "/documents/{document_id}/review",
    response_model=DocumentReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get review context for a document",
    description="Return latest completed run and its active interpretation.",
    responses={
        404: {"description": "Document not found (NOT_FOUND)."},
        409: {"description": "No completed run available for review (CONFLICT)."},
    },
)
def get_document_review_context(
    request: Request, document_id: DocumentIdPath
) -> DocumentReviewResponse | JSONResponse:
    """Return review context based on the latest completed run."""

    repository = cast(DocumentRepository, request.app.state.document_repository)
    storage = cast(FileStorage, request.app.state.file_storage)
    if get_document(document_id=document_id, repository=repository) is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )

    review = get_document_review(
        document_id=document_id,
        repository=repository,
        storage=storage,
    )
    if review is None:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message="Review context is not available.",
            details={"reason": "NO_COMPLETED_RUN"},
        )
    if review.review is None:
        reason = review.unavailable_reason or "NO_COMPLETED_RUN"
        message = (
            "Review is not available until a completed run exists."
            if reason == "NO_COMPLETED_RUN"
            else "Review interpretation is not available for the latest completed run."
        )
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details={"reason": reason},
        )

    log_event(
        event_type="DOCUMENT_REVIEW_VIEWED",
        document_id=document_id,
        run_id=review.review.latest_completed_run.run_id,
    )

    return DocumentReviewResponse(
        document_id=review.review.document_id,
        latest_completed_run=LatestCompletedRunReviewResponse(
            run_id=review.review.latest_completed_run.run_id,
            state=review.review.latest_completed_run.state,
            completed_at=review.review.latest_completed_run.completed_at,
            failure_type=review.review.latest_completed_run.failure_type,
        ),
        active_interpretation=ActiveInterpretationReviewResponse(
            interpretation_id=review.review.active_interpretation.interpretation_id,
            version_number=review.review.active_interpretation.version_number,
            data=review.review.active_interpretation.data,
        ),
        raw_text_artifact=RawTextArtifactAvailabilityResponse(
            run_id=review.review.raw_text_artifact.run_id,
            available=review.review.raw_text_artifact.available,
        ),
        review_status=review.review.review_status,
        reviewed_at=review.review.reviewed_at,
        reviewed_by=review.review.reviewed_by,
    )


@router.get(
    "/documents/{document_id}/review/debug/visits",
    response_model=None,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Debug visit context as HTML",
    description="Render a temporary HTML page with per-visit raw text context.",
    responses={
        404: {"description": "Document not found (NOT_FOUND)."},
        409: {"description": "No completed run available for review (CONFLICT)."},
    },
)
def get_document_review_visit_debug_page(
    request: Request, document_id: DocumentIdPath
) -> HTMLResponse | JSONResponse:
    repository = cast(DocumentRepository, request.app.state.document_repository)
    storage = cast(FileStorage, request.app.state.file_storage)
    if get_document(document_id=document_id, repository=repository) is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )

    resolved = _resolve_review_context(
        document_id=document_id, repository=repository, storage=storage
    )
    if isinstance(resolved, JSONResponse):
        return resolved
    review_data, raw_text = resolved
    visits = review_data.active_interpretation.data.get("visits")
    visit_sections = build_visit_debug_sections(visits=visits, raw_text=raw_text)
    html_body = render_visit_debug_html(document_id=document_id, visit_sections=visit_sections)
    return HTMLResponse(content=html_body, status_code=status.HTTP_200_OK)


@router.get(
    "/documents/{document_id}/review/debug/visit-scoping",
    response_model=VisitScopingMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get visit scoping observability metrics",
    description="Return per-visit assignment and raw text anchoring coverage metrics.",
    responses={
        404: {"description": "Document not found (NOT_FOUND)."},
        409: {"description": "No completed run available for review (CONFLICT)."},
    },
)
def get_document_review_visit_scoping_observability(
    request: Request, document_id: DocumentIdPath
) -> JSONResponse:
    repository = cast(DocumentRepository, request.app.state.document_repository)
    storage = cast(FileStorage, request.app.state.file_storage)
    if get_document(document_id=document_id, repository=repository) is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )

    resolved = _resolve_review_context(
        document_id=document_id, repository=repository, storage=storage
    )
    if isinstance(resolved, JSONResponse):
        return resolved
    review_data, raw_text = resolved
    visits = review_data.active_interpretation.data.get("visits")
    payload = build_visit_scoping_metrics(visits=visits, raw_text=raw_text)
    payload["document_id"] = document_id
    payload["run_id"] = review_data.latest_completed_run.run_id
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@router.post(
    "/documents/{document_id}/reviewed",
    response_model=ReviewStatusToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark a document as reviewed",
    description="Idempotently mark a document as reviewed.",
    responses={404: {"description": "Document not found (NOT_FOUND)."}},
)
def mark_document_reviewed_route(
    request: Request,
    document_id: DocumentIdPath,
) -> ReviewStatusToggleResponse | JSONResponse:
    repository = cast(DocumentRepository, request.app.state.document_repository)
    result = mark_document_reviewed(document_id=document_id, repository=repository)
    if result is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )
    return ReviewStatusToggleResponse(
        document_id=result.document_id,
        review_status=result.review_status,
        reviewed_at=result.reviewed_at,
        reviewed_by=result.reviewed_by,
    )


@router.delete(
    "/documents/{document_id}/reviewed",
    response_model=ReviewStatusToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="Reopen a reviewed document",
    description="Idempotently reopen a reviewed document.",
    responses={404: {"description": "Document not found (NOT_FOUND)."}},
)
def reopen_document_review_route(
    request: Request,
    document_id: DocumentIdPath,
) -> ReviewStatusToggleResponse | JSONResponse:
    repository = cast(DocumentRepository, request.app.state.document_repository)
    result = reopen_document_review(document_id=document_id, repository=repository)
    if result is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )
    return ReviewStatusToggleResponse(
        document_id=result.document_id,
        review_status=result.review_status,
        reviewed_at=result.reviewed_at,
        reviewed_by=result.reviewed_by,
    )


@router.post(
    "/runs/{run_id}/interpretations",
    response_model=InterpretationEditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interpretation version for a run",
    description="Apply veterinarian edits by creating a new active interpretation version.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request payload (INVALID_REQUEST)."},
        422: {"model": ErrorResponse, "description": "Validation error (UNPROCESSABLE_ENTITY)."},
        404: {"description": "Processing run not found (NOT_FOUND)."},
        409: {"description": "Editing blocked by run/version constraints (CONFLICT)."},
    },
)
def edit_run_interpretation(
    request: Request,
    run_id: RunIdPath,
    payload: InterpretationEditRequest,
) -> InterpretationEditResponse | JSONResponse:
    repository = cast(DocumentRepository, request.app.state.document_repository)
    outcome = apply_interpretation_edits(
        run_id=run_id,
        base_version_number=payload.base_version_number,
        changes=[change.model_dump() for change in payload.changes],
        repository=repository,
    )
    if outcome is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Processing run not found.",
        )

    if outcome.invalid_reason is not None:
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_REQUEST",
            message="Interpretation edit payload is invalid.",
            details={"reason": outcome.invalid_reason},
        )

    if outcome.conflict_reason is not None:
        reason = outcome.conflict_reason
        message = {
            "REVIEW_BLOCKED_BY_ACTIVE_RUN": (
                "Review and editing are blocked while a processing run is active."
            ),
            "INTERPRETATION_NOT_AVAILABLE": (
                "Interpretation editing is only available for completed runs."
            ),
            "INTERPRETATION_MISSING": "Interpretation is not available for this run.",
            "BASE_VERSION_MISMATCH": "Interpretation version conflict. Refresh and retry.",
        }.get(reason, "Interpretation editing is not available.")
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details={"reason": reason},
        )

    if outcome.result is None:  # pragma: no cover - defensive
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while editing interpretation.",
        )

    log_event(
        event_type="INTERPRETATION_EDITED",
        document_id=None,
        run_id=run_id,
    )
    return InterpretationEditResponse(
        run_id=outcome.result.run_id,
        interpretation_id=outcome.result.interpretation_id,
        version_number=outcome.result.version_number,
        data=outcome.result.data,
    )
