from __future__ import annotations

from backend.app.domain.models import ProcessingRunState, ProcessingRunSummary
from backend.app.domain.status import derive_document_status


def test_derive_status_when_no_runs() -> None:
    status_view = derive_document_status(None)
    assert status_view.status.value == "UPLOADED"
    assert status_view.failure_type is None


def test_derive_status_for_queued_run() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.QUEUED,
        failure_type=None,
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "PROCESSING"
    assert status_view.failure_type is None


def test_derive_status_for_running_run() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.RUNNING,
        failure_type=None,
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "PROCESSING"
    assert status_view.failure_type is None


def test_derive_status_for_completed_run() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "COMPLETED"
    assert status_view.status_message == "Processing completed."
    assert status_view.failure_type is None


def test_derive_status_for_failed_run_maps_failure_type() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.FAILED,
        failure_type="EXTRACTION_FAILED",
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "FAILED"
    assert status_view.status_message == "Processing failed during extraction."
    assert status_view.failure_type == "EXTRACTION_FAILED"


def test_derive_status_for_failed_run_maps_low_quality_failure_type() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.FAILED,
        failure_type="EXTRACTION_LOW_QUALITY",
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "FAILED"
    assert (
        status_view.status_message
        == "Processing failed because extracted text quality was too low."
    )
    assert status_view.failure_type == "EXTRACTION_LOW_QUALITY"


def test_derive_status_for_failed_run_maps_interpretation_failure_message() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.FAILED,
        failure_type="INTERPRETATION_FAILED",
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "FAILED"
    assert status_view.status_message == "Processing failed during interpretation."
    assert status_view.failure_type == "INTERPRETATION_FAILED"


def test_derive_status_for_failed_run_defaults_unknown_failure() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.FAILED,
        failure_type=None,
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "FAILED"
    assert status_view.status_message == "Processing failed due to an unknown error."
    assert status_view.failure_type == "UNKNOWN_ERROR"


def test_derive_status_for_timed_out_run_includes_failure_type() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.TIMED_OUT,
        failure_type="INTERPRETATION_FAILED",
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "TIMED_OUT"
    assert status_view.status_message == "Processing timed out."
    assert status_view.failure_type == "INTERPRETATION_FAILED"


def test_derive_status_for_timed_out_run_defaults_unknown_failure() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state=ProcessingRunState.TIMED_OUT,
        failure_type=None,
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "TIMED_OUT"
    assert status_view.status_message == "Processing timed out."
    assert status_view.failure_type == "UNKNOWN_ERROR"


def test_derive_status_for_unknown_state_falls_back_to_unknown_failed() -> None:
    latest_run = ProcessingRunSummary(
        run_id="run-1",
        state="UNKNOWN_STATE",  # type: ignore[arg-type]
        failure_type="EXTRACTION_FAILED",
    )
    status_view = derive_document_status(latest_run)
    assert status_view.status.value == "FAILED"
    assert status_view.status_message == "Processing failed due to an unknown error."
    assert status_view.failure_type == "UNKNOWN_ERROR"
