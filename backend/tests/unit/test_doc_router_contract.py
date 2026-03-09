from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROUTER_ROOT = REPO_ROOT / "docs" / "agent_router"
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
AUTHORITY_DOC = ROUTER_ROOT / "00_AUTHORITY.md"
FALLBACK_DOC = ROUTER_ROOT / "00_FALLBACK.md"
RULES_INDEX_DOC = ROUTER_ROOT / "00_RULES_INDEX.md"

DOC_REF_PATTERN = re.compile(r"(docs/[A-Za-z0-9_./-]+\.md)")

MAX_ROOT_AGENTS_CHARS = 4000
MAX_AUTHORITY_CHARS = 3000


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_doc_refs(text: str) -> set[str]:
    return set(DOC_REF_PATTERN.findall(text))


def test_entrypoint_contract_paths_exist() -> None:
    assert ROOT_AGENTS.exists(), "Missing root AGENTS.md entrypoint."
    assert AUTHORITY_DOC.exists(), "Missing authority router document."
    assert FALLBACK_DOC.exists(), "Missing fallback router document."
    assert RULES_INDEX_DOC.exists(), "Missing rules index document."

    agents_text = _read_text(ROOT_AGENTS)
    assert "docs/agent_router/00_AUTHORITY.md" in agents_text
    assert "docs/agent_router/00_FALLBACK.md" in agents_text


def test_authority_plan_audit_intent_exists() -> None:
    authority_text = _read_text(AUTHORITY_DOC)
    assert "Plan audit" in authority_text, (
        "00_AUTHORITY.md must include a 'Plan audit' intent entry."
    )
    assert "EXECUTION_PROTOCOL" in authority_text, (
        "Plan audit intent must route to EXECUTION_PROTOCOL module."
    )


def test_entrypoint_docs_stay_small() -> None:
    assert len(_read_text(ROOT_AGENTS)) <= MAX_ROOT_AGENTS_CHARS
    assert len(_read_text(AUTHORITY_DOC)) <= MAX_AUTHORITY_CHARS


def test_router_doc_references_resolve() -> None:
    missing_refs: list[str] = []

    for markdown_file in ROUTER_ROOT.rglob("*.md"):
        for ref in _extract_doc_refs(_read_text(markdown_file)):
            if not (REPO_ROOT / ref).exists():
                missing_refs.append(f"{markdown_file}: {ref}")

    assert not missing_refs, "Found unresolved docs references:\n" + "\n".join(missing_refs)


def test_rules_index_owner_modules_exist() -> None:
    missing_refs: list[str] = []

    for ref in _extract_doc_refs(_read_text(RULES_INDEX_DOC)):
        if not (REPO_ROOT / ref).exists():
            missing_refs.append(ref)

    assert not missing_refs, "Rules index references missing files:\n" + "\n".join(missing_refs)


def test_router_docs_do_not_use_legacy_top_level_paths() -> None:
    forbidden_paths = (
        "docs/00_AUTHORITY.md",
        "docs/00_FALLBACK.md",
        "docs/00_RULES_INDEX.md",
        "docs/01_WORKFLOW/",
        "docs/02_PRODUCT/",
        "docs/03_SHARED/",
        "docs/04_PROJECT/",
    )
    violations: list[str] = []

    for markdown_file in ROUTER_ROOT.rglob("*.md"):
        text = _read_text(markdown_file)
        for forbidden in forbidden_paths:
            if forbidden in text:
                violations.append(f"{markdown_file}: {forbidden}")

    assert not violations, "Found legacy paths in router docs:\n" + "\n".join(violations)


def test_operational_modules_do_not_directly_load_human_docs() -> None:
    forbidden_prefixes = ("docs/shared/", "docs/projects/veterinary-medical-records/")
    violations: list[str] = []

    for subfolder in ("01_WORKFLOW", "02_PRODUCT"):
        folder = ROUTER_ROOT / subfolder
        for markdown_file in folder.rglob("*.md"):
            for ref in _extract_doc_refs(_read_text(markdown_file)):
                if ref.startswith(forbidden_prefixes):
                    violations.append(f"{markdown_file}: {ref}")

    assert not violations, (
        "Operational modules should route through docs/agent_router/*, "
        "not direct human docs:\n" + "\n".join(violations)
    )


def test_project_split_entries_include_new_product_and_ux_modules() -> None:
    product_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "PRODUCT_DESIGN" / "00_entry.md")
    ux_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "UX_DESIGN" / "00_entry.md")

    assert (
        "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/75_4-4-critical-non-reversible-changes-policy.md"
        in product_entry
    )
    assert (
        "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/76_conceptual-model-local-schema-global-schema-and-mapping.md"
        in product_entry
    )
    assert (
        "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/77_global-schema-canonical-field-list.md"
        in product_entry
    )
    assert (
        "docs/agent_router/04_PROJECT/UX_DESIGN/55_review-ui-rendering-rules-global-schema-template.md"
        in ux_entry
    )


def test_project_split_entry_includes_frontend_global_schema_rendering_module() -> None:
    frontend_entry = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "FRONTEND_IMPLEMENTATION" / "00_entry.md"
    )
    assert (
        "docs/agent_router/04_PROJECT/FRONTEND_IMPLEMENTATION/65_review-rendering-backbone-global-schema.md"
        in frontend_entry
    )


def test_project_split_entry_includes_design_system_module() -> None:
    project_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "00_entry.md")
    assert "docs/agent_router/04_PROJECT/DESIGN_SYSTEM/00_entry.md" in project_entry


def test_project_split_entry_includes_implementation_plan_us32_module() -> None:
    plan_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "IMPLEMENTATION_PLAN" / "00_entry.md")
    release5 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "110_release-5-editing-learning-signals-human-corrections.md"
    )

    assert (
        "docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/275_us-32-align-review-rendering-to-global-schema-template.md"
        in plan_entry
    )
    assert "US-32 — Align review rendering to Global Schema template" in release5


def test_project_split_entry_includes_implementation_plan_us35_module() -> None:
    plan_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "IMPLEMENTATION_PLAN" / "00_entry.md")
    release4 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "100_release-4-assisted-review-in-context-high-value-higher-risk.md"
    )

    assert (
        "docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/276_us-35-resizable-splitter-between-pdf-viewer-and-structured-data-panel.md"
        in plan_entry
    )
    assert "US-35 — Resizable splitter between PDF Viewer and Structured Data panel" in release4


def test_project_split_entry_includes_implementation_plan_us41_module() -> None:
    plan_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "IMPLEMENTATION_PLAN" / "00_entry.md")
    release5 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "110_release-5-editing-learning-signals-human-corrections.md"
    )

    assert (
        "docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/"
        "277_us-41-show-top-5-candidate-suggestions-in-field-edit-modal.md" in plan_entry
    )
    assert "US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal" in release5


def test_project_split_entry_includes_implementation_plan_us42_module() -> None:
    plan_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "IMPLEMENTATION_PLAN" / "00_entry.md")
    release6 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "120_release-6-explicit-overrides-workflow-closure.md"
    )

    assert (
        "docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/"
        "278_us-42-provide-evaluator-friendly-installation-execution-docker-first.md" in plan_entry
    )
    assert "US-42 — Provide evaluator-friendly installation & execution (Docker-first)" in release6


def test_implementation_plan_us42_status_is_propagated() -> None:
    source_plan = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "04-delivery"
        / "Backlog"
        / "us-42-provide-evaluator-friendly-installation-execution.md"
    )
    owner_module = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "278_us-42-provide-evaluator-friendly-installation-execution-docker-first.md"
    )

    assert "**Status**: Implemented (2026-02-19)" in source_plan
    assert "**Status**: Implemented (2026-02-19)" in owner_module


def test_technical_design_unassigned_contract_clarification_is_propagated() -> None:
    source_doc = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "02-tech"
        / "technical-design.md"
    )
    owner_doc = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "TECHNICAL_DESIGN"
        / "505_d9-structured-interpretation-schema-visit-grouped-normative.md"
    )

    expected_term = "explicit contract value"
    expected_phrase = "single synthetic `unassigned` group is valid"

    assert expected_term in source_doc
    assert expected_term in owner_doc
    assert expected_phrase in source_doc
    assert expected_phrase in owner_doc


def test_technical_design_sufficient_evidence_boundary_is_propagated() -> None:
    source_doc = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "02-tech"
        / "technical-design.md"
    )
    owner_doc = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "TECHNICAL_DESIGN"
        / "505_d9-structured-interpretation-schema-visit-grouped-normative.md"
    )

    required_terms = (
        "Sufficient evidence boundary for assigned VisitGroup creation",
        "visit context (`visita|consulta|control|revisión|seguimiento|ingreso|alta`)",
        "MUST NOT create assigned VisitGroups",
        "ambiguous date tokens without sufficient visit context",
    )

    for term in required_terms:
        assert term in source_doc
        assert term in owner_doc


def test_way_of_working_plan_level_pr_roadmap_is_propagated() -> None:
    source_doc = _read_text(REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md")
    owner_doc = _read_text(ROUTER_ROOT / "03_SHARED" / "WAY_OF_WORKING" / "50_pull-requests.md")

    source_terms = (
        "Plan-Level Pull Request Roadmap",
        "Each phase belongs to exactly one Pull Request",
        "Each execution step carries a `**[PR-X]**` tag",
    )
    owner_terms = (
        "Plan-level PR Roadmap",
        "Each phase belongs to exactly one PR",
        "Each execution step in the Execution Status must carry a `**[PR-X]**` tag",
    )

    for term in source_terms:
        assert term in source_doc
    for term in owner_terms:
        assert term in owner_doc


def test_way_of_working_branch_naming_worktree_prefix_is_propagated() -> None:
    source_doc = _read_text(REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md")
    owner_doc = _read_text(
        ROUTER_ROOT / "03_SHARED" / "WAY_OF_WORKING" / "30_branching-strategy.md"
    )
    workflow_doc = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "BRANCHING" / "00_entry.md")

    required_terms = (
        "Canonical format:",
        "codex/<worktree>/<category>/<slug>",
        "Category-specific branch patterns:",
        "Legacy format `<worktree>/<category>/<slug>` is temporarily allowed during migration.",
        "Legacy format `<category>/<slug>` is temporarily allowed during migration.",
        "Detached HEAD is exempt from this naming convention.",
    )

    for term in required_terms:
        assert term in source_doc
        assert term in owner_doc
        assert term in workflow_doc


def test_way_of_working_canonical_branch_creation_rules_are_propagated() -> None:
    source_doc = _read_text(REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md")
    start_work_doc = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "START_WORK" / "00_entry.md")
    branching_doc = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "BRANCHING" / "00_entry.md")

    start_work_terms = (
        "build `<branch-name>` using the canonical format `codex/<worktree>/<category>/<slug>`",
        "Derive `worktree` from the current repository top-level folder name",
        "user story -> `feature`",
        "user-facing improvement -> `improvement`",
        "technical work -> `fix`, `docs`, `chore`, `refactor`, or `ci`",
    )
    branching_terms = (
        "Creation-time rule:",
        "During `Starting New Work`, the agent must derive and create branch names "
        "in canonical format",
        "category mapping defined in Section 1.",
    )

    for term in start_work_terms:
        assert term in source_doc
        assert term in start_work_doc

    for term in branching_terms:
        assert term in source_doc
        assert term in branching_doc


def test_pull_request_procedure_ai_automation_clauses_are_propagated() -> None:
    source_doc = _read_text(REPO_ROOT / "docs" / "shared" / "03-ops" / "way-of-working.md")
    owner_doc = _read_text(ROUTER_ROOT / "03_SHARED" / "WAY_OF_WORKING" / "50_pull-requests.md")
    workflow_doc = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "PULL_REQUESTS" / "00_entry.md")

    required_terms = (
        "When the user explicitly requests Pull Request creation or update",
        "After a Pull Request is merged into `main`, "
        "the AI assistant must run this cleanup automatically",
    )

    for term in required_terms:
        assert term in source_doc
        assert term in owner_doc
        assert term in workflow_doc


def test_user_visible_entry_includes_design_system_module() -> None:
    user_visible_entry = _read_text(ROUTER_ROOT / "02_PRODUCT" / "USER_VISIBLE" / "00_entry.md")
    design_system_entry = _read_text(ROUTER_ROOT / "02_PRODUCT" / "DESIGN_SYSTEM" / "00_entry.md")

    assert "docs/agent_router/02_PRODUCT/DESIGN_SYSTEM/00_entry.md" in user_visible_entry
    assert "docs/agent_router/04_PROJECT/DESIGN_SYSTEM/00_entry.md" in design_system_entry


def test_code_review_protocol_requires_pr_comment_urls_and_follow_up() -> None:
    code_review_entry = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "CODE_REVIEW" / "00_entry.md")
    pr_commenting = _read_text(ROUTER_ROOT / "01_WORKFLOW" / "CODE_REVIEW" / "20_pr_commenting.md")

    assert "Mandatory publication protocol (blocking)" in code_review_entry
    assert "the PR comment URL is returned to the user" in code_review_entry
    assert "follow-up PR comment" in code_review_entry

    assert "Blocking execution sequence" in pr_commenting
    assert "Return the published PR comment URL" in pr_commenting
    assert "Return the follow-up PR comment URL" in pr_commenting
    assert (
        "This follow-up must be published automatically as part of the "
        "remediation workflow (do not wait for a separate user prompt)." in pr_commenting
    )


def test_product_design_module_76_includes_confidence_context_contract_terms() -> None:
    module_76 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "PRODUCT_DESIGN"
        / "76_conceptual-model-local-schema-global-schema-and-mapping.md"
    )

    for required_term in (
        "candidate_confidence",
        "field_mapping_confidence",
        "Context (Deterministic)",
        "Learnable Unit (`mapping_id`)",
        "Signals & Weighting (qualitative)",
        "Policy State (soft behavior)",
        "Confidence Propagation & Calibration",
        "Global Schema keys/order do not change automatically during this propagation",
    ):
        assert required_term in module_76


def test_project_owner_modules_include_confidence_tooltip_breakdown_propagation() -> None:
    ux_module = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "UX_DESIGN" / "50_4-veterinarian-review-flow.md"
    )
    design_system_module = _read_text(ROUTER_ROOT / "04_PROJECT" / "DESIGN_SYSTEM" / "00_entry.md")
    technical_module = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "TECHNICAL_DESIGN" / "140_7-confidence-technical-contract.md"
    )
    backend_module = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "BACKEND_IMPLEMENTATION"
        / "100_structured-interpretation-schema.md"
    )
    frontend_module = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "FRONTEND_IMPLEMENTATION" / "110_confidence-rendering.md"
    )
    implementation_plan_release = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "IMPLEMENTATION_PLAN"
        / "110_release-5-editing-learning-signals-human-corrections.md"
    )
    technical_b3 = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "TECHNICAL_DESIGN"
        / "320_b3-minimal-api-endpoint-map-authoritative.md"
    )

    assert "Confidence tooltip breakdown (veterinarian UI)" in ux_module
    assert "Propagation note:" in design_system_module
    assert "Tooltip breakdown visibility contract (MVP)" in technical_module
    assert "Unit/scale: ratio in `[0,1]` when present." in technical_module
    assert "Unit: signed percentage points" in technical_module
    assert "Tooltip breakdown data sourcing (MVP)" in backend_module
    assert "Confidence tooltip breakdown rendering (MVP)" in frontend_module
    assert (
        "US-39 — Align veterinarian confidence signal with mapping confidence policy"
        in implementation_plan_release
    )
    assert (
        "US-40 — Implement field-level confidence tooltip breakdown" in implementation_plan_release
    )
    assert "US-32 — Align review rendering to Global Schema template" in implementation_plan_release
    assert (
        "US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal"
        in implementation_plan_release
    )
    assert "Field Candidate Suggestions (standard review payload)" in technical_b3


def test_technical_design_entry_includes_d9_visit_grouped_module() -> None:
    technical_entry = _read_text(ROUTER_ROOT / "04_PROJECT" / "TECHNICAL_DESIGN" / "00_entry.md")

    assert (
        "docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/"
        "505_d9-structured-interpretation-schema-visit-grouped-normative.md" in technical_entry
    )


def test_product_and_ux_owner_modules_include_visit_grouping_and_copy_updates() -> None:
    product_module = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "PRODUCT_DESIGN" / "77_global-schema-canonical-field-list.md"
    )
    ux_module = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "UX_DESIGN"
        / "55_review-ui-rendering-rules-global-schema-template.md"
    )

    assert "## Visit grouping (MVP)" in product_module
    assert "`document_date` is removed from the MVP schema" in product_module
    assert "`claim_id` is removed from the MVP schema" in product_module
    assert (
        "owner_id (string) (optional; product semantics in MVP: "
        "owner address shown as label" in product_module
    )
    assert "Key -> UI label -> Section (UI)" in product_module

    assert (
        "Render fixed non-visit sections plus a dedicated **Visitas** grouping block." in ux_module
    )
    assert (
        "No heuristics grouping in UI; grouping comes from `visits[]` in the canonical contract."
        in ux_module
    )
    assert "Synthetic unassigned group copy is fixed: **Sin asignar / Sin fecha**." in ux_module
    assert (
        "Review state remains document-level in MVP, even when multiple visits are present."
        in ux_module
    )


def test_frontend_implementation_note_includes_build_determinism_and_required_checks() -> None:
    source_doc = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "02-tech"
        / "frontend-implementation.md"
    )
    owner_module = _read_text(
        ROUTER_ROOT / "04_PROJECT" / "FRONTEND_IMPLEMENTATION" / "150_implementation-note.md"
    )

    required_source_terms = (
        "For deterministic CI and local builds, keep test/setup files out of the "
        "production TypeScript compilation scope",
        "Repository operations recommendation: protect `main` and require both "
        "`quality` and `frontend_test_build` checks before merge.",
    )
    for term in required_source_terms:
        assert term in source_doc

    required_owner_terms = (
        "For deterministic CI and local builds, keep test/setup files out of the "
        "production TypeScript compilation scope",
        "Repository operations recommendation: protect `main` and require both "
        "`quality` and `frontend_test_build` checks before merge.",
    )
    for term in required_owner_terms:
        assert term in owner_module


def test_backend_implementation_schema_contract_wording_is_propagated() -> None:
    source_doc = _read_text(
        REPO_ROOT
        / "docs"
        / "projects"
        / "veterinary-medical-records"
        / "02-tech"
        / "backend-implementation.md"
    )
    owner_doc = _read_text(
        ROUTER_ROOT
        / "04_PROJECT"
        / "BACKEND_IMPLEMENTATION"
        / "100_structured-interpretation-schema.md"
    )

    required_phrase = "Structured Interpretation Schema visit-grouped canonical contract"
    assert required_phrase in source_doc
    assert required_phrase in owner_doc
