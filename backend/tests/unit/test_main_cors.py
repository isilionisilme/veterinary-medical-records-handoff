from __future__ import annotations

from backend.app.main import _get_cors_origins
from backend.app.settings import clear_settings_cache


def test_get_cors_origins_defaults_include_isolated_playwright_ports(monkeypatch) -> None:
    monkeypatch.delenv("VET_RECORDS_CORS_ORIGINS", raising=False)
    clear_settings_cache()

    origins = set(_get_cors_origins())

    assert {
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:80",
        "http://127.0.0.1:80",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:15173",
        "http://127.0.0.1:15173",
        "http://localhost:25173",
        "http://127.0.0.1:25173",
        "http://localhost:35173",
        "http://127.0.0.1:35173",
    }.issubset(origins)


def test_get_cors_origins_prefers_explicit_environment_override(monkeypatch) -> None:
    monkeypatch.setenv(
        "VET_RECORDS_CORS_ORIGINS",
        "https://example.test,http://127.0.0.1:9999",
    )
    clear_settings_cache()

    assert _get_cors_origins() == ["https://example.test", "http://127.0.0.1:9999"]
