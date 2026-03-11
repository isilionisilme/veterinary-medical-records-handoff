from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dev" / "plan-start-check.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("plan_start_check", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_plan(tmp_path: Path, relative_path: str, content: str) -> Path:
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _plan_template(
    *,
    branch: str = "`docs/example-branch`",
    worktree: str = "`D:/Git/worktrees/example`",
    execution_mode: str = "`Semi-supervised`",
    model_assignment: str = "`Uniform`",
) -> str:
    return "\n".join(
        [
            "# Plan",
            f"**Branch:** {branch}",
            f"**Worktree:** {worktree}",
            f"**Execution Mode:** {execution_mode}",
            f"**Model Assignment:** {model_assignment}",
            "",
            "## Execution Status",
            "- [ ] P1-A task",
            "",
        ]
    )


def test_collect_reports_all_resolved(tmp_path: Path) -> None:
    module = _load_module()
    _write_plan(tmp_path, "PLAN_ok.md", _plan_template())

    reports = module.collect_reports(tmp_path, repo_root=tmp_path)

    assert len(reports) == 1
    report = reports[0]
    assert report.relative_path == "PLAN_ok.md"
    assert report.unresolved_fields == ()
    assert all(field.resolved for field in report.fields)


def test_run_partial_resolution_returns_exit_1_and_lists_missing_fields(tmp_path: Path) -> None:
    module = _load_module()
    _write_plan(
        tmp_path,
        "PLAN_partial.md",
        _plan_template(
            worktree="PENDING PLAN-START RESOLUTION",
            model_assignment="PENDING USER SELECTION",
        ),
    )

    exit_code = module.run(tmp_path, repo_root=tmp_path)
    rendered = module.render_report(module.collect_reports(tmp_path, repo_root=tmp_path))

    assert exit_code == 1
    assert "PLAN_partial.md" in rendered
    assert "Worktree: ❌ unresolved" in rendered
    assert "Model Assignment: ❌ unresolved" in rendered
    assert "UNRESOLVED: Worktree, Model Assignment" in rendered


def test_spanish_placeholder_is_reported_as_unresolved(tmp_path: Path) -> None:
    module = _load_module()
    _write_plan(
        tmp_path,
        "PLAN_pending_es.md",
        _plan_template(branch="pendiente"),
    )

    reports = module.collect_reports(tmp_path, repo_root=tmp_path)

    assert len(reports) == 1
    assert reports[0].unresolved_fields == ("Branch",)


def test_run_no_active_plan_ignores_completed_directory(tmp_path: Path) -> None:
    module = _load_module()
    _write_plan(tmp_path, "completed/PLAN_done.md", _plan_template())

    exit_code = module.run(tmp_path, repo_root=tmp_path)

    assert exit_code == 0
    assert module.collect_reports(tmp_path, repo_root=tmp_path) == []


def test_run_multiple_active_plans_reports_each_plan(tmp_path: Path) -> None:
    module = _load_module()
    _write_plan(tmp_path, "PLAN_ok.md", _plan_template())
    _write_plan(
        tmp_path,
        "nested/PLAN_partial.md",
        _plan_template(branch="PENDING PLAN-START RESOLUTION"),
    )

    reports = module.collect_reports(tmp_path, repo_root=tmp_path)
    rendered = module.render_report(reports)

    assert len(reports) == 2
    paths = {report.relative_path for report in reports}
    assert paths == {"PLAN_ok.md", "nested/PLAN_partial.md"}
    assert "PLAN_ok.md" in rendered
    assert "nested/PLAN_partial.md" in rendered
    assert "Summary: ALL RESOLVED" in rendered
    assert "UNRESOLVED: Branch" in rendered


def test_cli_reports_unresolved_plan(tmp_path: Path) -> None:
    _write_plan(
        tmp_path,
        "PLAN_cli.md",
        _plan_template(execution_mode="PENDING USER SELECTION"),
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--plan-dir", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert "PLAN_cli.md" in result.stdout
    assert "Execution Mode:" in result.stdout
    assert "unresolved" in result.stdout
    assert "Next action:" in result.stdout
