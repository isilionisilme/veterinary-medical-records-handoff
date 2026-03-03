from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "quality" / "check_brand_compliance.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_brand_compliance", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_allowed_hex_includes_current_brand_colors() -> None:
    module = _load_guard_module()
    assert "#ebf5ff" in module.ALLOWED_HEX
    assert "#fc4e1b" in module.ALLOWED_HEX
