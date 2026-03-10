# Plan Execution Protocol

> **Canonical source of truth.**
> This document is the single authoritative reference for how AI agents execute plan steps in this project.
>
> **Governance:**
> - This file is a canonical document maintained by humans.
> - Router modules are derived outputs generated from this canonical source.
> - Flow is **canonical → router only**. Router files MUST NOT be edited directly.
> - Any direct edit to a router file may be overwritten during the next regeneration cycle.

---

## Purpose

This protocol governs how AI agents execute plan steps in a structured, auditable manner using the plan's configured execution mode. It defines execution rules, completion integrity, CI verification, handoff conventions, and the full iteration lifecycle.

### Role taxonomy (availability-safe)

- **Planning agent**: owns plan authoring/updates, hard-gate decisions, and prompt preparation.
- **Execution agent**: owns implementation steps from pre-written prompts.

All routing and handoff rules in this document MUST use role labels (not model or vendor names).

AI assistants must stop and report the blocker when a protocol step cannot be completed as defined.

---

## File Structure

```
docs/projects/veterinary-medical-records/03-ops/
└── plan-execution-protocol.md      ← YOU ARE HERE

docs/projects/veterinary-medical-records/04-delivery/plans/
├── PLAN_<YYYY-MM-DD>_<SLUG>.md     ← Active plan (single flat file)
└── completed/
    └── PLAN_<YYYY-MM-DD>_<SLUG>.md ← Completed plan
```

**Active plan file:** For new plans, the agent attaches `plans/PLAN_<YYYY-MM-DD>_<SLUG>.md` when executing a continuation-intent request (for example: "continue", "go", "let's go", "proceed", "resume").
New plans are single flat files — no plan folders, no annex files. Legacy folder-based active plans remain accepted during migration while any active branch still resolves to `plans/<plan-folder>/PLAN_<YYYY-MM-DD>_<SLUG>.md`. Active-plan resolution searches for a matching `PLAN_*.md` outside `completed/`, regardless of nesting.
See [`plan-creation.md` §1](plan-creation.md#1-how-to-create-a-plan) for naming and location conventions.
The active plan source file contains: Execution Status (checkboxes), Prompt Queue, Active Prompt, and iteration-specific context.

---

## 1. Execution Mode Defaults

Unless the active plan records a different selection in `**Execution Mode:**`, the default execution mode is **Semi-supervised**. After completing the current task according to the active mode and closure rules, the agent applies the **decision table in §10** to determine whether to chain or stop.

### Single-Chat Execution Rule (Hard Rule)

Keep execution in the current chat by default.

The agent may recommend switching chat only when:
1. expected token-efficiency benefit is significant, or
2. a hard capability blocker requires another agent/model.

In both cases, the agent MUST explain the reason briefly and wait for explicit user decision.

**Safety limit:** if the agent detects context exhaustion (truncated responses, state loss), it must stop at the current step, complete it cleanly (full SCOPE BOUNDARY) and generate the handoff.

---

## 2. Atomic Iterations

Never mix scope between steps. Each step in Execution Status is an atomic unit: execute its objective and mark progress. Commit and push behavior are governed by the plan's execution mode (see §7 — Execution Mode). If a step fails, report — do not continue to the next one.

**Plan-mode governance (hard rule):** While a plan is active, all git operations (commit, push, branch) are governed by this protocol. Ad-hoc user requests that imply git operations are interpreted through the lens of the active plan step and routed to SCOPE BOUNDARY (§13). There is no "just commit and push" shortcut.

---

## 3. Extended Execution State

For visibility and traceability, mark the active step with the appropriate label **without changing the base checkbox**.

| State | Syntax |
|-------|--------|
| Pending | `- [ ] F?-? ...` |
| In progress | `- [ ] F?-? ... ⏳ IN PROGRESS (<agent>, <date>)` |
| Blocked | `- [ ] F?-? ... 🚫 BLOCKED (<short reason>)` |
| Completed | `- [x] F?-? ...` |

**Mandatory rules:**
1. Do not use `[-]`, `[~]`, `[...]` or variants: only `[ ]` or `[x]`.
2. Before executing a `[ ]` step, mark it `⏳ IN PROGRESS (<agent>, <date>)`.
3. `IN PROGRESS` and `BLOCKED` are text labels, not checkbox states.
4. On completion, remove any label and mark `[x]`.
5. On completion, **append the code commit short SHA** for traceability: `- [x] F?-? — Description — ✅ \`abc1234f\``. If the step produced no code change (e.g., a verification or check step), use `✅ \`no-commit (<reason>)\`` instead of a SHA.
6. For `BLOCKED`, include brief reason and next action.

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

For plan scope principle, operational override step schema, and commit task specification rules, see [`plan-creation.md` §2 - Plan Scope Principle](plan-creation.md#2-plan-scope-principle-hard-rule).

These rules are enforced at plan creation time. The execution agent validates override step schema completeness before executing any operational step. If a required field is missing, STOP and ask the planning agent to update the plan.

### Pull Request progress tracking (conditional)
If a PR already exists and the user requested update in this step, reflect completed-step progress in the PR body using `gh pr edit <pr_number> --body "..."`.

### PR traceability in plan metadata (mandatory)

When a PR is created for the plan branch, the execution agent MUST update the `**PR:**` field in the plan file with the actual PR link (e.g., `[#220](https://github.com/…/pull/220)`) in the same commit or the immediately following plan-update commit. A plan with a merged or open PR whose `**PR:**` field still shows the placeholder text is a compliance failure.

### Pre-PR Requirements

Before opening or updating a PR, the pre-PR commit history review hard rule defined in [way-of-working.md §5](../../shared/03-ops/way-of-working.md#5-pull-request-workflow) must be satisfied.

### Agent-user interaction rule

See **AGENTS.md → Global rules → Agent-user interaction rule**. That rule is the authoritative, cross-cutting definition. All references to "Agent-user interaction rule (§7)" in this document defer to it.

#### Auto-resolution of unambiguous choices

When a mandatory plan-start choice has a **single unambiguous answer derivable from the current execution context**, the agent MUST:

1. Resolve it automatically (do not ask the user).
2. State the resolved value and the evidence used.
   Example: *"Worktree: `d:\Git\worktrees\tercero` (current active workspace)."*
3. Record it in the plan file as usual.

A choice is unambiguous when:
- **Worktree:** The agent is already operating inside a specific worktree (e.g., the VS Code workspace root). Asking the user to "select" the worktree they already opened is redundant.
- **Execution Mode / Model Assignment:** These always require user input (multiple valid options exist) unless the plan file already records a prior selection.

If the agent is uncertain whether a choice is unambiguous, it MUST ask.

### Execution Worktree Selection (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must ask the user where to execute the plan.

**Mandatory behavior:**
- List **all existing worktrees** first (for example using `git worktree list`).
- Offer two choices:
  1. Use one of the listed existing worktrees.
  2. Create a new worktree (user chooses path and base branch, unless explicitly delegated).
- Do not start step 1 until the user explicitly selects one option.
- Record the selected execution worktree path in the active plan source file.
- All plan execution commands and file edits must stay within the selected worktree.

**Auto-resolution:** If the agent is already executing inside a worktree (e.g., the active VS Code workspace), that worktree is auto-resolved per the Agent-user interaction rule (§7). The agent records it in the plan and informs the user without asking. The interactive selection (list worktrees + offer create) only applies when the worktree cannot be determined from context.

### Execution Mode (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must ask the user to select the execution mode.

**Options:**

| Mode | Per-task gate | Per-checkpoint gate | Commit | Push | Hard-gates (🚧) | Max retries |
|---|---|---|---|---|---|---|
| **Supervised** | L2 | L3 | Manual (user approval) | Manual | User decides | 2 |
| **Semi-supervised** | L1 | L2 | Manual (user approval) | Manual | User decides | 2 |
| **Autonomous** | L2 | L3 | Automatic | Automatic | Agent decides (documented) | 10 |

**Mandatory behavior:**
- Ask the user to choose one mode before step 1 starts.
- Present options using the Agent-user interaction rule (§7).
- Record the selected mode in the active plan source file.
- Record format: `**Execution Mode:** <selected-mode>`
- If the user does not choose, default to **Semi-supervised**.
- The selected mode applies to the full plan unless the user explicitly changes it.

#### Mode definitions

**Supervised:**
- After completing each task, run L2 (`scripts/ci/test-L2.ps1 -BaseRef main`). Fix until green (max 2 attempts; on 3rd failure STOP and report). Then wait for user instructions.
- At `📌` commit checkpoints, escalate to L3 (`scripts/ci/test-L3.ps1 -BaseRef main`). Fix until green (max 2 attempts; on 3rd failure STOP and report). Then wait for user instructions.
- Commit and push require explicit user approval.
- Hard-gates require user decision.

**Semi-supervised:**
- After completing each task, run L1 (`scripts/ci/test-L1.ps1 -BaseRef HEAD`). Fix until green (max 2 attempts; on 3rd failure STOP and report).
- At `📌` commit checkpoints, run L2 (`scripts/ci/test-L2.ps1 -BaseRef main`). Fix until green (max 2 attempts; on 3rd failure STOP and report). Then wait for user instructions.
- Commit and push require explicit user approval.
- Hard-gates require user decision.

**Autonomous:**
- After completing each task, run L2 (`scripts/ci/test-L2.ps1 -BaseRef main`). Fix until green (max 10 attempts; on 11th failure STOP and report).
- At `📌` commit checkpoints, run L3 (`scripts/ci/test-L3.ps1 -BaseRef main`). Fix until green (max 10 attempts; on 11th failure STOP and report).
- Commit and push are automatic after tests pass.
- Hard-gates: the agent uses its best judgment, documents the decision and rationale, and continues. Exception: hard-gates marked `🚧🔒 NEVER-SKIP` still require user decision.
- **Autonomous decision log:** After plan completion, include an "Autonomous decisions" section in the PR body listing every hard-gate decision with rationale.

#### Git policy by execution mode

- `commit`:
  - `Supervised` / `Semi-supervised`: requires explicit user approval.
  - `Autonomous`: automatic after tests pass.
- `push`: always manual/user-triggered in Supervised and Semi-supervised. Automatic in Autonomous.
- Pull Request creation/update: always manual/user-triggered.
- Merge: always explicit user approval.

#### Plan-file commit hygiene (hard rule)

- **Progress marks (`[x]`):** Include the plan-file update in the same commit as the implementation it tracks. Do not create a separate commit solely to mark a step complete.
- **Scope changes** (adding, removing, or rewriting steps mid-execution): Use a dedicated commit with message `docs(plan): <description of scope change>`. A scope change is a deliberate decision, not noise.
- **Never amend the plan-start snapshot.** That commit is the execution baseline and may already be pushed. Amending it would require a force-push and destroy the temporal reference.

#### Task completion (all modes)

Mark the task `[x]` immediately upon completing the work — do not wait for CI or test results. Test verification is a subsequent obligation, not a prerequisite for marking completion.

#### Checkpoint pause rule (hard rule)

After any commit checkpoint (`📌`) whose instruction includes waiting for the user (e.g., "Then wait for user"), no further plan step may be read, explored, or executed until the user explicitly authorizes continuation after the checkpoint validation result. The checkpoint acts as a blocking gate equivalent to a hard-gate (`🚧`). This applies to all execution modes, including Autonomous.

#### Checkpoint commit gate (hard rule)

When the agent pauses at a `📌` checkpoint (per the checkpoint pause rule), the pause MUST include a **commit proposal** before the agent waits for user instructions. The proposal contains:

1. A proposed commit message (following the project's `conventional-commits` convention).
2. The list of changed files (`git status --short`).

Present using the Agent-user interaction rule (§7). Place the commit message in the question header and the options below.
If the environment supports interactive UI option selectors, the agent MUST use them for this proposal. Text fallback is allowed only when UI selection is unavailable.

**Supervised / Semi-supervised response handling:**

| User response | Agent action |
|---|---|
| **Commit** (recommended default) | Stage, commit with the proposed message, then continue. |
| **Skip** | Continue to next phase without committing. |
| **Amend message** (freeform input) | Stage, commit with the user-provided message, then continue. |
| Bare continuation ("continue", "sigue", "next", "go") without addressing the proposal | Re-present the commit proposal and require an explicit selection before proceeding. |

**Autonomous mode:** The agent auto-commits after tests pass (per Git policy). No proposal is presented.

> **Default:** Commit proposals remain pending until the user explicitly chooses `Commit`, `Skip`, or `Amend message`. No implicit approval is allowed.

#### Interrupted checkpoint proposals (hard rule)

If execution stops before the user explicitly answers a checkpoint commit proposal, the proposal expires for that turn.

On the next resume/continuation message (for example: `go`, `continue`, `sigue`), the agent MUST:

1. Recompute or restate the current commit proposal.
2. Present it again using the Agent-user interaction rule (§7).
3. Wait for an explicit user selection.

The agent MUST NOT treat a resume message by itself as prior approval.

#### Plan-start snapshot (hard rule)

After all mandatory plan-start choices are resolved and recorded in the plan file, the agent MUST:

1. Run `scripts/ci/test-L1.ps1 -BaseRef HEAD`.
2. Commit the plan file with message: `docs(plan): record plan-start choices for <plan-slug>`.
3. This commit establishes the execution baseline. No implementation step may begin before this commit exists.

### Model Assignment (Mandatory Plan-Start Choice)

Before executing the first step of a plan, the agent must ask the user to select the model assignment mode.

**Options:**
1. **Default** — Planning agent uses the most-capable available model; Execution agent uses the standard-cost model.
2. **Uniform** — Both roles use the standard-cost model.
3. **Custom** — User specifies which model to use for each role.

**Mandatory behavior:**
- Ask the user to choose one mode before step 1 starts.
- Present options using the Agent-user interaction rule (§7).
- Record the selected mode in the active plan source file.
- Record format: `**Model Assignment:** <selected-mode>`
- If the user does not choose, default to **Default**.
- The selected mode applies to the full plan unless the user explicitly changes it.

#### Task-type criteria for model tags

| Task type | Assigned model | Rationale |
|---|---|---|
| Read-only verification, prerequisite checks, baseline snapshots, evidence recording, documentation | Standard | Low complexity, structured output |
| Test writing, scaffolding, mechanical extraction, wiring, validation, dead code removal, cleanup | Standard | Good for structured code tasks |
| High-complexity decomposition, deep conditional logic refactoring, behavior-preserving rewrites of high-CC code | Most-capable | Justified only for tasks requiring deep reasoning |
| Hard-gates (🚧) | No tag | User decision, not model-dependent |

Use the most-capable model only when the step involves decomposing functions with cyclomatic complexity > 30, rewriting deeply nested conditional logic, or tasks where behavioral equivalence is hard to verify mechanically. Default to the standard model when in doubt.

#### Model routing rule (hard rule)

Each step in Execution Status carries a `[Model]` tag (e.g., `[GPT 5.4]`, `[Claude Opus 4.6]`).

**Pre-execution check:** Before starting any step, the agent MUST verify that its own model matches the step's `[Model]` tag. If the tag names a different model, the agent MUST NOT execute the step. Instead, STOP and tell the user:

> "This step is assigned to [Model X]. I am [Model Y]. Please switch to the correct model and say 'continue'."

**Post-completion check:** On step completion, check the `[Model]` tag of the next pending step. If it differs from the current model, STOP immediately and tell the user:

> "Next step recommends [Model X]. Switch to that model and say 'continue'."

Do NOT auto-chain across model boundaries.

#### Mid-Execution PR Split (Guided Protocol)

When a plan was created with a single PR but during execution the scope grows beyond what a single PR can reasonably deliver, the agent MUST follow this guided protocol:

1. **Halt** — Complete the current step. Do NOT start a new one. Tell the user: *"Step [current] is done. Before continuing, I need to address a scope issue."*
2. **Diagnose and propose** — Explain why a split is needed and present a proposed split table showing which steps go into which PR. Ask: *"Do you approve this split, or would you adjust the boundaries?"*
3. **Await approval (🚧 hard-gate)** — The user approves or adjusts.
4. **Restructure in-place** — Apply all changes in the existing plan file following the `plan-creation.md` §5 "Retrofitting a PR split during execution" procedure. Then tell the user: *"I've restructured the plan. Here is the updated Execution Status and PR Roadmap. Please review."*
5. **Confirm** — Wait for user confirmation.
6. **Commit** — `docs(plan): retrofit PR split for <plan-slug>`
7. **Resume** — Continue execution. Use branch-transition protocol (§13 STEP 0) when crossing PR boundaries.

The agent MUST guide the user step-by-step through this process, explicitly stating which protocol step is current, what will be done next, and what remains.

---

## 8. Step Completion Integrity (Hard Rules)

### NO-BATCH
**Prohibited: batching unrelated plan steps in a single commit.**

Commits must remain coherent to the currently closed implementation step(s) and their validated scope.

### EVIDENCE BLOCK (Mandatory on Every Step Close)

Every step completion message **MUST** include:

```
📋 Evidence:
- Step: F?-?
- Code commit: <SHA>
- Plan commit: <SHA>
```

If any field is missing, the step is NOT considered completed.

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

### Per-Task and Per-Checkpoint Test Gates (Hard Rule)

During plan execution, agents MUST run tests at two granularities: per-task and per-checkpoint. The specific test level at each granularity is determined by the active Execution Mode (see §7).

| Trigger | Command by level |
|---|---|
| After completing any plan task | L1: `scripts/ci/test-L1.ps1 -BaseRef HEAD` · L2: `scripts/ci/test-L2.ps1 -BaseRef main` |
| At every commit checkpoint (📌) | L2: `scripts/ci/test-L2.ps1 -BaseRef main` · L3: `scripts/ci/test-L3.ps1 -BaseRef main` |

**Retry limits** are defined per Execution Mode (see §7). On exceeding the retry limit: STOP and report to the user.

These gates complement the SCOPE BOUNDARY preflight levels. The per-task gate ensures each individual task leaves the codebase in a passing state. The per-checkpoint gate validates the cumulative branch state at natural commit boundaries.

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

For prompt types and creation lifecycle, see [`plan-creation.md` §6 - Prompt Strategy](plan-creation.md#6-prompt-strategy).

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

> **Presentation rule:** All options in hard-gates MUST be presented following the Agent-user interaction rule (AGENTS.md → Global rules).

In 🚧 steps, the planning agent presents options:
```
Backlog items:
1. ✅ Centralize config — Impact: High, Effort: S
2. ✅ Add health check — Impact: Medium, Effort: S
3. ❌ Migrate to PostgreSQL — Impact: High, Effort: L (OUT OF SCOPE)
```
The user responds with numbers: `1, 2, 4` or `all` or `none`.
The planning agent records the decision, commits, prepares the prompt, and directs to the execution agent.

---

## 13. SCOPE BOUNDARY Procedure

> **Activation rule:** Any commit or push request during active plan execution MUST go through this procedure. If the user requests "commit", "push", or another git operation while a plan step is active, treat it as a SCOPE BOUNDARY trigger — not as an isolated command.

Execute the **applicable** steps in the order below. For commit-only requests, execute STEP 0/STEP A/STEP B and skip push/PR/CI steps unless explicitly requested.

### STEP 0 — Branch Verification (Hard-Stop)
1. Read `**Branch:**` from the plan file.
  - If `**Branch:**` is missing or blank: create the branch following the branching convention in AGENTS.md, record it in the plan's `**Branch:**` field, and commit the plan update before proceeding.
2. Check current branch: `git branch --show-current`.
3. If current branch matches `**Branch:**`: proceed.
4. If mismatch: **STOP immediately.** Alert the user: "Current branch `<actual>` does not match plan branch `<expected>`. Switch to the correct branch before continuing." Do NOT commit, push, or checkout.

**Branch-transition protocol.** To change branches during plan execution, the agent MUST:
1. Verify the target branch is documented in the plan's PR Roadmap table. If not, add it first.
2. If there are uncommitted changes in the working tree, commit them with a `WIP: <description>` message on the current branch. WIP commits bypass pre-commit checks (they will be amended or squashed before push/PR).
3. Update the plan's `**Branch:**` field to the target branch.
4. Switch to the target branch.
5. Inform the user which branch is now active.
Switching without following this protocol is a compliance failure.

### STEP A — Commit Code (plan file untouched)
1. Stage files defined by the active implementation step scope (never unrelated files).
2. Commit with test proof in message.

### STEP B — Commit Plan Update
1. Apply completion rules per §3.
2. Stage and commit plan file only.

### STEP C — Push Both Commits (Conditional)
Run this step only if the user explicitly requested push in the current step.
1. `git push origin <branch>`
2. If the user explicitly requested PR creation/update in this step, apply PR workflow rules per §14. Otherwise, skip PR creation/update.

### STEP D — Update Active PR Description (Conditional)
Run this step only if:
1. STEP C ran, and
2. the user explicitly requested PR creation/update in the current step.
Then update PR body per §7.

### STEP E — CI Gate (Conditional)
Run this step only if STEP C ran.
1. Check CI: `gh run list --branch <branch> --limit 1 --json status,conclusion,databaseId`
2. If in_progress: wait 30s and retry (up to 10).
3. If CI fails, report the failure details and wait for user instructions.

### STEP F — Chain or Stop
- **PRE-CONDITION:** STEP A must have completed.
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
5. If `**Branch:**` was missing in the plan file, the agent must have already created and recorded it in STEP 0. Verify the field is populated before proceeding.

### PR Creation (User-Triggered)
PR creation remains mandatory for delivery through review, but it is **not automatic**. The agent creates or updates a PR only when the user explicitly requests it. When created, record the PR number in the plan. If a PR already exists for the branch, update it instead of creating a new one.

### PR Readiness (Automatic)
When all steps are `[x]` and CI is green:
1. If a PR exists: update title/body/classification and report PR number + URL to user.
2. If no PR exists: STOP and ask the user whether to create it now (PR is required before merge).
3. **Hard-gate:** user decides when to merge.

### Iteration Close-Out Procedure (Pre-Merge)

> **Hard rule:** Close-out runs BEFORE the merge, on the feature branch itself. This avoids creating artificial close-out branches and PRs.

When user says "merge", execute close-out first:

1. **Verify clean working tree** and `git fetch --prune`.
2. **Plan reconciliation** — If any steps are `[ ]`, present each to user: Defer / Drop / Mark complete.
3. **Update IMPLEMENTATION_HISTORY.md** — Add timeline row and cumulative progress.
4. **Move plan file to completed archive** — `git mv plans/<plan-file> plans/completed/<plan-file>`.
  Keep the file name unchanged to preserve links.
5. **DOC_UPDATES normalization** — For qualifying `.md` files only.
6. **Commit + push** — `docs(closeout): archive <plan-slug> and backlog artifacts` on the feature branch.
7. **Wait for CI green** on the close-out commit.
8. **Mirror to docs repository** — If applicable.

#### Backlog item lifecycle

Backlog items (`US-*.md`, `IMP-*.md`, `ARCH-*.md`) follow this status lifecycle:
- `Planned` — initial state.
- `In Progress` — set when plan execution starts (first step marked in-progress).
- `Done` — set automatically during closeout, before moving to `completed/`.

The agent updates `**Status:**` at each transition automatically.

#### Closeout commit (uniform rule — single-PR and multi-PR)

Every plan's **last PR** (or only PR) includes a closeout commit as its final commit before merge. This commit:

1. Sets the backlog item's `**Status:**` to `Done`.
2. **Moves the plan file** to `plans/completed/`.
3. **Moves the backlog artifact** (`US-*.md`, `IMP-*.md`, `ARCH-*.md`, or equivalent) to `Backlog/completed/` — if the artifact exists.
4. **Updates every relative link** in surrounding docs that pointed to the old paths so they resolve to the new `completed/` locations.
5. If any of the above does not apply, states `N/A` explicitly in the commit message body.

**Commit message:** `docs(closeout): archive <plan-slug> and backlog artifacts`

**Stacked PRs rule:** Only the last PR of the stack performs the closeout move. Intermediate PRs must NOT move artifacts to `completed/`; doing so breaks link resolution in sibling branches that haven't rebased yet.

**Validation before push:**
- Run doc-contract / doc-link tests locally and confirm green.
- Verify with `git diff --name-status main...HEAD` that the expected `R` (rename) or `D`+`A` entries appear for the moved files.

**PR closeout checklist (add to last PR body):**

```markdown
### Closeout
- [ ] Backlog status set to `Done`
- [ ] Plan moved to `completed/` (or N/A)
- [ ] Backlog artifact moved to `completed/` (or N/A)
- [ ] Relative links updated after move
- [ ] Doc-contract tests pass locally
```

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

- The active plan source file checkboxes are the source of truth (`PLAN_<YYYY-MM-DD>_<SLUG>.md`).
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

When asked to add a new User Story, update the delivery docs in three places:

1. Add the story in the relevant **User Stories (in order)** list for its release.
2. Create or update the dedicated backlog item file for that story.
3. Add or update the story row in the **Backlog Index**.

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
- Story has a dedicated backlog item file with required fields.
- Story appears in **Backlog Index** with the correct release assignment.
- Formatting and section structure remain consistent with existing stories.
- No unrelated documentation edits are bundled.

