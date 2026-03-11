# Plan: Canonical Operational Execution Policy Alignment (IMP-01)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `codex/veterinary-medical-records/docs/imp-01-canonical-policy-alignment`
**PR:** [#241](https://github.com/isilionisilme/veterinary-medical-records/pull/241)
**Backlog item:** [imp-01-canonical-operational-execution-policy-alignment.md](../../Backlog/imp-01-canonical-operational-execution-policy-alignment.md)
**Prerequisite:** None
**Worktree:** `D:/Git/veterinary-medical-records`
**CI Mode:** `1) Strict step gate`
**Agents:** Planning agent (plan authoring) → Execution agent (implementation)
**Automation Mode:** `Supervisado`
**Iteration:** pending

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

Current canonical operational docs contain conflicting semantics around auto-commit conditions. Specifically:

1. **CT-\* contradiction:** `plan-execution-protocol.md` §2 and `way-of-working.md` §3 require an explicit commit-task (`CT-*`) for auto-commit in `Semiautomatico`/`Automatico` modes. But `plan-execution-protocol.md` §7 states these modes "may be executed automatically" with no CT-\* mention. Meanwhile, `plan-creation.md` §2 **explicitly forbids** `CT-*` as plan checklist items.
2. **Missing plan-start rule:** Automation mode appears in plan metadata templates but is not a mandatory plan-start choice in `plan-execution-protocol.md` §7 (only worktree + CI mode are required).
3. **Missing pre-PR rule:** Active plans reference pre-PR commit history review as a requirement, but no canonical doc defines it as a hard rule.

These inconsistencies enable ambiguous execution behavior across different agent chats.

### Canonical files in scope

| File | Key sections to modify |
|---|---|
| `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` | §2 (Atomic Iterations), §7 (Plan Governance) |
| `docs/shared/03-ops/way-of-working.md` | §3 (Commit Discipline), §5 (Pull Request Workflow) |

### Files explicitly out of scope

- `plan-creation.md` — already correct (forbids CT-\* as plan steps).
- `execution-rules.md` — compatibility stub, defers to canonical.
- `docs/agent_router/*` — auto-generated router files. Regeneration deferred to subsequent IMP.

---

## Objective

1. Remove `CT-*` / `commit-task` as an auto-commit prerequisite from all canonical docs.
2. Consolidate git behavior by automation mode: `Supervisado` = explicit confirmation; `Semiautomatico`/`Automatico` = automatic commit allowed; `push` = always manual.
3. Add mandatory automation mode selection as a plan-start choice.
4. Add explicit pre-PR commit history review hard rule.
5. Ensure the resulting policy is deterministic and self-sufficient for any implementer chat.

---

## Scope Boundary

- **In scope:** Editing canonical operational policy text in `plan-execution-protocol.md` and `way-of-working.md` only. Static content validation.
- **Out of scope:** Router regeneration, CI scripts/guards, plan migrations, backend/frontend product behavior changes.

---

## Design Decisions

### DD-1: Commit behavior tied to automation mode, not to step-level CT-\* markers

**Rationale:** `plan-creation.md` already forbids CT-\* as plan checklist items. The CT-\* language in §2 and way-of-working §3 is a legacy artifact. Automation mode selection at plan start is the correct governance mechanism — it provides deterministic, mode-based commit behavior without requiring per-step markers that are architecturally forbidden.

### DD-2: Automation mode selection as third mandatory plan-start choice

**Rationale:** Worktree and CI mode are already mandatory plan-start choices. Automation mode is equally critical for deterministic execution because it governs commit behavior throughout the plan. Making it a mandatory choice before step 1 — with `Supervisado` as default — preserves safety while eliminating ambiguity.

### DD-3: Pre-PR commit history review as a hard rule in way-of-working.md

**Rationale:** Active plans already practice this informally. Codifying it as a canonical hard rule ensures it applies universally (not just to plans) and cannot be skipped by a new chat with no prior context.

---

## Commit recommendations (inline, non-blocking)

- After P1-A + P1-B: recommend `docs(ops): remove CT-* auto-commit prerequisite from canonical policy`.
- After P1-C + P1-D: recommend `docs(ops): add automation mode selection and pre-PR review hard rules`.
- In `Supervisado`, each commit requires explicit user confirmation.
- Push remains manual in all modes.
- PR creation/update is user-triggered only and requires pre-PR commit-history review.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — user review/decision required

### Phase 1 — Remove CT-\* auto-commit prerequisite

- [x] P1-A 🔄 — **plan-execution-protocol.md §2**: Rewrite the `Atomic Iterations` paragraph to remove all CT-\* / commit-task language. Commit behavior must depend solely on automation mode: `Supervisado` = explicit confirmation required; `Semiautomatico`/`Automatico` = automatic commit permitted within active step scope. Keep push = always manual. Keep the fail-stop rule. — ✅ `9902a051f`
- [x] P1-B 🔄 — **way-of-working.md §3**: Rewrite the "Agent commit confirmation (hard rule)" bullet. Outside of an active plan in `Semiautomatico`/`Automatico` mode, agents must present staged files and proposed message and wait for confirmation. Remove all `CT-*` / `commit-task` references. — ✅ `9902a051f`

### Phase 2 — Add missing mandatory rules

- [x] P2-A 🔄 — **plan-execution-protocol.md §7**: Add "Automation Mode Selection (Mandatory Plan-Start Choice)" subsection after the existing CI Execution Mode subsection. Define the three options (`Supervisado`, `Semiautomatico`, `Automatico`), default to `Supervisado`, require explicit user selection before step 1, and require recording in plan source file. Include text-fallback instruction when no option selector is available. — ✅ `315425230`
- [x] P2-B 🔄 — **way-of-working.md §5**: Add "Pre-PR Commit History Review (Hard Rule)" subsection within Pull Request Workflow. Require review of commit history on the feature branch before opening or updating a PR. Criteria: commits coherent and scoped, messages follow conventions, no unrelated changes, history readable. If issues found, amend/reorder/squash before PR. — ✅ `315425230`
- [x] P2-C 🔄 — **plan-execution-protocol.md §7**: Add cross-reference to Pre-PR Commit History Review rule from way-of-working.md, under the PR traceability subsection or as a new "Pre-PR requirements" subsection. — ✅ `315425230`

### Phase 3 — Validation

- [x] P3-A 🔄 — **Static content check**: Grep all canonical docs (`docs/projects/*/03-ops/*.md`, `docs/shared/03-ops/*.md`) for residual `CT-*`, `commit-task` language that conditions auto-commit behavior. Any hit = failure; fix before proceeding. — ✅ `no-commit (validated; only non-governing mention remains in plan-creation.md)`
- [x] P3-B 🔄 — **Internal consistency review**: Cross-check that commit/push/PR rules are stated identically across `plan-execution-protocol.md` and `way-of-working.md`. Verify: (a) no doc says auto-commit depends on CT-\*, (b) push is manual in all modes, (c) PR creation is user-triggered only, (d) automation mode selection is a mandatory plan-start choice, (e) pre-PR commit review is a hard rule. — ✅ `58750eae0`
- [x] P3-C 🚧 — **Hard-gate**: User validates the final canonical text. Acceptance criteria from IMP-01: — ✅ `no-commit (validated in chat; L2 PASS)`
  - Canonical policy no longer requires CT-\*/commit-task for automatic commits.
  - Commit/push/PR behavior by mode is documented once and without contradictions.
  - Canonical docs include explicit Pre-PR Commit History Review hard rule.
  - Canonical docs include explicit plan-start automation mode selection rule.
  - The resulting policy is deterministic and self-sufficient.

---

## Prompt Queue

### Prompt 1 — P1-A + P1-B: Remove CT-\* auto-commit prerequisite

**Steps:** P1-A, P1-B
**Files:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`, `docs/shared/03-ops/way-of-working.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §2 "Atomic Iterations" (line ~69). The current paragraph reads:

   > Never mix scope between steps. Each step in Execution Status is an atomic unit: execute its objective and mark progress. Commit behavior is governed by automation mode: `Supervisado` requires explicit confirmation, while `Semiautomatico` and `Automatico` may auto-commit only when the active step explicitly defines an explicit commit task (`CT-*`). That explicit commit task (`CT-*`) is the only case where auto-commit without user confirmation is permitted. Push is always manual. If a step fails, report — do not continue to the next one.

   Replace with:

   > Never mix scope between steps. Each step in Execution Status is an atomic unit: execute its objective and mark progress. Commit behavior is governed by the plan's automation mode (see §7 — Automation Mode Selection): `Supervisado` requires explicit user confirmation before each commit; `Semiautomatico` and `Automatico` permit automatic commits scoped to the active step. Push is always manual. If a step fails, report — do not continue to the next one.

   Verify: the paragraph no longer contains `CT-*` or `commit-task`. The plan-mode governance hard rule below it stays unchanged.

2. Open `way-of-working.md`. Locate §3 "Commit Discipline" (line ~125). The current bullet reads:

   > **Agent commit confirmation (hard rule):** Outside of an active plan with an explicit commit-task (`CT-*`), AI agents must present the staged files and proposed commit message to the user and wait for explicit confirmation before running `git commit`. Auto-commit is only permitted when executing a pre-approved commit-task in a plan.

   Replace with:

   > **Agent commit confirmation (hard rule):** AI agents must present the staged files and proposed commit message to the user and wait for explicit confirmation before running `git commit`. Auto-commit without user confirmation is only permitted during active plan execution when the plan's automation mode is `Semiautomatico` or `Automatico` (see plan-execution-protocol.md §7).

   Verify: the bullet no longer contains `CT-*` or `commit-task`.

**Commit recommendation:** `docs(ops): remove CT-* auto-commit prerequisite from canonical policy`

---

### Prompt 2 — P2-A: Add Automation Mode Selection

**Steps:** P2-A
**Files:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §7 "Plan Governance". Find the end of the "CI Execution Mode (Mandatory Plan-Start Choice)" subsection (ends just before `---` / `## 8`).

2. Insert the following new subsection **after** CI Execution Mode and **before** the `---` separator to §8:

   ```markdown
   ### Automation Mode Selection (Mandatory Plan-Start Choice)

   Before executing the first step of a plan, the agent must ask the user to select the commit automation mode.

   **Options:**
   1. **Supervisado** — Explicit user confirmation required before each commit.
   2. **Semiautomatico** — Automatic commits permitted, scoped to the active step.
   3. **Automatico** — Automatic commits permitted across the full plan scope.

   **Mandatory behavior:**
   - Ask the user to choose one mode before step 1 starts.
   - If the interaction environment does not support option selectors, present the options as numbered text and accept the user's text reply.
   - Record the selected mode in the active plan source file (`PLAN_<date>_<slug>.md`).
   - Record format: `**Automation Mode:** <selected-mode>`
   - If the user does not choose, default to **Supervisado**.
   - The selected mode applies to the full plan unless the user explicitly changes it.
   - Mode behavior: see "Git policy by automation mode" above in this section.
   ```

3. Verify: the three mandatory plan-start choices are now Worktree, CI Mode, and Automation Mode.

---

### Prompt 3 — P2-B + P2-C: Add Pre-PR Commit History Review

**Steps:** P2-B, P2-C
**Files:** `docs/shared/03-ops/way-of-working.md`, `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `way-of-working.md`. Locate §5 "Pull Request Workflow". Find the "Pull Request Procedure" subsection (the numbered list starting with "When an AI coding assistant..."). Insert the following new subsection **before** "Pull Request Procedure":

   ```markdown
   ### Pre-PR Commit History Review (Hard Rule)

   Before opening or updating a Pull Request, the agent MUST review the commit history on the feature branch to ensure:

   - Commits are coherent and scoped to single logical changes.
   - Commit messages follow conventions (`Story <ID>: ...` or `<type>: ...`).
   - No unrelated refactors or accidental changes appear in any commit.
   - Commit history is readable and supports reasoning and review.

   If issues are found, amend, reorder, or squash commits before opening the PR.
   ```

2. Open `plan-execution-protocol.md`. Locate §7 "Plan Governance", subsection "PR traceability in plan metadata (mandatory)". Add the following paragraph immediately after that subsection:

   ```markdown
   ### Pre-PR Requirements

   Before opening or updating a PR, the pre-PR commit history review hard rule defined in [way-of-working.md §5](../../shared/03-ops/way-of-working.md#5-pull-request-workflow) must be satisfied.
   ```

3. Verify: both files reference the pre-PR review rule and the canonical definition lives in way-of-working.md.

**Commit recommendation (covers P2-A + P2-B + P2-C):** `docs(ops): add automation mode selection and pre-PR review hard rules`

---

### Prompt 4 — P3-A + P3-B: Static content check and consistency review

**Steps:** P3-A, P3-B
**Files:** All canonical ops docs (read-only validation)

**Instructions:**

1. **P3-A — Static content check.** Run:
   ```powershell
   Get-ChildItem -Recurse -Include *.md "docs/projects/veterinary-medical-records/03-ops", "docs/shared/03-ops" | Select-String -Pattern "CT-\*|commit-task" -CaseSensitive:$false
   ```
   Expected: zero matches that condition auto-commit on CT-\*. If any hit remains, fix it before proceeding.

2. **P3-B — Internal consistency review.** Open `plan-execution-protocol.md` and `way-of-working.md` side by side and verify:
   - (a) No doc says auto-commit depends on CT-\*.
   - (b) `push` is manual in all modes (both files).
   - (c) PR creation/update is user-triggered only (both files).
   - (d) Automation Mode Selection is a mandatory plan-start choice (plan-execution-protocol.md §7).
   - (e) Pre-PR Commit History Review is a hard rule (way-of-working.md §5) and cross-referenced (plan-execution-protocol.md §7).

   Report PASS/FAIL per criterion. If any FAIL, fix before proceeding.

---

### Prompt 5 — P3-C: User validation hard-gate 🚧

**Steps:** P3-C
**Files:** None (user review)

**Instructions:**

Present the user with the final state of both canonical files and the acceptance criteria checklist:

- [ ] Canonical policy no longer requires CT-\*/commit-task for automatic commits.
- [ ] Commit/push/PR behavior by mode is documented once and without contradictions.
- [ ] Canonical docs include explicit Pre-PR Commit History Review hard rule.
- [ ] Canonical docs include explicit plan-start automation mode selection rule.
- [ ] The resulting policy is deterministic and self-sufficient.

Wait for explicit user approval before marking the plan complete.

---

## Active Prompt

Pending plan approval.

---

## Acceptance Criteria

From [IMP-01 backlog item](../../Backlog/imp-01-canonical-operational-execution-policy-alignment.md):

1. Canonical policy no longer requires `CT-*`/`commit-task` for automatic commits.
2. Commit/push/PR behavior by mode is documented once and without contradictions.
3. Canonical docs include an explicit `Pre-PR Commit History Review` hard rule.
4. Canonical docs include an explicit plan-start automation mode selection rule.
5. The resulting policy is deterministic and self-sufficient for an implementer chat with no prior context.

---

## Validation Checklist

- [ ] Static content checks confirm no canonical rule states that auto-commit depends on `CT-*`.
- [ ] Static content checks confirm `push` is manual in all modes.
- [ ] Static content checks confirm PR creation/update is user-triggered only.
- [ ] Internal consistency review confirms no contradictory policy clauses remain in canonical operational docs.

---

## How to Test

1. Open `plan-execution-protocol.md` and verify §2 no longer mentions `CT-*` or `commit-task` as auto-commit prerequisites.
2. Open `way-of-working.md` §3 and verify the agent commit confirmation rule references automation mode, not `CT-*`.
3. Open `plan-execution-protocol.md` §7 and verify "Automation Mode Selection" is listed as a mandatory plan-start choice alongside Worktree and CI Mode.
4. Open `way-of-working.md` §5 and verify "Pre-PR Commit History Review" exists as a hard rule.
5. Run `grep -ri "CT-\*\|commit-task" docs/projects/*/03-ops/*.md docs/shared/03-ops/*.md` — expect zero hits conditioning auto-commit on CT-\*.
6. Read the policy end-to-end as a new agent with no prior context and verify it is unambiguous.
