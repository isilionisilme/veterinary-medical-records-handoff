from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ci" / "check_plan_execution_guard.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_plan_execution_guard", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_plan(tmp_path: Path, relative_path: str, content: str) -> Path:
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


HAPPY_PLAN = """# Plan
**Branch:** `feature/test`

## Execution Status
- [ ] P1-A task ⏳ IN PROGRESS (Execution agent, 2026-03-09)
"""

NO_EXEC_STATUS_PLAN = """# Plan
**Branch:** `feature/test`

## Context
- details
"""

CLEAN_PLAN = """# Plan
**Branch:** `feature/test`

## Execution Status
- [x] P1-A task — ✅ `abc12345`
- [x] P1-B task — ✅ `def67890`
"""


def test_resolve_no_plan(tmp_path: Path) -> None:
    module = _load_guard_module()
    assert module.resolve_active_plan("feature/test", tmp_path) is None


def test_resolve_single_match(tmp_path: Path) -> None:
    module = _load_guard_module()
    plan = _write_plan(tmp_path, "PLAN_single.md", HAPPY_PLAN)
    resolved = module.resolve_active_plan("feature/test", tmp_path)
    assert resolved == plan


def test_resolve_ambiguous_raises(tmp_path: Path) -> None:
    module = _load_guard_module()
    _write_plan(tmp_path, "PLAN_a.md", HAPPY_PLAN)
    _write_plan(tmp_path, "nested/PLAN_b.md", HAPPY_PLAN)

    try:
        module.resolve_active_plan("feature/test", tmp_path)
        raise AssertionError("Expected PlanResolutionError for ambiguous branch match")
    except module.PlanResolutionError as exc:
        assert "Ambiguous active plan resolution" in str(exc)


def test_validate_execution_status_present() -> None:
    module = _load_guard_module()
    errors = module.validate_execution_status(HAPPY_PLAN, Path("PLAN_ok.md"))
    assert errors == []


def test_validate_execution_status_missing() -> None:
    module = _load_guard_module()
    errors = module.validate_execution_status(NO_EXEC_STATUS_PLAN, Path("PLAN_missing.md"))
    assert len(errors) == 1
    assert "missing '## Execution Status' section" in errors[0]


def test_multiple_in_progress_steps_fail() -> None:
    module = _load_guard_module()
    errors = module.validate_single_active_step(
        """# Plan
**Branch:** `feature/test`

## Execution Status
- [ ] P1-A task ⏳ IN PROGRESS (Execution agent, 2026-03-09)
- [ ] P1-B task ⏳ IN PROGRESS (Execution agent, 2026-03-09)
"""
    )
    assert errors == [
        "Multiple active steps found. At most one step may be IN PROGRESS.\n"
        "- [ ] P1-A task ⏳ IN PROGRESS (Execution agent, 2026-03-09)\n"
        "- [ ] P1-B task ⏳ IN PROGRESS (Execution agent, 2026-03-09)"
    ]


def test_all_closed_passes(tmp_path: Path) -> None:
    module = _load_guard_module()
    _write_plan(tmp_path, "PLAN_closed.md", CLEAN_PLAN)
    exit_code = module.run_guard("feature/test", tmp_path)
    assert exit_code == 0


def test_single_in_progress_passes(tmp_path: Path) -> None:
    module = _load_guard_module()
    _write_plan(tmp_path, "PLAN_happy.md", HAPPY_PLAN)
    exit_code = module.run_guard("feature/test", tmp_path)
    assert exit_code == 0


def test_no_plan_branch_passes(tmp_path: Path) -> None:
    module = _load_guard_module()
    _write_plan(tmp_path, "PLAN_other.md", HAPPY_PLAN.replace("feature/test", "other/branch"))
    exit_code = module.run_guard("feature/test", tmp_path)
    assert exit_code == 0


def test_run_guard_fails_when_execution_status_missing(tmp_path: Path) -> None:
    module = _load_guard_module()
    _write_plan(tmp_path, "PLAN_missing.md", NO_EXEC_STATUS_PLAN)
    exit_code = module.run_guard("feature/test", tmp_path)
    assert exit_code == 1
