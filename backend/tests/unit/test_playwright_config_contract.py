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
    assert "const defaultFrontendPort = process.env.CI || useExternalServers ? 5173 : 15173" in text
    assert "PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`" in text
    assert "PLAYWRIGHT_BACKEND_BASE_URL || `http://127.0.0.1:${backendPort}`" in text
    assert "const maxWorkers = Math.max(1, cpuCount);" in text
    assert "const workers = Math.min(maxWorkers, requestedWorkers);" in text


def test_playwright_declares_webserver_bootstrap_for_backend_and_frontend() -> None:
    text = _read_playwright_config()

    assert 'PLAYWRIGHT_EXTERNAL_SERVERS === "1"' in text
    assert "const webServer = useExternalServers" in text
    assert "webServer," in text
    assert "const defaultBackendPort = process.env.CI || useExternalServers ? 8000 : 18000" in text
    assert "uvicorn backend.app.main:create_app" in text
    assert "url: `${backendBaseURL}/openapi.json`" in text
    assert "VITE_API_BASE_URL: backendBaseURL" in text
    assert "node ./node_modules/vite/bin/vite.js --host 127.0.0.1 --port ${frontendPort}" in text
    assert "resolveWorkerCount(process.env.PLAYWRIGHT_CI_WORKERS) ?? ciDefaultWorkers" in text
    assert (
        "const localDefaultWorkers = Math.min(12, maxWorkers, "
        "Math.max(1, Math.floor(cpuCount * 0.75)));" in text
    )
