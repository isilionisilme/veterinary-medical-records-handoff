from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_field_normalizers_import_succeeds_in_clean_process() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        [sys.executable, "-c", "import backend.app.application.field_normalizers"],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
