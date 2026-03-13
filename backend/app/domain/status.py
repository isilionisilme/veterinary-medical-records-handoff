"""Domain services for document status derivation."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.models import ProcessingRunState, ProcessingRunSummary, ProcessingStatus


@dataclass(frozen=True, slots=True)
class DocumentStatusView:
    """Derived document status and explanatory metadata."""

    status: ProcessingStatus
    status_message: str
    failure_type: str | None


_FAILURE_TYPE_MAP = {
    "EXTRACTION_FAILED": "EXTRACTION_FAILED",
    "EXTRACTION_LOW_QUALITY": "EXTRACTION_LOW_QUALITY",
    "INTERPRETATION_FAILED": "INTERPRETATION_FAILED",
}


def derive_document_status(latest_run: ProcessingRunSummary | None) -> DocumentStatusView:
    """Derive the current document status from the latest processing run.

    Args:
        latest_run: Latest processing run summary, or None when no runs exist.

    Returns:
        A derived status view suitable for API responses and UI messaging.
    """

    if latest_run is None:
        return DocumentStatusView(
            status=ProcessingStatus.UPLOADED,
            status_message="Uploaded. Processing has not started.",
            failure_type=None,
        )

    if latest_run.state in {ProcessingRunState.QUEUED, ProcessingRunState.RUNNING}:
        return DocumentStatusView(
            status=ProcessingStatus.PROCESSING,
            status_message="Processing is in progress.",
            failure_type=None,
        )

    if latest_run.state == ProcessingRunState.COMPLETED:
        return DocumentStatusView(
            status=ProcessingStatus.COMPLETED,
            status_message="Processing completed.",
            failure_type=None,
        )

    # Failure category is always exposed for terminal failure states to keep
    # status explainable. If a run does not provide a known category, we fall
    # back to UNKNOWN_ERROR.
    failure_type = _FAILURE_TYPE_MAP.get(latest_run.failure_type or "", "UNKNOWN_ERROR")

    if latest_run.state == ProcessingRunState.FAILED:
        return DocumentStatusView(
            status=ProcessingStatus.FAILED,
            status_message=_failed_message(failure_type),
            failure_type=failure_type,
        )

    if latest_run.state == ProcessingRunState.TIMED_OUT:
        return DocumentStatusView(
            status=ProcessingStatus.TIMED_OUT,
            status_message="Processing timed out.",
            failure_type=failure_type,
        )

    return DocumentStatusView(
        status=ProcessingStatus.FAILED,
        status_message="Processing failed due to an unknown error.",
        failure_type="UNKNOWN_ERROR",
    )


def _failed_message(failure_type: str) -> str:
    if failure_type == "EXTRACTION_FAILED":
        return "Processing failed during extraction."
    if failure_type == "EXTRACTION_LOW_QUALITY":
        return "Processing failed because extracted text quality was too low."
    if failure_type == "INTERPRETATION_FAILED":
        return "Processing failed during interpretation."
    return "Processing failed due to an unknown error."


_STATUS_LABELS = {
    ProcessingStatus.UPLOADED: "Uploaded",
    ProcessingStatus.PROCESSING: "Processing",
    ProcessingStatus.COMPLETED: "Ready for review",
    ProcessingStatus.FAILED: "Failed",
    ProcessingStatus.TIMED_OUT: "Processing timed out",
}


def map_status_label(status: ProcessingStatus) -> str:
    """Map internal status to a user-facing, non-blocking label.

    Args:
        status: Derived document status value.

    Returns:
        User-facing status label.
    """

    return _STATUS_LABELS.get(status, "Unknown")
