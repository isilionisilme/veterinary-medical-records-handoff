from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
DOC_GOVERNANCE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "doc-governance.yml"
RULES_INDEX = REPO_ROOT / "docs" / "agent_router" / "00_RULES_INDEX.md"
DOC_UPDATES_ENTRY = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "00_entry.md"
)
DOC_UPDATES_NORMALIZE = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "20_normalize_rules.md"
)
DOC_UPDATES_CHECKLIST = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "30_checklist.md"
)
DOC_UPDATES_TEST_IMPACT_MAP = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "test_impact_map.json"
)
DOC_UPDATES_ROUTER_PARITY_MAP = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "DOC_UPDATES" / "router_parity_map.json"
)
WAY_OF_WORKING = REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md"
CODE_REVIEW_OWNER = (
    REPO_ROOT / "docs" / "agent_router" / "03_SHARED" / "WAY_OF_WORKING" / "60_code-reviews.md"
)
CODE_REVIEW_ENTRY = (
    REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "CODE_REVIEW" / "00_entry.md"
)
EXECUTION_RULES = (
    REPO_ROOT / "docs" / "projects" / "veterinary-medical-records" / "03-ops" / "execution-rules.md"
)
BACKEND_IMPLEMENTATION_ROUTER_ENTRY = (
    REPO_ROOT / "docs" / "agent_router" / "04_PROJECT" / "BACKEND_IMPLEMENTATION" / "00_entry.md"
)
TECHNICAL_DESIGN_ROUTER_ENTRY = (
    REPO_ROOT / "docs" / "agent_router" / "04_PROJECT" / "TECHNICAL_DESIGN" / "00_entry.md"
)
DOC_TEST_SYNC_GUARD = REPO_ROOT / "scripts" / "docs" / "check_doc_test_sync.py"
DOC_ROUTER_PARITY_GUARD = REPO_ROOT / "scripts" / "docs" / "check_doc_router_parity.py"
PRECOMMIT_HOOK = REPO_ROOT / ".githooks" / "pre-commit"
PRECOMMIT_INSTALLER = REPO_ROOT / "scripts" / "ci" / "install-pre-commit-hook.ps1"
DOCS_ROOT = REPO_ROOT / "docs"
ADR_ROOT = REPO_ROOT / "docs" / "projects" / "veterinary-medical-records" / "02-tech" / "adr"
ADR_INDEX = ADR_ROOT / "index.md"
ADR_ARCH_0006 = ADR_ROOT / "ADR-ARCH-0006-frontend-stack-react-tanstack-query-vite.md"
ADR_ARCH_0008 = ADR_ROOT / "ADR-ARCH-0008-confidence-scoring-algorithm.md"
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n", re.DOTALL)
GITHUB_PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
GITHUB_INSTRUCTIONS_DIR = REPO_ROOT / ".github" / "instructions"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_frontmatter(path: Path) -> dict[str, object]:
    text = _read_text(path)
    match = FRONTMATTER_PATTERN.match(text)
    assert match, f"Missing YAML frontmatter: {path.relative_to(REPO_ROOT)}"
    data = yaml.safe_load(match.group("frontmatter"))
    assert isinstance(data, dict), f"Frontmatter must be a mapping: {path.relative_to(REPO_ROOT)}"
    return data


def test_doc_updates_core_files_exist() -> None:
    assert ROOT_AGENTS.exists(), "Missing AGENTS.md router entrypoint."
    assert DOC_UPDATES_ENTRY.exists(), "Missing DOC_UPDATES entry module."
    assert DOC_UPDATES_NORMALIZE.exists(), "Missing DOC_UPDATES normalization module."
    assert DOC_UPDATES_CHECKLIST.exists(), "Missing DOC_UPDATES checklist module."
    assert DOC_UPDATES_TEST_IMPACT_MAP.exists(), "Missing DOC_UPDATES test impact map."
    assert DOC_UPDATES_ROUTER_PARITY_MAP.exists(), "Missing DOC_UPDATES router parity map."
    assert DOC_TEST_SYNC_GUARD.exists(), "Missing doc/test sync guard script."
    assert DOC_ROUTER_PARITY_GUARD.exists(), "Missing doc/router parity guard script."
    assert PRECOMMIT_HOOK.exists(), "Missing pre-commit hook entrypoint."
    assert PRECOMMIT_INSTALLER.exists(), "Missing pre-commit hook installer."
    assert RULES_INDEX.exists(), "Missing rules index."


def test_github_operational_prompts_exist() -> None:
    expected_files = {
        "code-review.prompt.md",
        "doc-updates.prompt.md",
        "pr-workflow.prompt.md",
        "scope-boundary.prompt.md",
        "start-work.prompt.md",
    }

    actual_files = {path.name for path in GITHUB_PROMPTS_DIR.glob("*.prompt.md")}

    assert actual_files == expected_files


def test_github_instructions_exist() -> None:
    expected_files: set[str] = set()

    actual_files = {path.name for path in GITHUB_INSTRUCTIONS_DIR.glob("*.instructions.md")}

    assert actual_files == expected_files


def test_instructions_files_have_valid_applyto_patterns() -> None:
    for instructions_file in sorted(GITHUB_INSTRUCTIONS_DIR.glob("*.instructions.md")):
        frontmatter = _load_frontmatter(instructions_file)
        apply_to = frontmatter.get("applyTo")
        assert isinstance(apply_to, str) and apply_to.strip(), (
            f"Missing applyTo in {instructions_file.relative_to(REPO_ROOT)}"
        )

        matches = {
            path.relative_to(REPO_ROOT).as_posix()
            for path in REPO_ROOT.glob(apply_to)
            if path.is_file()
        }
        assert matches, (
            f"applyTo pattern {apply_to!r} in {instructions_file.relative_to(REPO_ROOT)} "
            "does not match any file"
        )


def test_docs_top_level_folders_are_limited_to_human_and_router_groups() -> None:
    actual_dirs = {
        child.name
        for child in DOCS_ROOT.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    }
    assert actual_dirs == {"shared", "projects", "agent_router"}


def test_adr_index_tracks_arch_0006_and_arch_0008() -> None:
    assert ADR_ARCH_0006.exists()
    assert ADR_ARCH_0008.exists()

    index_text = _read_text(ADR_INDEX)
    assert "ADR-ARCH-0006" in index_text
    assert "ADR-ARCH-0008" in index_text


def test_agents_routes_docs_updated_intent_to_doc_updates() -> None:
    text = _read_text(ROOT_AGENTS)
    lower = text.lower()
    assert "docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md" in text
    assert "documentation was updated" in lower
    assert "run the doc_updates normalization pass once" in lower


def test_doc_updates_entry_covers_triggers_and_summary_schema() -> None:
    text = _read_text(DOC_UPDATES_ENTRY)
    lower = text.lower()
    assert "A: user specifies document(s)" in text
    assert "B: user does not specify docs" in text
    assert "C: user asks to update a legacy/reference doc" in text
    assert "Use case D" in text
    assert "Use case E" in text
    assert "git status --porcelain" in text
    assert "git diff --name-status" in text
    assert "git diff --cached --name-status" in text
    assert "@{upstream}..HEAD" in text
    assert "<base_ref>...HEAD" in text
    assert "git diff -- <path>" in text
    assert "test_impact_map.json" in text
    assert "router_parity_map.json" in text
    assert "Related tests/guards updated" in text
    assert "Evidence source" in text
    assert "Source→Router parity" in text
    assert "DOC_UPDATES Summary" in text
    assert "Propagation gaps" in text
    assert "show me the unpropagated changes" in lower
    assert "muestrame los cambios no propagados" in lower


def test_doc_updates_entry_requires_snippet_minimum_inputs() -> None:
    text = _read_text(DOC_UPDATES_ENTRY)
    assert "If snippet lacks file path or section context" in text


def test_normalization_rules_enforce_diff_first_and_owner_updates() -> None:
    text = _read_text(DOC_UPDATES_NORMALIZE)
    assert "Inspect change evidence first" in text
    assert "Rule change" in text
    assert "Clarification" in text
    assert "Navigation" in text
    assert "Mixed classification is allowed within one file" in text
    assert "update/create owner module before summary output" in text
    assert "new rule id is introduced" in text
    assert "owner module changes" in text
    assert "routing/intent changes" in text
    assert "source-to-router parity" in text.lower()
    assert (
        "if Rule change exists with no propagation and no blocker reason, treat as failure" in text
    )
    assert "Known mappings" in text
    assert "do not auto-pick silently" in text


def test_checklist_enforces_discovery_and_anti_loop() -> None:
    text = _read_text(DOC_UPDATES_CHECKLIST)
    assert "git status --porcelain" in text
    assert "git diff --name-status" in text
    assert "@{upstream}..HEAD" in text
    assert "<base_ref>...HEAD" in text
    assert "Normaliz" in text and "no loop" in text.lower()
    assert "DOC_UPDATES Summary" in text
    assert "Propagation gaps" in text
    assert "related test/guard file was updated" in text
    assert "router_parity_map.json" in text
    assert "Source-to-router parity status" in text
    assert "Evidence source per processed doc" in text


def test_doc_test_sync_map_has_minimum_rules() -> None:
    text = _read_text(DOC_UPDATES_TEST_IMPACT_MAP)
    assert '"fail_on_unmapped_docs": true' in text
    assert '"doc_glob": "docs/agent_router/*.md"' in text
    assert '"doc_glob": "docs/agent_router/**/*.md"' in text
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/99-archive/12-factor-audit.md"'
        in text
    )
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/backend-implementation.md"'
        in text
    )
    assert '"doc_glob": "docs/projects/veterinary-medical-records/01-product/ux-design.md"' in text
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/technical-design.md"' in text
    )
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/03-ops/execution-rules.md"' in text
    )
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/03-ops/'
        'architecture-audit-process.md"' in text
    )
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/audits/'
        'architecture-review-*.md"' in text
    )
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/audits/'
        'improvement-backlog-*.md"' in text
    )
    assert '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/adr/**/*.md"' in text
    assert '"owner_any"' in text
    assert '"docs/agent_router/03_SHARED/WAY_OF_WORKING/*.md"' in text
    assert '"docs/agent_router/04_PROJECT/BACKEND_IMPLEMENTATION/*.md"' in text
    assert '"doc_glob": "docs/shared/01-product/brand-guidelines.md"' in text
    assert '"doc_glob": "docs/shared/01-product/ux-guidelines.md"' in text
    assert '"doc_glob": "docs/shared/02-tech/coding-standards.md"' in text
    assert '"doc_glob": "docs/shared/02-tech/documentation-guidelines.md"' in text
    assert "test_doc_updates_contract.py" in text
    assert "check_brand_compliance.py" in text


def test_router_parity_map_has_product_design_rule() -> None:
    text = _read_text(DOC_UPDATES_ROUTER_PARITY_MAP)
    assert '"fail_on_unmapped_sources": true' in text
    assert '"required_source_globs"' in text
    assert '"docs/projects/veterinary-medical-records/*.md"' in text
    assert '"docs/shared/*.md"' in text
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/99-archive/12-factor-audit.md"'
        in text
    )
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/01-product/product-design.md"'
        in text
    )
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/02-tech/technical-design.md"'
        in text
    )
    assert '"source_doc": "docs/shared/03-ops/way-of-working.md"' in text
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/03-ops/execution-rules.md"' in text
    )
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/03-ops/'
        'architecture-audit-process.md"' in text
    )
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/02-tech/audits/'
        'architecture-review-*.md"' in text
    )
    assert (
        '"source_doc": "docs/projects/veterinary-medical-records/02-tech/audits/'
        'improvement-backlog-*.md"' in text
    )
    assert (
        '"path": "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/'
        '76_conceptual-model-local-schema-global-schema-and-mapping.md"' in text
    )
    assert '"required_terms"' in text


def test_code_review_guidance_terms_are_propagated() -> None:
    source_text = _read_text(WAY_OF_WORKING)
    owner_text = _read_text(CODE_REVIEW_OWNER)
    entry_text = _read_text(CODE_REVIEW_ENTRY)

    source_terms = (
        "Database migrations/schema safety",
        "Severity Classification",
        "Large Diff Policy",
        "Pre-Existing Issues",
    )
    owner_terms = (
        "Pre-review checklist",
        "Severity classification criteria",
        "Large diff policy",
        "Pre-existing issues policy",
    )

    for term in source_terms:
        assert term in source_text
    for term in owner_terms:
        assert term in owner_text

    assert "Pre-review gate (required before diff reading)" in entry_text
    assert "Database migrations/schema safety" in entry_text
    assert "Pre-existing issues" in entry_text


def test_preflight_levels_policy_is_documented_for_pr_flow() -> None:
    source_text = _read_text(WAY_OF_WORKING)
    pr_router = (
        REPO_ROOT / "docs" / "agent_router" / "03_SHARED" / "WAY_OF_WORKING" / "50_pull-requests.md"
    )
    pr_router_text = _read_text(pr_router)
    readme_text = _read_text(REPO_ROOT / "README.md")
    source_lower = source_text.lower()
    router_lower = pr_router_text.lower()

    required_source_terms = (
        "local preflight levels",
        "l1 — quick",
        "l2 — push",
        "l3 — full",
        "before pull request creation",
        "preflight auto-fix policy",
        "maximum automatic remediation loop",
        "forcefrontend",
        "forcefull",
        "ci is green",
    )

    for term in required_source_terms:
        assert term in source_lower

    router_terms = (
        "local preflight levels",
        "l1 — quick",
        "l2 — push",
        "l3 — full",
        "before pr creation/update",
        "auto-fix policy when preflight fails",
        "maximum automatic remediation loop: 2 attempts",
        "forcefrontend",
        "forcefull",
        "ci is green",
    )

    for term in router_terms:
        assert term in router_lower

    assert "test-L1.ps1" in readme_text
    assert "test-L2.ps1" in readme_text
    assert "test-L3.ps1" in readme_text
    assert "install-pre-commit-hook.ps1" in readme_text
    assert "Maximum automatic remediation loop: 2 attempts" in pr_router_text


def test_post_merge_cleanup_requires_remote_branch_deletion() -> None:
    source_text = _read_text(WAY_OF_WORKING)
    shared_pr_router = _read_text(
        REPO_ROOT / "docs" / "agent_router" / "03_SHARED" / "WAY_OF_WORKING" / "50_pull-requests.md"
    )
    workflow_pr_router = _read_text(
        REPO_ROOT / "docs" / "agent_router" / "01_WORKFLOW" / "PULL_REQUESTS" / "00_entry.md"
    )

    required_term = (
        "Attempt to delete the remote branch (`git push origin --delete <branch-name>`)."
    )
    fallback_term = (
        "If it fails because the branch is missing, protected, or you lack permissions, "
        "report it and continue cleanup."
    )

    assert required_term in source_text
    assert required_term in shared_pr_router
    assert required_term in workflow_pr_router
    assert fallback_term in source_text
    assert fallback_term in shared_pr_router
    assert fallback_term in workflow_pr_router


def test_owner_entries_track_iteration_4_doc_propagation() -> None:
    backend_text = _read_text(BACKEND_IMPLEMENTATION_ROUTER_ENTRY)
    technical_text = _read_text(TECHNICAL_DESIGN_ROUTER_ENTRY)
    parity_guard_text = _read_text(DOC_ROUTER_PARITY_GUARD)

    assert "infra (infrastructure)" in backend_text
    assert "backend/app/infra/" in backend_text
    assert "infra (infrastructure)" in technical_text
    assert "Known Limitations propagation note" in technical_text
    assert "Checked source->router parity against mapped changed docs" in parity_guard_text


def test_rules_index_contains_known_mapping_hints() -> None:
    text = _read_text(RULES_INDEX)
    assert "Known mapping hints" in text
    assert "50_3-typography-exact-fonts-mandatory.md" in text
    assert "40_2-color-system-exact-values-mandatory.md" in text
    assert "04_PROJECT/UX_DESIGN/00_entry.md" in text


def test_governance_checks_moved_to_separate_workflow() -> None:
    """Verify that doc governance checks have been moved from ci.yml to doc-governance.yml."""
    ci_text = _read_text(CI_WORKFLOW)
    governance_text = _read_text(DOC_GOVERNANCE_WORKFLOW)

    assert "paths-ignore" not in ci_text
    assert "check_doc_test_sync.py" not in ci_text
    assert "check_doc_router_parity.py" not in ci_text
    assert "check_doc_test_sync.py" in governance_text
    assert "check_doc_router_parity.py" in governance_text


def test_execution_rules_exist_and_contain_core_sections() -> None:
    rules_text = _read_text(EXECUTION_RULES)
    assert "Execution mode defaults" in rules_text
    assert "SCOPE BOUNDARY" in rules_text
    assert "Plan-edit-last" in rules_text
    assert "CI GATE" in rules_text
    assert "AUTO-CHAIN" in rules_text
    assert "Commit conventions" in rules_text


def test_execution_rules_reference_preflight_levels() -> None:
    """execution-rules.md must reference L1/L2/L3 preflight levels so agents
    discover the local preflight system when following the execution protocol."""
    rules_text = _read_text(EXECUTION_RULES)
    # Script references (post-reorg paths under scripts/ci/)
    assert "test-L1" in rules_text
    assert "test-L2" in rules_text
    assert "test-L3" in rules_text
    # Level labels
    assert "L1 —" in rules_text or "L1 — Quick" in rules_text
    assert "L2 —" in rules_text or "L2 — Push" in rules_text
    assert "L3 —" in rules_text or "L3 — Full" in rules_text
