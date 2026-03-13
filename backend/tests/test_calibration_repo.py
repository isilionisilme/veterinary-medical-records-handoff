from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.infra import database
from backend.app.infra.sqlite_calibration_repo import SqliteCalibrationRepo


def test_sqlite_calibration_repo_constructs_and_tracks_counts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "calibration-repo.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    database.ensure_schema()

    repo = SqliteCalibrationRepo()
    repo.increment_calibration_signal(
        context_key="dog:cbc",
        field_key="hemoglobin",
        mapping_id=None,
        policy_version="v1",
        signal_type="accepted_unchanged",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    counts = repo.get_calibration_counts(
        context_key="dog:cbc",
        field_key="hemoglobin",
        mapping_id=None,
        policy_version="v1",
    )
    assert counts == (1, 0)
