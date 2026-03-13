"""Integration tests for document processing history endpoint."""

from __future__ import annotations

import io
import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.infra import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")
    database.ensure_schema()
    return db_path


@pytest.fixture
def test_client(test_db):
    from backend.app.main import app

    with TestClient(app) as client:
        yield client


def _upload_sample_document(test_client: TestClient) -> str:
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"]


def _insert_run(
    *,
    document_id: str,
    run_id: str,
    state: str,
    created_at: str,
    started_at: str | None,
    completed_at: str | None,
    failure_type: str | None,
) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, document_id, state, created_at, started_at, completed_at, failure_type),
        )
        conn.commit()


def _insert_step_status(
    *,
    run_id: str,
    created_at: str,
    step_name: str,
    step_status: str,
    attempt: int,
    started_at: str | None,
    ended_at: str | None,
    error_code: str | None,
) -> None:
    payload = {
        "step_name": step_name,
        "step_status": step_status,
        "attempt": attempt,
        "started_at": started_at,
        "ended_at": ended_at,
        "error_code": error_code,
        "details": None,
    }
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO artifacts (artifact_id, run_id, artifact_type, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid4()), run_id, "STEP_STATUS", json.dumps(payload), created_at),
        )
        conn.commit()


def test_processing_history_returns_runs_and_step_artifacts(test_client):
    document_id = _upload_sample_document(test_client)
    older_run_id = str(uuid4())
    latest_run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=older_run_id,
        state="FAILED",
        created_at="2026-02-01T10:00:00+00:00",
        started_at="2026-02-01T10:00:01+00:00",
        completed_at="2026-02-01T10:00:05+00:00",
        failure_type="EXTRACTION_FAILED",
    )
    _insert_run(
        document_id=document_id,
        run_id=latest_run_id,
        state="COMPLETED",
        created_at="2026-02-01T11:00:00+00:00",
        started_at="2026-02-01T11:00:01+00:00",
        completed_at="2026-02-01T11:00:06+00:00",
        failure_type=None,
    )

    _insert_step_status(
        run_id=older_run_id,
        created_at="2026-02-01T10:00:02+00:00",
        step_name="EXTRACTION",
        step_status="RUNNING",
        attempt=1,
        started_at="2026-02-01T10:00:02+00:00",
        ended_at=None,
        error_code=None,
    )
    _insert_step_status(
        run_id=older_run_id,
        created_at="2026-02-01T10:00:04+00:00",
        step_name="EXTRACTION",
        step_status="FAILED",
        attempt=1,
        started_at="2026-02-01T10:00:02+00:00",
        ended_at="2026-02-01T10:00:04+00:00",
        error_code="EXTRACTION_FAILED",
    )

    response = test_client.get(f"/documents/{document_id}/processing-history")
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == document_id
    assert [run["run_id"] for run in payload["runs"]] == [older_run_id, latest_run_id]

    first_run = payload["runs"][0]
    assert first_run["failure_type"] == "EXTRACTION_FAILED"
    assert len(first_run["steps"]) == 2
    assert first_run["steps"][0]["step_status"] == "RUNNING"
    assert first_run["steps"][1]["step_status"] == "FAILED"
    assert first_run["steps"][1]["error_code"] == "EXTRACTION_FAILED"


def test_processing_history_returns_not_found_for_unknown_document(test_client):
    response = test_client.get("/documents/00000000-0000-0000-0000-000000000000/processing-history")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "NOT_FOUND"
