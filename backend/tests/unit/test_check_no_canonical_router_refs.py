from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_guard_module():
    module_path = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "docs"
        / "check_no_canonical_router_refs.py"
    )
    spec = importlib.util.spec_from_file_location("check_no_canonical_router_refs", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_categorize_violation_marks_plan_paths_as_planning_meta_doc():
    guard = _load_guard_module()
    path = (
        guard.REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "04-delivery"
        / "plans"
        / "PLAN_2026-03-05_RENUMBER-ROUTER-MINIFILES.md"
    )

    category = guard.categorize_violation(path, "See docs/agent_router/00_AUTHORITY.md")

    assert category == "planning/meta-doc"


def test_categorize_violation_marks_canonical_reference_as_operational():
    guard = _load_guard_module()
    path = guard.REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md"

    category = guard.categorize_violation(path, "Use docs/agent_router/00_AUTHORITY.md first.")

    assert category == "operational"
