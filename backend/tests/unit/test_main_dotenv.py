from __future__ import annotations

from pathlib import Path

from backend.app.config import confidence_policy_explicit_config_diagnostics
from backend.app.main import _is_dev_runtime, _load_backend_dotenv_for_dev


def test_load_backend_dotenv_for_dev_configures_confidence_policy(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_LOW_MAX", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_MID_MAX", raising=False)

    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            [
                "VET_RECORDS_CONFIDENCE_POLICY_VERSION=v1-test",
                "VET_RECORDS_CONFIDENCE_LOW_MAX=0.5",
                "VET_RECORDS_CONFIDENCE_MID_MAX=0.75",
            ]
        ),
        encoding="utf-8",
    )

    loaded = _load_backend_dotenv_for_dev(dotenv_path=dotenv_path, dev_runtime=True)
    assert loaded is True

    configured, reason, missing_keys, invalid_keys = confidence_policy_explicit_config_diagnostics()
    assert configured is True
    assert reason == "policy_configured"
    assert missing_keys == []
    assert invalid_keys == []


def test_is_dev_runtime_detects_reload_flag(monkeypatch) -> None:
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("VET_RECORDS_ENV", raising=False)
    monkeypatch.delenv("UVICORN_RELOAD", raising=False)
    monkeypatch.setattr("sys.argv", ["uvicorn", "backend.app.main:create_app", "--reload"])

    assert _is_dev_runtime() is True
