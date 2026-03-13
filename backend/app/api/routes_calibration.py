"""Extraction observability/calibration API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from backend.app.api.schemas import (
    ExtractionRunPersistResponse,
    ExtractionRunsAggregateSummaryResponse,
    ExtractionRunsListResponse,
    ExtractionRunSnapshotRequest,
    ExtractionRunTriageResponse,
)
from backend.app.application.extraction_observability import (
    get_extraction_runs,
    get_latest_extraction_run_triage,
    persist_extraction_run_snapshot,
    summarize_extraction_runs,
)
from backend.app.config import extraction_observability_enabled

from .routes_common import error_response, extraction_observability_disabled_response

router = APIRouter(tags=["Calibration"])
logger = logging.getLogger(__name__)


@router.post(
    "/debug/extraction-runs",
    response_model=ExtractionRunPersistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Persist extraction observability snapshot",
    description="Persist extraction run snapshot locally and log diff versus previous run.",
)
def persist_debug_extraction_run(
    payload: ExtractionRunSnapshotRequest,
) -> ExtractionRunPersistResponse | JSONResponse:
    if not extraction_observability_enabled():
        return extraction_observability_disabled_response()

    try:
        result = persist_extraction_run_snapshot(payload.model_dump())
    except ValueError as exc:
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_REQUEST",
            message=str(exc),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to persist extraction observability snapshot")
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while persisting extraction snapshot.",
            details={"reason": str(exc)},
        )

    response_payload = ExtractionRunPersistResponse(
        document_id=str(result["document_id"]),
        run_id=str(result["run_id"]),
        stored_runs=int(result["stored_runs"]),
        changed_fields=int(result["changed_fields"]),
    )
    response_status = (
        status.HTTP_201_CREATED if bool(result.get("was_created", True)) else status.HTTP_200_OK
    )
    return JSONResponse(
        status_code=response_status,
        content=response_payload.model_dump(),
    )


@router.get(
    "/debug/extraction-runs/{document_id}",
    response_model=ExtractionRunsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get persisted extraction observability snapshots",
    description="Return persisted extraction snapshots for a document (latest first).",
)
def list_debug_extraction_runs(document_id: str) -> ExtractionRunsListResponse | JSONResponse:
    if not extraction_observability_enabled():
        return extraction_observability_disabled_response()

    runs = get_extraction_runs(document_id)
    return ExtractionRunsListResponse(document_id=document_id, runs=runs)


@router.get(
    "/debug/extraction-runs/{document_id}/triage",
    response_model=ExtractionRunTriageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get extraction triage for latest persisted run",
    description="Return triage report for the latest persisted extraction snapshot.",
)
def get_debug_extraction_run_triage(document_id: str) -> ExtractionRunTriageResponse | JSONResponse:
    if not extraction_observability_enabled():
        return extraction_observability_disabled_response()

    triage = get_latest_extraction_run_triage(document_id)
    if triage is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="No extraction snapshots found for this document.",
        )

    return ExtractionRunTriageResponse(**triage)


@router.get(
    "/debug/extraction-runs/{document_id}/summary",
    response_model=ExtractionRunsAggregateSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated extraction evidence for recent runs",
    description=(
        "Aggregate missing/rejected/accepted counts over latest persisted runs and expose "
        "representative top1 samples for triage."
    ),
)
def get_debug_extraction_run_summary(
    document_id: str,
    limit: int = Query(20, ge=1, le=20, description="How many latest runs to aggregate."),
    run_id: str | None = Query(
        None,
        description="Optional run id to summarize a specific persisted extraction snapshot.",
    ),
) -> ExtractionRunsAggregateSummaryResponse | JSONResponse:
    if not extraction_observability_enabled():
        return extraction_observability_disabled_response()

    if isinstance(run_id, str):
        run_id = run_id.strip() or None

    summary = summarize_extraction_runs(document_id=document_id, limit=limit, run_id=run_id)
    if summary is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="No extraction snapshots found for this document.",
        )

    return ExtractionRunsAggregateSummaryResponse(**summary)
