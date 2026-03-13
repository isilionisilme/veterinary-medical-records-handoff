from __future__ import annotations

from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import clear_settings_cache


@pytest.fixture(autouse=True)
def clear_cached_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "documents.db"


@pytest.fixture
def storage_path(tmp_path: Path) -> Path:
    path = tmp_path / "storage"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def test_client_factory(
    monkeypatch: pytest.MonkeyPatch,
    db_path: Path,
    storage_path: Path,
) -> Generator[Callable[..., TestClient], None, None]:
    clients: list[TestClient] = []

    def _factory(
        *,
        disable_processing: bool = True,
        extraction_obs: str | None = None,
        auth_token: str | None = None,
    ) -> TestClient:
        monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
        monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(storage_path))
        if disable_processing:
            monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")
        else:
            monkeypatch.delenv("VET_RECORDS_DISABLE_PROCESSING", raising=False)

        if extraction_obs is None:
            monkeypatch.delenv("VET_RECORDS_EXTRACTION_OBS", raising=False)
        else:
            monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", extraction_obs)

        if auth_token is None:
            monkeypatch.delenv("AUTH_TOKEN", raising=False)
        else:
            monkeypatch.setenv("AUTH_TOKEN", auth_token)

        clear_settings_cache()
        client = TestClient(create_app())
        clients.append(client)
        return client

    yield _factory

    for client in clients:
        client.close()
