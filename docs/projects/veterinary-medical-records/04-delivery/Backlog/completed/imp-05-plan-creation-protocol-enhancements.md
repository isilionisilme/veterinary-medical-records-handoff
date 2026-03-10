# IMP-05 — Plan Creation Protocol Enhancements

**Status:** Done

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (canonical docs + router regeneration only)

**Technical Outcome**
Reduce plan-creation prompt overrides to a one-liner by absorbing recurring plan-authoring rules into the canonical operational documents (`plan-creation.md` and `plan-execution-protocol.md`).

**Problem Statement**
Every time a plan is created, the user must supply a long ad-hoc prompt with rules for commit checkpoints, model assignment, test gates, PR closeout, merge strategy, and PR URL tracking. Most of these rules are stable and belong in the canonical docs. Repeating them per-plan risks drift, omissions, and wasted tokens.

**Scope**

### S1 — Commit checkpoint format in plans (`plan-creation.md` §2)

Extend the existing "Required inline commit recommendation format" to prescribe the blockquote checkpoint format:

```
> 📌 **Commit checkpoint — Phase N complete.** Suggested message: `<type>(<scope>): <description>`. Run L2 tests; if red, fix and re-run until green. Then wait for user.
```

Checkpoint recommendations remain guidance (not executable checklist items), consistent with the Plan Scope Principle.

### S2 — Model Assignment as plan-start choice (`plan-execution-protocol.md` §7)

Add a new mandatory plan-start choice: **Model Assignment**.

Options:
1. **Default** — Planning agent = most-capable available model, Execution agent = standard model.
2. **Uniform** — Both roles use standard model.
3. **Custom** — User specifies per-role.

Sub-rules:
- Record the selected mode in the plan metadata as `**Model Assignment:** <selected-mode>`.
- Each step in Execution Status carries a `[Model]` tag based on a task-type criteria table.
- **Model routing rule (hard rule):** On step completion, if the next pending step's `[Model]` tag differs from the current model, STOP and tell the user: "Next step recommends [Model X]. Switch to that model and say 'continue'."

### S3 — Formalize test gates per task and per checkpoint (`plan-execution-protocol.md` §9)

Make explicit:
- After completing every task: run `scripts/ci/test-L1.ps1 -BaseRef HEAD`. Fix until green (max 2 attempts; on 3rd failure STOP and report).
- At every commit checkpoint: run `scripts/ci/test-L2.ps1 -BaseRef main`. Fix until green (max 2 attempts; on 3rd failure STOP and report).

This aligns with the existing Local Preflight Integration table but makes the per-task L1 obligation explicit (currently only "before commit" is stated).

### S4 — PR Roadmap: integration strategy table (`plan-creation.md` §5)

When `## PR Roadmap` is present, require:

1. A one-line summary stating the total number of PRs.
2. A **Merge strategy** declaration.
3. An integration table with columns: `PR | Branch | Scope | Depends on | Status | URL`.

Merge strategy definitions:

| Strategy | Rule | When to use |
|---|---|---|
| `Independent` | PRs merge to `main` in any order | PRs touch disjoint areas with no code dependency |
| `Sequential` | PR-N merges before PR-N+1; each targets `main` | PR-N+1 depends on code delivered by PR-N |
| `Stacked-rebase` | PR-N+1 branches from PR-N; after merge of PR-N, rebase PR-N+1 onto `main` | Parallel development with linear dependency |

Default: `Sequential` when any PR declares a dependency; `Independent` otherwise.

URL traceability rule: when a PR is created, update Status to `Open` and URL to the actual link. A plan with an open/merged PR whose URL column still shows `—` is a compliance failure.

For plans with a single PR, the existing `**PR:**` metadata field remains sufficient.

#### Mid-execution PR split (retrofitting)

When a plan was created with a single PR but during execution the scope grows beyond what a single PR can reasonably deliver, the agent MUST follow this guided protocol:

1. **Halt.** Complete the current step. Do NOT start a new one.
2. **Inform.** Tell the user: "This plan has grown beyond a single PR. I recommend splitting it. Here is my proposed split:" followed by a table showing which steps go into which PR and why.
3. **Await approval (🚧 hard-gate).** The user approves or adjusts the boundaries.
4. **Restructure in-place.** All changes happen in the existing plan file (no new documents):
   - Add `## PR Roadmap` with integration strategy table (columns: PR, Branch, Scope, Depends on, Status, URL).
   - Declare merge strategy.
   - Re-tag every step in `## Execution Status` with `[PR-X]` (completed steps get `[PR-1]` retroactively).
   - Insert `📌` commit checkpoints at PR boundaries if not already present.
   - Update `**PR:**` metadata to `See ## PR Roadmap`.
   - Register the current branch as PR-1's branch in the table.
5. **Confirm.** Present the restructured plan to the user for confirmation.
6. **Commit.** Message: `docs(plan): retrofit PR split for <plan-slug>`.
7. **Resume.** Continue execution. Use branch-transition protocol (S8) when crossing PR boundaries.

The agent MUST guide the user step-by-step through this process, explicitly stating which step is current, what will be done, and what remains.

### S5 — PR Closeout Protocol integration (`plan-execution-protocol.md` §14)

Merge the PR Closeout Protocol into the existing Iteration Close-Out Procedure:

#### Backlog item lifecycle

Backlog items (`US-*.md`, `IMP-*.md`, `ARCH-*.md`) follow this status lifecycle:
- `Planned` — initial state when the item is in the backlog.
- `In Progress` — set when plan execution starts (first step marked in-progress).
- `Done` — set automatically during closeout, immediately before moving to `completed/`.

The agent updates the `**Status:**` field in the backlog artifact at each transition. No hard-gate is needed — the agent does this automatically.

#### Closeout commit (uniform rule — single-PR and multi-PR)

Every plan's **last PR** (or only PR) includes a closeout commit as its final commit before merge. This commit:

1. Sets the backlog item's `**Status:**` to `Done`.
2. **Moves the plan file** to `plans/completed/`.
3. **Moves the backlog artifact** to `Backlog/completed/` — if the artifact exists.
4. **Updates every relative link** in surrounding docs that pointed to the old paths.
5. If any of the above does not apply, states `N/A` explicitly in the commit message body.

- Commit message: `docs(closeout): archive <plan-slug> and backlog artifacts`.
- Intermediate PRs in a stack must NOT move artifacts to `completed/`.
- The closeout is automatic (no hard-gate) — easily reversible via `git mv`.
- Add a closeout checklist to the PR body template.

### S6 — PR-first planning order (`plan-creation.md` §5)

Add rule: when a plan may span multiple PRs, determine PR boundaries **before** writing the Execution Status and commit checkpoints — not after. The current "evaluate post-hoc" flow risks misaligned checkpoints.

### S9 — Flat plan structure (`plan-creation.md` §1)

Simplify plan storage from folder-based to flat files:

1. **No plan folders.** Plans are single files: `plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`. Remove the folder convention and the folder-matching name rule.
2. **No annex files.** Remove `PR-X.md` annex file convention. All PR detail goes inline (sections within the plan file). If a plan is too large for one file, it should be split into separate plans (one per backlog item).
3. **Completed plans.** Move to `plans/completed/PLAN_<YYYY-MM-DD>_<SLUG>.md` (file, not folder).
4. **Update template steps.** Replace "Create plan folder" + "Create root file" with a single "Create plan file" step.

### S7 — Unified Execution Mode (`plan-execution-protocol.md` §7, §8, §3)

Replace CI Execution Mode (Strict step gate / Pipeline depth-1 / End-of-plan gate) and Automation Mode (Supervisado / Semiautomático / Automático) with a single **Execution Mode** plan-start choice:

| Mode | Per-task gate | Per-checkpoint gate | Commit | Push | Hard-gates | Max retries |
|---|---|---|---|---|---|---|
| **Supervised** | L2 | L3 | Manual | Manual | User decides | 2 |
| **Semi-supervised** | L1 | L2 | Manual | Manual | User decides | 2 |
| **Autonomous** | L2 | L3 | Automatic | Automatic | Agent decides (documented) | 10 |

Additional rules:
- **Task completion (all modes):** Mark `[x]` immediately upon completing the work — do not wait for CI.
- **Supervised checkpoints:** The agent already pauses after each task; at `📌` checkpoints the test level escalates to L3.
- **Autonomous hard-gate safeguards:** (a) document each decision with rationale, (b) include "Autonomous decisions" summary in the PR body, (c) plan authors may mark `🚧🔒 NEVER-SKIP` on gates that require user decision even in Autonomous.
- **Autonomous push:** automatic after commit.

Removals from `plan-execution-protocol.md`:
- §7: CI Execution Mode and Automation Mode Selection subsections.
- §8: CI Mode 2 pipeline block, PLAN-UPDATE-IMMEDIATE, STEP-LOCK, AUTO-HANDOFF GUARD.
- §3: STEP LOCKED row in Extended Execution State table.
- §1: Update automation mode reference to execution mode.

Plan-start choices after S7: Worktree, Execution Mode, Model Assignment (3 instead of 4).

**Plan-start UX rule:** When asking plan-start choices, agents must prefer interactive UI option selectors (e.g., clickable option lists) over plain text. Fall back to numbered text options only when the interaction environment does not support UI selectors.

### S8 — Branch Guard (`plan-execution-protocol.md` §11, §14)

Strengthen STEP 0 (Branch Verification) and §14 (Branch Creation) so that:

1. **Branch field is mandatory.** Every plan MUST have a `**Branch:**` metadata field. If missing when execution starts, the agent creates the branch (following branching conventions), annotates it in the plan, and commits the plan update before proceeding.
2. **Continuous branch guard.** The agent MUST verify `git branch --show-current` matches `**Branch:**` before every commit operation (STEP 0 already runs, but is now a hard-stop — no implicit fallback). If a mismatch is detected: STOP, alert the user, and do NOT commit.
3. **Branch-transition protocol.** The agent MUST NOT change branches without following this protocol:
   1. The target branch must already be documented in the plan’s PR Roadmap table. If not, add it first.
   2. If there are uncommitted changes in the working tree, commit them with a `WIP: <description>` message on the current branch. WIP commits bypass pre-commit checks (they will be amended or squashed before push/PR).
   3. Update the plan’s `**Branch:**` field to the target branch.
   4. Switch to the target branch.
   5. Inform the user which branch is now active.
   - Switching without following this protocol is a compliance failure.

**Out of Scope**
- No changes to scripts or CI (owned by IMP-03).
- No migration of existing plans (owned by IMP-04).
- No product/API/UI changes.
- No router file edits (regenerated from canonical sources).

**Acceptance Criteria**
- `plan-creation.md` includes commit checkpoint format, integration strategy table, merge strategy definitions, URL traceability rule, PR-first planning order, mid-execution PR split retrofitting protocol, and flat plan structure.
- `plan-execution-protocol.md` includes unified Execution Mode (Supervised / Semi-supervised / Autonomous) replacing CI Execution Mode and Automation Mode, Model Assignment plan-start choice with routing rule, mode-specific test gates per task/checkpoint with retry limits, expanded close-out procedure with backlog lifecycle and uniform closeout commit rule, and strengthened Branch Guard (hard-stop + branch-transition protocol).
- `plan-execution-protocol.md` STEP 0 and §14 include branch guard: mandatory `**Branch:**` field, continuous verification before commits, and branch-transition protocol (S8).
- Old CI Execution Mode, Automation Mode, pipeline rules (CI Mode 2, STEP LOCKED, PLAN-UPDATE-IMMEDIATE, AUTO-HANDOFF GUARD) are removed from `plan-execution-protocol.md`.
- A new plan created after these changes requires no ad-hoc prompt overrides beyond "Create the plan for the attached document."
- Router files regenerated from updated canonical sources pass doc-contract tests.

**Validation Checklist**
- Create a test plan using only the one-line prompt and verify all six scope items are produced by the agent without additional prompting.
- Verify `## PR Roadmap` contains integration table and merge strategy when multi-PR.
- Verify model tags appear on every execution step.
- Verify commit checkpoints use the prescribed blockquote format.
- Verify close-out procedure covers artifact archival for the last PR only.
- Verify execution mode table defines three modes with distinct test levels, commit/push policy, and hard-gate handling.
- Verify old CI Execution Mode, Automation Mode, pipeline rules, STEP LOCKED, PLAN-UPDATE-IMMEDIATE, and AUTO-HANDOFF GUARD are removed.
- Doc-contract and link tests pass after changes.

**Risks and Mitigations**
- Risk: over-prescribing plan format reduces agent flexibility.
  - Mitigation: rules define minimum structure, not exhaustive content. Optional sections remain optional.
- Risk: model routing rule causes frequent stops in small plans.
  - Mitigation: the "Uniform" option eliminates routing stops when not needed.
- Risk: merge strategy definitions may not cover future GitHub features (merge queues, etc.).
  - Mitigation: "Custom" escape hatch; definitions can be extended later.

**Dependencies**
- Should land after or with IMP-01 (canonical policy alignment) so the base documents are stable.
- Independent of IMP-02 (router sync) and IMP-03 (CI guards).

---
