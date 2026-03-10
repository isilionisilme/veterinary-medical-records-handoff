from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
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
BACKLOG_DIR = (
    REPO_ROOT / "docs" / "projects" / "veterinary-medical-records" / "04-delivery" / "Backlog"
)
IMPLEMENTATION_PLAN = (
    REPO_ROOT
    / "docs"
    / "projects"
    / "veterinary-medical-records"
    / "04-delivery"
    / "implementation-plan.md"
)
IMPLEMENTATION_PLAN_ROUTER_ENTRY = (
    REPO_ROOT / "docs" / "agent_router" / "04_PROJECT" / "IMPLEMENTATION_PLAN" / "00_entry.md"
)
IMPLEMENTATION_PLAN_ROUTER_RELEASE_6 = (
    REPO_ROOT
    / "docs"
    / "agent_router"
    / "04_PROJECT"
    / "IMPLEMENTATION_PLAN"
    / "120_release-6-explicit-overrides-workflow-closure.md"
)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_relative_markdown_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        target = match.group(1).strip()
        if not target:
            continue
        if target.startswith(("http://", "https://", "mailto:", "#", "<")):
            continue
        target_path = target.split("#", 1)[0].strip()
        if not target_path:
            continue
        targets.append(target_path)
    return targets


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


def test_docs_top_level_folders_are_limited_to_human_and_router_groups() -> None:
    actual_dirs = {
        child.name
        for child in DOCS_ROOT.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    }
    assert actual_dirs == {"shared", "projects", "agent_router"}


def test_agents_routes_docs_updated_intent_to_doc_updates() -> None:
    text = _read_text(ROOT_AGENTS)
    lower = text.lower()
    assert "docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md" in text
    assert "documentation was updated" in lower
    assert "run the doc_updates normalization pass once" in lower
    assert "belongs to the active agent for this chat" in text


def test_step_eligibility_rule_is_canonical_and_persistent() -> None:
    """After the auto-chain redesign, agent identity no longer blocks execution.
    Hard-gates and missing prompts are the only mandatory stop points.
    The eligibility rule references the decision table instead of
    re-declaring the logic inline."""
    rules_text = _read_text(EXECUTION_RULES)
    # New eligibility rule exists and references the decision table
    assert "Step eligibility rule" in rules_text
    assert "decision table" in rules_text
    assert "first `[ ]`" in rules_text
    # Old agent-identity handoff messages must NOT exist
    assert "This step does not belong to the active agent" not in rules_text
    # Old Spanish leftovers must NOT exist
    assert "selecciona el agente asignado para ese paso" not in rules_text
    assert "Vuelve a Claude (este chat)" not in rules_text
    assert "Vuelve al chat de Claude" not in rules_text


def test_token_efficiency_policy_persists_for_continue_flow() -> None:
    agents_text = _read_text(ROOT_AGENTS)
    rules_text = _read_text(EXECUTION_RULES)

    assert "iterative-retrieval" in agents_text
    assert "strategic-compact" in agents_text
    assert "iterative-retrieval" in rules_text
    assert "strategic-compact" in rules_text


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


def test_commit_automation_and_pre_pr_history_policy_propagates_to_owner_modules() -> None:
    execution_source = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "03-ops"
        / "plan-execution-protocol.md"
    )
    execution_owner = _read_text(
        REPO_ROOT
        / "docs"
        / "agent_router"
        / "03_SHARED"
        / "EXECUTION_PROTOCOL"
        / "50_rollback-governance.md"
    )
    wow_source = _read_text(WAY_OF_WORKING)
    wow_owner = _read_text(
        REPO_ROOT / "docs" / "agent_router" / "03_SHARED" / "WAY_OF_WORKING" / "50_pull-requests.md"
    )

    assert "### Execution Mode (Mandatory Plan-Start Choice)" in execution_source
    assert "### Pre-PR Requirements" in execution_source
    assert "select the execution mode" in execution_source

    assert "Execution Mode (Mandatory Plan-Start Choice)" in execution_owner
    assert "Pre-PR Requirements" in execution_owner

    assert "### Pre-PR Commit History Review (Hard Rule)" in wow_source
    assert "review the commit history on the feature branch" in wow_source
    assert "Pre-PR Commit History Review (Hard Rule)" in wow_owner


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


def test_commit_confirmation_policy_is_documented_across_general_and_plan_modes() -> None:
    source_text = _read_text(WAY_OF_WORKING)
    plan_protocol = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "03-ops"
        / "plan-execution-protocol.md"
    )

    assert "Agent commit confirmation (hard rule)" in source_text
    assert "Auto-commit without user confirmation is only permitted" in source_text
    assert "execution mode is `Autonomous`" in source_text
    assert "wait for explicit confirmation before running `git commit`" in source_text

    assert "Commit and push behavior are governed by the plan's execution mode" in plan_protocol
    assert "`Supervised` / `Semi-supervised`: requires explicit user approval" in plan_protocol
    assert "`Autonomous`: automatic after tests pass" in plan_protocol


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


def test_implementation_plan_tracks_us08_us09_us32_us39_as_implemented() -> None:
    text = _read_text(IMPLEMENTATION_PLAN)
    assert "[US-08 — Edit structured data](Backlog/us-08-edit-structured-data.md)" in text
    assert (
        "[US-09 — Capture correction signals](Backlog/us-09-capture-correction-signals.md)"
    ) in text
    assert (
        "[US-32 — Align review rendering to Global Schema template]"
        "(Backlog/us-32-align-review-rendering-to-global-schema-template.md)"
        " (Implemented 2026-02-17)"
    ) in text
    assert (
        "[US-39 — Align veterinarian confidence signal with mapping confidence policy]"
        "(Backlog/us-39-align-veterinarian-confidence-signal-with-mapping.md)"
    ) in text
    assert "User Story Details" not in text
    assert "Improvement Details" not in text
    assert "[Backlog Index](Backlog/README.md)" in text


def test_implementation_plan_router_tracks_us45_propagation() -> None:
    entry_text = _read_text(IMPLEMENTATION_PLAN_ROUTER_ENTRY)
    release_6_text = _read_text(IMPLEMENTATION_PLAN_ROUTER_RELEASE_6)
    assert (
        "279a_us-45-visit-detection-mvp-deterministic-contract-driven-coverage-improvement.md"
        in entry_text
    )
    assert (
        "US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement)"
        in release_6_text
    )


def test_implementation_plan_router_tracks_us46_propagation() -> None:
    source_text = _read_text(IMPLEMENTATION_PLAN)
    entry_text = _read_text(IMPLEMENTATION_PLAN_ROUTER_ENTRY)
    release_6_text = _read_text(IMPLEMENTATION_PLAN_ROUTER_RELEASE_6)

    assert (
        "[US-46 — Deterministic Visit Assignment Coverage MVP (Schema)]"
        "(Backlog/us-46-deterministic-visit-assignment-coverage-mvp-schema.md)" in source_text
    )
    assert "279b_us-46-deterministic-visit-assignment-coverage-mvp-schema.md" in entry_text
    assert "US-46 — Deterministic Visit Assignment Coverage MVP (Schema)" in release_6_text


def test_implementation_plan_backlog_split_propagates_to_owner_entry() -> None:
    source_text = _read_text(IMPLEMENTATION_PLAN)
    entry_text = _read_text(IMPLEMENTATION_PLAN_ROUTER_ENTRY)
    add_story_text = _read_text(
        REPO_ROOT
        / "docs"
        / "agent_router"
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "65_add-user-story-workflow.md"
    )

    assert "[Backlog Index](Backlog/README.md)" in source_text
    assert (
        "Story and improvement specifications now live in "
        "`docs/projects/veterinary-medical-records/04-delivery/Backlog/`"
    ) in entry_text
    assert "implementation-plan.md` reduced to release sequencing plus backlog links" in entry_text
    assert "Create or update the dedicated backlog item file for the story" in add_story_text
    assert "Add or update the consolidated index row for the story." in add_story_text


def test_backlog_markdown_relative_links_resolve() -> None:
    broken_links: list[str] = []

    for markdown_file in sorted(BACKLOG_DIR.rglob("*.md")):
        text = _read_text(markdown_file)
        for target in _iter_relative_markdown_targets(text):
            resolved = (markdown_file.parent / target).resolve(strict=False)
            if not resolved.exists():
                broken_links.append(f"{markdown_file.relative_to(REPO_ROOT)} -> {target}")

    assert not broken_links, "Broken relative markdown links:\n" + "\n".join(broken_links)


def test_ci_does_not_ignore_markdown_only_changes() -> None:
    text = _read_text(CI_WORKFLOW)
    assert "paths-ignore" not in text
    assert "check_doc_test_sync.py" in text
    assert "check_doc_router_parity.py" in text


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
