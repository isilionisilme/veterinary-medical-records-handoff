# Plan: IMP-13 PR-3 — Migrate Router Rules to Runbooks

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-13-operational-runbook-architecture.md](../Backlog/imp-13-operational-runbook-architecture.md)
**Branch:** PENDING PLAN-START RESOLUTION
**PR:** Pending (PR created on explicit user request)
**User Story:** IMP-13
**Prerequisite:** PR-2 (Fase B) merged to `main`; AGENTS.md rewired to `.prompt.md` routing.
**Worktree:** PENDING PLAN-START RESOLUTION
**Execution Mode:** PENDING USER SELECTION
**Model Assignment:** PENDING USER SELECTION

---

## Context

PR-1 created the runbook layer (6 `.prompt.md`, 2 `.instructions.md`, `plan-start-check.py`). PR-2 activated it by rewiring AGENTS.md to route intents to runbooks. However, the runbooks are currently 8–10 line stubs. The full operational rules (1000+ lines across 40+ router modules) still live in `docs/agent_router/`. This creates a split-brain problem: AGENTS.md routes to runbooks, but agents that need the actual rules must still navigate the router. Evidence from real usage confirms agents skip rules, ask wrong questions, and produce incomplete plans because the runbooks lack sufficient detail.

## Objective

1. Make each existing runbook self-contained by embedding the full operational rules from its corresponding router module(s).
2. Create new runbooks for 3 procedures that currently have no runbook: start-work, doc-updates, pr-workflow.
3. Update AGENTS.md routing table to include the new runbooks.
4. Validate that all intents route correctly to self-contained runbooks.

## Scope Boundary

- **In scope:** All `.prompt.md` files (6 existing + 3 new), AGENTS.md routing table update.
- **Out of scope:** Router module deletion (PR-4), CI script changes, reference modules (CODING_STANDARDS, DOCUMENTATION_GUIDELINES, BRAND_GUIDELINES, UX_GUIDELINES, 02_PRODUCT, 04_PROJECT, extraction), contract test changes beyond routing table adjustments.

---

## PR Partition Gate

- **Estimated change size:** ~10 files, ~1500 net lines added (all Markdown/prompt files).
- **PR classification:** Docs-only — no code size limit applies.
- **Semantic risk:** Low — adding content to runbooks without removing from router or changing routing behavior.
- **Review load:** >800 lines, informational note only (docs-only exemption).
- **Decision:** Single PR. Runbook enrichment is one coherent semantic axis.
- **Split trigger:** If any runbook exceeds 150 lines or total diff exceeds 3000 lines, open user decision gate.

---

## Source Mapping

Each runbook draws from specific router modules. This table is the authoritative mapping for execution.

### Existing runbooks — enrichment sources

| Runbook | Router source(s) | Key rules to embed |
|---|---|---|
| `plan-create.prompt.md` | `EXECUTION_PROTOCOL/10_purpose.md`, `PULL_REQUESTS/00_entry.md`, `START_WORK/00_entry.md`, `BRANCHING/00_entry.md` | Agent taxonomy (Planning/Execution per step), PR partition gate procedure, branch-first requirement, branch naming convention, PR Roadmap format for multi-PR plans |
| `plan-start.prompt.md` | `EXECUTION_PROTOCOL/20_execution-mode.md`, `EXECUTION_PROTOCOL/30_iterations-state.md` | Full Execution Mode definitions (Supervised/Semi-supervised/Autonomous) with test gates per mode, Model Assignment options (Default/Uniform/Custom), single-chat execution rule |
| `plan-resume.prompt.md` | `EXECUTION_PROTOCOL/40_step-eligibility.md`, `EXECUTION_PROTOCOL/60_step-completion.md`, `EXECUTION_PROTOCOL/80_next-step-prompt.md`, `EXECUTION_PROTOCOL/110_conventions.md` | Step eligibility rule, continuation-intent-only rule, task chaining policy (blocking vs non-blocking), evidence block format, next-step decision table (§10), prompt resolution priority, token-efficiency policy |
| `plan-closeout.prompt.md` | `EXECUTION_PROTOCOL/100_iteration-lifecycle.md`, `PULL_REQUESTS/00_entry.md` | Iteration lifecycle closeout, post-merge cleanup (stash check, branch deletion), backlog artifact archival |
| `code-review.prompt.md` | `CODE_REVIEW/00_entry.md` | Pre-review CI prerequisite, depth selection (Light/Standard/Deep/Deep-critical), deep review lens procedure, 7 focus areas with details, severity classification criteria, mandatory output template, publication as PR comment, follow-up verification, pre-existing issues policy, large diff policy, entrypoint-size warning |
| `scope-boundary.prompt.md` | `EXECUTION_PROTOCOL/70_format-preflight.md`, `EXECUTION_PROTOCOL/90_hard-gates-scope.md`, `TESTING/10_how_to_run.md` | Format-before-commit (prettier + ruff commands), L1/L2/L3 preflight integration table, preflight auto-fix policy (max 2 attempts), two-commit strategy details, hard-gate structured decision protocol |

### New runbooks — source modules

| Runbook | Router source(s) | Key rules to embed |
|---|---|---|
| `start-work.prompt.md` | `START_WORK/00_entry.md`, `BRANCHING/00_entry.md` | Branch-first procedure (5 steps), category mapping table, slug rules, clean-tree verification |
| `doc-updates.prompt.md` | `DOC_UPDATES/00_entry.md`, `DOC_UPDATES/20_normalize_rules.md`, `DOC_UPDATES/30_checklist.md`, `DOC_UPDATES/10_reference_first.md` | Three trigger scenarios, file discovery + diff inspection, R/C/N classification, normalization pass, test_impact_map enforcement, router_parity_map enforcement, verification checklist, mandatory output table, propagation gaps |
| `pr-workflow.prompt.md` | `PULL_REQUESTS/00_entry.md` | PR classification table, title conventions, body format (heredoc, body-file), commit history review, pre-PR preflight with partition gate, pre-merge review check, UX/Brand compliance section, post-merge cleanup |

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent without user intervention
- 🚧 hard-gate — requires user review/decision

### Phase 0 — Plan-start preflight (mandatory)

- [ ] P0-A 🔄 — Resolve execution branch and update `**Branch:**` metadata.
- [ ] P0-B 🔄 — Resolve execution worktree and update `**Worktree:**` metadata.
- [ ] P0-C 🚧 — Ask user to choose `Execution Mode` and update metadata.
- [ ] P0-D 🚧 — Ask user to choose `Model Assignment` and update metadata.
- [ ] P0-E 🔄 — Record plan-start snapshot commit.

### Phase 1 — Enrich existing runbooks

- [ ] P1-A 🔄 — Enrich `plan-create.prompt.md` with agent taxonomy, branch-first, naming, partition gate, PR Roadmap format.
- [ ] P1-B 🔄 — Enrich `plan-start.prompt.md` with full Execution Mode definitions, Model Assignment options, single-chat rule.
- [ ] P1-C 🔄 — Enrich `plan-resume.prompt.md` with step eligibility, task chaining, evidence block, next-step table, token-efficiency.
- [ ] P1-D 🔄 — Enrich `plan-closeout.prompt.md` with iteration lifecycle, post-merge cleanup, artifact archival.
- [ ] P1-E 🔄 — Enrich `code-review.prompt.md` with full depth selection, lens procedure, 7 focus areas, severity rules, template, publication, follow-up.
- [ ] P1-F 🔄 — Enrich `scope-boundary.prompt.md` with format-before-commit, L1/L2/L3 table, auto-fix policy, hard-gate protocol.

> 📌 **Commit checkpoint — P1 complete.** Suggested message: `docs(ops): enrich existing runbooks with router operational rules (IMP-13)`. Run L1; if red, fix and re-run. Then wait for user.

### Phase 2 — Create new runbooks

- [ ] P2-A 🔄 — Create `start-work.prompt.md` with branch-first procedure, naming, category mapping.
- [ ] P2-B 🔄 — Create `doc-updates.prompt.md` with full DOC_UPDATES procedure, normalization, enforcement maps, output format.
- [ ] P2-C 🔄 — Create `pr-workflow.prompt.md` with PR lifecycle: classification, title, body, commit review, partition gate, post-merge cleanup.

> 📌 **Commit checkpoint — P2 complete.** Suggested message: `docs(ops): create start-work, doc-updates, and pr-workflow runbooks (IMP-13)`. Run L1; if red, fix and re-run. Then wait for user.

### Phase 3 — Update AGENTS.md routing and validate

- [ ] P3-A 🔄 — Update AGENTS.md routing table to add entries for `start-work`, `doc-updates`, `pr-workflow`.
- [ ] P3-B 🔄 — Run L2 validation (`scripts/ci/test-L2.ps1 -BaseRef main`). Fix any contract test failures.

> 📌 **Commit checkpoint — P3 complete.** Suggested message: `refactor(ops): update AGENTS.md routing for new runbooks (IMP-13)`. Run L2; if red, fix and re-run. Then wait for user.

### Phase 4 — User validation

- [ ] P4-A 🚧 — Hard-gate: user validates runbooks in cold-chat tests:
  1. "Create a plan" → loads `plan-create.prompt.md` with full rules.
  2. "Continue the plan" → runs `plan-start-check.py`, loads `plan-start.prompt.md` with full rules.
  3. "Start work on X" → loads `start-work.prompt.md`.
  4. "I updated docs" → loads `doc-updates.prompt.md`.
  5. "Create a PR" → loads `pr-workflow.prompt.md`.

### Documentation task

- [ ] DOC-1 🔄 — `no-doc-needed` — The runbooks ARE the delivered documentation. No separate docs required.

---

## Prompt Queue

| # | Prompt | Target phase |
|---|---|---|
| 1 | Prompt 1 — Plan-start preflight | P0 |
| 2 | Prompt 2 — Enrich existing runbooks | P1 |
| 3 | Prompt 3 — Create new runbooks | P2 |
| 4 | Prompt 4 — Update routing and validate | P3 |
| 5 | Prompt 5 — User validation gate | P4 |

## Active Prompt

None — plan not yet started.

---

## Prompts

### Prompt 1 — Plan-start preflight

Execute standard Phase 0:
1. Resolve Branch from active execution branch.
2. Resolve Worktree from active VS Code workspace.
3. Present Execution Mode options with full definitions. Wait for selection.
4. Present Model Assignment options. Wait for selection.
5. Record all values. Run L1. Commit snapshot.

### Prompt 2 — Enrich existing runbooks

For each of the 6 existing `.prompt.md` files, read the corresponding router source module(s) from the Source Mapping table, then rewrite the runbook to be self-contained:

**Enrichment rules:**
- Preserve the existing numbered-checklist structure.
- Embed the operational rules inline — do NOT use "see module X" references.
- Keep each runbook under 120 lines. Compress verbose prose into actionable rules.
- Preserve exact phrasing for contract-tested phrases (verify against `test_doc_router_contract.py`, `test_doc_updates_contract.py`, `test_doc_updates_e2e_contract.py`).
- Include decision tables, severity classifications, and format templates verbatim where they are normative.

**Per-runbook checklist (execute for each):**
1. Read the router source module(s).
2. Read the current `.prompt.md`.
3. Identify rules present in router but missing from runbook.
4. Rewrite runbook with embedded rules.
5. Verify no contract-tested phrase was lost.

Commit all 6 enriched runbooks together.

### Prompt 3 — Create new runbooks

Create 3 new `.prompt.md` files following the same format as enriched runbooks:

**`start-work.prompt.md`:**
- Source: `START_WORK/00_entry.md` + `BRANCHING/00_entry.md`
- Must include: clean-tree check, base branch update, branch creation with naming, category mapping table, slug rules.

**`doc-updates.prompt.md`:**
- Source: `DOC_UPDATES/00_entry.md` + `20_normalize_rules.md` + `30_checklist.md` + `10_reference_first.md`
- Must include: 3 trigger scenarios, file discovery (3 evidence sources), R/C/N classification, normalization pass, test_impact_map enforcement, router_parity_map enforcement, verification checklist, mandatory output table format, propagation gaps format, anti-loop rule.

**`pr-workflow.prompt.md`:**
- Source: `PULL_REQUESTS/00_entry.md`
- Must include: PR classification table, title conventions, body format (recommended body-file), commit history review, partition gate, pre-merge review check, UX/Brand compliance section, post-merge cleanup (5 steps).

Commit all 3 new runbooks together.

### Prompt 4 — Update routing and validate

1. Read current AGENTS.md.
2. Add routing entries for `start-work.prompt.md`, `doc-updates.prompt.md`, `pr-workflow.prompt.md`.
3. Verify all 9 runbooks are reachable from AGENTS.md routing table.
4. Run L2 (`scripts/ci/test-L2.ps1 -BaseRef main`).
5. Fix any contract test failures (adjust tests if routing table changed, but do NOT weaken behavioral assertions).
6. Commit.

### Prompt 5 — User validation gate (P4)

Present user with 5 cold-chat test instructions (see P4-A). Wait for results. If all pass, mark plan complete.

---

## Acceptance criteria

1. All 6 existing runbooks are self-contained — no "see module X" operational references needed.
2. 3 new runbooks exist: `start-work.prompt.md`, `doc-updates.prompt.md`, `pr-workflow.prompt.md`.
3. AGENTS.md routes to all 9 runbooks.
4. L2 test suite passes.
5. Cold-chat validation confirms agents follow full rules (not stubs) when loading runbooks.

## How to test

1. **Runbook completeness:** For each runbook, verify it contains the key rules from its router source (per Source Mapping table).
2. **Contract integrity:** `pytest backend/tests/unit/test_doc_router_contract.py backend/tests/unit/test_doc_updates_contract.py backend/tests/unit/test_doc_updates_e2e_contract.py` — all pass.
3. **Routing coverage:** Grep AGENTS.md for all 9 `.prompt.md` filenames — all present.
4. **L2 green:** `scripts/ci/test-L2.ps1 -BaseRef main` — passes.
5. **Cold-chat:** 5 intent tests (P4-A) — each loads the correct self-contained runbook.

## Risks and limitations

- Runbooks may exceed target length when embedding full rules. Mitigation: compress verbose prose, use tables, target 120 lines max per runbook.
- Contract tests may assert phrases that move from router to runbooks. Mitigation: verify contract-tested phrases before and after migration; adjust test expectations only for legitimate path changes.
- Router modules remain after this PR (deleted in PR-4). During this interim, rules exist in two places. Mitigation: this is intentional — additive-only change makes rollback safe.
