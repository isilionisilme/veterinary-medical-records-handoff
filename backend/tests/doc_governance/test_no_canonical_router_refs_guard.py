from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "docs" / "check_no_canonical_router_refs.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_no_canonical_router_refs", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_allows_governance_note_in_header_content() -> None:
    module = _load_guard_module()
    text = """# Title

> Router files under `docs/agent_router/` are derived outputs generated from this canonical source.

Body.
"""

    violations = module.find_violations_in_text(text)

    assert violations == []


def test_blocks_same_note_outside_header_window() -> None:
    module = _load_guard_module()
    filler = "\n".join([f"Line {i}" for i in range(1, 35)])
    governance_note = (
        "\n\n> Router files under `docs/agent_router/` are derived outputs "
        "generated from this canonical source.\n"
    )
    text = "# Title\n\n" + filler + governance_note

    violations = module.find_violations_in_text(text)

    assert len(violations) == 1
    assert "docs/agent_router" in violations[0][1]


def test_blocks_operational_router_path_reference() -> None:
    module = _load_guard_module()
    text = "Use `docs/agent_router/00_AUTHORITY.md` for routing.\n"

    violations = module.find_violations_in_text(text)

    assert len(violations) == 1
    assert "00_AUTHORITY.md" in violations[0][1]


def test_header_rule_ignores_yaml_frontmatter_lines() -> None:
    module = _load_guard_module()
    text = """---
title: Canonical Doc
owner: team
---

> Router files under `docs/agent_router/` are derived outputs generated from this canonical source.
"""

    violations = module.find_violations_in_text(text)

    assert violations == []


def test_excludes_plan_paths_from_scan() -> None:
    module = _load_guard_module()

    completed = (
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "04-delivery"
        / "plans"
        / "completed"
        / "COMPLETED_demo.md"
    )
    active = (
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "04-delivery"
        / "plans"
        / "PLAN_demo.md"
    )

    assert module.is_excluded_canonical_path(completed)
    assert module.is_excluded_canonical_path(active)


def test_iter_markdown_files_skips_delivery_plans(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_guard_module()

    docs_root = (
        tmp_path / "docs" / "projects" / "veterinary-medical-records" / "04-delivery" / "plans"
    )
    completed_dir = docs_root / "completed"
    completed_dir.mkdir(parents=True)
    active_file = docs_root / "PLAN_active.md"
    completed_file = completed_dir / "COMPLETED_old.md"
    active_file.write_text("# active\n", encoding="utf-8")
    completed_file.write_text("# old\n", encoding="utf-8")

    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CANONICAL_TARGETS", [tmp_path / "docs" / "projects"])

    scanned = module.iter_markdown_files()

    assert active_file not in scanned
    assert completed_file not in scanned


def test_categorize_backlog_as_planning_meta_doc() -> None:
    module = _load_guard_module()

    backlog_path = (
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "04-delivery"
        / "Backlog"
        / "imp-13-operational-runbook-architecture.md"
    )
    line = "- `docs/agent_router/01_WORKFLOW/START_WORK/`"

    category = module.categorize_violation(backlog_path, line)

    assert category == "planning/meta-doc"
