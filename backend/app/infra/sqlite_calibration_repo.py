"""SQLite calibration aggregate repository."""

from __future__ import annotations

import json
from typing import Literal

from backend.app.infra import database


class SqliteCalibrationRepo:
    """SQLite-backed repository for calibration counters and snapshots."""

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
        accept_inc = 1 if signal_type == "accepted_unchanged" else 0
        edit_inc = 1 if signal_type == "edited" else 0
        self.apply_calibration_deltas(
            context_key=context_key,
            field_key=field_key,
            mapping_id=mapping_id,
            policy_version=policy_version,
            accept_delta=accept_inc,
            edit_delta=edit_inc,
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
        mapping_scope_key = mapping_id if mapping_id is not None else "__null__"
        with database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO calibration_aggregates (
                    context_key,
                    field_key,
                    mapping_id,
                    mapping_id_scope_key,
                    policy_version,
                    accept_count,
                    edit_count,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(context_key, field_key, mapping_id_scope_key, policy_version)
                DO UPDATE SET
                    accept_count = MAX(0, calibration_aggregates.accept_count + ?),
                    edit_count = MAX(0, calibration_aggregates.edit_count + ?),
                    updated_at = excluded.updated_at
                """,
                (
                    context_key,
                    field_key,
                    mapping_id,
                    mapping_scope_key,
                    policy_version,
                    max(accept_delta, 0),
                    max(edit_delta, 0),
                    updated_at,
                    accept_delta,
                    edit_delta,
                ),
            )
            conn.commit()

    def get_calibration_counts(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
    ) -> tuple[int, int] | None:
        mapping_scope_key = mapping_id if mapping_id is not None else "__null__"
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT accept_count, edit_count
                FROM calibration_aggregates
                WHERE context_key = ?
                  AND field_key = ?
                  AND mapping_id_scope_key = ?
                  AND policy_version = ?
                """,
                (context_key, field_key, mapping_scope_key, policy_version),
            ).fetchone()

        if row is None:
            return None
        return int(row["accept_count"]), int(row["edit_count"])

    def get_latest_applied_calibration_snapshot(
        self,
        *,
        document_id: str,
    ) -> tuple[str, dict[str, object]] | None:
        with database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT a.run_id, a.payload
                FROM artifacts a
                INNER JOIN processing_runs pr ON pr.run_id = a.run_id
                WHERE pr.document_id = ?
                  AND a.artifact_type = 'CALIBRATION_REVIEW_SNAPSHOT'
                ORDER BY a.created_at DESC
                """,
                (document_id,),
            ).fetchall()

        for row in rows:
            payload = json.loads(row["payload"])
            if not isinstance(payload, dict):
                continue
            if payload.get("status") != "applied":
                continue
            return str(row["run_id"]), payload
        return None
