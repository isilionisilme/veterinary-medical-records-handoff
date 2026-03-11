from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "quality" / "architecture_metrics.py"
TARGET_FILE = "backend/app/application/documents/review_service.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("architecture_metrics", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _data_with_loc(loc: int) -> dict:
    return {
        "loc": {"files": {TARGET_FILE: loc}},
        "radon_cc": {"functions": []},
    }


def test_preexisting_small_delta_warns_but_does_not_fail() -> None:
    module = _load_module()
    data = _data_with_loc(605)

    with patch.object(module, "_base_ref_loc", return_value=600):
        warnings, failures = module.check_thresholds(
            data,
            max_cc=30,
            max_loc=500,
            warn_cc=11,
            changed_backend_paths={TARGET_FILE},
            base_ref="main",
            max_loc_growth=50,
        )

    assert failures == []
    assert len(warnings) == 1
    assert "pre-existing, delta +5" in warnings[0]


def test_threshold_crossing_fails() -> None:
    module = _load_module()
    data = _data_with_loc(510)

    with patch.object(module, "_base_ref_loc", return_value=490):
        warnings, failures = module.check_thresholds(
            data,
            max_cc=30,
            max_loc=500,
            warn_cc=11,
            changed_backend_paths={TARGET_FILE},
            base_ref="main",
            max_loc_growth=50,
        )

    assert warnings == []
    assert len(failures) == 1
    assert "FAIL: LOC 510 > 500" in failures[0]


def test_preexisting_large_growth_fails() -> None:
    module = _load_module()
    data = _data_with_loc(680)

    with patch.object(module, "_base_ref_loc", return_value=600):
        warnings, failures = module.check_thresholds(
            data,
            max_cc=30,
            max_loc=500,
            warn_cc=11,
            changed_backend_paths={TARGET_FILE},
            base_ref="main",
            max_loc_growth=50,
        )

    assert warnings == []
    assert len(failures) == 1
    assert "growth cap 50" in failures[0]


def test_below_threshold_has_no_warnings_or_failures() -> None:
    module = _load_module()
    data = _data_with_loc(200)

    warnings, failures = module.check_thresholds(
        data,
        max_cc=30,
        max_loc=500,
        warn_cc=11,
        changed_backend_paths={TARGET_FILE},
        base_ref="main",
        max_loc_growth=50,
    )

    assert warnings == []
    assert failures == []


def test_no_base_ref_preserves_absolute_fail_behavior() -> None:
    module = _load_module()
    data = _data_with_loc(600)

    warnings, failures = module.check_thresholds(
        data,
        max_cc=30,
        max_loc=500,
        warn_cc=11,
        changed_backend_paths={TARGET_FILE},
        base_ref=None,
        max_loc_growth=50,
    )

    assert warnings == []
    assert len(failures) == 1
    assert "FAIL: LOC 600 > 500" in failures[0]
