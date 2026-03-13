"""Integration tests covering the document HTTP endpoints."""

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


def test_upload_success_creates_document(test_client):
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == app_models.ProcessingStatus.UPLOADED.value
    assert payload["created_at"]
    document_id = payload["document_id"]

    with database.get_connection() as conn:
        document = conn.execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,),
        ).fetchone()
        assert document, "Document should exist in the database."
        assert document["original_filename"] == "record.pdf"
        assert document["content_type"] == "application/pdf"
        assert document["file_size"] == len(b"%PDF-1.5 sample")
        assert document["review_status"] == "IN_REVIEW"
        history = conn.execute(
            "SELECT * FROM document_status_history WHERE document_id = ?",
            (document_id,),
        ).fetchall()
        assert len(history) == 1
        assert history[0]["status"] == app_models.ProcessingStatus.UPLOADED.value
        assert history[0]["run_id"] is None

    storage_path = get_storage_root() / document_id / "original.pdf"
    assert storage_path.exists()


def test_upload_rejects_unsupported_type(test_client):
    files = {"file": ("record.txt", io.BytesIO(b"plain text"), "text/plain")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 415
    payload = response.json()
    assert payload["error_code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_upload_limits_size(test_client):
    from backend.app.main import MAX_UPLOAD_SIZE

    large_content = b"A" * (MAX_UPLOAD_SIZE + 1)
    files = {"file": ("record.pdf", io.BytesIO(large_content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 413
    assert response.json()["error_code"] == "FILE_TOO_LARGE"


def test_upload_rejects_oversized_via_content_length_header(test_client, monkeypatch):
    from backend.app.api import routes_documents
    from backend.app.main import MAX_UPLOAD_SIZE

    async def fail_if_read(*_args, **_kwargs):
        pytest.fail("upload endpoint should reject oversized Content-Length before reading body")

    monkeypatch.setattr(routes_documents.UploadFile, "read", fail_if_read)
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    response = test_client.post(
        "/documents/upload",
        files=files,
        headers={"content-length": str(MAX_UPLOAD_SIZE + 1)},
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "FILE_TOO_LARGE"


def test_upload_rejects_oversized_via_streaming(test_client, monkeypatch):
    from backend.app.api import routes_documents
    from backend.app.main import MAX_UPLOAD_SIZE

    monkeypatch.setattr(routes_documents, "_request_content_length", lambda _request: None)
    large_content = b"A" * (MAX_UPLOAD_SIZE + 1)
    files = {"file": ("record.pdf", io.BytesIO(large_content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 413
    assert response.json()["error_code"] == "FILE_TOO_LARGE"


def test_upload_normal_file_still_works(test_client, monkeypatch):
    from backend.app.api import routes_documents

    monkeypatch.setattr(routes_documents, "_request_content_length", lambda _request: None)
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["status"] == app_models.ProcessingStatus.UPLOADED.value


def test_upload_rejects_empty_file(test_client):
    files = {"file": ("record.pdf", io.BytesIO(b""), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_REQUEST"


def test_get_document_returns_metadata_and_state(test_client):
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    upload_response = test_client.post("/documents/upload", files=files)
    assert upload_response.status_code == 201
    document_id = upload_response.json()["document_id"]

    response = test_client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == document_id
    assert payload["original_filename"] == "record.pdf"
    assert payload["content_type"] == "application/pdf"
    assert payload["file_size"] == len(b"%PDF-1.5 sample")
    assert payload["status"] == app_models.ProcessingStatus.UPLOADED.value
    assert payload["status_message"]
    assert payload["failure_type"] is None
    assert payload["review_status"] == "IN_REVIEW"
    assert payload["reviewed_at"] is None
    assert payload["latest_run"] is None
    assert isinstance(payload["created_at"], str)
    assert payload["created_at"]
    assert payload["updated_at"]


def test_get_document_returns_404_when_missing(test_client):
    response = test_client.get("/documents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "NOT_FOUND"
    assert payload["message"] == "Document not found."
