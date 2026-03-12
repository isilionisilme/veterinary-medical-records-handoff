from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from backend.app.api import routes_health


def test_health_live_returns_alive_status(test_client_factory) -> None:
    with test_client_factory(auth_token=None) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_health_ready_returns_ok_with_database_and_storage_checks(test_client_factory) -> None:
    with test_client_factory(auth_token=None) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "ok"
    assert payload["storage"] == "ok"


def test_health_returns_ok_with_database_and_storage_checks(test_client_factory) -> None:
    with test_client_factory(auth_token=None) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "ok"
    assert payload["storage"] == "ok"


def test_health_returns_degraded_when_database_check_fails(
    test_client_factory, monkeypatch
) -> None:
    @contextmanager
    def _failing_connection() -> Iterator[None]:
        raise RuntimeError("database unavailable")
        yield

    with test_client_factory(auth_token=None) as client:
        monkeypatch.setattr(routes_health.database, "get_connection", _failing_connection)
        response = client.get("/health")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["database"] == "error"


def test_health_ready_returns_degraded_when_database_check_fails(
    test_client_factory, monkeypatch
) -> None:
    @contextmanager
    def _failing_connection() -> Iterator[None]:
        raise RuntimeError("database unavailable")
        yield

    with test_client_factory(auth_token=None) as client:
        monkeypatch.setattr(routes_health.database, "get_connection", _failing_connection)
        response = client.get("/health/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["database"] == "error"
