"""Integration tests covering document download and preview endpoints."""

import io

import pytest
from fastapi.testclient import TestClient

from backend.app.infra import database
from backend.app.infra.file_storage import get_storage_root


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    database.ensure_schema()
    return db_path


@pytest.fixture
def test_client(test_db):
    from backend.app.main import app

    with TestClient(app) as client:
        yield client


def _upload_sample_document(test_client: TestClient) -> tuple[str, bytes]:
    sample_content = b"%PDF-1.5 sample"
    files = {"file": ("record.pdf", io.BytesIO(sample_content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"], sample_content


def test_get_document_download_returns_pdf_inline(test_client):
    document_id, sample_content = _upload_sample_document(test_client)

    response = test_client.get(f"/documents/{document_id}/download")
    assert response.status_code == 200
    assert response.content == sample_content
    assert response.headers["content-type"].startswith("application/pdf")
    assert "inline" in response.headers["content-disposition"].lower()
    assert "record.pdf" in response.headers["content-disposition"]


def test_get_document_download_returns_attachment_when_download_true(test_client):
    document_id, _ = _upload_sample_document(test_client)

    response = test_client.get(f"/documents/{document_id}/download?download=true")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"].lower()


def test_get_document_download_returns_410_when_missing_file(test_client):
    document_id, _ = _upload_sample_document(test_client)

    storage_path = get_storage_root() / document_id / "original.pdf"
    storage_path.unlink()

    response = test_client.get(f"/documents/{document_id}/download")
    assert response.status_code == 410
    payload = response.json()
    assert payload["error_code"] == "ARTIFACT_MISSING"


def test_get_document_download_returns_404_when_document_missing(test_client):
    response = test_client.get("/documents/00000000-0000-0000-0000-000000000000/download")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "NOT_FOUND"
