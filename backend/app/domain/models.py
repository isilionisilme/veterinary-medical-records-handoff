"""Domain models for veterinary medical records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProcessingStatus(str, Enum):
    """Derived document status values exposed to clients."""

    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class ProcessingRunState(str, Enum):
    """Processing run lifecycle states."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class StepName(str, Enum):
    """Processing pipeline step identifiers."""

    EXTRACTION = "EXTRACTION"
    INTERPRETATION = "INTERPRETATION"


class StepStatus(str, Enum):
    """Per-step lifecycle state stored in STEP_STATUS artifacts."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class ReviewStatus(str, Enum):
    """Human review status for a document."""

    IN_REVIEW = "IN_REVIEW"
    REVIEWED = "REVIEWED"


@dataclass(frozen=True, slots=True)
class Document:
    """Immutable document metadata record stored by the system."""

    document_id: str
    original_filename: str
    content_type: str
    file_size: int
    storage_path: str
    created_at: str
    updated_at: str
    review_status: ReviewStatus
    reviewed_at: str | None = None
    reviewed_by: str | None = None
    reviewed_run_id: str | None = None


@dataclass(frozen=True, slots=True)
class ProcessingRunSummary:
    """Minimal view of a processing run for status derivation."""

    run_id: str
    state: ProcessingRunState
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class ProcessingRun:
    """Processing run record used by the in-process scheduler."""

    run_id: str
    document_id: str
    state: ProcessingRunState
    created_at: str


@dataclass(frozen=True, slots=True)
class ProcessingRunDetail:
    """Detailed processing run data for processing history views."""

    run_id: str
    state: ProcessingRunState
    created_at: str
    started_at: str | None
    completed_at: str | None
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class ProcessingRunDetails:
    """Detailed processing run data including document ownership."""

    run_id: str
    document_id: str
    state: ProcessingRunState
    created_at: str
    started_at: str | None
    completed_at: str | None
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class StepArtifact:
    """Persisted run-scoped STEP_STATUS artifact payload."""

    step_name: StepName
    step_status: StepStatus
    attempt: int
    started_at: str | None
    ended_at: str | None
    error_code: str | None
    created_at: str


@dataclass(frozen=True, slots=True)
class DocumentWithLatestRun:
    """Document metadata paired with the latest processing run summary."""

    document: Document
    latest_run: ProcessingRunSummary | None
