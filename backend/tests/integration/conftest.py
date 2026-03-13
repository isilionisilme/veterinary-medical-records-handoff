from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.infra import database


@pytest.fixture
def test_db(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch):
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
