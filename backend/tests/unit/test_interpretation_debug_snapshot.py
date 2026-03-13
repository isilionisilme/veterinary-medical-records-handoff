from __future__ import annotations

import json
from uuid import uuid4

import pytest

from backend.app.infra import database
from scripts.dev.interpretation_debug_snapshot import build_snapshot


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    database.ensure_schema()
    return db_path


def _insert_document(document_id: str) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (
                document_id,
                original_filename,
                content_type,
                file_size,
                storage_path,
                created_at,
                updated_at,
                review_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                "record.pdf",
                "application/pdf",
                123,
                f"{document_id}/original.pdf",
                "2026-02-13T10:00:00+00:00",
                "2026-02-13T10:00:00+00:00",
                "IN_REVIEW",
            ),
        )
        conn.commit()


def _insert_completed_run(document_id: str, run_id: str) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id,
                document_id,
                state,
                created_at,
                started_at,
                completed_at,
                failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                document_id,
                "COMPLETED",
                "2026-02-13T10:00:00+00:00",
                "2026-02-13T10:00:01+00:00",
                "2026-02-13T10:00:05+00:00",
                None,
            ),
        )
        conn.commit()


def _insert_artifact(run_id: str, artifact_type: str, payload: str) -> None:
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
                payload,
                "2026-02-13T10:00:06+00:00",
            ),
        )
        conn.commit()


def test_snapshot_reports_failure_reason_when_interpretation_artifact_missing(test_db) -> None:
    document_id = "doc-missing-interpretation"
    run_id = "run-missing-interpretation"
    _insert_document(document_id)
    _insert_completed_run(document_id, run_id)
    _insert_artifact(
        run_id,
        "STEP_STATUS",
        json.dumps(
            {
                "step_name": "INTERPRETATION",
                "step_status": "FAILED",
                "attempt": 1,
                "started_at": "2026-02-13T10:00:02+00:00",
                "ended_at": "2026-02-13T10:00:04+00:00",
                "error_code": "INTERPRETATION_VALIDATION_FAILED",
                "details": {"errors": ["bad output"]},
            }
        ),
    )

    snapshot = build_snapshot(document_id)

    assert snapshot["structured_interpretation_artifact"]["exists"] is False
    assert snapshot["failure_reason"]["step_error_code"] == "INTERPRETATION_VALIDATION_FAILED"


def test_snapshot_reports_parsing_errors_for_invalid_interpretation_json(test_db) -> None:
    document_id = "doc-invalid-json"
    run_id = "run-invalid-json"
    _insert_document(document_id)
    _insert_completed_run(document_id, run_id)
    _insert_artifact(run_id, "STRUCTURED_INTERPRETATION", "{invalid-json")

    snapshot = build_snapshot(document_id)

    structured = snapshot["structured_interpretation_artifact"]
    assert structured["exists"] is True
    assert structured["parsing_errors"]
    assert "Invalid interpretation JSON payload" in structured["parsing_errors"][0]
