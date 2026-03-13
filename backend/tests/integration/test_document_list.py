"""Integration tests covering document list endpoint."""

import io

import pytest
from fastapi.testclient import TestClient

from backend.app.domain import models as app_models
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


def _upload_sample_document(test_client: TestClient, filename: str) -> str:
    content = b"%PDF-1.5 sample"
    files = {"file": (filename, io.BytesIO(content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"]


def test_list_documents_returns_uploaded_documents(test_client):
    doc_id = _upload_sample_document(test_client, "record.pdf")

    response = test_client.get("/documents")
    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 50
    assert payload["offset"] == 0
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["document_id"] == doc_id
    assert item["original_filename"] == "record.pdf"
    assert item["status"] == app_models.ProcessingStatus.UPLOADED.value
    assert item["status_label"] == "Uploaded"
    assert item["failure_type"] is None
    assert item["review_status"] == "IN_REVIEW"
    assert item["reviewed_at"] is None


def test_list_documents_returns_processing_status_from_latest_run(test_client):
    doc_id = _upload_sample_document(test_client, "record.pdf")

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "run-123",
                doc_id,
                app_models.ProcessingRunState.RUNNING.value,
                "2026-02-06T10:00:00+00:00",
                "2026-02-06T10:00:01+00:00",
                None,
                None,
            ),
        )
        conn.commit()

    response = test_client.get("/documents")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["status"] == app_models.ProcessingStatus.PROCESSING.value
    assert item["status_label"] == "Processing"


def test_list_documents_returns_failure_type_for_failed_run(test_client):
    doc_id = _upload_sample_document(test_client, "record.pdf")

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "run-456",
                doc_id,
                app_models.ProcessingRunState.FAILED.value,
                "2099-02-06T11:00:00+00:00",
                "2026-02-06T11:00:01+00:00",
                "2026-02-06T11:00:05+00:00",
                "EXTRACTION_FAILED",
            ),
        )
        conn.commit()

    response = test_client.get("/documents")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["status"] == app_models.ProcessingStatus.FAILED.value
    assert item["status_label"] == "Failed"
    assert item["failure_type"] == "EXTRACTION_FAILED"
