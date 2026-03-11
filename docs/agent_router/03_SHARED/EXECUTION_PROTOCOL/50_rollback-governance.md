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

### Pull Request progress tracking (conditional)
If a PR already exists and the user requested update in this step, reflect completed-step progress in the PR body using `gh pr edit <pr_number> --body "..."`.

### PR traceability in plan metadata (mandatory)

When a PR is created for the plan branch, the execution agent MUST update the `**PR:**` field in the plan file with the actual PR link (e.g., `[#220](https://github.com/…/pull/220)`) in the same commit or the immediately following plan-update commit. A plan with a merged or open PR whose `**PR:**` field still shows the placeholder text is a compliance failure.

### Pre-PR Requirements

Before opening or updating a PR, the pre-PR commit history review hard rule defined in [way-of-working.md §5](../../../shared/03-ops/way-of-working.md#5-pull-request-workflow) must be satisfied.

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
- If the user does not choose, do not start step 1. Re-present the question and require an explicit selection.
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

1. Verify `**Branch:**`, `**Worktree:**`, `**Execution Mode:**`, and `**Model Assignment:**` all contain resolved non-placeholder values.
2. Run `scripts/ci/test-L1.ps1 -BaseRef HEAD`.
3. Commit the plan file with message: `docs(plan): record plan-start choices for <plan-slug>`.
4. This commit establishes the execution baseline. No implementation step may begin before this commit exists.

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
- If the user does not choose, do not start step 1. Re-present the question and require an explicit selection.
- The selected mode applies to the full plan unless the user explicitly changes it.

#### Plan-start preflight gate (hard rule)

On the first `go` / `continue` / `resume` turn for an active plan, the agent MUST inspect `**Branch:**`, `**Worktree:**`, `**Execution Mode:**`, and `**Model Assignment:**` before attempting normal execution.

If any of those fields is blank or still contains placeholder text such as `PENDING PLAN-START RESOLUTION`, `PENDING USER SELECTION`, `Pending`, or equivalent unresolved wording, the agent MUST suspend normal execution and complete plan-start first.

Until plan-start is fully resolved and the snapshot commit exists, the agent may only:

1. Read the plan/protocol and inspect repository safety state.
2. List worktrees or auto-resolve the current workspace worktree.
3. Create, select, or switch to the execution branch documented for the plan.
4. Ask the user the mandatory plan-start questions.
5. Update the plan file with the resolved values.
6. Run `scripts/ci/test-L1.ps1 -BaseRef HEAD` for the snapshot preflight.
7. Commit `docs(plan): record plan-start choices for <plan-slug>`.

Until that snapshot commit exists, the agent MUST NOT mark any non-plan-start step `⏳ IN PROGRESS`, edit implementation files, or run implementation-targeted tests.

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
