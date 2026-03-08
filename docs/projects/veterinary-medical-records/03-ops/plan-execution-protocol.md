# Plan Execution Protocol

> Canonical source of truth for plan execution behavior.
> Router files under `docs/agent_router/` are derived from this file.

---

## Purpose

Define a deterministic execution protocol so plans, git operations, and hard-gates stay synchronized.

---

## 1. Semi-Unattended Execution (Default Mode)

Default behavior is semi-unattended execution controlled by plan steps and hard-gates.

### Mandatory Plan-Start Choices (before Step 1)

Before executing the first step of any plan, collect and record in plan metadata:

1. Execution worktree.
2. CI mode.
3. Automation mode:
   - `Supervisado`: commit manual, push manual, pause at hard-gates.
   - `Semiautomatico`: commit automatic allowed, push manual, pause at hard-gates.
   - `Automatico`: commit automatic allowed, push manual, pause at hard-gates (including final pre-PR gate).

If UI supports option selectors, use selector UI. If not, use textual fallback.

---

## 2. Atomic Iterations

Never mix scope between plan steps.

- Execute one step objective at a time.
- A step is complete only when it is marked `[x]` in `Execution Status`.
- Operational actions are protocol behavior; they are not plan steps.

---

## 3. Extended Execution State

| State | Syntax |
|---|---|
| Pending | `- [ ] F?-? ...` |
| In progress | `- [ ] F?-? ... ⏳ IN PROGRESS (<agent>, <date>)` |
| Blocked | `- [ ] F?-? ... 🚫 BLOCKED (<reason>)` |
| Step locked | `- [ ] F?-? ... 🔒 STEP LOCKED (...)` |
| Completed | `- [x] F?-? ...` |

Rules:
1. Only `[ ]` and `[x]` checkboxes are valid.
2. Mark `⏳ IN PROGRESS` before execution.
3. Remove runtime labels when closing the step as `[x]`.
4. At most one `⏳ IN PROGRESS` or `🔒 STEP LOCKED` step at a time.
5. Do not start a new step while a `🔒 STEP LOCKED` exists.

---

## 4. Step Eligibility Rule (Hard Rule)

On continuation intent:
1. Read `Execution Status`.
2. Pick first pending `[ ]` step (including labeled in-progress/blocked lines).
3. If next step belongs to another agent role, stop and hand off.
4. Apply decision table from §10.

---

## 5. Continuation-Intent-Only Rule

If continuation intent includes extra scope requests:
1. Pause execution.
2. Ask user to choose: continue plan as-is or update plan scope first.
3. Resume only after explicit choice.

---

## 6. Rollback Procedure

If a completed step introduces regressions:
1. Revert/fix code safely.
2. Return affected plan step from `[x]` to `[ ]`.
3. Report blocker and recovery path.

---

## 7. Plan Governance

### Scope and structure

- `PLAN_*.md` must not include operational tasks (`commit-task`, `create-pr`, `merge-pr`, `CT-*` checkboxes).
- Commit guidance is inline recommendation under implementation steps (when/scope/message/validation).
- Every active plan must include a documentation-wiki step that closes either:
  - with delivered docs, or
  - with `no-doc-needed` rationale.

### Git policy by automation mode

- `commit`:
  - `Supervisado`: requires explicit user confirmation.
  - `Semiautomatico`: may be executed automatically.
  - `Automatico`: may be executed automatically.
- `push`: always manual/user-triggered in all modes.
- Merge: always explicit user approval.

### PR policy

- PR is required before merge.
- PR creation/update is user-triggered only.
- Agent never auto-creates PR unless user explicitly requests it in that moment.

### Pre-PR Commit History Review (Hard Rule)

Before recommending PR creation/update:
1. Review actual branch history.
2. Ensure commit grouping tells a coherent technical narrative.
3. Reorder/squash/split only with explicit user confirmation.
4. If history quality is poor, stop and propose cleanup first.

---

## 8. Step Completion Integrity (Hard Rules)

1. A step counts as completed only when marked `[x]` (no runtime labels).
2. Required evidence must exist before closure when the plan/protocol asks for it.
3. If evidence is missing, keep step pending/blocked and do not proceed.
4. Chat todo projection must remain synchronized with plan checkboxes.

---

## 9. Format-Before-Commit (Mandatory)

Before every commit:
1. Run formatter/lint/preflight for changed scope (L1 minimum).
2. Fix blocking issues.
3. Commit only after checks pass or user explicitly approves an allowed exception.

Local minimum gates:
- Before commit: `scripts/ci/test-L1.ps1 -BaseRef HEAD`
- Before push: `scripts/ci/test-L2.ps1 -BaseRef main`
- Before PR create/update: `scripts/ci/test-L3.ps1 -BaseRef main`

---

## 10. Next-Step Message (Mandatory)

After each step, state next action using:

| Prompt exists? | Hard-gate? | Action |
|---|---|---|
| YES | NO | Auto-chain next step |
| YES | YES | Stop for user decision |
| NO | NO | Stop and request planning prompt |
| NO | YES | Stop for user decision |

---

## 11. Prompt Strategy

Resolution order: Prompt Queue -> Active Prompt -> stop and request planning update.

After executing a step, clear or refresh `Active Prompt` according to plan state.

---

## 12. Hard-Gates: Structured Decision Protocol

For hard-gate steps:
1. Present numbered options with impact/effort.
2. User responds with option numbers/all/none.
3. Record decision in plan before continuing.

---

## 13. SCOPE BOUNDARY Procedure

Activation: any commit/push request during active plan execution.

Steps:
1. Verify branch matches plan metadata.
2. Validate preflight level.
3. Commit according to current automation mode policy.
4. Keep plan and execution status synchronized (mark `[x]` only after closure criteria).
5. Push only on explicit user request.
6. If user requested PR action, run PR workflow after pre-PR history review.
7. Apply §10 decision table (chain or stop).

---

## 14. Iteration Lifecycle Protocol

```
Branch creation -> Plan steps -> Pre-PR history review -> PR (user-triggered) -> User merge approval -> Close-out
```

Rules:
1. Create/switch to plan branch before first step.
2. Execute steps until all `[x]` and validations pass.
3. Perform mandatory pre-PR history review.
4. Create/update PR only when requested by user.
5. Merge only with explicit user approval.
6. Close-out includes moving plan to `completed/` and final plan documentation commit.

---

## 15. Plan Todo Projection (Chat) (Hard Rule)

During execution:
1. Project pending plan steps as chat todos.
2. Keep exactly one todo `in_progress`.
3. Mark todo completed only when corresponding step is `[x]`.
4. If divergence is detected, reconcile from plan file immediately.

---

## 16. Token-Efficiency Policy

Use:
1. `iterative-retrieval` before each step.
2. `strategic-compact` at step close.
3. Minimal necessary context loading.

---

## 17. Commit Conventions

Use:
`<type>(plan-<id>): <short description>`

Examples:
- `feat(plan-p1): owner_address extraction hardening`
- `test(plan-p3): benchmark and regression evidence`
- `docs(plan-d6): wiki documentation update`

---

## 18. How to Add a New User Story

When adding a user story, update `IMPLEMENTATION_PLAN.md`:
1. Story order under release section.
2. Full story detail block with acceptance criteria and dependencies.
