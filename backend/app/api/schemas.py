"""Pydantic schemas for HTTP request/response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Health status: 'healthy' or 'degraded'")
    database: str = Field(description="Database connectivity status")
    storage: str = Field(description="File storage status")


class ErrorResponse(BaseModel):
    detail: str = Field(description="Human-readable error message")


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    status: str = Field(..., description="Current processing status of the document.")
    created_at: str = Field(..., description="UTC ISO timestamp when the document was registered.")


class ProcessingRunResponse(BaseModel):
    run_id: str = Field(..., description="Unique identifier of the processing run.")
    state: str = Field(..., description="Current processing run state.")
    created_at: str = Field(..., description="UTC ISO timestamp when the run was created.")


class LatestRunResponse(BaseModel):
    run_id: str = Field(..., description="Unique identifier of the processing run.")
    state: str = Field(..., description="Current processing run state.")
    failure_type: str | None = Field(
        None, description="Failure category for the run when applicable."
    )


class DocumentResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    original_filename: str = Field(..., description="Original filename recorded at upload time.")
    content_type: str = Field(..., description="MIME type recorded at upload time.")
    file_size: int = Field(..., description="File size in bytes.")
    created_at: str = Field(..., description="UTC ISO timestamp when the document was registered.")
    updated_at: str = Field(
        ..., description="UTC ISO timestamp when the document was last updated."
    )
    status: str = Field(..., description="Current processing status of the document.")
    status_message: str = Field(
        ..., description="Human-readable explanation of the current status."
    )
    failure_type: str | None = Field(
        None, description="Failure category when processing failed or timed out."
    )
    review_status: str = Field(..., description="Human review state for the document.")
    reviewed_at: str | None = Field(
        None, description="UTC ISO timestamp when the document was marked as reviewed."
    )
    reviewed_by: str | None = Field(
        None, description="Optional user identifier that marked the document as reviewed."
    )
    latest_run: LatestRunResponse | None = Field(
        None, description="Latest processing run summary when available."
    )


class DocumentListItemResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    original_filename: str = Field(..., description="Original filename recorded at upload time.")
    created_at: str = Field(..., description="UTC ISO timestamp when the document was registered.")
    status: str = Field(..., description="Current processing status of the document.")
    status_label: str = Field(..., description="User-facing status label for list display.")
    failure_type: str | None = Field(
        None, description="Failure category when processing failed or timed out."
    )
    review_status: str = Field(..., description="Human review state for the document.")
    reviewed_at: str | None = Field(
        None, description="UTC ISO timestamp when the document was marked as reviewed."
    )
    reviewed_by: str | None = Field(
        None, description="Optional user identifier that marked the document as reviewed."
    )


class DocumentListResponse(BaseModel):
    items: list[DocumentListItemResponse] = Field(
        ..., description="Paginated list of documents with derived status."
    )
    limit: int = Field(..., description="Maximum number of items returned.")
    offset: int = Field(..., description="Pagination offset.")
    total: int = Field(..., description="Total number of documents available.")


class ProcessingStepResponse(BaseModel):
    step_name: str = Field(..., description="Step identifier.")
    step_status: str = Field(..., description="Step execution status.")
    attempt: int = Field(..., description="Attempt number for this step status.")
    started_at: str | None = Field(None, description="UTC ISO timestamp for step start.")
    ended_at: str | None = Field(None, description="UTC ISO timestamp for step end.")
    error_code: str | None = Field(None, description="Step-level error code when failed.")


class ProcessingHistoryRunResponse(BaseModel):
    run_id: str = Field(..., description="Unique identifier of the processing run.")
    state: str = Field(..., description="Processing run state.")
    failure_type: str | None = Field(None, description="Run-level failure category.")
    started_at: str | None = Field(None, description="UTC ISO timestamp when the run started.")
    completed_at: str | None = Field(None, description="UTC ISO timestamp when the run completed.")
    steps: list[ProcessingStepResponse] = Field(
        ..., description="Step statuses derived from STEP_STATUS artifacts."
    )


class ProcessingHistoryResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    runs: list[ProcessingHistoryRunResponse] = Field(
        ..., description="Chronological processing runs and their steps."
    )


class RawTextArtifactResponse(BaseModel):
    run_id: str = Field(..., description="Unique identifier of the processing run.")
    artifact_type: str = Field(..., description="Artifact type identifier.")
    content_type: str = Field(..., description="Content type for the raw text artifact.")
    text: str = Field(..., description="Extracted raw text content.")


class LatestCompletedRunReviewResponse(BaseModel):
    run_id: str = Field(..., description="Unique identifier of the latest completed run.")
    state: str = Field(..., description="Processing run state.")
    completed_at: str | None = Field(None, description="UTC ISO timestamp when the run completed.")
    failure_type: str | None = Field(None, description="Run-level failure category.")


class ActiveInterpretationReviewResponse(BaseModel):
    interpretation_id: str = Field(..., description="Active interpretation identifier.")
    version_number: int = Field(..., description="Active interpretation version number.")
    data: dict[str, object] = Field(..., description="Structured interpretation payload.")


class RawTextArtifactAvailabilityResponse(BaseModel):
    run_id: str = Field(..., description="Processing run identifier.")
    available: bool = Field(..., description="Whether raw text is available for this run.")


class DocumentReviewResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    latest_completed_run: LatestCompletedRunReviewResponse = Field(
        ..., description="Latest completed run used for review."
    )
    active_interpretation: ActiveInterpretationReviewResponse = Field(
        ..., description="Active interpretation for the review run."
    )
    raw_text_artifact: RawTextArtifactAvailabilityResponse = Field(
        ..., description="Raw text availability for the review run."
    )
    review_status: str = Field(..., description="Human review state for the document.")
    reviewed_at: str | None = Field(
        None, description="UTC ISO timestamp when the document was marked as reviewed."
    )
    reviewed_by: str | None = Field(
        None, description="Optional user identifier that marked the document as reviewed."
    )


class ReviewStatusToggleResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document.")
    review_status: str = Field(..., description="Updated human review state.")
    reviewed_at: str | None = Field(None, description="UTC ISO timestamp for reviewed state.")
    reviewed_by: str | None = Field(
        None, description="Optional user identifier that marked the document as reviewed."
    )


class InterpretationChangeRequest(BaseModel):
    op: Literal["ADD", "UPDATE", "DELETE"] = Field(..., description="Change operation to apply.")
    field_id: str | None = Field(None, description="Existing field identifier for UPDATE/DELETE.")
    key: str | None = Field(None, description="Field key for ADD operations.")
    value: object | None = Field(None, description="Field value for ADD/UPDATE operations.")
    value_type: str | None = Field(None, description="Field value type for ADD/UPDATE operations.")


class InterpretationEditRequest(BaseModel):
    base_version_number: int = Field(
        ..., ge=1, description="Expected active interpretation version number."
    )
    changes: list[InterpretationChangeRequest] = Field(
        ..., min_length=1, description="List of field-level changes to apply."
    )


class InterpretationEditResponse(BaseModel):
    run_id: str = Field(..., description="Processing run identifier.")
    interpretation_id: str = Field(..., description="New active interpretation identifier.")
    version_number: int = Field(..., description="New active interpretation version number.")
    data: dict[str, object] = Field(..., description="Updated structured interpretation payload.")


class ExtractionFieldSnapshotRequest(BaseModel):
    status: Literal["missing", "rejected", "accepted"] = Field(
        ..., description="Field extraction status."
    )
    confidence: Literal["low", "mid", "high"] | None = Field(
        None, description="Confidence bucket when applicable."
    )
    valueNormalized: str | None = Field(
        None, description="Final normalized value used by the UI when accepted."
    )
    valueRaw: str | None = Field(
        None, description="Optional raw extracted value before normalization."
    )
    reason: str | None = Field(
        None, description="Validator rejection reason when status is rejected."
    )
    rawCandidate: str | None = Field(
        None, description="Optional raw candidate value used during extraction triage."
    )
    sourceHint: str | None = Field(
        None, description="Optional source location hint for the raw candidate."
    )
    topCandidates: list[dict[str, object]] | None = Field(
        None,
        description="Optional top candidate list (max 3) with value/confidence/source hints.",
    )


class ExtractionCountsSnapshotRequest(BaseModel):
    totalFields: int
    accepted: int
    rejected: int
    missing: int
    low: int
    mid: int
    high: int


class ExtractionRunSnapshotRequest(BaseModel):
    runId: str
    documentId: str
    createdAt: str
    schemaVersion: Literal["canonical"]
    fields: dict[str, ExtractionFieldSnapshotRequest]
    counts: ExtractionCountsSnapshotRequest


class ExtractionRunPersistResponse(BaseModel):
    document_id: str
    run_id: str
    stored_runs: int
    changed_fields: int


class ExtractionRunsListResponse(BaseModel):
    document_id: str
    runs: list[dict[str, object]]


class ExtractionTriageSummaryResponse(BaseModel):
    accepted: int
    missing: int
    rejected: int
    low: int
    mid: int
    high: int


class ExtractionTriageItemResponse(BaseModel):
    field: str
    value: str | None = None
    reason: str | None = None
    flags: list[str] = Field(default_factory=list)
    rawCandidate: str | None = None
    sourceHint: str | None = None


class ExtractionRunTriageResponse(BaseModel):
    documentId: str
    runId: str
    createdAt: str
    summary: ExtractionTriageSummaryResponse
    missing: list[ExtractionTriageItemResponse]
    rejected: list[ExtractionTriageItemResponse]
    suspiciousAccepted: list[ExtractionTriageItemResponse]


class ExtractionRunFieldSummaryResponse(BaseModel):
    field: str
    missing_count: int
    rejected_count: int
    accepted_count: int
    suspicious_count: int
    has_candidates: bool = False
    missing_with_candidates_count: int = 0
    missing_without_candidates_count: int = 0
    top1_sample: str | None = None
    avg_conf: float | None = None
    avg_top1_conf: float | None = None
    top_key_tokens: str | None = None


class ExtractionRunsAggregateSummaryResponse(BaseModel):
    document_id: str
    total_runs: int
    considered_runs: int
    missing_fields_with_candidates: int = 0
    missing_fields_without_candidates: int = 0
    fields: list[ExtractionRunFieldSummaryResponse]
    most_missing_fields: list[ExtractionRunFieldSummaryResponse]
    most_rejected_fields: list[ExtractionRunFieldSummaryResponse]


# --- Clinic address lookup ---


class ClinicAddressLookupRequest(BaseModel):
    clinic_name: str = Field(
        ..., min_length=1, description="Name of the clinic to look up the address for."
    )


class ClinicAddressLookupResponse(BaseModel):
    found: bool = Field(description="Whether a matching address was found.")
    address: str | None = Field(None, description="The resolved clinic address, if found.")
    source: str = Field(description="Source of the lookup result (e.g. 'clinic_catalog').")
