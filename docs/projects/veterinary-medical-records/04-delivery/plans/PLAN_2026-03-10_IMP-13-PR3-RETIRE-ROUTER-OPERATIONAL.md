# Plan: IMP-13 — Remove Router And Doc Governance Infrastructure

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-13-operational-runbook-architecture.md](../Backlog/imp-13-operational-runbook-architecture.md)
**Branch:** fix/handoff-audit-parity
**PR:** See ## PR Roadmap
**User Story:** IMP-13 Fases C+D
**Prerequisite:** Router/runbook migration already landed; remaining obsolete infrastructure is safe to retire.
**Worktree:** D:/Git/veterinary-medical-records-app
**Execution Mode:** Autonomous
**Model Assignment:** GPT-5.4 (A1)

---

## Context

The repository still contained a large amount of obsolete router/doc-governance infrastructure that is not part of the veterinary product itself. During execution, the actual retirement work grew beyond the original single-PR shape: the scope now removes the full `docs/agent_router/` tree, the `backend/tests/doc_governance/` suite, dedicated governance scripts/workflows, and the local branch-name enforcement tied to that infrastructure.

The real diff is strongly deletion-heavy and mechanically cohesive, but too large to ship comfortably as one PR. The partition gate therefore triggered a mandatory split, and the user approved `Option B`.

## Objective

1. Remove obsolete router/doc-governance infrastructure from the repository.
2. Clean active instructions, CI/preflight, docs tooling, and repo references so nothing operational points at the removed infrastructure.
3. Keep historical plan docs and benchmark artifacts intact as archival records.
4. Validate the remaining backend suite stays green after the retirement.

## Scope Boundary

- **In scope:** `docs/agent_router/` removal, `backend/tests/doc_governance/` removal, governance script/workflow removal, branch-name validation removal from local preflight, active-reference cleanup, and backend validation.
- **Out of scope:** historical delivery plans, historical benchmark data (`metrics/llm_benchmarks/runs.jsonl`), and unrelated product features.

---

## PR Roadmap

Delivery split into 2 sequential PRs.
Merge strategy: Sequential.

| PR | Branch | Phases | Scope | Depends on | Status | URL |
|---|---|---|---|---|---|---|
| PR-1 | fix/handoff-audit-parity | P1 | Remove obsolete router/doc-governance assets and dedicated governance workflow/files | None | In progress | — |
| PR-2 | fix/handoff-audit-parity-cleanup | P2-P3 | Clean active tooling/instructions/preflight references and carry final validation/closeout | PR-1 | Not started | — |

Roadmap notes:
- PR-1 projected scope is very large in file count and total deleted lines, but it is predominantly mechanical deletion of obsolete infrastructure. This is the user-approved `Option B` split rationale.
- PR-2 keeps the integration cleanup reviewable in isolation: instructions, preflight/docs tooling, residual references, and validation.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent without user intervention
- 🚧 hard-gate — requires user review/decision

### Phase 0 — Plan-start preflight

- [x] P0-A 🔄 [PR-1] — Resolve execution branch and update `**Branch:**` metadata.
- [x] P0-B 🔄 [PR-1] — Resolve execution worktree and update `**Worktree:**` metadata.
- [x] P0-C 🚧 [PR-1] — Ask user to choose `Execution Mode` and update metadata.
- [x] P0-D 🚧 [PR-1] — Ask user to choose `Model Assignment` and update metadata.
- [ ] P0-E 🔄 [PR-1] — Record retrofit/plan-start snapshot commit.

### Phase 1 — Retire Obsolete Infrastructure

- [x] P1-A 🔄 [PR-1] — Delete the full `docs/agent_router/` tree.
- [x] P1-B 🔄 [PR-1] — Delete `backend/tests/doc_governance/` and dedicated governance artifacts under `scripts/docs/` and `.github/workflows/`.
- [x] P1-C 🔄 [PR-1] — Remove root-level governance artifacts no longer used (`doc_change_classification.json`, related generated outputs).

> 📌 **Commit checkpoint — PR-1 implementation scope complete.** Suggested message: `refactor(ops): remove router and doc governance infrastructure`. Run L1 before commit and L2 before push. Then wait for user.

### Phase 2 — Clean Active Tooling And References

- [ ] P2-A 🔄 [PR-2] — Update active instructions/runbooks and docs tooling to remove operational references to the removed infrastructure.
- [ ] P2-B 🔄 [PR-2] — Remove branch-name validation hooks from local preflight and CI helper docs.
- [ ] P2-C 🔄 [PR-2] — Clean residual active-code references (for example `sync_docs_to_wiki.py`, benchmark backfill helper, frontmatter exclusions, README/pytest/docs script indexes).

> 📌 **Commit checkpoint — PR-2 cleanup scope complete.** Suggested message: `fix(repo): clean tooling after router retirement`. Run L1 before commit and L2 before push. Then wait for user.

### Phase 3 — Validation And Closeout

- [ ] P3-A 🔄 [PR-2] — Verify no active repo references remain outside archival records.
- [ ] P3-B 🔄 [PR-2] — Run backend validation after the retirement work (`750 passed, 2 xfailed`, coverage above threshold).

- [ ] P3-C 🚧 [PR-2] — User reviews the restructured plan before scope-boundary commits start.

> 📌 **Commit checkpoint — Multi-PR closeout ready.** Suggested messages: PR-1 `refactor(ops): remove router and doc governance infrastructure`; PR-2 `fix(repo): clean tooling after router retirement`. Run L2 before push and L3 before PR creation/update. Then wait for user.

### Documentation task

- [ ] DOC-1 🔄 [PR-2] — `no-doc-needed` — This work removes obsolete operational infrastructure only. No user-facing documentation required.

---

## Prompt Queue

| # | Prompt | Target phase |
|---|---|---|
| 1 | Resolve remaining plan-start hard-gates and record retrofit snapshot | P0 |
| 2 | Commit PR-1 implementation slice | P1 |
| 3 | Branch-transition to PR-2 and commit cleanup slice | P2 |
| 4 | Run PR-level validation and prepare PR descriptions | P3 |

## Active Prompt

None — plan not yet started.

---

## Acceptance criteria

1. `docs/agent_router/` and `backend/tests/doc_governance/` are removed from the active product codebase.
2. Active instructions, preflight, and docs tooling no longer point to the removed infrastructure.
3. Historical plan docs and benchmark data remain unchanged as archival records.
4. Backend validation remains green after the retirement work.

## How to test

1. **Reference sweep:** search for `agent_router|doc_governance|validate-branch-name.ps1` in active code/docs → only archival records may remain.
2. **Backend validation:** run `python -m pytest backend/tests/ -x --tb=short -q` → green.
3. **Preflight before git ops:** run `scripts/ci/test-L1.ps1 -BaseRef HEAD` before commit, `scripts/ci/test-L2.ps1 -BaseRef main` before push, and `scripts/ci/test-L3.ps1 -BaseRef main` before PR creation/update.

## Risks and limitations

- The working tree already contains both PR slices together. The split must therefore be executed carefully with scoped commits/branch transitions.
- Plan-start compliance was incomplete when execution began (`Execution Mode` and `Model Assignment` unresolved). Mitigation: resolve both before any commit/push/PR operation.
