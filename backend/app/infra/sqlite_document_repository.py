"""Backward-compatible SQLite repository facade.

This adapter preserves the existing public API while delegating to aggregate
focused repositories:
- documents: `SqliteDocumentRepo`
- runs/artifacts: `SqliteRunRepo`
- calibration: `SqliteCalibrationRepo`
"""

from __future__ import annotations

from typing import Literal

from backend.app.domain.models import (
    Document,
    DocumentWithLatestRun,
    ProcessingRun,
    ProcessingRunDetail,
    ProcessingRunDetails,
    ProcessingRunState,
    ProcessingRunSummary,
    ProcessingStatus,
    StepArtifact,
)
from backend.app.infra.sqlite_calibration_repo import SqliteCalibrationRepo
from backend.app.infra.sqlite_document_repo import SqliteDocumentRepo
from backend.app.infra.sqlite_run_repo import SqliteRunRepo


class SqliteDocumentRepository:
    """Facade implementing the unified repository contract."""

    def __init__(self) -> None:
        self._documents = SqliteDocumentRepo()
        self._runs = SqliteRunRepo()
        self._calibration = SqliteCalibrationRepo()

    def create(self, document: Document, status: ProcessingStatus) -> None:
        self._documents.create(document, status)

    def get(self, document_id: str) -> Document | None:
        return self._documents.get(document_id)

    def list_documents(self, *, limit: int, offset: int) -> list[DocumentWithLatestRun]:
        return self._documents.list_documents(limit=limit, offset=offset)

    def count_documents(self) -> int:
        return self._documents.count_documents()

    def update_review_status(
        self,
        *,
        document_id: str,
        review_status: str,
        updated_at: str,
        reviewed_at: str | None,
        reviewed_by: str | None,
        reviewed_run_id: str | None,
    ) -> Document | None:
        return self._documents.update_review_status(
            document_id=document_id,
            review_status=review_status,
            updated_at=updated_at,
            reviewed_at=reviewed_at,
            reviewed_by=reviewed_by,
            reviewed_run_id=reviewed_run_id,
        )

    def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
        return self._runs.get_latest_run(document_id)

    def get_run(self, run_id: str) -> ProcessingRunDetails | None:
        return self._runs.get_run(run_id)

    def get_latest_completed_run(self, document_id: str) -> ProcessingRunDetails | None:
        return self._runs.get_latest_completed_run(document_id)

    def create_processing_run(
        self,
        *,
        run_id: str,
        document_id: str,
        state: ProcessingRunState,
        created_at: str,
    ) -> None:
        self._runs.create_processing_run(
            run_id=run_id,
            document_id=document_id,
            state=state,
            created_at=created_at,
        )

    def list_queued_runs(self, *, limit: int) -> list[ProcessingRun]:
        return self._runs.list_queued_runs(limit=limit)

    def try_start_run(self, *, run_id: str, document_id: str, started_at: str) -> bool:
        return self._runs.try_start_run(
            run_id=run_id, document_id=document_id, started_at=started_at
        )

    def complete_run(
        self,
        *,
        run_id: str,
        state: ProcessingRunState,
        completed_at: str,
        failure_type: str | None,
    ) -> None:
        self._runs.complete_run(
            run_id=run_id,
            state=state,
            completed_at=completed_at,
            failure_type=failure_type,
        )

    def recover_orphaned_runs(self, *, completed_at: str) -> int:
        return self._runs.recover_orphaned_runs(completed_at=completed_at)

    def list_processing_runs(self, *, document_id: str) -> list[ProcessingRunDetail]:
        return self._runs.list_processing_runs(document_id=document_id)

    def list_step_artifacts(self, *, run_id: str) -> list[StepArtifact]:
        return self._runs.list_step_artifacts(run_id=run_id)

    def append_artifact(
        self,
        *,
        run_id: str,
        artifact_type: str,
        payload: dict[str, object],
        created_at: str,
    ) -> None:
        self._runs.append_artifact(
            run_id=run_id,
            artifact_type=artifact_type,
            payload=payload,
            created_at=created_at,
        )

    def get_latest_artifact_payload(
        self, *, run_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        return self._runs.get_latest_artifact_payload(
            run_id=run_id,
            artifact_type=artifact_type,
        )

    def get_latest_applied_calibration_snapshot(
        self,
        *,
        document_id: str,
    ) -> tuple[str, dict[str, object]] | None:
        return self._calibration.get_latest_applied_calibration_snapshot(
            document_id=document_id,
        )

    def increment_calibration_signal(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        signal_type: Literal["edited", "accepted_unchanged"],
        updated_at: str,
    ) -> None:
        self._calibration.increment_calibration_signal(
            context_key=context_key,
            field_key=field_key,
            mapping_id=mapping_id,
            policy_version=policy_version,
            signal_type=signal_type,
            updated_at=updated_at,
        )

    def apply_calibration_deltas(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        accept_delta: int,
        edit_delta: int,
        updated_at: str,
    ) -> None:
        self._calibration.apply_calibration_deltas(
            context_key=context_key,
            field_key=field_key,
            mapping_id=mapping_id,
            policy_version=policy_version,
            accept_delta=accept_delta,
            edit_delta=edit_delta,
            updated_at=updated_at,
        )

    def get_calibration_counts(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
    ) -> tuple[int, int] | None:
        return self._calibration.get_calibration_counts(
            context_key=context_key,
            field_key=field_key,
            mapping_id=mapping_id,
            policy_version=policy_version,
        )
