"""Port for processing runs and run artifacts persistence."""

from __future__ import annotations

from typing import Protocol

from backend.app.domain.models import (
    ProcessingRun,
    ProcessingRunDetail,
    ProcessingRunDetails,
    ProcessingRunState,
    ProcessingRunSummary,
    StepArtifact,
)


class RunRepository(Protocol):
    """Persistence contract for processing runs and run-scoped artifacts."""

    def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
        """Return the latest processing run summary for a document, if any."""

    def get_run(self, run_id: str) -> ProcessingRunDetails | None:
        """Return processing run details by run id, if it exists."""

    def get_latest_completed_run(self, document_id: str) -> ProcessingRunDetails | None:
        """Return the latest completed run for a document, if any."""

    def create_processing_run(
        self,
        *,
        run_id: str,
        document_id: str,
        state: ProcessingRunState,
        created_at: str,
    ) -> None:
        """Persist a new processing run."""

    def list_queued_runs(self, *, limit: int) -> list[ProcessingRun]:
        """Return queued processing runs in FIFO order."""

    def try_start_run(self, *, run_id: str, document_id: str, started_at: str) -> bool:
        """Attempt to transition a queued run to running."""

    def complete_run(
        self,
        *,
        run_id: str,
        state: ProcessingRunState,
        completed_at: str,
        failure_type: str | None,
    ) -> None:
        """Finalize a run with a terminal state."""

    def recover_orphaned_runs(self, *, completed_at: str) -> int:
        """Mark any RUNNING runs as FAILED with PROCESS_TERMINATED."""

    def list_processing_runs(self, *, document_id: str) -> list[ProcessingRunDetail]:
        """Return processing runs for a document ordered by creation time."""

    def list_step_artifacts(self, *, run_id: str) -> list[StepArtifact]:
        """Return STEP_STATUS artifacts for a run in chronological order."""

    def append_artifact(
        self,
        *,
        run_id: str,
        artifact_type: str,
        payload: dict[str, object],
        created_at: str,
    ) -> None:
        """Persist a run-scoped artifact record."""

    def get_latest_artifact_payload(
        self, *, run_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        """Return latest artifact payload for a run and artifact type."""
