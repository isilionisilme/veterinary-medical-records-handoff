from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "docs" / "check_router_directionality.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("check_router_directionality", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_manifest_mapping_maps_protected_targets() -> None:
    module = _load_guard_module()
    mapping = module._load_manifest_mapping(module.MANIFEST_PATH)
    assert mapping
    assert (
        "docs/agent_router/03_SHARED/WAY_OF_WORKING/10_starting-new-work-branch-first.md" in mapping
    )
    assert (
        "docs/shared/03-ops/way-of-working.md"
        in mapping[
            "docs/agent_router/03_SHARED/WAY_OF_WORKING/10_starting-new-work-branch-first.md"
        ]
    )


def test_load_manifest_mapping_supports_sources_block(tmp_path: Path) -> None:
    module = _load_guard_module()
    manifest = tmp_path / "MANIFEST.yaml"
    manifest.write_text(
        "\n".join(
            [
                "outputs:",
                "  - target: docs/agent_router/03_SHARED/WAY_OF_WORKING/00_entry.md",
                "    type: index",
                "    sources:",
                "      - docs/shared/03-ops/way-of-working.md",
                "      - docs/projects/veterinary-medical-records/03-ops/"
                "plan-execution-protocol.md",
            ]
        ),
        encoding="utf-8",
    )

    mapping = module._load_manifest_mapping(manifest)
    assert mapping["docs/agent_router/03_SHARED/WAY_OF_WORKING/00_entry.md"] == [
        "docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md",
        "docs/shared/03-ops/way-of-working.md",
    ]


def test_load_exempt_protected_files_reads_config(tmp_path: Path) -> None:
    module = _load_guard_module()
    config = tmp_path / "router_directionality_guard_config.json"
    config.write_text(
        json.dumps(
            {
                "exempt_protected_files": [
                    "docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json",
                    "docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json",
                ]
            }
        ),
        encoding="utf-8",
    )
    exempt_files = module._load_exempt_protected_files(config)
    assert "docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json" in exempt_files
    assert "docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json" in exempt_files


def test_load_exempt_protected_files_fails_when_missing(tmp_path: Path) -> None:
    module = _load_guard_module()
    with pytest.raises(SystemExit) as exc:
        module._load_exempt_protected_files(tmp_path / "missing.json")
    assert exc.value.code == 2
