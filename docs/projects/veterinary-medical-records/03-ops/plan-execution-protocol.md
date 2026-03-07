# Plan Execution Protocol

> **Canonical source of truth.**
> This document is the single authoritative reference for how AI agents execute plan steps in this project.
>
> **Governance:**
> - This file is a canonical document maintained by humans.
> - Router files under `docs/agent_router/` are derived outputs generated from this canonical source.
> - Flow is **canonical → router only**. Router files MUST NOT be edited directly.
> - Any direct edit to a router file may be overwritten during the next regeneration cycle.

---

## Purpose

This protocol governs how AI agents execute plan steps in a structured, auditable, and semi-unattended manner. It defines execution rules, completion integrity, CI verification, handoff conventions, and the full iteration lifecycle.

### Role taxonomy (availability-safe)

- **Planning agent**: owns plan authoring/updates, hard-gate decisions, and prompt preparation.
- **Execution agent**: owns implementation steps from pre-written prompts.

All routing and handoff rules in this document MUST use role labels (not model or vendor names).

AI assistants must stop and report the blocker when a protocol step cannot be completed as defined.

---

## File Structure

```
docs/projects/veterinary-medical-records/04-delivery/plans/
├── plan-execution-protocol.md      ← YOU ARE HERE
├── IMPLEMENTATION_HISTORY.md       ← Timeline of all iterations
├── PLAN_<date>_<slug>.md           ← Active iteration plans
├── completed/                      ← Finished iterations
│   └── COMPLETED_<date>_<slug>.md
```

**Active plan file:** The agent attaches the relevant `PLAN_*.md` file when executing a continuation-intent request (for example: "continue", "go", "let's go", "proceed", "resume").
Each plan file contains: Execution Status (checkboxes), Prompt Queue, Active Prompt, and iteration-specific context.

---

## 1. Semi-Unattended Execution (Default Mode)

The default execution mode is **semi-unattended**. After completing the current task according to the active mode and closure rules, the agent applies the **decision table in §10** to determine whether to chain or stop.

### Single-Chat Execution Rule (Hard Rule)

Keep execution in the current chat by default.

The agent may recommend switching chat only when:
1. expected token-efficiency benefit is significant, or
2. a hard capability blocker requires another agent/model.

In both cases, the agent MUST explain the reason briefly and wait for explicit user decision.

**Safety limit:** if the agent detects context exhaustion (truncated responses, state loss), it must stop at the current step, complete it cleanly (full SCOPE BOUNDARY) and generate the handoff.

---

## 2. Atomic Iterations

Never mix scope between steps. Each step in Execution Status is an atomic unit: execute its objective and mark progress. Commits/pushes are executed only when the active step is an explicit commit task (`CT-*`) defined in the plan — this is the only case where auto-commit without user confirmation is permitted. Outside of a `CT-*` step, the agent must present staged files and proposed message and wait for explicit confirmation (see `way-of-working.md` §3). If a step fails, report — do not continue to the next one.

**Plan-mode governance (hard rule):** While a plan is active, all git operations (commit, push, branch) are governed by this protocol. Ad-hoc user requests that imply git operations are interpreted through the lens of the active plan step and routed to SCOPE BOUNDARY (§13). There is no "just commit and push" shortcut.

---

## 3. Extended Execution State

For visibility and traceability, mark the active step with the appropriate label **without changing the base checkbox**.

| State | Syntax |
|-------|--------|
| Pending | `- [ ] F?-? ...` |
| In progress | `- [ ] F?-? ... ⏳ IN PROGRESS (<agent>, <date>)` |
| Blocked | `- [ ] F?-? ... 🚫 BLOCKED (<short reason>)` |
| Step locked | `- [ ] F?-? ... 🔒 STEP LOCKED (code committed, awaiting CI + plan update)` |
| Completed | `- [x] F?-? ...` |

**Mandatory rules:**
1. Do not use `[-]`, `[~]`, `[...]` or variants: only `[ ]` or `[x]`.
2. Before executing a `[ ]` step, mark it `⏳ IN PROGRESS (<agent>, <date>)`.
3. `IN PROGRESS` and `BLOCKED` are text labels, not checkbox states.
4. On completion, remove any label and mark `[x]`.
5. On completion, **append the code commit short SHA** for traceability: `- [x] F?-? — Description — ✅ \`abc1234f\``. If the step produced no code change (e.g., a verification or check step), use `✅ \`no-commit (<reason>)\`` instead of a SHA.
6. For `BLOCKED`, include brief reason and next action.
7. After code commit but before CI green + plan update, mark `🔒 STEP LOCKED`.

---

## 4. Step Eligibility Rule (Hard Rule)

**If the user expresses continuation intent (for example: "continue", "go", "let's go", "proceed", "resume"):**
Interpret continuation intent semantically, not as a literal command token.
1. Read the Execution Status and find the first `[ ]` (includes lines with `⏳ IN PROGRESS` or `🚫 BLOCKED` labels).
2. Apply the **decision table in §10** to determine the action (auto-chain, stop, or report).
3. If ambiguous: STOP and ask the user for clarification.

---

## 5. Continuation-Intent-Only Rule

**When the user expresses continuation intent, the agent executes ONLY what the plan dictates.** If the user's message includes additional instructions alongside the continuation request, the agent must:
1. **Pause and request scope confirmation** (do not silently ignore extra instructions).
2. Respond with two options: continue with the exact next plan step, or switch scope and ask the planning agent to update the plan and prompt.
3. Execute only after the user explicitly confirms one option.

### Task Chaining Policy

Defines how AI assistants must behave when executing chained plan steps.

#### Default behavior in chained mode

- Do **not** auto-fix failures by default when chaining steps.
- Record the failure with evidence (what failed, which files, and error output).
- Continue to the next step only if the failure is **non-blocking** for the current step.
- **STOP and escalate** on blocking conditions.

#### Blocking conditions (must STOP)

- A required preflight or CI gate failed and the step depends on it.
- Instructions contradict a canonical document or plan constraint.
- A dependency, permission, or required tool is missing.
- A security or data-loss risk is identified.
- An explicit hard-gate in the plan requires user review before proceeding.

#### Non-blocking failures (may continue)

- Pre-existing lint/test failures unrelated to the current step.
- Cosmetic or formatting issues that do not affect correctness.
- Warnings that do not block commit/push/PR gates.

#### Auto-fix allowance

- In **interactive single-task mode** (no plan), the assistant may attempt focused auto-fixes (max 2 attempts, scoped to the current change).
- In **chained-plan mode**, auto-fix is **not default**. The assistant documents the failure and lets the plan dictate the next action (continue, escalation, or explicit fix step).
- Auto-fixes must never go beyond the current change scope or introduce unrelated refactors.
- **Never bypass quality gates** (`--no-verify`, disabling tests/checks, weakening assertions) to force a pass.

#### Required output per step

Before handoff or auto-chain to the next step, each completed step must include:

- What changed (files and commits)
- Evidence (test output, CI status, and verification)
- Risks or open items
- Next-step handoff decision (continue, STOP, or handoff)

---

## 6. Rollback Procedure

If a completed step causes an issue not detected by tests:
1. `git revert HEAD` (reverts commit without losing history)
2. Edit Execution Status: change `[x]` back to `[ ]` for the affected step
3. Report to the planning agent for diagnosis before retrying

---

## 7. Plan Governance

### Plan Structure Rules

For plan scope principle, operational override step schema, and commit task specification rules, see [`plan-management.md` §5 - Plan Scope Principle](plan-management.md#5-plan-scope-principle-hard-rule).

These rules are enforced at plan creation time. The execution agent validates override step schema completeness before executing any operational step. If a required field is missing, STOP and ask the planning agent to update the plan.

### Approval Enforcement (Execution-Time)

When executing operational override steps, the execution agent enforces the `approval` field declared in the plan:

- `approval: auto` -> execute without requesting additional user confirmation.
- `approval: explicit-user-approval` -> STOP and request explicit user confirmation before executing.

For standard override types, runtime behavior is:

- `commit-task` -> `auto`
- `create-pr` -> `auto`
- `merge-pr` -> `explicit-user-approval`

### Pull Request progress tracking (mandatory)
Every completed step must be reflected in the active Pull Request. After push, the agent updates the PR body with `gh pr edit <pr_number> --body "..."`.

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

### Agent Availability Selection (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must ask the user which agents are available for task assignment.

**Options:**

1. **Claude Opus 4.6 + Codex 5.3** — Both agents available. The planning agent assigns steps to the most appropriate agent.
2. **Codex 5.3** — Only Codex available. All steps (planning and execution) are handled by Codex.
3. **Other** — Custom configuration (user specifies the available agents).

**Cost-aware assignment rule:**
Claude Opus 4.6 costs ~3x more tokens than Codex 5.3. When both agents are available, the planning agent MUST default to Codex unless the task has characteristics that clearly benefit from Claude (e.g., complex multi-file refactors, nuanced architectural decisions, tasks requiring deep contextual reasoning across many files). In equal conditions, always prefer Codex.

**Mandatory behavior:**
- Ask the user which agents are available before step 1 starts.
- Record the selected configuration in the active `PLAN_*.md` metadata (e.g., `**Agents:** <agent-1> + <agent-2>`).
- The planning agent uses this information to assign steps and determine handoff routing.
- If only one agent is available, all handoff rules become no-ops (the agent continues directly).

---

## 8. Step Completion Integrity (Hard Rules)

### NO-BATCH
**Prohibited: creating commits that do not match the active commit task definition.**

A single commit may include one or more implementation steps only if those steps are explicitly listed in that commit task's scope.

### CI Mode 2 — Pipeline Execution (Depth-1)

**Core principle:** Do not wait for CI between auto-chain steps. After pushing the commit bundle defined by the active commit task, immediately start the next implementation step. CI is checked *before starting* step N+2, keeping a maximum pipeline depth of 1.

#### Flow

```
Commit A → push → start working on B locally (do NOT wait for CI of A)
                   ↓
            B ready → check CI status of A
                       ├─ ✅ Green → run local tests for B → commit B → push → start C
                       └─ ❌ Red   → stash B → fix A → amend → force-push
                                     → pop B → run local tests for B → commit B → push → start C
```

#### Rules

1. **After pushing the commit bundle that contains step N:** start working on step N+1 **immediately**.
2. **Before starting step N+2:** check CI status of the latest pushed bundle that includes step N.
3. **A step is NOT marked `[x]` until CI is green for the pushed bundle that includes that step.**
4. **Always run the targeted preflight level** for the commit task scope before committing.
5. **Maximum pipeline depth: 1.** Never start step N+2 without CI of step N verified.
6. **Hard-gates (🚧)** require CI green for ALL pending steps before proceeding.
7. **Force-push is allowed** only on feature branches where a single agent is working.

#### Cancelled CI Runs

The CI workflow uses `cancel-in-progress: true` — a new push cancels the running CI for the same branch. This is expected and safe:
- CI-B validates the cumulative code (A + B). If CI-B is green, A is implicitly validated.
- Accept the **most recent completed green run** even if triggered by a later push.
- If the only completed run is cancelled, wait for the next run or re-trigger with `git commit --allow-empty`.

#### CI-FIRST Still Required For

- Hard-gate (🚧) steps
- The last step of an iteration (before merge)

### PLAN-UPDATE-IMMEDIATE
**After CI green for a step, the very next commit MUST be the plan update.** No intermediate code commits allowed. Sequence:
1. Code commit → Push → CI green → Plan-update commit → Push → Proceed

### STEP-LOCK
When a step has code pushed but CI has not yet passed:
- Mark: `🔒 STEP LOCKED (code committed, awaiting CI + plan update)`
- While LOCKED: no other step may begin execution, no handoff may be emitted, no auto-chain commit may occur.
- Lock released only when CI is green AND plan-update commit is pushed.

### EVIDENCE BLOCK (Mandatory on Every Step Close)

Every step completion message **MUST** include:

```
📋 Evidence:
- Step: F?-?
- Code commit: <SHA>
- CI run: <run_id> — <conclusion (success/failure)>
- Plan commit: <SHA>
```

If any field is missing, the step is NOT considered completed.

### AUTO-HANDOFF GUARD

Before emitting ANY handoff or auto-chain message:

1. Is the most recent CI run **green**?
2. Does the most recent commit correspond to the **plan-update commit**?

| CI green? | Plan committed? | Action |
|---|---|---|
| YES | YES | Proceed with handoff/chain |
| YES | NO | Commit plan update first |
| NO | any | **BLOCKED** — fix CI |
| unknown | any | **WAIT** — poll CI |

---

## 9. Format-Before-Commit (Mandatory)

**Before every `git commit`, the agent ALWAYS runs the project formatters:**
1. `cd frontend && npx prettier --write 'src/**/*.{ts,tsx,css}' && cd ..`
2. `ruff check backend/ --fix --quiet && ruff format backend/ --quiet`
3. If commit fails: re-run formatters, re-add, retry ONCE. Second failure: STOP.

> **Tip:** Running `scripts/ci/test-L1.ps1 -BaseRef HEAD` covers formatting, linting, and doc guards in a single command.

### Local Preflight Integration

| SCOPE BOUNDARY moment | Min. level | Command |
|---|---|---|
| Before commit (STEP A) | L1 | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| Before push (STEP C) | L2 | `scripts/ci/test-L2.ps1 -BaseRef main` |
| Before PR creation/update | L3 | `scripts/ci/test-L3.ps1 -BaseRef main` |
| Before merge to main | CI green | No local run needed |

### User Validation Environment (Mandatory)

When the agent asks the user to validate or test behavior manually, the agent MUST first start the project in **dev mode with hot reload enabled**.

Canonical command (this project):
1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`

Canonical stop command (this project):
1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml down`

Mandatory checks before asking user validation:
1. Backend reachable: `http://localhost:8000/health` returns HTTP 200.
2. Frontend reachable: `http://localhost:5173` returns HTTP 200.
3. If either check fails, STOP and report the blocker instead of asking the user to test.

---

## 10. Next-Step Message (Mandatory)

On completing a step, the agent ALWAYS tells the user the next move with concrete instructions.

**Decision table:**

| Prompt exists? | Hard-gate? | Action |
|---|---|---|
| YES | NO | **AUTO-CHAIN** — execute the next step directly. |
| YES | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |
| NO | NO | **STOP** — report: "No prompt exists for F?-?. The planning agent must write one." |
| NO | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |

---

## 11. Prompt Strategy

For prompt types and creation lifecycle, see [`plan-management.md` §6 - Prompt Strategy](plan-management.md#6-prompt-strategy).

### Resolution Priority (Execution-Time)

Prompt Queue -> Active Prompt -> STOP (ask the planning agent).

### Prompt Consumption (Execution Agent)

| Operation | Who | When |
|---|---|---|
| **Consume** | Execution agent | On step start, per resolution priority in this section |
| **Clean** | Execution agent | After step execution, clear `## Active Prompt` section content |

### Routing for Continuation Intent

Follow the **Step Eligibility Rule (§4)** to determine and execute the next step. After execution, run STEP F of SCOPE BOUNDARY.

---

## 12. Hard-Gates: Structured Decision Protocol

In 🚧 steps, the planning agent presents options as a numbered list:
```
Backlog items:
1. ✅ Centralize config — Impact: High, Effort: S
2. ✅ Add health check — Impact: Medium, Effort: S
3. ❌ Migrate to PostgreSQL — Impact: High, Effort: L (OUT OF SCOPE)
```
The user responds with numbers: `1, 2, 4` or `all` or `none`.
The planning agent records the decision, commits, prepares the prompt, and directs to the execution agent.

---

## 13. SCOPE BOUNDARY Procedure (Two-Commit Strategy for Commit Tasks)

> **Activation rule:** Any commit or push during active plan execution MUST go through this procedure. If the user requests "commit", "push", or any git operation while a plan step is active, treat it as a SCOPE BOUNDARY trigger — not as an isolated command.

Execute these steps **IN THIS EXACT ORDER**:

### STEP 0 — Branch Verification
1. Read `**Branch:**` from the plan file.
2. Check current branch: `git branch --show-current`.
3. If correct: proceed. If not: checkout or create.

### STEP A — Commit Code (plan file untouched)
1. Stage files defined in the commit task scope (never the plan file).
2. Commit with test proof in message.

### STEP B — Commit Plan Update
1. Apply completion rules per §3.
2. Stage and commit plan file only.

### STEP C — Push Both Commits
1. `git push origin <branch>`
2. Apply draft PR creation rules per §14.

### STEP D — Update Active PR Description
Update PR body per §7.

### STEP E — CI Gate
1. Check CI: `gh run list --branch <branch> --limit 1 --json status,conclusion,databaseId`
2. If in_progress: wait 30s and retry (up to 10).
3. Apply CI failure rules per §7 and AUTO-HANDOFF GUARD per §8.

### STEP F — Chain or Stop
- **PRE-CONDITION:** STEP A must have completed.
- Apply AUTO-HANDOFF GUARD per §8.
- Apply decision table per §10.

---

## 14. Iteration Lifecycle Protocol

```
Branch creation → Plan steps → PR readiness → User approval → Close-out → Merge
  [automatic]     [SCOPE BOUNDARY]  [automatic]   [hard-gate]   [automatic]  [automatic]
```

### Branch Creation (Before Any Plan Step)
1. Read `**Branch:**` from the plan.
2. `git fetch origin`
3. Create from latest main: `git checkout -b <branch> origin/main`.
4. If branch exists remotely: checkout and pull.

### Draft PR Creation (On First Push)
On the first push to a feature branch, create a draft PR immediately and record the PR number in the plan. If a PR already exists for the branch, skip creation.

### PR Readiness (Automatic)
When all steps are `[x]` and CI is green:
1. Convert draft PR to ready: `gh pr ready <pr_number>`.
2. Update title, body, classification.
3. Report PR number and URL to user.
4. **Hard-gate:** user decides when to merge.

### Iteration Close-Out Procedure (Pre-Merge)

> **Hard rule:** Close-out runs BEFORE the merge, on the feature branch itself. This avoids creating artificial close-out branches and PRs.

When user says "merge", execute close-out first:

1. **Verify clean working tree** and `git fetch --prune`.
2. **Plan reconciliation** — If any steps are `[ ]`, present each to user: Defer / Drop / Mark complete.
3. **Update IMPLEMENTATION_HISTORY.md** — Add timeline row and cumulative progress.
4. **Rename plan → completed archive** — `git mv` from active to `completed/`.
5. **DOC_UPDATES normalization** — For qualifying `.md` files only.
6. **Commit + push** — `docs(iter-close): iteration <N> close-out` on the feature branch.
7. **Wait for CI green** on the close-out commit.
8. **Mirror to docs repository** — If applicable.

### Merge (Automatic, After Close-Out)

Only after close-out is committed and CI is green:
1. Confirm PR is mergeable (CI green, no conflicts).
2. Squash merge: `gh pr merge <number> --squash --delete-branch`.
3. Switch to main, pull, delete local branch, clean stashes.

---

## 15. Plan Todo Projection (Chat) (Hard Rule)

During plan execution, the agent MUST project plan progress into chat todos.

### Required behavior

1. On continuation-intent requests, read `Execution Status` and create one chat todo per pending plan step (`- [ ]`).
2. Mark exactly one todo as `in_progress`: the current active step.
3. Mark a todo as `completed` only when the corresponding plan step is `[x]`.
4. If a plan step is `🚫 BLOCKED`, keep its todo as `in_progress` and include blocker context in the chat progress update.
5. Keep a rolling window of at least the next 3 pending steps visible in chat todos.
6. Todo titles MUST preserve plan step identifiers (for example: `F2-C — Update wiki section indexes`).

### Synchronization rules

- `PLAN_*.md` checkboxes are the source of truth.
- Chat todos are an execution-time projection and MUST stay synchronized with the plan.
- If plan and chat todos diverge, reconcile immediately from the plan before continuing.

---

## 16. Token-Efficiency Policy

To avoid context explosion:
1. **iterative-retrieval** before each step: load only current state, step objective, target files, guardrails, validation outputs.
2. **strategic-compact** at step close: summarize only the delta, validation, risks, and next move.
3. Do not carry full chat history if not necessary.
4. For chat-switch decisions, apply the **Single-Chat Execution Rule**.

> **Mandatory compact template:**
> - Step: F?-?
> - Delta: <concrete changes>
> - Validation: <tests/guards + result>
> - Risks/Open: <if applicable>

---

## 17. Commit Conventions

All commits in this flow follow the format:
```
<type>(plan-<id>): <short description>
```
Examples:
- `audit(plan-f1a): 12-factor compliance report + backlog`
- `refactor(plan-f2c): split App.tsx into page and API modules`
- `test(plan-f4c): add frontend coverage gaps for upload flow`
- `docs(plan-f5c): add ADR-ARCH-001 through ADR-ARCH-004`

---

## 18. How to Add a New User Story

When asked to add a new User Story, update [`IMPLEMENTATION_PLAN.md`](../04-delivery/IMPLEMENTATION_PLAN.md) in two places:

1. Add the story in the relevant **User Stories (in order)** list for its release.
2. Add or update the full **User Story Details** section for that story.

If the requested story is not yet scheduled in any release, schedule it in the Release Plan:
- Add it to an existing release, or
- Create a new release section when needed.

### Minimal required fields

- **ID** (e.g., `US-22`)
- **Title**
- **Goal** (via `User Story` statement)
- **Acceptance Criteria**
- **Tech Requirements** (in `Authoritative References`)
- **Dependencies** (in `Scope Clarification` and/or ordering references)

### Release assignment rules

- If the requester names a release explicitly, use that release.
- Otherwise, assign to the earliest viable release based on dependencies and existing story order.
- If no existing release is viable, create a new release after the last dependent release.

### Completion checklist

- Story appears in release-level **User Stories (in order)**.
- Story appears in **User Story Details** with required fields.
- Formatting and section structure remain consistent with existing stories.
- No unrelated documentation edits are bundled.
