# Plan: IMP-13 PR-4 — Retire Router Operational Layer (Fases C+D)

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-13-operational-runbook-architecture.md](../Backlog/imp-13-operational-runbook-architecture.md)
**Branch:** PENDING PLAN-START RESOLUTION
**PR:** Pending (PR created on explicit user request)
**User Story:** IMP-13 Fases C+D
**Prerequisite:** PR-3 (Migrate Router Rules to Runbooks) merged to `main`; all runbooks self-contained; user has validated the new operational layer works in real usage.
**Worktree:** PENDING PLAN-START RESOLUTION
**Execution Mode:** PENDING USER SELECTION
**Model Assignment:** PENDING USER SELECTION

---

## Context

PR-1 created the new operational layer. PR-2 activated it by rewiring AGENTS.md. The old router operational directories still exist but are no longer the primary routing path. This plan removes them, updates CI scripts and MANIFEST.yaml to reflect the new structure, relocates utility files, and performs final validation.

## Objective

1. Delete router operational directories that are now replaced by `.prompt.md` files.
2. Update CI scripts, `00_AUTHORITY.md`, and `MANIFEST.yaml` to remove references to deleted paths.
3. Relocate `router_parity_map.json` and `test_impact_map.json` to `scripts/docs/`.
4. Create `.github/copilot-instructions.md` with minimal global rules.
5. Full L3 validation.

## Scope Boundary

- **In scope:** Router operational directory deletion, `00_AUTHORITY.md` update, CI script updates, MANIFEST.yaml update, map JSON relocation, `copilot-instructions.md` creation, L3 validation.
- **Out of scope:** `.prompt.md`/`.instructions.md` changes (done in PR-1), AGENTS.md rewiring (done in PR-2), reference router modules (CODING_STANDARDS, UX_GUIDELINES, BRAND_GUIDELINES, DOCUMENTATION_GUIDELINES, 02_PRODUCT, 04_PROJECT, extraction, extraction-tracking).

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent without user intervention
- 🚧 hard-gate — requires user review/decision

### Phase 0 — Plan-start preflight

- [ ] P0-A 🔄 — Resolve execution branch and update `**Branch:**` metadata.
- [ ] P0-B 🔄 — Resolve execution worktree and update `**Worktree:**` metadata.
- [ ] P0-C 🚧 — Ask user to choose `Execution Mode` and update metadata.
- [ ] P0-D 🚧 — Ask user to choose `Model Assignment` and update metadata.
- [ ] P0-E 🔄 — Record plan-start snapshot commit.

### Phase 1 — Retire operational directories

- [ ] P1-A 🔄 — Delete router operational directories: `01_WORKFLOW/START_WORK`, `01_WORKFLOW/PULL_REQUESTS`, `01_WORKFLOW/CODE_REVIEW`, `01_WORKFLOW/TESTING`, `01_WORKFLOW/BRANCHING`, `03_SHARED/EXECUTION_PROTOCOL`, `03_SHARED/WAY_OF_WORKING`.
- [ ] P1-B 🔄 — Update `docs/agent_router/00_AUTHORITY.md`: remove intent entries for deleted operational modules, keep reference entries.
- [ ] P1-C 🔄 — Update `docs/agent_router/MANIFEST.yaml`: remove entries for deleted operational modules.
- [ ] P1-D 🔄 — Run `python scripts/docs/generate-router-files.py` and confirm no drift.

> 📌 **Commit checkpoint — P1 complete.** Suggested message: `refactor(ops): retire router operational directories (IMP-13)`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 2 — Update CI scripts

- [ ] P2-A 🔄 — Update `scripts/docs/check_router_directionality.py`: remove/adjust references to deleted paths.
- [ ] P2-B 🔄 — Update `scripts/docs/check_doc_router_parity.py`: update if DOC_UPDATES path changes.
- [ ] P2-C 🔄 — Update `metrics/llm_benchmarks/scripts/backfill_daily.py`: update router path references.
- [ ] P2-D 🔄 — Run L2 validation. Fix any failures.

> 📌 **Commit checkpoint — P2 complete.** Suggested message: `fix(ci): update CI scripts for post-retirement router structure`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 3 — Cleanup

- [ ] P3-A 🔄 — Relocate `router_parity_map.json` and `test_impact_map.json` from `docs/agent_router/01_WORKFLOW/DOC_UPDATES/` to `scripts/docs/`. Update all references.
- [ ] P3-B 🔄 — Create `.github/copilot-instructions.md` with minimal global rules subset (branch naming, no commits to main).

> 📌 **Commit checkpoint — P3 complete.** Suggested message: `refactor(ops): relocate map JSONs and add copilot-instructions.md`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 4 — Final validation

- [ ] P4-A 🔄 — Run full L3 validation. Confirm all tests pass and router generation has no drift.
- [ ] P4-B 🚧 — Hard-gate: user reviews final state before plan closeout.

> 📌 **Commit checkpoint — PR-3 complete (Fases C+D).** Suggested message: `refactor(ops): complete Fases C+D — retire router operational layer (IMP-13)`. Run L3 tests; if red, fix and re-run until green. Then wait for user.

### Documentation task

- [ ] DOC-1 🔄 — `no-doc-needed` — This plan removes obsolete operational infrastructure. No user-facing documentation required.

---

## Prompt Queue

| # | Prompt | Target phase |
|---|---|---|
| 1 | Execute Phase 0 plan-start preflight | P0 |
| 2 | Retire operational directories and update MANIFEST | P1 |
| 3 | Update CI scripts | P2 |
| 4 | Cleanup: relocate maps, create copilot-instructions | P3 |
| 5 | Final L3 validation | P4 |

## Active Prompt

None — plan not yet started.

---

## Acceptance criteria

1. Router operational directories (`01_WORKFLOW/START_WORK`, `EXECUTION_PROTOCOL`, etc.) are deleted.
2. `00_AUTHORITY.md` and `MANIFEST.yaml` reflect the reduced router structure.
3. CI scripts pass without referencing deleted paths.
4. `router_parity_map.json` and `test_impact_map.json` relocated to `scripts/docs/`.
5. `.github/copilot-instructions.md` exists with minimal global rules.
6. Router generation (`generate-router-files.py --check`) passes with no drift.
7. Full L3 test suite passes.

## How to test

1. **Router integrity:** Run `python scripts/docs/generate-router-files.py --check` → no drift.
2. **CI scripts:** Run each CI script individually → no errors from missing paths.
3. **L3 green:** Run `scripts/ci/test-L3.ps1` → all tests pass.
4. **No stale references:** `grep -r "01_WORKFLOW/START_WORK\|EXECUTION_PROTOCOL\|WAY_OF_WORKING" --include="*.py" --include="*.md"` → no hits outside of canonical docs and changelogs.

## Risks and limitations

- CI scripts may break when router directories are removed. Mitigation: P2 updates scripts; L2 gate validates before proceeding.
- `generate-router-files.py` may produce unexpected output after deletions. Mitigation: P1-D runs generation immediately after deletions to catch issues early.
