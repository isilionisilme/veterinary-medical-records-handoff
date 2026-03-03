from __future__ import annotations

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
ENGINEERING_PLAYBOOK = REPO_ROOT / "docs" / "shared" / "03-ops" / "engineering-playbook.md"
CODE_REVIEW_OWNER = (
    REPO_ROOT
    / "docs"
    / "agent_router"
    / "03_SHARED"
    / "ENGINEERING_PLAYBOOK"
    / "220_code-reviews.md"
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def test_identity_handoff_message_is_canonical_and_persistent() -> None:
    codex_message = (
        '"⚠️ Este paso no corresponde al agente activo. **STOP.** '
        "El siguiente paso es de **GPT-5.3-Codex**. "
        "Abre un chat nuevo en Copilot → selecciona **GPT-5.3-Codex** "
        '→ adjunta el `PLAN` activo → escribe `Continúa`."'
    )
    claude_message = (
        '"⚠️ Este paso no corresponde al agente activo. **STOP.** '
        "El siguiente paso es de **Claude Opus 4.6**. "
        "Abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** "
        '→ adjunta el `PLAN` activo → escribe `Continúa`."'
    )
    ambiguous = "selecciona el agente asignado para ese paso"
    same_chat_1 = "Vuelve a Claude (este chat)"
    same_chat_2 = "Vuelve al chat de Claude"
    no_prompt_handoff = "Vuelve al chat de **Claude Opus 4.6** y pídele que escriba el prompt"
    agents_text = _read_text(ROOT_AGENTS)
    rules_text = _read_text(EXECUTION_RULES)
    assert codex_message in agents_text
    assert claude_message in agents_text
    assert codex_message in rules_text
    assert claude_message in rules_text
    assert no_prompt_handoff in rules_text
    assert ambiguous not in agents_text
    assert ambiguous not in rules_text
    assert same_chat_1 not in rules_text
    assert same_chat_2 not in rules_text


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
    assert '"doc_glob": "docs/shared/03-ops/engineering-playbook.md"' in text
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/backend-implementation.md"'
        in text
    )
    assert '"doc_glob": "docs/projects/veterinary-medical-records/01-product/ux-design.md"' in text
    assert (
        '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/technical-design.md"' in text
    )
    assert '"doc_glob": "docs/projects/veterinary-medical-records/02-tech/adr/**/*.md"' in text
    assert '"owner_any"' in text
    assert '"docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/*.md"' in text
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
    assert '"source_doc": "docs/shared/03-ops/engineering-playbook.md"' in text
    assert (
        '"path": "docs/agent_router/04_PROJECT/PRODUCT_DESIGN/'
        '76_conceptual-model-local-schema-global-schema-and-mapping.md"' in text
    )
    assert '"required_terms"' in text


def test_code_review_guidance_terms_are_propagated() -> None:
    source_text = _read_text(ENGINEERING_PLAYBOOK)
    owner_text = _read_text(CODE_REVIEW_OWNER)
    entry_text = _read_text(CODE_REVIEW_ENTRY)

    required_terms = (
        "Pre-review checklist",
        "Severity classification criteria",
        "Database migrations and schema changes",
        "Large diff policy",
        "Pre-existing issues policy",
    )

    for term in required_terms:
        assert term in source_text
        assert term in owner_text

    assert "Pre-review gate (required before diff reading)" in entry_text
    assert "Database migrations/schema safety" in entry_text
    assert "Pre-existing issues" in entry_text


def test_preflight_levels_policy_is_documented_for_pr_flow() -> None:
    source_text = _read_text(ENGINEERING_PLAYBOOK)
    pr_router = (
        REPO_ROOT
        / "docs"
        / "agent_router"
        / "03_SHARED"
        / "ENGINEERING_PLAYBOOK"
        / "210_pull-requests.md"
    )
    pr_router_text = _read_text(pr_router)
    readme_text = _read_text(REPO_ROOT / "README.md")

    required_terms = (
        "Local preflight levels",
        "L1 — Quick",
        "L2 — Push",
        "L3 — Full",
        "before PR creation/update",
        "before merge",
        "Auto-fix policy when preflight fails",
        "Maximum automatic remediation loop: 2 attempts",
        "ForceFrontend",
        "ForceFull",
        "Before merge to `main`",
        "Relevant change",
    )

    for term in required_terms:
        assert term in source_text
        assert term in pr_router_text

    assert "test-L1.ps1" in readme_text
    assert "test-L2.ps1" in readme_text
    assert "test-L3.ps1" in readme_text
    assert "preflight-quick.ps1" in readme_text
    assert "preflight-push.ps1" in readme_text
    assert "preflight-full.ps1" in readme_text
    assert "install-pre-commit-hook.ps1" in readme_text
    assert "Maximum automatic remediation loop: 2 attempts" in pr_router_text


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
    assert "## US-08 — Edit structured data" in text
    assert "## US-09 — Capture correction signals" in text
    assert "## US-32 — Align review rendering to Global Schema template" in text
    assert "## US-39 — Align veterinarian confidence signal with mapping confidence policy" in text
    assert (
        "## US-32 — Align review rendering to Global Schema template\n\n"
        "**Status**: Implemented (2026-02-17)"
    ) in text
    assert text.count("**Status**: Implemented (2026-02-17)") >= 3


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

    assert "## US-46 — Deterministic Visit Assignment Coverage MVP (Schema)" in source_text
    assert "279b_us-46-deterministic-visit-assignment-coverage-mvp-schema.md" in entry_text
    assert "US-46 — Deterministic Visit Assignment Coverage MVP (Schema)" in release_6_text


def test_ci_does_not_ignore_markdown_only_changes() -> None:
    text = _read_text(CI_WORKFLOW)
    assert "paths-ignore" not in text
    assert "check_doc_test_sync.py" in text
    assert "check_doc_router_parity.py" in text


def test_execution_rules_exist_and_contain_core_sections() -> None:
    rules_text = _read_text(EXECUTION_RULES)
    assert "Semi-unattended execution" in rules_text
    assert "SCOPE BOUNDARY" in rules_text
    assert "Plan-edit-last" in rules_text
    assert "CI GATE" in rules_text
    assert "AUTO-CHAIN" in rules_text
    assert "Commit conventions" in rules_text
