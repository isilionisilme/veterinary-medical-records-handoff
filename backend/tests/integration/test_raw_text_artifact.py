"""Integration tests covering raw text artifact retrieval."""

import io

import pytest
from fastapi.testclient import TestClient

from backend.app.domain import models as app_models
from backend.app.infra import database
from backend.app.infra.file_storage import get_storage_root


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
    content = b"%PDF-1.5 sample"
    files = {"file": ("record.pdf", io.BytesIO(content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"]


def _insert_run(
    *, document_id: str, run_id: str, state: app_models.ProcessingRunState, failure_type: str | None
) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                document_id,
                state.value,
                "2026-02-06T10:00:00+00:00",
                "2026-02-06T10:00:01+00:00",
                (
                    "2026-02-06T10:00:05+00:00"
                    if state == app_models.ProcessingRunState.COMPLETED
                    else None
                ),
                failure_type,
            ),
        )
        conn.commit()


def test_get_raw_text_returns_payload_for_completed_run(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = "run-raw-text-1"
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        "Historia clinica: perro macho con fiebre y vomitos. "
        "Se pauta tratamiento y control en 48 horas.",
        encoding="utf-8",
    )

    response = test_client.get(f"/runs/{run_id}/artifacts/raw-text")
    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == run_id
    assert payload["artifact_type"] == "RAW_TEXT"
    assert payload["content_type"] == "text/plain"
    assert "Historia clinica" in payload["text"]


def test_get_raw_text_returns_409_when_run_not_ready(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = "run-raw-text-queued"
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.RUNNING,
        failure_type=None,
    )

    response = test_client.get(f"/runs/{run_id}/artifacts/raw-text")
    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "RAW_TEXT_NOT_READY"


def test_get_raw_text_returns_409_when_not_available(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = "run-raw-text-failed"
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.FAILED,
        failure_type="EXTRACTION_FAILED",
    )

    response = test_client.get(f"/runs/{run_id}/artifacts/raw-text")
    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "RAW_TEXT_NOT_AVAILABLE"


def test_get_raw_text_returns_410_when_missing_file(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = "run-raw-text-missing"
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    response = test_client.get(f"/runs/{run_id}/artifacts/raw-text")
    assert response.status_code == 410
    payload = response.json()
    assert payload["error_code"] == "ARTIFACT_MISSING"


def test_get_raw_text_returns_404_when_run_missing(test_client):
    response = test_client.get("/runs/does-not-exist/artifacts/raw-text")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "NOT_FOUND"
