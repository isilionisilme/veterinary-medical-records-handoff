from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[3]
PARITY_MAP = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "router_parity_map.json"
)
PARITY_SCRIPT = REPO_ROOT / "scripts" / "docs" / "check_doc_router_parity.py"


def _load_evaluate_parity():
    spec = importlib.util.spec_from_file_location("check_doc_router_parity", PARITY_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate_parity


def _unlink_fixture_file(path: Path) -> None:
    try:
        path.unlink()
    except PermissionError:
        os.chmod(path, 0o666)
        path.unlink(missing_ok=True)


def test_router_parity_map_file_exists() -> None:
    assert PARITY_MAP.exists(), "Missing router parity map JSON."


def test_evaluate_parity_reports_missing_terms_when_source_changes() -> None:
    evaluate_parity = _load_evaluate_parity()
    changed_files = ["docs/projects/veterinary-medical-records/01-product/product-design.md"]
    fixture_rel = f"tmp/parity-fixture-{uuid4().hex}.md"
    rules = [
        {
            "source_doc": "docs/projects/veterinary-medical-records/01-product/product-design.md",
            "router_modules": [
                {
                    "path": fixture_rel,
                    "required_terms": ["required-term"],
                }
            ],
        }
    ]

    fixture = REPO_ROOT / fixture_rel
    fixture.parent.mkdir(parents=True, exist_ok=True)
    try:
        fixture.write_text("fixture without required term", encoding="utf-8")
        findings = evaluate_parity(
            changed_files,
            rules,
            REPO_ROOT,
            fail_on_unmapped_sources=False,
            required_source_globs=[],
        )
        assert findings
        assert "missing required terms" in findings[0]
    finally:
        if fixture.exists():
            _unlink_fixture_file(fixture)
            if fixture.exists():
                print(f"WARNING: could not remove parity fixture file: {fixture}")


def test_evaluate_parity_skips_when_source_not_changed() -> None:
    evaluate_parity = _load_evaluate_parity()
    changed_files = ["docs/projects/veterinary-medical-records/01-product/ux-design.md"]
    rules = [
        {
            "source_doc": "docs/projects/veterinary-medical-records/01-product/product-design.md",
            "router_modules": [
                {
                    "path": (
                        "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/"
                        "76_conceptual-model-local-schema-global-schema-and-mapping.md"
                    ),
                    "required_terms": ["field_mapping_confidence"],
                }
            ],
        }
    ]

    findings = evaluate_parity(
        changed_files,
        rules,
        REPO_ROOT,
        fail_on_unmapped_sources=False,
        required_source_globs=[],
    )

    assert findings == []


def test_evaluate_parity_fails_on_unmapped_required_source() -> None:
    evaluate_parity = _load_evaluate_parity()
    findings = evaluate_parity(
        changed_files=["docs/projects/veterinary-medical-records/02-tech/technical-design.md"],
        rules=[
            {
                "source_doc": (
                    "docs/projects/veterinary-medical-records/01-product/product-design.md"
                ),
                "router_modules": [
                    {
                        "path": "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/00_entry.md",
                        "required_terms": ["PRODUCT_DESIGN — Modules"],
                    }
                ],
            }
        ],
        repo_root=REPO_ROOT,
        fail_on_unmapped_sources=True,
        required_source_globs=["docs/projects/veterinary-medical-records/*.md"],
    )
    assert len(findings) == 1
    assert "missing Source→Router parity mapping" in findings[0]


def test_evaluate_parity_excludes_source_matching_required_and_excluded_globs() -> None:
    evaluate_parity = _load_evaluate_parity()
    findings = evaluate_parity(
        changed_files=["docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_X.md"],
        rules=[
            {
                "source_doc": (
                    "docs/projects/veterinary-medical-records/01-product/product-design.md"
                ),
                "router_modules": [
                    {
                        "path": "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/00_entry.md",
                        "required_terms": ["PRODUCT_DESIGN"],
                    }
                ],
            }
        ],
        repo_root=REPO_ROOT,
        fail_on_unmapped_sources=True,
        required_source_globs=["docs/projects/veterinary-medical-records/**/*.md"],
        exclude_source_globs=["docs/projects/veterinary-medical-records/04-delivery/plans/**"],
    )
    assert findings == []
