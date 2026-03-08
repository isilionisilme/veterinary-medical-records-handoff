"""Contract guard for Playwright local E2E configuration.

Prevents regressions where E2E points to an invalid default base URL
or stops bootstrapping local servers automatically.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLAYWRIGHT_CONFIG = REPO_ROOT / "frontend" / "playwright.config.ts"


def _read_playwright_config() -> str:
    return PLAYWRIGHT_CONFIG.read_text(encoding="utf-8")


def test_playwright_default_base_url_points_to_local_frontend_port() -> None:
    text = _read_playwright_config()
    assert 'PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173"' in text


def test_playwright_declares_webserver_bootstrap_for_backend_and_frontend() -> None:
    text = _read_playwright_config()

    assert 'PLAYWRIGHT_EXTERNAL_SERVERS === "1"' in text
    assert "const webServer = useExternalServers" in text
    assert "webServer," in text
    assert "uvicorn backend.app.main:create_app" in text
    assert 'url: "http://127.0.0.1:8000/health"' in text
    assert "npm run dev -- --host 127.0.0.1 --port 5173" in text
