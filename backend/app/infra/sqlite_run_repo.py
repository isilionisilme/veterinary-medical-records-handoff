"""SQLite run/artifact aggregate repository."""

from __future__ import annotations

import json
from uuid import uuid4

from backend.app.domain.models import (
    ProcessingRun,
    ProcessingRunDetail,
    ProcessingRunDetails,
    ProcessingRunState,
    ProcessingRunSummary,
    StepArtifact,
    StepName,
    StepStatus,
)
from backend.app.infra import database


class SqliteRunRepo:
    """SQLite-backed repository for processing runs and artifacts."""

    def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    run_id,
                    state,
                    failure_type
                FROM processing_runs
                WHERE document_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return ProcessingRunSummary(
            run_id=row["run_id"],
            state=ProcessingRunState(row["state"]),
            failure_type=row["failure_type"],
        )

    def get_run(self, run_id: str) -> ProcessingRunDetails | None:
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    run_id,
                    document_id,
                    state,
                    created_at,
                    started_at,
                    completed_at,
                    failure_type
                FROM processing_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        return ProcessingRunDetails(
            run_id=row["run_id"],
            document_id=row["document_id"],
            state=ProcessingRunState(row["state"]),
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            failure_type=row["failure_type"],
        )

    def get_latest_completed_run(self, document_id: str) -> ProcessingRunDetails | None:
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    run_id,
                    document_id,
                    state,
                    created_at,
                    started_at,
                    completed_at,
                    failure_type
                FROM processing_runs
                WHERE document_id = ? AND state = ?
                ORDER BY completed_at DESC, created_at DESC
                LIMIT 1
                """,
                (document_id, ProcessingRunState.COMPLETED.value),
            ).fetchone()

        if row is None:
            return None

        return ProcessingRunDetails(
            run_id=row["run_id"],
            document_id=row["document_id"],
            state=ProcessingRunState(row["state"]),
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            failure_type=row["failure_type"],
        )

    def create_processing_run(
        self,
        *,
        run_id: str,
        document_id: str,
        state: ProcessingRunState,
        created_at: str,
    ) -> None:
        with database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO processing_runs (
                    run_id,
                    document_id,
                    state,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (run_id, document_id, state.value, created_at),
            )
            conn.commit()

    def list_queued_runs(self, *, limit: int) -> list[ProcessingRun]:
        with database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    run_id,
                    document_id,
                    state,
                    created_at
                FROM processing_runs
                WHERE state = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (ProcessingRunState.QUEUED.value, limit),
            ).fetchall()

        return [
            ProcessingRun(
                run_id=row["run_id"],
                document_id=row["document_id"],
                state=ProcessingRunState(row["state"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def try_start_run(self, *, run_id: str, document_id: str, started_at: str) -> bool:
        with database.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE processing_runs
                SET state = ?, started_at = ?
                WHERE run_id = ?
                  AND state = ?
                  AND NOT EXISTS (
                    SELECT 1
                    FROM processing_runs
                    WHERE document_id = ?
                      AND state = ?
                  )
                """,
                (
                    ProcessingRunState.RUNNING.value,
                    started_at,
                    run_id,
                    ProcessingRunState.QUEUED.value,
                    document_id,
                    ProcessingRunState.RUNNING.value,
                ),
            )
            conn.commit()
        return cursor.rowcount == 1

    def complete_run(
        self,
        *,
        run_id: str,
        state: ProcessingRunState,
        completed_at: str,
        failure_type: str | None,
    ) -> None:
        with database.get_connection() as conn:
            conn.execute(
                """
                UPDATE processing_runs
                SET state = ?, completed_at = ?, failure_type = ?
                WHERE run_id = ?
                """,
                (state.value, completed_at, failure_type, run_id),
            )
            conn.commit()

    def recover_orphaned_runs(self, *, completed_at: str) -> int:
        with database.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE processing_runs
                SET state = ?, completed_at = ?, failure_type = ?
                WHERE state = ?
                """,
                (
                    ProcessingRunState.FAILED.value,
                    completed_at,
                    "PROCESS_TERMINATED",
                    ProcessingRunState.RUNNING.value,
                ),
            )
            conn.commit()
        return cursor.rowcount

    def list_processing_runs(self, *, document_id: str) -> list[ProcessingRunDetail]:
        with database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    run_id,
                    state,
                    created_at,
                    started_at,
                    completed_at,
                    failure_type
                FROM processing_runs
                WHERE document_id = ?
                ORDER BY created_at ASC
                """,
                (document_id,),
            ).fetchall()

        return [
            ProcessingRunDetail(
                run_id=row["run_id"],
                state=ProcessingRunState(row["state"]),
                created_at=row["created_at"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
                failure_type=row["failure_type"],
            )
            for row in rows
        ]

    def list_step_artifacts(self, *, run_id: str) -> list[StepArtifact]:
        with database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT payload, created_at
                FROM artifacts
                WHERE run_id = ? AND artifact_type = ?
                ORDER BY created_at ASC
                """,
                (run_id, "STEP_STATUS"),
            ).fetchall()

        artifacts: list[StepArtifact] = []
        for row in rows:
            payload = json.loads(row["payload"])
            artifacts.append(
                StepArtifact(
                    step_name=StepName(payload["step_name"]),
                    step_status=StepStatus(payload["step_status"]),
                    attempt=int(payload["attempt"]),
                    started_at=payload.get("started_at"),
                    ended_at=payload.get("ended_at"),
                    error_code=payload.get("error_code"),
                    created_at=row["created_at"],
                )
            )
        return artifacts

    def append_artifact(
        self,
        *,
        run_id: str,
        artifact_type: str,
        payload: dict[str, object],
        created_at: str,
    ) -> None:
        with database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO artifacts (artifact_id, run_id, artifact_type, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    run_id,
                    artifact_type,
                    json.dumps(payload, separators=(",", ":")),
                    created_at,
                ),
            )
            conn.commit()

    def get_latest_artifact_payload(
        self, *, run_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT payload
                FROM artifacts
                WHERE run_id = ? AND artifact_type = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (run_id, artifact_type),
            ).fetchone()

        if row is None:
            return None

        payload = json.loads(row["payload"])
        if not isinstance(payload, dict):
            return None
        return payload
