# Plan: IMP-13 PR-2 — Activate Runbook Routing (Fase B)

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-13-operational-runbook-architecture.md](../Backlog/imp-13-operational-runbook-architecture.md)
**Branch:** `refactor/imp-13-activate-runbook-routing`
**PR:** Pending (PR created on explicit user request)
**User Story:** IMP-13 Fase B
**Prerequisite:** PR-1 (Fase A) merged to `main`; `.prompt.md`, `.instructions.md`, and `plan-start-check.py` already exist and are validated.
**Worktree:** `d:\Git\worktrees\cuarto`
**Execution Mode:** Autonomous
**Model Assignment:** `Uniform` (GPT-5.4)

---

## Context

PR-1 created the new operational layer (`.prompt.md` runbooks, `.instructions.md` context files, `plan-start-check.py`) alongside the existing router. This plan rewires `AGENTS.md` to use the new operational layer as the primary path, replacing the multi-level router chain for operational processes. The old router directories remain intact as fallback until PR-3 retires them.

## Objective

Rewire `AGENTS.md` to route operational intents through `.prompt.md` runbooks instead of the agent router operational layer. Update contract tests to validate the new structure.

## Scope Boundary

- **In scope:** AGENTS.md rewrite, contract test updates, possible `00_AUTHORITY.md` touch.
- **Out of scope:** Creation of new `.prompt.md`/`.instructions.md` files (done in PR-1), router directory deletions (PR-3), CI script changes (PR-3).

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent without user intervention
- 🚧 hard-gate — requires user review/decision

### Phase 0 — Plan-start preflight

- [x] P0-A 🔄 — Resolve execution branch and update `**Branch:**` metadata. — ✅ `pending-snapshot`
- [x] P0-B 🔄 — Resolve execution worktree and update `**Worktree:**` metadata. — ✅ `pending-snapshot`
- [x] P0-C 🚧 — Ask user to choose `Execution Mode` and update metadata. — ✅ `pending-snapshot`
- [x] P0-D 🚧 — Ask user to choose `Model Assignment` and update metadata. — ✅ `pending-snapshot`
- [x] P0-E 🔄 — Record plan-start snapshot commit. — ✅ `d662fa94`

### Phase 1 — Rewire AGENTS.md

- [x] P1-A 🔄 — Rewrite `AGENTS.md` (~20–30 lines): global rules (no commits to main, branch naming), intent → `.prompt.md` mapping table, reference pointers to remaining router modules, plan enforcement script instruction. — ✅ `bde5ee7d`
- [x] P1-B 🔄 — Update `docs/agent_router/00_AUTHORITY.md` if needed: add note that operational intents are now handled by `.prompt.md` files. — ✅ `no-commit (AGENTS.md now owns operational routing; 00_AUTHORITY.md remains fallback/reference-only)`

> 📌 **Commit checkpoint — P1 complete.** Suggested message: `refactor(ops): rewire AGENTS.md to operational runbooks (IMP-13)`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 2 — Update contract tests

- [x] P2-A 🔄 — Update `backend/tests/unit/test_doc_router_contract.py` to validate the new AGENTS.md structure (`.prompt.md` references, reduced line count) instead of old routing chain expectations. — ✅ `pending-checkpoint`
- [x] P2-B 🔄 — Run full test suite. Fix any failures. — ✅ `pending-checkpoint`

> 📌 **Commit checkpoint — P2 complete.** Suggested message: `test(ops): update contract tests for runbook-based AGENTS.md`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 3 — User validation

- [ ] P3-A 🚧 — Hard-gate: user validates that the new AGENTS.md works in real usage (cold chat test) before proceeding to router retirement in PR-3.

> 📌 **Commit checkpoint — PR-2 complete (Fase B).** Suggested message: `refactor(ops): complete Fase B — activate runbook routing (IMP-13)`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Documentation task

- [x] DOC-1 🔄 — `no-doc-needed` — AGENTS.md itself serves as the operational routing documentation. — ✅ `no-commit (AGENTS.md is the delivered operational doc)`

---

## Prompt Queue

| # | Prompt | Target phase |
|---|---|---|
| 1 | Execute Phase 0 plan-start preflight | P0 |
| 2 | Rewrite AGENTS.md and update authority | P1 |
| 3 | Update contract tests | P2 |
| 4 | User validation gate | P3 |

## Active Prompt

Prompt 4 — User validation gate (P3).

---

## Acceptance criteria

1. `AGENTS.md` is under 30 lines and routes operational intents to `.prompt.md` files.
2. `AGENTS.md` includes pointer to remaining router reference modules.
3. `AGENTS.md` includes instruction to run `scripts/dev/plan-start-check.py` before any plan step.
4. Contract tests validate the new AGENTS.md structure.
5. All tests pass (L2 green).

## How to test

1. **AGENTS.md routing:** Start a cold chat and say "create a plan" → verify the agent loads `plan-create.prompt.md` instead of navigating the router.
2. **Cold chat plan-start:** Start a cold chat and say "continue the plan" → verify the agent runs `plan-start-check.py` and follows `plan-start.prompt.md`.
3. **L2 green:** Run `scripts/ci/test-L2.ps1 -BaseRef main` → all tests pass.
