from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_doc_test_sync.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_doc_test_sync", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _clear_relaxed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Keep tests deterministic regardless of CI/job-level env vars.
    monkeypatch.delenv("DOC_SYNC_RELAXED", raising=False)


def test_evaluate_sync_passes_when_no_docs_changed() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["frontend/src/App.tsx"],
        rules=[
            {
                "doc_glob": "docs/agent_router/**/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            }
        ],
        fail_on_unmapped_docs=True,
    )
    assert findings == []


def test_evaluate_sync_fails_when_mapped_doc_changes_without_related_file() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/shared/01-product/brand-guidelines.md"],
        rules=[
            {
                "doc_glob": "docs/shared/01-product/brand-guidelines.md",
                "required_any": ["scripts/check_brand_compliance.py"],
            }
        ],
        fail_on_unmapped_docs=True,
    )
    assert len(findings) == 1
    assert "check_brand_compliance.py" in findings[0]


def test_evaluate_sync_passes_when_mapped_doc_and_related_file_change() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=[
            "docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md",
            "backend/tests/unit/test_doc_updates_contract.py",
        ],
        rules=[
            {
                "doc_glob": "docs/agent_router/**/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            }
        ],
        fail_on_unmapped_docs=True,
    )
    assert findings == []


def test_evaluate_sync_covers_root_router_docs() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/agent_router/00_AUTHORITY.md"],
        rules=[
            {
                "doc_glob": "docs/agent_router/*.md",
                "required_any": ["backend/tests/unit/test_doc_router_contract.py"],
            }
        ],
        fail_on_unmapped_docs=True,
    )
    assert len(findings) == 1
    assert "test_doc_router_contract.py" in findings[0]


def test_evaluate_sync_fails_on_unmapped_doc_in_required_scope() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/projects/veterinary-medical-records/01-product/ux-design.md"],
        rules=[
            {
                "doc_glob": "docs/shared/01-product/brand-guidelines.md",
                "required_any": ["scripts/check_brand_compliance.py"],
            }
        ],
        fail_on_unmapped_docs=True,
        required_doc_globs=["docs/projects/veterinary-medical-records/*.md", "docs/shared/*.md"],
    )
    assert len(findings) == 1
    assert "not mapped in test_impact_map.json" in findings[0]


def test_evaluate_sync_ignores_unmapped_doc_outside_required_scope() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/agent_router/extraction/STRATEGY.md"],
        rules=[
            {
                "doc_glob": "docs/shared/01-product/brand-guidelines.md",
                "required_any": ["scripts/check_brand_compliance.py"],
            }
        ],
        fail_on_unmapped_docs=True,
        required_doc_globs=["docs/projects/veterinary-medical-records/*.md", "docs/shared/*.md"],
    )
    assert findings == []


def test_evaluate_sync_excludes_doc_matching_required_and_excluded_globs() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_X.md"],
        rules=[
            {
                "doc_glob": "docs/shared/01-product/brand-guidelines.md",
                "required_any": ["scripts/check_brand_compliance.py"],
            }
        ],
        fail_on_unmapped_docs=True,
        required_doc_globs=["docs/projects/veterinary-medical-records/**/*.md"],
        exclude_doc_globs=["docs/projects/veterinary-medical-records/04-delivery/plans/**"],
    )
    assert findings == []


def test_evaluate_sync_fails_on_unmapped_doc_when_fail_closed_enabled() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/agent_router/extraction/STRATEGY.md"],
        rules=[
            {
                "doc_glob": "docs/agent_router/**/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            }
        ],
        fail_on_unmapped_docs=True,
    )
    assert len(findings) == 1
    assert "related tests/guards" in findings[0]


def test_evaluate_sync_fails_when_owner_propagation_missing() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=["docs/shared/03-ops/engineering-playbook.md"],
        rules=[
            {
                "doc_glob": "docs/shared/*.md",
                "owner_any": ["docs/agent_router/03_SHARED/**/*.md"],
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            },
            {
                "doc_glob": "docs/agent_router/**/*.md",
            },
        ],
        fail_on_unmapped_docs=True,
    )
    assert len(findings) == 2
    assert any("related tests/guards" in finding for finding in findings)
    assert any("owner propagation" in finding for finding in findings)


def test_evaluate_sync_passes_when_owner_and_related_files_change() -> None:
    module = _load_guard_module()
    findings = module.evaluate_sync(
        changed_files=[
            "docs/shared/03-ops/engineering-playbook.md",
            "docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/150_documentation-guidelines.md",
            "backend/tests/unit/test_doc_updates_contract.py",
        ],
        rules=[
            {
                "doc_glob": "docs/shared/*.md",
                "owner_any": ["docs/agent_router/03_SHARED/**/*.md"],
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            },
            {
                "doc_glob": "docs/agent_router/**/*.md",
            },
        ],
        fail_on_unmapped_docs=True,
    )
    assert findings == []
