"""Review-related API routes."""

from __future__ import annotations

import html
import re
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
from backend.app.application.documents._shared import _locate_visit_date_occurrences_from_raw_text
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from .routes_common import error_response, log_event

router = APIRouter(tags=["Review"])
UUID_PATH_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
DocumentIdPath = Annotated[str, Path(..., pattern=UUID_PATH_PATTERN)]
RunIdPath = Annotated[str, Path(..., pattern=UUID_PATH_PATTERN)]
_NEXT_VISIT_BOUNDARY_PATTERN = re.compile(
    r"(?:\s*)?visita\s+(?:consulta\s+general|administrativa)\s+del\s+d[ií]a",
    re.IGNORECASE,
)
_NON_ANCHORED_RAW_CONTEXT_SENTINELS = {
    "Raw text no disponible para este run.",
    "No se pudieron inferir offsets de contexto en raw text.",
    "Sin ancla de fecha para recortar contexto.",
    "Sin ventana de contexto disponible.",
}


def _render_visit_debug_html(*, document_id: str, visit_sections: list[dict[str, str]]) -> str:
    cards: list[str] = []
    for section in visit_sections:
        title = html.escape(section["title"])
        subtitle = html.escape(section["subtitle"])
        raw_context = html.escape(section["raw_context"])
        cards.append(
            "<section style='border:1px solid #d8dee6;border-radius:10px;padding:12px;"
            "margin:12px 0;background:#fff;'>"
            f"<h3 style='margin:0 0 6px 0;font-size:16px;color:#1f2937;'>{title}</h3>"
            f"<p style='margin:0 0 10px 0;color:#4b5563;font-size:13px;'>{subtitle}</p>"
            "<pre style='white-space:pre-wrap;word-break:break-word;background:#f8fafc;"
            "border:1px solid #e5e7eb;border-radius:8px;padding:10px;font-size:13px;"
            "line-height:1.45;max-height:360px;overflow:auto;'>"
            f"{raw_context}"
            "</pre>"
            "</section>"
        )

    cards_html = "".join(cards) if cards else "<p>No hay visitas disponibles.</p>"
    escaped_document_id = html.escape(document_id)
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8' />"
        f"<title>Visit Debug - {escaped_document_id}</title>"
        "</head><body style='font-family:Segoe UI,Arial,sans-serif;background:#f3f4f6;"
        "margin:0;padding:20px;color:#111827;'>"
        f"<h1 style='margin:0 0 12px 0;'>Debug de visitas - {escaped_document_id}</h1>"
        "<p style='margin:0 0 18px 0;color:#374151;'>"
        "Vista temporal de diagnóstico. Muestra el texto crudo asociado a cada visita."
        "</p>"
        f"{cards_html}"
        "</body></html>"
    )


def _build_visit_debug_sections(*, visits: object, raw_text: str | None) -> list[dict[str, str]]:
    if not isinstance(visits, list):
        return []

    assigned_visits = [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    if not assigned_visits:
        return []

    if not isinstance(raw_text, str) or not raw_text.strip():
        return [
            {
                "title": f"Visita {index + 1} ({visit.get('visit_date') or 'sin fecha'})",
                "subtitle": f"visit_id={visit.get('visit_id') or 'n/a'}",
                "raw_context": "Raw text no disponible para este run.",
            }
            for index, visit in enumerate(assigned_visits)
        ]

    offsets_by_date: dict[str, list[int]] = {}
    for normalized_date, offset in _locate_visit_date_occurrences_from_raw_text(raw_text=raw_text):
        offsets_by_date.setdefault(normalized_date, []).append(offset)

    consumed_by_date: dict[str, int] = {}
    sections_with_offsets: list[tuple[dict[str, str], int | None]] = []
    for index, visit in enumerate(assigned_visits):
        visit_id = str(visit.get("visit_id") or "n/a")
        visit_date = visit.get("visit_date")
        normalized_date = visit_date if isinstance(visit_date, str) else None
        anchor_offset: int | None = None
        if normalized_date is not None:
            offsets = offsets_by_date.get(normalized_date, [])
            consumed = consumed_by_date.get(normalized_date, 0)
            if consumed < len(offsets):
                anchor_offset = offsets[consumed]
                consumed_by_date[normalized_date] = consumed + 1

        sections_with_offsets.append(
            (
                {
                    "title": f"Visita {index + 1} ({normalized_date or 'sin fecha'})",
                    "subtitle": f"visit_id={visit_id}",
                    "raw_context": "",
                },
                anchor_offset,
            )
        )

    sorted_anchors = sorted(
        [
            (idx, offset)
            for idx, (_, offset) in enumerate(sections_with_offsets)
            if offset is not None
        ],
        key=lambda item: item[1],
    )
    if not sorted_anchors:
        for section, _ in sections_with_offsets:
            section["raw_context"] = "No se pudieron inferir offsets de contexto en raw text."
        return [section for section, _ in sections_with_offsets]

    offset_windows: dict[int, tuple[int, int]] = {}
    for anchor_index, (section_index, start_offset) in enumerate(sorted_anchors):
        next_start = (
            sorted_anchors[anchor_index + 1][1]
            if anchor_index + 1 < len(sorted_anchors)
            else len(raw_text)
        )
        offset_windows[section_index] = (start_offset, next_start)

    for section_index, (section, offset) in enumerate(sections_with_offsets):
        if offset is None:
            section["raw_context"] = "Sin ancla de fecha para recortar contexto."
            continue
        window = offset_windows.get(section_index)
        if window is None:
            section["raw_context"] = "Sin ventana de contexto disponible."
            continue
        start_offset, end_offset = window
        window_text = raw_text[start_offset:end_offset]
        boundary_match = _NEXT_VISIT_BOUNDARY_PATTERN.search(window_text)
        if boundary_match is not None and boundary_match.start() > 0:
            end_offset = start_offset + boundary_match.start()

        section["raw_context"] = raw_text[start_offset:end_offset].strip() or "(vacío)"

    return [section for section, _ in sections_with_offsets]


def _build_visit_scoping_metrics(*, visits: object, raw_text: str | None) -> dict[str, object]:
    if not isinstance(visits, list):
        return {
            "summary": {
                "total_visits": 0,
                "assigned_visits": 0,
                "anchored_visits": 0,
                "unassigned_field_count": 0,
                "raw_text_available": bool(raw_text and raw_text.strip()),
            },
            "visits": [],
        }

    assigned_visits = [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    raw_text_available = bool(isinstance(raw_text, str) and raw_text.strip())
    debug_sections = _build_visit_debug_sections(visits=visits, raw_text=raw_text)
    metrics_rows: list[dict[str, object]] = []

    for index, visit in enumerate(assigned_visits):
        fields = visit.get("fields")
        field_count = (
            len([field for field in fields if isinstance(field, dict)])
            if isinstance(fields, list)
            else 0
        )
        section = debug_sections[index] if index < len(debug_sections) else None
        raw_context = section["raw_context"] if isinstance(section, dict) else ""
        anchored = (
            raw_text_available
            and bool(raw_context)
            and (raw_context not in _NON_ANCHORED_RAW_CONTEXT_SENTINELS)
        )

        metrics_rows.append(
            {
                "visit_index": index + 1,
                "visit_id": visit.get("visit_id"),
                "visit_date": visit.get("visit_date"),
                "field_count": field_count,
                "anchored_in_raw_text": anchored,
                "raw_context_chars": len(raw_context) if anchored else 0,
            }
        )

    unassigned_field_count = 0
    for visit in visits:
        if not isinstance(visit, dict) or visit.get("visit_id") != "unassigned":
            continue
        fields = visit.get("fields")
        if isinstance(fields, list):
            unassigned_field_count += len([field for field in fields if isinstance(field, dict)])

    anchored_visits = len(
        [
            visit_metrics
            for visit_metrics in metrics_rows
            if visit_metrics["anchored_in_raw_text"] is True
        ]
    )

    return {
        "summary": {
            "total_visits": len(visits),
            "assigned_visits": len(assigned_visits),
            "anchored_visits": anchored_visits,
            "unassigned_field_count": unassigned_field_count,
            "raw_text_available": raw_text_available,
        },
        "visits": metrics_rows,
    }


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
    visit_sections = _build_visit_debug_sections(visits=visits, raw_text=raw_text)
    html_body = _render_visit_debug_html(document_id=document_id, visit_sections=visit_sections)
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
    payload = _build_visit_scoping_metrics(visits=visits, raw_text=raw_text)
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
