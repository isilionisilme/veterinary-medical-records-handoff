<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 6. Rollback Procedure

If a completed step causes an issue not detected by tests:
1. `git revert HEAD` (reverts commit without losing history)
2. Edit Execution Status: change `[x]` back to `[ ]` for the affected step
3. Report to the planning agent for diagnosis before retrying

---

## 7. Plan Governance

### Plan Structure Rules

For plan scope principle, operational override step schema, and commit task specification rules, see [`plan-creation.md` §2 - Plan Scope Principle](plan-creation.md#2-plan-scope-principle-hard-rule).

These rules are enforced at plan creation time. The execution agent validates override step schema completeness before executing any operational step. If a required field is missing, STOP and ask the planning agent to update the plan.

### Git policy by automation mode

- `commit`:
  - `Supervisado`: requires explicit user confirmation.
  - `Semiautomatico`: may be executed automatically.
  - `Automatico`: may be executed automatically.
- `push`: always manual/user-triggered in all modes.
- Merge: always explicit user approval.

### Pull Request progress tracking (conditional)
If a PR already exists and the user requested update in this step, reflect completed-step progress in the PR body using `gh pr edit <pr_number> --body "..."`.

### PR traceability in plan metadata (mandatory)

When a PR is created for the plan branch, the execution agent MUST update the `**PR:**` field in the plan file with the actual PR link (e.g., `[#220](https://github.com/…/pull/220)`) in the same commit or the immediately following plan-update commit. A plan with a merged or open PR whose `**PR:**` field still shows the placeholder text is a compliance failure.

### Execution Worktree Selection (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must ask the user where to execute the plan.

**Mandatory behavior:**
- List **all existing worktrees** first (for example using `git worktree list`).
- Offer two choices:
  1. Use one of the listed existing worktrees.
  2. Create a new worktree (user chooses path and base branch, unless explicitly delegated).
- Do not start step 1 until the user explicitly selects one option.
- Record the selected execution worktree path in the active `PLAN_*.md`.
- All plan execution commands and file edits must stay within the selected worktree.

### CI Execution Mode (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must offer the user exactly these three options:

1. **Strict step gate** — A new step cannot start until CI for the immediately previous completed step is green.
2. **Pipeline depth-1 gate** — A new step can start while CI runs, but step N+2 cannot be started until CI for step N is green.
3. **End-of-plan gate** — CI is not checked between steps; CI is checked after all planned implementation steps are done.

**Mandatory behavior:**
- Ask the user to choose one mode before step 1 starts.
- Record the selected mode in the active `PLAN_*.md`.
- If the user does not choose, default to **Mode 2 (Pipeline depth-1 gate)**.
- The selected mode applies to the full plan unless the user explicitly changes it.
- Hard-gates (🚧), inter-agent handoffs, and merge readiness still require CI green.
- Local tests are necessary but NOT sufficient. If a required CI gate is red, the agent must diagnose, attempt focused fixes, and rerun CI (max 2 attempts) before asking the user for guidance.
- Mode 2 operational flow and edge cases are defined in **Section 8 — CI Mode 2 — Pipeline Execution (Depth-1)**.

---
