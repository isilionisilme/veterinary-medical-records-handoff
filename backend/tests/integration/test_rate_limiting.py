from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from backend.app.infra import database
from backend.app.settings import clear_settings_cache


@pytest.fixture
def rate_limited_client(tmp_path, monkeypatch):
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")
    monkeypatch.setenv("VET_RECORDS_RATE_LIMIT_UPLOAD", "1/minute")
    monkeypatch.setenv("VET_RECORDS_RATE_LIMIT_DOWNLOAD", "30/minute")

    clear_settings_cache()
    database.ensure_schema()

    from backend.app.main import create_app

    clear_settings_cache()
    with TestClient(create_app()) as client:
        yield client


def test_limiter_is_configured_on_app(rate_limited_client: TestClient):
    assert hasattr(rate_limited_client.app.state, "limiter")


def test_upload_rate_limit_returns_429_when_exceeded(rate_limited_client: TestClient):
    files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample"), "application/pdf")}
    first_response = rate_limited_client.post("/documents/upload", files=files)
    assert first_response.status_code == 201

    second_files = {"file": ("record.pdf", io.BytesIO(b"%PDF-1.5 sample 2"), "application/pdf")}
    second_response = rate_limited_client.post("/documents/upload", files=second_files)
    assert second_response.status_code == 429
