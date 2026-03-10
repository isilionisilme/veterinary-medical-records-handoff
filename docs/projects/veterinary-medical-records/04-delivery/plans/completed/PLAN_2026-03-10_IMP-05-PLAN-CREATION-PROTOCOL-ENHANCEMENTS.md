# Plan: Plan Creation Protocol Enhancements (IMP-05)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.
>
> **Policy mode: Draft (IMP-05 target).** This plan dogfoods the rules it introduces. Model tags, commit checkpoints, integration strategy table, and test gate obligations are applied here as working-draft policy even though they are not yet merged into canonical docs.

**Branch:** `docs/imp-05-plan-creation-protocol-enhancements`
**PR:** [#262](https://github.com/isilionisilme/veterinary-medical-records/pull/262)
**Backlog item:** [imp-05-plan-creation-protocol-enhancements.md](../../Backlog/completed/imp-05-plan-creation-protocol-enhancements.md)
**Prerequisite:** IMP-01 merged (canonical policy stable)
**Worktree:** `d:\Git\worktrees\tercero`
**Execution Mode:** `Semi-supervised`
**Model Assignment:** `Default`

---

## Agent Instructions

> **Draft-policy rules (IMP-05 dogfooding).** Rules 1–3 and 5 below apply as draft policy because this plan introduces them (S2, S3, S7, S8). After IMP-05 merges, they will live in canonical docs and should not be repeated in future plans.

1. **After every task**, run `scripts/ci/test-L1.ps1 -BaseRef HEAD`. Fix until green (max 2 attempts; on 3rd failure STOP and report).
2. **At every commit checkpoint (📌)**, run `scripts/ci/test-L2.ps1 -BaseRef main`. Fix until green (max 2 attempts; on 3rd failure STOP and report). Then wait for user instructions.
3. **Model routing (hard rule).** Each step has a `[Model]` tag. On step completion, check the `[Model]` tag of the next pending step. If it differs from the current model, STOP immediately and tell the user: "Next step recommends [Model X]. Switch to that model and say 'continue'." Do NOT auto-chain across model boundaries.
4. **Documentation task:** This plan modifies canonical documentation directly — no separate wiki task needed. Rationale: the deliverables _are_ the docs.
5. **Branch guard (hard rule).** Before every commit, verify `git branch --show-current` matches the plan’s `**Branch:**` field (`docs/imp-05-plan-creation-protocol-enhancements`). On mismatch: STOP and alert the user. To change branches, follow the branch-transition protocol: (1) target branch must be in PR Roadmap, (2) WIP-commit uncommitted changes on current branch, (3) update `**Branch:**`, (4) switch, (5) inform the user of the new active branch.

---

## Context

Every time a plan is created, the user supplies a long ad-hoc prompt with rules for commit checkpoints, model assignment, test gates, PR closeout, merge strategy, and PR URL tracking. These rules are stable and should live in canonical docs. This plan implements nine scope items (S1–S9) that make the canonical docs self-sufficient so the plan-creation prompt reduces to a one-liner.

### Canonical files in scope

| File | Sections to modify |
|---|---|
| `AGENTS.md` | Global rules (agent-user interaction rule) |
| `docs/projects/veterinary-medical-records/03-ops/plan-creation.md` | §1 (flat plan structure), §2 (commit checkpoint format), §5 (PR Roadmap: integration table, merge strategy, PR-first order) |
| `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` | §3 (remove STEP LOCKED), §7 (unified Execution Mode + Model Assignment), §8 (remove pipeline rules), §9 (test gates framework), §14 (PR Closeout integration) |

### Files explicitly out of scope

- `execution-rules.md` — compatibility stub.
- `docs/agent_router/*` — auto-generated; will be regenerated after canonical changes land.
- Scripts, CI, backend, frontend — no changes.

---

## Objective

1. Add commit checkpoint blockquote format to `plan-creation.md` §2. **(S1)**
2. Add Model Assignment as mandatory plan-start choice to `plan-execution-protocol.md` §7. **(S2)**
3. Formalize mode-specific test gates per task and per checkpoint in `plan-execution-protocol.md` §9. **(S3)**
4. Add integration strategy table, merge strategy definitions, and URL traceability to `plan-creation.md` §5. **(S4)**
5. Merge PR Closeout Protocol into `plan-execution-protocol.md` §14 Iteration Close-Out. **(S5)**
6. Add PR-first planning order rule to `plan-creation.md` §5. **(S6)**
7. Replace CI Execution Mode + Automation Mode with unified Execution Mode (Supervised / Semi-supervised / Autonomous) in `plan-execution-protocol.md` §7, §8, §3. **(S7)**
8. Strengthen Branch Guard in `plan-execution-protocol.md` §11 (STEP 0) and §14: mandatory `**Branch:**` field, continuous branch verification, and branch-transition protocol. **(S8)**
9. Flatten plan structure in `plan-creation.md` §1: remove folder convention and annex files, single file per plan. **(S9)**

---

## Scope Boundary

- **In scope:** Editing canonical operational policy text in `plan-creation.md` and `plan-execution-protocol.md`. Removing obsolete CI Execution Mode, Automation Mode, and pipeline rules. Strengthening branch guard rules. Static content validation. Router regeneration.
- **Out of scope:** CI scripts/guards, plan migrations (IMP-04), backend/frontend product behavior, existing plan files.

---

## PR Roadmap

Single PR delivering all six scope items. Both target files are canonical operational docs with no code dependency.

**Merge strategy:** N/A (single PR).

| PR | Branch | Scope | Depends on | Status | URL |
|---|---|---|---|---|---|
| PR-1 | `docs/imp-05-plan-creation-protocol-enhancements` | All S1–S9 canonical doc changes + router regen | None | Open | [#262](https://github.com/isilionisilme/veterinary-medical-records/pull/262) |

**PR partition gate evidence:**
- Estimated changed files: 4 (2 canonical docs + 2 regenerated router files).
- Estimated changed lines: ~120.
- Semantic risk: docs-only, single concern (operational policy). No backend/frontend/schema mix.
- Size guardrails: well under 400 lines / 15 files.
- Decision: **Option A** — single PR. Cohesive low-risk documentation changes.

---

## Design Decisions

### DD-1: All six items in a single PR

All changes target two canonical docs and their derived router files. There is no semantic risk from mixing them — they are all additive policy text for the same operational surface. Splitting would add PR overhead without reducing review risk.

### DD-2: Dogfooding draft policy

This plan applies IMP-05 target rules (model tags, commit checkpoints, integration table) to itself. This validates the rules before they are canonical and produces a real-world test case.

### DD-3: Router regeneration as a single validation step

Router files are auto-generated from canonical sources. Rather than regenerating after each individual change, we regenerate once after all canonical edits are done and validate with L2/L3.

### DD-4: Unified Execution Mode replaces two separate choices

CI Execution Mode × Automation Mode gave 9 theoretical combinations, most impractical. The three new modes (Supervised / Semi-supervised / Autonomous) unify test levels, commit/push policy, and hard-gate behavior into a single coherent choice, reducing plan-start questions from 4 to 3.

### DD-5: Branch Guard as hard-stop with controlled transitions

STEP 0 already verifies the branch, but silently falls back to checkout/create. S8 upgrades this to a hard-stop on mismatch: the agent must alert the user and never commit to the wrong branch. Branch switching is allowed only via a branch-transition protocol (target in PR Roadmap, update `**Branch:**`, notify user). This prevents accidental cross-branch work while supporting legitimate multi-PR splits.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — user review/decision required

### Phase 1 — plan-creation.md changes (S1, S4, S6, S9)

- [x] P1-A 🔄 `[GPT 5.4]` — **S1: Commit checkpoint format.** In `plan-creation.md` §2, after the existing "Required inline commit recommendation format" subsection, add a new "Commit checkpoint blockquote format" subsection prescribing the `📌` blockquote format for commit checkpoints in plans. — ✅ `no-commit (checkpoint commit deferred)`
- [x] P1-B 🔄 `[GPT 5.4]` — **S6: PR-first planning order.** In `plan-creation.md` §5, before the "PR sizing and split criteria" subsection, add a rule that when a plan may span multiple PRs, PR boundaries must be determined before writing Execution Status and commit checkpoints. — ✅ `no-commit (checkpoint commit deferred)`
- [x] P1-C 🔄 `[GPT 5.4]` — **S4: Integration strategy table and merge strategy.** In `plan-creation.md` §5, under the existing "When `## PR Roadmap` is present" block, add: (a) integration strategy table requirement with mandatory columns, (b) merge strategy definitions table, (c) URL traceability hard rule. — ✅ `no-commit (checkpoint commit deferred)`
- [x] P1-D 🔄 `[GPT 5.4]` — **S9: Flat plan structure.** In `plan-creation.md` §1: (a) replace folder-based naming/location with flat file convention (`plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`); (b) remove annex file convention (`PR-X.md`); (c) update completed plans path to `plans/completed/PLAN_<YYYY-MM-DD>_<SLUG>.md`; (d) update template steps to single "Create plan file" step. — ✅ `no-commit (checkpoint commit deferred)`

> 📌 **Commit checkpoint — Phase 1 complete.** Suggested message: `docs(ops): add commit checkpoint format, PR-first order, integration strategy, and flat plan structure to plan-creation`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 2 — plan-execution-protocol.md changes (S7, S2, S8, S3, S5)

- [x] P2-A 🔄 `[GPT 5.4]` — **S7: Unified Execution Mode.** In `plan-execution-protocol.md`: (a) replace CI Execution Mode + Automation Mode in §7 with a single "Execution Mode" subsection defining Supervised, Semi-supervised, and Autonomous modes; (b) remove CI Mode 2 pipeline block, STEP LOCKED, PLAN-UPDATE-IMMEDIATE, and AUTO-HANDOFF GUARD from §8; (c) remove STEP LOCKED row from §3; (d) update plan-start choices to Worktree + Execution Mode + Model Assignment. Also adds checkpoint pause rule and plan-start snapshot rule. ✅ (GitHub Copilot, 2026-03-10)
- [x] P2-B 🔄 `[GPT 5.4]` — **S2: Model Assignment plan-start choice.** In `plan-execution-protocol.md` §7, after the new "Execution Mode" subsection, add "Model Assignment (Mandatory Plan-Start Choice)" with options (Default, Uniform, Custom), task-type criteria table, recording format, and model routing hard rule. ✅ (GitHub Copilot, 2026-03-10)
- [x] P2-E 🔄 `[GPT 5.4]` — **S8: Branch Guard.** In `plan-execution-protocol.md`: (a) strengthen STEP 0 in §11 to hard-stop on branch mismatch (no silent fallback); (b) add branch-transition protocol (target in PR Roadmap, update `**Branch:**`, notify user); (c) in §14 Branch Creation, add: if `**Branch:**` is missing, create it and annotate the plan before proceeding. ✅ (GitHub Copilot, 2026-03-10)
- [x] P2-C 🔄 `[GPT 5.4]` — **S3: Test gates framework.** In `plan-execution-protocol.md` §9, after the "Local Preflight Integration" table, add a "Per-Task and Per-Checkpoint Test Gates" subsection defining the gate concept, retry limits (max 2 in Supervised/Semi-supervised, max 10 in Autonomous), and linking to the Execution Mode definitions for specific test levels. ✅ (GitHub Copilot, 2026-03-10)
- [x] P2-D 🔄 `[GPT 5.4]` — **S5: PR Closeout Protocol.** In `plan-execution-protocol.md` §14, extend the "Iteration Close-Out Procedure" to add: (a) backlog item lifecycle (Planned → In Progress → Done), (b) uniform closeout commit rule for single-PR and multi-PR plans (move plan + backlog to `completed/`), (c) link update requirement, (d) closeout checklist for PR body, (e) stacked PRs rule (only last PR does closeout). ✅ (GitHub Copilot, 2026-03-10)

> 📌 **Commit checkpoint — Phase 2 complete.** Suggested message: `docs(ops): add execution modes, model assignment, test gates, and PR closeout to plan-execution-protocol`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 3 — Router regeneration and validation

- [x] P3-A 🔄 `[GPT 5.4]` — **Regenerate router files.** Run `python scripts/docs/generate-router-files.py`. Stage and verify the regenerated files reflect the new canonical content. ✅ (GitHub Copilot, 2026-03-10)

> 📌 **Commit checkpoint — Phase 3 complete.** Suggested message: `docs(router): regenerate router files from updated canonical sources`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 4 — Final validation

- [x] P4-T 🔄 `[Claude Opus 4.6]` — **Model routing guard test.** Dummy task: print "Model routing guard works — this task is for Claude." This step exists solely to test the pre-execution model verification rule. If the executing agent is not Claude, it must refuse and prompt the user to switch. ✅ (Claude Opus 4.6, 2026-03-10)
- [x] P4-A 🔄 `[GPT 5.4]` — **Cross-check consistency.** Read both canonical files end-to-end and verify: (a) commit checkpoint format is defined in §2, (b) PR-first order rule exists in §5, (c) integration table and merge strategy are in §5, (d) Model Assignment is in §7, (e) test gates are in §9, (f) closeout protocol is in §14. Report PASS/FAIL per item. ✅ (GitHub Copilot, 2026-03-10)
- [x] P4-B 🚧 — **Hard-gate: user validates final canonical text.** Present acceptance criteria checklist. Wait for explicit approval. ✅ (User approved, 2026-03-10)

### Phase 5 — Closeout

- [x] P5-A 🔄 `[GPT 5.4]` — **Closeout commit.** Move plan file to `plans/completed/`. Move `imp-05-plan-creation-protocol-enhancements.md` to `Backlog/completed/`. Update relative links. Verify with `git diff --name-status main...HEAD`. ✅ `3b96497d`

> 📌 **Commit checkpoint — Phase 5 complete.** Suggested message: `docs(closeout): archive IMP-05 plan and backlog artifacts`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

---

## Prompt Queue

### Prompt 1 — P1-A: Commit checkpoint blockquote format (S1)

**Step:** P1-A
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-creation.md`

**Instructions:**

1. Open `plan-creation.md`. Locate §2 "Plan Scope Principle (Hard Rule)", subsection "Required inline commit recommendation format" (ends with the line about `CT-*` prohibition).

2. After that subsection (before the `---` separator to §3), insert:

   ```markdown
   ### Commit checkpoint blockquote format

   When a plan includes commit checkpoint recommendations, use this blockquote format:

   > 📌 **Commit checkpoint — <Phase/group> complete.** Suggested message: `<type>(<scope>): <description>`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

   Rules:
   - Checkpoint blockquotes are guidance, not executable checklist items (consistent with the Plan Scope Principle).
   - Place checkpoints after the last step of a logical group or phase.
   - The suggested commit message must follow [way-of-working.md §3](../../../../../shared/03-ops/way-of-working.md) conventions.
   - The L2 reference is `scripts/ci/test-L2.ps1 -BaseRef main`.
   ```

3. Verify: the new subsection sits between the existing commit recommendation format and the §3 separator.

---

### Prompt 2 — P1-B: PR-first planning order (S6)

**Step:** P1-B
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-creation.md`

**Instructions:**

1. Open `plan-creation.md`. Locate §5 "Pull Request Policy in Plans". Find the line `- During plan creation, the planning agent MUST estimate the required number of PRs and record that decision in \`## PR Roadmap\`.`

2. Immediately after that bullet, insert:

   ```markdown
   - **PR-first planning order (hard rule):** When a plan may span multiple PRs, determine PR boundaries and record them in `## PR Roadmap` **before** writing `## Execution Status` and commit checkpoints. Post-hoc PR partitioning risks misaligned checkpoints and step-to-PR tag inconsistencies.
   ```

3. Verify: the new rule appears before the "PR sizing and split criteria" subsection.

---

### Prompt 3 — P1-C: Integration strategy table and merge strategy (S4)

**Step:** P1-C
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-creation.md`

**Instructions:**

1. Open `plan-creation.md`. Locate the block that starts with `When \`## PR Roadmap\` is present:` (currently has 3 bullets about section location, `[PR-X]` tags, and annex files).

2. After the existing 3 bullets, append the following content (still under the "When `## PR Roadmap` is present" block, before the `### Plan-start requirement` subsection):

   ```markdown

   #### Integration strategy table (mandatory)

   The roadmap MUST open with:
   1. A one-line summary stating the total number of PRs.
   2. A **Merge strategy** declaration.
   3. An integration table with these exact columns:

   | Column | Content |
   |---|---|
   | PR | PR identifier (`PR-1`, `PR-2`, …) |
   | Branch | Branch name for this PR |
   | Scope | One-line description of what this PR delivers |
   | Depends on | Other PR identifiers this PR depends on, or `None` |
   | Status | `Not started` · `In progress` · `Open` · `Merged` |
   | URL | PR URL when created, otherwise `—` |

   Example:

   ```
   Delivery split into 3 sequential PRs.
   Merge strategy: Sequential.

   | PR | Branch | Scope | Depends on | Status | URL |
   |---|---|---|---|---|---|
   | PR-1 | feat/foo-api | Backend API + unit tests | None | In progress | — |
   | PR-2 | feat/foo-frontend | Frontend + E2E tests | PR-1 | Not started | — |
   | PR-3 | feat/foo-docs | Documentation + closeout | PR-2 | Not started | — |
   ```

   For plans with a single PR, the `**PR:**` metadata field remains sufficient and the integration strategy table is optional.

   #### Merge strategy definitions

   | Strategy | Rule | When to use |
   |---|---|---|
   | `Independent` | PRs merge to `main` in any order | PRs touch disjoint areas with no code dependency |
   | `Sequential` | PR-N merges before PR-N+1; each targets `main` | PR-N+1 depends on code delivered by PR-N |
   | `Stacked-rebase` | PR-N+1 branches from PR-N; after merge of PR-N, rebase PR-N+1 onto `main` | Parallel development with linear dependency |

   Default: `Sequential` when any PR declares a dependency; `Independent` otherwise.

   #### URL traceability (hard rule)

   When a PR is created, update the integration table: set Status to `Open` and URL to the actual PR link (e.g., `[#221](https://github.com/…/pull/221)`). A plan with an open or merged PR whose URL column still shows `—` is a compliance failure.

   #### Retrofitting a PR split during execution

   A plan that started as single-PR may need splitting mid-execution. When the agent or user identifies this, the agent MUST follow this guided protocol:

   1. **Halt** — Complete the current step. Do NOT start a new one. Tell the user: *"Step [current] is done. Before continuing, I need to address a scope issue."*
   2. **Diagnose and propose** — Explain why a split is needed and present a proposed split table:
      > "This plan has grown beyond a single PR. I recommend splitting it into N PRs. Here is my proposal:"
      >
      > | PR | Steps | Scope | Rationale |
      > |---|---|---|---|
      > | PR-1 | P1-A through P2-C | … | … |
      > | PR-2 | P3-A through P5-A | … | … |
      >
      > "Do you approve this split, or would you adjust the boundaries?"
   3. **Await approval (🚧 hard-gate)** — The user approves or adjusts.
   4. **Restructure in-place** — All changes in the existing plan file (no new documents):
      - Add `## PR Roadmap` with integration strategy table.
      - Declare merge strategy.
      - Re-tag every step in `## Execution Status` with `[PR-X]` (completed steps get `[PR-1]` retroactively).
      - Insert `📌` commit checkpoints at PR boundaries if missing.
      - Update `**PR:**` metadata → `See ## PR Roadmap`.
      - Register the current branch as PR-1's branch.
      - Tell the user: *"I've restructured the plan. Here is the updated Execution Status and PR Roadmap. Please review."*
   5. **Confirm** — Wait for user confirmation of the restructured plan.
   6. **Commit** — `docs(plan): retrofit PR split for <plan-slug>`
   7. **Resume** — Continue execution. Use branch-transition protocol (S8) when crossing PR boundaries.

   The agent MUST guide the user step-by-step, explicitly stating which protocol step is current, what will be done next, and what remains.
   ```

3. Verify: the three new subsubsections (`Integration strategy table`, `Merge strategy definitions`, `URL traceability`) and the `Retrofitting a PR split during execution` subsection appear under the `When \`## PR Roadmap\` is present` block, before `### Plan-start requirement`.

---

### Prompt 4 — P1-D: Flat plan structure (S9)

**Step:** P1-D
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-creation.md`

**Instructions:**

1. Open `plan-creation.md`. Locate §1 "How to Create a Plan", subsection "Naming and location".

2. Replace the current content of "Naming and location" (lines about plan folder naming, active plan location, canonical root file, legacy compatibility, annex files, and completed plans location) with:

   ```markdown
   ### Naming and location

   - Plan file naming convention: `PLAN_<YYYY-MM-DD>_<SLUG>.md`
   - Active plan location: `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`
   - Completed plans location: `docs/projects/veterinary-medical-records/04-delivery/plans/completed/PLAN_<YYYY-MM-DD>_<SLUG>.md`
   - Plans are **single files** — no plan folders, no annex files (`PR-X.md`). All plan content lives in the root `.md` file.
   ```

3. In the "Required plan template" subsection, replace steps 1–2:
   ```
   1. Create plan folder: `plans/<plan-folder>/`.
   2. Create root file: `plans/<plan-folder>/PLAN_<YYYY-MM-DD>_<SLUG>.md` (matching the folder name).
   ```
   with:
   ```
   1. Create plan file: `plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`.
   ```
   Renumber subsequent steps (old step 3 becomes step 2, etc.).

4. In the "When `## PR Roadmap` is present" block, find and **delete** the bullet:
   ```
   - If a PR requires implementation detail that would bloat the plan root file, create/update `PR-X.md` annex files in the same folder and link them from the roadmap.
   ```

5. Verify: §1 no longer mentions plan folders, annex files, or `PR-X.md`. The template has a single "Create plan file" step.

---

### Prompt 5 — P2-A: Unified Execution Mode (S7)

**Step:** P2-A
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. In §7 "Plan Governance", **delete** the following two subsections entirely:
   - `### CI Execution Mode (Mandatory Plan-Start Choice)` (and all its content including the three options, mandatory behavior list, and the Mode 2 reference)
   - `### Automation Mode Selection (Mandatory Plan-Start Choice)` (and all its content including the three options and mandatory behavior list)

2. In their place, insert:

   ```markdown
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
   - If the interaction environment does not support option selectors, present the options as numbered text and accept the user's text reply.
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

   #### Task completion (all modes)

   Mark the task `[x]` immediately upon completing the work — do not wait for CI or test results. Test verification is a subsequent obligation, not a prerequisite for marking completion.

   #### Mid-Execution PR Split (Guided Protocol)

   When a plan was created with a single PR but during execution the scope grows beyond what a single PR can reasonably deliver, the agent MUST follow this guided protocol:

   1. **Halt** — Complete the current step. Do NOT start a new one. Tell the user: *"Step [current] is done. Before continuing, I need to address a scope issue."*
   2. **Diagnose and propose** — Explain why a split is needed and present a proposed split table showing which steps go into which PR. Ask: *"Do you approve this split, or would you adjust the boundaries?"*
   3. **Await approval (🚧 hard-gate)** — The user approves or adjusts.
   4. **Restructure in-place** — Apply all changes in the existing plan file following the `plan-creation.md` §5 "Retrofitting a PR split during execution" procedure. Then tell the user: *"I've restructured the plan. Here is the updated Execution Status and PR Roadmap. Please review."*
   5. **Confirm** — Wait for user confirmation.
   6. **Commit** — `docs(plan): retrofit PR split for <plan-slug>`
   7. **Resume** — Continue execution. Use branch-transition protocol (§11 STEP 0) when crossing PR boundaries.

   The agent MUST guide the user step-by-step through this process, explicitly stating which protocol step is current, what will be done next, and what remains.
   ```

3. In §8 "Step Completion Integrity (Hard Rules)", **delete** the following subsections:
   - `### CI Mode 2 — Pipeline Execution (Depth-1)` (including Flow diagram, Rules, Cancelled CI Runs, CI-FIRST Still Required For)
   - `### PLAN-UPDATE-IMMEDIATE`
   - `### STEP-LOCK`
   - `### AUTO-HANDOFF GUARD`

   Keep `### NO-BATCH` and `### EVIDENCE BLOCK`.

4. In §3 "Extended Execution State", **delete** the `Step locked` row from the table:
   ```
   | Step locked | `- [ ] F?-? ... 🔒 STEP LOCKED (code committed, awaiting CI + plan update)` |
   ```
   Also delete rule 7: `7. After code commit but before CI green + plan update, mark 🔒 STEP LOCKED.`

5. In §1, find `Commit behavior is governed by the plan's automation mode (see §7 — Automation Mode Selection)` and update to: `Commit behavior is governed by the plan's execution mode (see §7 — Execution Mode)`.

6. Add a general rule at the top of §7 (before the first plan-start subsection) applicable to all plan-start choices:

   ```markdown
   ### Plan-start interaction rule

   When presenting mandatory plan-start choices, agents MUST prefer interactive UI option selectors (e.g., clickable option lists) when the environment supports them. Fall back to numbered text options only when the interaction environment does not support UI selectors.

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
   ```

7. In the **existing** `### Execution Worktree Selection (Mandatory Plan-Start Choice)` subsection (which is kept, not deleted), append the following paragraph after the last bullet of "Mandatory behavior":

   ```markdown
   **Auto-resolution:** If the agent is already executing inside a worktree (e.g., the active VS Code workspace), that worktree is auto-resolved per the Plan-start interaction rule (§7). The agent records it in the plan and informs the user without asking. The interactive selection (list worktrees + offer create) only applies when the worktree cannot be determined from context.
   ```

8. Verify: §7 now has three plan-start choices (Worktree, Execution Mode, Model Assignment), the Plan-start interaction rule with auto-resolution, the Mid-Execution PR Split protocol, and the old CI Mode, Automation Mode, and pipeline rules are gone.

---

### Prompt 6 — P2-B: Model Assignment plan-start choice (S2)

**Step:** P2-B
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §7 "Plan Governance". Find the end of the "Execution Mode (Mandatory Plan-Start Choice)" subsection.

2. Insert the following new subsection **after** Execution Mode and **before** the `---` separator to §8:

   ```markdown
   ### Model Assignment (Mandatory Plan-Start Choice)

   Before executing the first step of a plan, the agent must ask the user to select the model assignment mode.

   **Options:**
   1. **Default** — Planning agent uses the most-capable available model; Execution agent uses the standard-cost model.
   2. **Uniform** — Both roles use the standard-cost model.
   3. **Custom** — User specifies which model to use for each role.

   **Mandatory behavior:**
   - Ask the user to choose one mode before step 1 starts.
   - **Prefer interactive UI option selectors** (e.g., clickable option lists) when the environment supports them.
   - If the interaction environment does not support option selectors, present the options as numbered text and accept the user's text reply.
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

   Each step in Execution Status carries a `[Model]` tag (e.g., `[GPT 5.4]`, `[Claude Opus 4.6]`). On step completion, check the `[Model]` tag of the next pending step. If it differs from the current model, STOP immediately and tell the user:

   > "Next step recommends [Model X]. Switch to that model and say 'continue'."

   Do NOT auto-chain across model boundaries.
   ```

3. Verify: the three mandatory plan-start choices are now Worktree, Execution Mode, and Model Assignment.

---

### Prompt 7 — P2-E: Branch Guard and Test Gates (S8, S3)

**Step:** P2-E
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §11 "Commit and Push Operatives", subsection "STEP 0 — Branch Verification".

2. Replace the current STEP 0 content with the following strengthened version:

   ```markdown
   ### STEP 0 — Branch Verification (Hard-Stop)
   1. Read `**Branch:**` from the plan file.
      - If `**Branch:**` is missing or blank: create the branch following the branching convention in AGENTS.md, record it in the plan’s `**Branch:**` field, and commit the plan update before proceeding.
   2. Check current branch: `git branch --show-current`.
   3. If current branch matches `**Branch:**`: proceed.
   4. If mismatch: **STOP immediately.** Alert the user: "Current branch `<actual>` does not match plan branch `<expected>`. Switch to the correct branch before continuing." Do NOT commit, push, or checkout.

   **Branch-transition protocol.** To change branches during plan execution, the agent MUST:
   1. Verify the target branch is documented in the plan’s PR Roadmap table. If not, add it first.
   2. If there are uncommitted changes in the working tree, commit them with a `WIP: <description>` message on the current branch. WIP commits bypass pre-commit checks (they will be amended or squashed before push/PR).
   3. Update the plan’s `**Branch:**` field to the target branch.
   4. Switch to the target branch.
   5. Inform the user which branch is now active.
   Switching without following this protocol is a compliance failure.
   ```

3. Locate §14 "Iteration Lifecycle Protocol", subsection "Branch Creation (Before Any Plan Step)".

4. Add the following note after step 4 ("If branch exists remotely: checkout and pull."):

   ```markdown
   5. If `**Branch:**` was missing in the plan file, the agent must have already created and recorded it in STEP 0. Verify the field is populated before proceeding.
   ```

5. Verify: STEP 0 now uses "Hard-Stop" in its heading, includes the missing-branch auto-creation rule, and includes the branch-transition protocol.

**Step:** P2-C
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §9 "Format-Before-Commit (Mandatory)". Find the "Local Preflight Integration" table (ends just before `### User Validation Environment`).

2. After the Local Preflight Integration table and before `### User Validation Environment`, insert:

   ```markdown
   ### Per-Task and Per-Checkpoint Test Gates (Hard Rule)

   During plan execution, agents MUST run tests at two granularities: per-task and per-checkpoint. The specific test level at each granularity is determined by the active Execution Mode (see §7).

   | Trigger | Command by level |
   |---|---|
   | After completing any plan task | L1: `scripts/ci/test-L1.ps1 -BaseRef HEAD` · L2: `scripts/ci/test-L2.ps1 -BaseRef main` |
   | At every commit checkpoint (📌) | L2: `scripts/ci/test-L2.ps1 -BaseRef main` · L3: `scripts/ci/test-L3.ps1 -BaseRef main` |

   **Retry limits** are defined per Execution Mode (see §7). On exceeding the retry limit: STOP and report to the user.

   These gates complement the SCOPE BOUNDARY preflight levels. The per-task gate ensures each individual task leaves the codebase in a passing state. The per-checkpoint gate validates the cumulative branch state at natural commit boundaries.
   ```

3. Verify: the new subsection sits between "Local Preflight Integration" and "User Validation Environment".

---

### Prompt 8 — P2-D: PR Closeout Protocol (S5)

**Step:** P2-D
**File:** `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`

**Instructions:**

1. Open `plan-execution-protocol.md`. Locate §14 "Iteration Lifecycle Protocol", subsection "Iteration Close-Out Procedure (Pre-Merge)". Find the existing numbered list (items 1–8).

2. After item 8 ("Mirror to docs repository"), add the following:

   ```markdown

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
   ```

3. Verify: the new subsection appears after item 8 and before `### Merge (Automatic, After Close-Out)`.

---

### Prompt 9 — P3-A: Router regeneration

**Step:** P3-A
**Files:** Generated router files under `docs/agent_router/`

**Instructions:**

1. Run: `python scripts/docs/generate-router-files.py`
2. Check which files were modified: `git diff --name-only`
3. Stage the modified router files.
4. Verify no unexpected files were changed.

---

### Prompt 10 — P4-A: Cross-check consistency

**Step:** P4-A
**Files:** Both canonical docs (read-only validation)

**Instructions:**

1. Read `plan-creation.md` and verify:
   - (a) §2 contains "Commit checkpoint blockquote format" subsection.
   - (b) §5 contains PR-first planning order rule.
   - (c) §5 contains integration strategy table, merge strategy definitions, URL traceability subsections, and retrofitting a PR split during execution.
   - (d) §1 uses flat file convention (`plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`), no plan folders, no annex files.
   - (e) §1 template has a single "Create plan file" step (no folder creation).
   - (f) §5 does NOT mention `PR-X.md` annex files.

2. Read `plan-execution-protocol.md` and verify:
   - (g) §7 contains "Execution Mode (Mandatory Plan-Start Choice)" with Supervised, Semi-supervised, Autonomous modes and their test/commit/push/hard-gate definitions.
   - (h) §7 contains "Mid-Execution PR Split (Guided Protocol)" subsection with halt-diagnose-approve-restructure-confirm-commit-resume steps.
   - (h) §7 contains "Model Assignment (Mandatory Plan-Start Choice)" subsection with options (Default, Uniform, Custom), criteria table, and routing rule.
   - (i) §9 contains "Per-Task and Per-Checkpoint Test Gates" subsection with mode-specific levels and retry limits.
   - (j) §14 contains "Closeout commit (uniform rule)" subsection with backlog lifecycle, single/multi-PR closeout, stacked PRs rule, and PR body checklist.
   - (k) §11 STEP 0 uses "Hard-Stop" heading, includes missing-branch auto-creation, and includes branch-transition protocol (S8).
   - (l) §14 Branch Creation references STEP 0 for missing branch handling (S8).
   - (m) §7 does NOT contain "CI Execution Mode" or "Automation Mode Selection" subsections.
   - (n) §8 does NOT contain "CI Mode 2", "PLAN-UPDATE-IMMEDIATE", "STEP-LOCK", or "AUTO-HANDOFF GUARD".
   - (o) §3 does NOT contain "Step locked" row.

3. Report PASS/FAIL per item (a–o). If any FAIL, fix before proceeding.

---

### Prompt 11 — P4-B: User validation hard-gate 🚧

**Step:** P4-B
**Files:** None (user review)

**Instructions:**

Present the user with the acceptance criteria checklist:

- [ ] `plan-creation.md` includes commit checkpoint blockquote format (S1).
- [ ] `plan-creation.md` includes PR-first planning order rule (S6).
- [ ] `plan-creation.md` includes integration strategy table, merge strategy definitions, URL traceability, and mid-execution PR split retrofitting protocol (S4).
- [ ] `plan-creation.md` uses flat file convention — no plan folders, no annex files (S9).
- [ ] `plan-execution-protocol.md` includes unified Execution Mode with three modes: Supervised, Semi-supervised, Autonomous (S7).
- [ ] `plan-execution-protocol.md` — old CI Execution Mode, Automation Mode, pipeline rules, STEP LOCKED removed (S7).
- [ ] `plan-execution-protocol.md` STEP 0 uses "Hard-Stop", includes missing-branch creation, and branch-transition protocol (S8).
- [ ] `plan-execution-protocol.md` includes Model Assignment plan-start choice with routing rule (S2).
- [ ] `plan-execution-protocol.md` includes mode-specific test gates per task/checkpoint with retry limits (S3).
- [ ] `plan-execution-protocol.md` includes PR Closeout Protocol with backlog lifecycle and uniform closeout commit rule (S5).
- [ ] Router files regenerated and passing.
- [ ] A new plan created with "Create the plan for the attached document" would not need ad-hoc overrides.

Wait for explicit user approval.

---

### Prompt 12 — P5-A: Closeout commit

**Step:** P5-A
**Files:** Plan file, backlog artifact, surrounding links

**Instructions:**

1. Move plan file:
   ```powershell
   git mv "docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-10_IMP-05-PLAN-CREATION-PROTOCOL-ENHANCEMENTS.md" "docs/projects/veterinary-medical-records/04-delivery/plans/completed/PLAN_2026-03-10_IMP-05-PLAN-CREATION-PROTOCOL-ENHANCEMENTS.md"
   ```

2. Move backlog artifact:
   ```powershell
   git mv "docs/projects/veterinary-medical-records/04-delivery/Backlog/imp-05-plan-creation-protocol-enhancements.md" "docs/projects/veterinary-medical-records/04-delivery/Backlog/completed/imp-05-plan-creation-protocol-enhancements.md"
   ```

3. Search for relative links pointing to the old paths and update them.

4. Verify:
   ```powershell
   git diff --name-status main...HEAD
   ```
   Confirm `R` (rename) entries for the moved files.

5. Run doc-contract tests: `scripts/ci/test-L2.ps1 -BaseRef main`

---

## Active Prompt

Pending plan approval.

---

## Acceptance Criteria

From [IMP-05 backlog item](../../Backlog/completed/imp-05-plan-creation-protocol-enhancements.md):

1. `plan-creation.md` includes commit checkpoint format, integration strategy table, merge strategy definitions, URL traceability rule, PR-first planning order, flat plan structure (no folders, no annex files), and mid-execution PR split retrofitting protocol.
2. `plan-execution-protocol.md` includes unified Execution Mode (Supervised / Semi-supervised / Autonomous), Model Assignment plan-start choice with routing rule, mode-specific test gates with retry limits, expanded close-out procedure with backlog lifecycle and uniform closeout commit rule, and strengthened Branch Guard (hard-stop, auto-creation, branch-transition protocol).
3. Old CI Execution Mode, Automation Mode, pipeline rules (CI Mode 2, STEP LOCKED, PLAN-UPDATE-IMMEDIATE, AUTO-HANDOFF GUARD) are removed from `plan-execution-protocol.md`.
4. A new plan created after these changes requires no ad-hoc prompt overrides beyond "Create the plan for the attached document."
5. Router files regenerated from updated canonical sources pass doc-contract tests.

---

## How to test

1. After merging, open a new chat and say: "Create the plan for the attached document" (attaching any backlog item).
2. Verify the agent produces a plan with:
   - Commit checkpoints in `📌` blockquote format.
   - Model tags on every execution step.
   - Integration strategy table in `## PR Roadmap` (if multi-PR).
   - Merge strategy declared.
   - Execution Mode selection offered (Supervised / Semi-supervised / Autonomous).
   - Test gate levels matching the selected Execution Mode.
   - Closeout step in the last phase.
   - Plan created as a single flat file (no folder, no annex files).
3. Simulate a mid-execution scope increase scenario and verify the agent follows the guided PR split protocol (halt → diagnose → propose → await approval → restructure in-place → confirm → commit → resume).
3. Confirm no ad-hoc override rules were needed.
4. Verify `plan-execution-protocol.md` no longer contains CI Execution Mode, Automation Mode, pipeline depth-1, STEP LOCKED, or AUTO-HANDOFF GUARD.
