# Plan: IMP-13 PR-1 — Create Runbook Layer (Fase A)

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-13-operational-runbook-architecture.md](../Backlog/imp-13-operational-runbook-architecture.md)
**Branch:** `docs/imp-13-operational-runbook-architecture`
**PR:** [#267](https://github.com/isilionisilme/veterinary-medical-records/pull/267)
**User Story:** IMP-13 Fase A
**Prerequisite:** `main` up to date and tests green; branch `docs/imp-13-operational-runbook-architecture` already exists.
**Worktree:** `D:/Git/worktrees/cuarto`
**Execution Mode:** `Semi-supervised`
**Model Assignment:** `Uniform`

---

## Context

The current operational governance relies on a multi-level routing chain (~1000 lines of fragmented protocol). Agents saturate their context navigating conditional prose and fail to follow plan-start rules deterministically. This plan creates the new operational layer — `.prompt.md` runbooks, `.instructions.md` context files, and an enforcement script — alongside the existing system. Nothing is modified or deleted.

## Objective

Create all new operational artifacts (additive only):
1. `scripts/dev/plan-start-check.py` — deterministic enforcement script.
2. Six `.prompt.md` runbooks in `.github/prompts/`.
3. Two `.instructions.md` context files in `.github/instructions/`.
4. Dry-run validation confirming the new artifacts work.

## Scope Boundary

- **In scope:** `plan-start-check.py` + tests, `.prompt.md` files, `.instructions.md` files, dry-run validation.
- **Out of scope:** AGENTS.md changes, router modifications, CI script changes, directory deletions. These belong to PR-2 and PR-3 plans.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent without user intervention
- 🚧 hard-gate — requires user review/decision
- `[P]` Planning agent · `[E]` Execution agent

### Phase 0 — Plan-start preflight

- [x] P0-A 🔄 [P] — Resolve execution branch and update `**Branch:**` metadata.
- [x] P0-B 🔄 [P] — Resolve execution worktree and update `**Worktree:**` metadata.
- [x] P0-C 🚧 [P] — Ask user to choose `Execution Mode` and update metadata.
- [x] P0-D 🚧 [P] — Ask user to choose `Model Assignment` and update metadata.
- [x] P0-E 🔄 [P] — Record plan-start snapshot commit. — ✅ `76e0556d6`

### Phase 1 — Plan-start enforcement script

- [x] P1-A 🔄 [E] — Create `scripts/dev/plan-start-check.py`: glob active `PLAN_*.md`, parse four mandatory fields (`Branch`, `Worktree`, `Execution Mode`, `Model Assignment`), report resolved/unresolved, output structured next-action text. — ✅ `9cf211622`
- [x] P1-B 🔄 [E] — Add unit tests for `plan-start-check.py` covering: all resolved, partial resolution, no active plan, multiple active plans. — ✅ `9cf211622`

> 📌 **Commit checkpoint — P1 complete.** Suggested message: `feat(ops): add plan-start-check enforcement script with tests`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 2 — Operational prompts

- [x] P2-A 🔄 [E] — Create `plan-create.prompt.md` in `.github/prompts/`: self-contained plan creation checklist sourced from `plan-creation.md` essentials. Under 50 lines. — ✅ `8de02374`
- [x] P2-B 🔄 [E] — Create `plan-start.prompt.md`: plan-start choices + preflight gate sourced from protocol §4, §7. Under 50 lines. — ✅ `8de02374`
- [x] P2-C 🔄 [E] — Create `plan-resume.prompt.md`: plan resume flow sourced from protocol §4, §5, §10 decision table. Under 50 lines. — ✅ `8de02374`
- [x] P2-D 🔄 [E] — Create `plan-closeout.prompt.md`: closeout lifecycle sourced from protocol §14, §13. Under 50 lines. — ✅ `8de02374`
- [x] P2-E 🔄 [E] — Create `code-review.prompt.md`: code review operational rules. Under 50 lines. — ✅ `8de02374`
- [x] P2-F 🔄 [E] — Create `scope-boundary.prompt.md`: commit/push during active plan sourced from protocol §13 SCOPE BOUNDARY. Under 50 lines. — ✅ `8de02374`

> 📌 **Commit checkpoint — P2 complete.** Suggested message: `feat(ops): add operational .prompt.md runbooks`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 3 — Pattern-triggered instructions

- [x] P3-A 🔄 [E] — Create `plan-files.instructions.md` in `.github/instructions/` with `applyTo: **/plans/PLAN_*.md`. Content: atomic iterations, mark `[x]` with SHA, no scope mixing, checkpoint pause, evidence block. — ✅ `6d75946c`
- [x] P3-B 🔄 [E] — Create `backlog-files.instructions.md` in `.github/instructions/` with `applyTo: **/Backlog/*.md`. Content: status lifecycle, naming convention, link format. — ✅ `6d75946c`

> 📌 **Commit checkpoint — P3 complete.** Suggested message: `feat(ops): add pattern-triggered .instructions.md context files`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 4 — Dry-run validation

- [x] P4-A 🔄 [E] — Dry-run: simulate plan creation from cold chat using `plan-create.prompt.md`. Document result. — ✅ `no-commit (dry-run validation only)`
- [x] P4-B 🔄 [E] — Dry-run: simulate plan-start with unresolved metadata using `plan-start.prompt.md` + `plan-start-check.py`. Document result. — ✅ `no-commit (dry-run validation only)`
- [x] P4-C 🔄 [E] — Dry-run: simulate plan resume using `plan-resume.prompt.md`. Document result. — ✅ `no-commit (dry-run validation only)`
- [x] P4-D 🚧 [P] — Hard-gate: user reviews dry-run results and confirms Fase A is complete. — ✅ `no-commit (user confirmation)`

#### Validation Log

##### P4-A — PASS

- Synthetic plan skeleton created from the `plan-create.prompt.md` checklist contained all required sections from `plan-creation.md` §1, including metadata placeholders, Phase 0 preflight, Prompt Queue, Active Prompt, Acceptance criteria, How to test, and DOC-1.
- Temporary file was deleted after validation.

##### P4-B — PASS

- `plan-start-check.py --plan-dir docs/projects/veterinary-medical-records/04-delivery/plans/_dry_run_tmp` returned exit code `1` with all four metadata fields unresolved, then returned exit code `0` after simulated resolution to current branch/worktree plus selected execution mode/model assignment.
- `plan-start.prompt.md` statically validated the required behavior: detect all four fields, auto-resolve Branch and Worktree, present Execution Mode and Model Assignment choices, stop if placeholders remain, and run `L1`.
- Temporary file was deleted after validation.

##### P4-C — PASS

- Current plan state resolves the first open step as `P4-A`, which matches the expected next executable step for resume logic.
- `plan-resume.prompt.md` statically validated the required control flow: read Execution Status, resolve Prompt Queue, mark `⏳ IN PROGRESS`, apply the decision table, and stop on blocked steps.

##### Dry-run limitation

- The available tools do not provide a supported way to invoke the VS Code prompt picker directly, so prompt execution was validated by controlled simulation and static contract inspection rather than by picker invocation.

> 📌 **Commit checkpoint — PR-1 complete (Fase A).** Suggested message: `feat(ops): complete Fase A — operational runbook layer (IMP-13)`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Documentation task

- [x] DOC-1 🔄 [E] — `no-doc-needed` — ✅ `no-commit (no-doc-needed)` — This plan creates operational governance artifacts. The `.prompt.md` and `.instructions.md` files themselves serve as documentation.

---

## Prompt Queue

### Prompt 1 — P0-E: Plan-start snapshot commit

**Pre-written** · Target: P0-E · **Status: CONSUMED** (P0-E complete ✅ `76e0556d6`)

---

### Prompt 2 — P1: plan-start-check.py + unit tests

**Pre-written** · Target: P1-A, P1-B · **Status: CONSUMED** (P1 complete ✅ `9cf211622`)

---

### Prompt 3 — P2: Six .prompt.md runbooks

**Pre-written** · Target: P2-A through P2-F · **Status: CONSUMED** (P2 complete ✅ `8de02374`)

Create directory `.github/prompts/` if it doesn't exist. Each file uses `.prompt.md` extension with YAML front matter containing `mode: agent` and a `description` field. Each file must be **under 50 lines**, self-contained, and written as a deterministic checklist the agent follows step-by-step. No prose — only numbered action steps with clear exit conditions.

**P2-A — `plan-create.prompt.md`**

Description: "Create a new plan following project conventions."

Source: `plan-creation.md` §1-§5. Distill into checklist:
1. Verify the backlog item exists and is `Planned` or `In Progress`.
2. Create `PLAN_<YYYY-MM-DD>_<SLUG>.md` in the plans directory.
3. Populate required template sections: Title, Operational rules pointer, Metadata (with PENDING placeholders), Context, Objective, Scope Boundary, Execution Status (Phase 0 mandatory), Prompt Queue, Active Prompt, Acceptance criteria, How to test.
4. Add Documentation task (DOC-1) per §3.
5. Run PR partition gate (§5): estimate size, evaluate semantic risk, classify buckets, open decision gate if thresholds exceeded.
6. Write pre-written prompts for non-dependent steps (§6).
7. If multi-PR: add `## PR Roadmap` with integration strategy table before writing Execution Status.
8. Commit: `docs(plan): create <plan-slug>`.

**P2-B — `plan-start.prompt.md`**

Description: "Resolve plan-start choices and record snapshot."

Source: protocol §7 (plan-start preflight gate, execution mode, model assignment, worktree selection, plan-start snapshot). Checklist:
1. Read plan file. Inspect `**Branch:**`, `**Worktree:**`, `**Execution Mode:**`, `**Model Assignment:**`.
2. For each unresolved field:
   - Branch: check current branch, auto-resolve if matches plan context.
   - Worktree: auto-resolve to current VS Code workspace (`$PWD`).
   - Execution Mode: present 3 options (Supervised / Semi-supervised / Autonomous) with table summary. Wait for user.
   - Model Assignment: present 3 options (Default / Uniform / Custom). Wait for user.
3. Record resolved values in plan file.
4. Run `scripts/ci/test-L1.ps1 -BaseRef HEAD`.
5. Commit: `docs(plan): record plan-start choices for <plan-slug>`.
6. Inform user: plan-start complete, ready for execution.

**P2-C — `plan-resume.prompt.md`**

Description: "Resume execution of an active plan."

Source: protocol §4 (step eligibility), §5 (continuation-intent-only), §10 (decision table). Checklist:
1. Read Execution Status. Find first `[ ]` step (includes `⏳ IN PROGRESS` or `🚫 BLOCKED`).
2. If `⏳ IN PROGRESS`: resume that step from where it left off.
3. If `🚫 BLOCKED`: report blocker, ask user for resolution.
4. Check Prompt Queue for matching prompt. If exists: consume it. If not: STOP and ask planning agent.
5. Apply decision table: prompt exists + no hard-gate → auto-chain. Hard-gate → STOP and report. No prompt → STOP.
6. Mark step `⏳ IN PROGRESS (<agent>, <date>)`.
7. Execute step scope. On completion: mark `[x]` with SHA, run per-task test gate, output evidence block.
8. Apply decision table for next step.

**P2-D — `plan-closeout.prompt.md`**

Description: "Close out a plan before merge."

Source: protocol §14 (iteration close-out procedure, backlog lifecycle, closeout commit). Checklist:
1. Verify all steps are `[x]`. If any `[ ]`: present each to user — Defer / Drop / Mark complete.
2. Verify clean working tree: `git status --porcelain`.
3. `git fetch --prune`.
4. Update backlog item `**Status:**` to `Done`.
5. Move plan file: `git mv plans/<plan-file> plans/completed/<plan-file>`.
6. Move backlog artifact to `Backlog/completed/` if it exists.
7. Update relative links pointing to old paths.
8. Run doc-contract tests locally.
9. Commit: `docs(closeout): archive <plan-slug> and backlog artifacts`.
10. Push. Wait for CI green.
11. If PR exists: update PR body with closeout checklist.

**P2-E — `code-review.prompt.md`**

Description: "Run a structured code review on a pull request."

Source: `way-of-working.md` §6 (code review workflow, via router 00_entry.md). Checklist:
1. **Pre-review checks:** Confirm CI status. CI red → STOP, offer to diagnose. CI in progress → wait.
2. Confirm scope: list changed files and PR description.
3. Recommend review depth (Light / Standard / Deep / Deep critical) based on risk profile. Wait for user confirmation.
4. If Deep/Deep critical: propose lenses, launch parallel sub-agent reviews, consolidate.
5. Review focus areas (7): layering, maintainability, testability, simplicity, CI/tooling, DB safety, UX/brand.
6. Classify findings: Must-fix (blocks merge) / Should-fix / Nice-to-have.
7. Output using `AI Code Review` template exactly.
8. Publish review as PR comment. Return URL.

**P2-F — `scope-boundary.prompt.md`**

Description: "Execute commit/push during active plan execution."

Source: protocol §13 (SCOPE BOUNDARY procedure). Checklist:
1. **STEP 0 — Branch verification:** Read `**Branch:**` from plan. Verify current branch matches. Mismatch → STOP.
2. **STEP A — Commit code:** Stage implementation files only (never unrelated). Commit with test proof.
3. **STEP B — Commit plan update:** Apply §3 completion rules. Stage and commit plan file.
4. **STEP C — Push (conditional):** Only if user explicitly requested push. `git push origin <branch>`.
5. **STEP D — Update PR (conditional):** Only if STEP C ran and user requested PR update.
6. **STEP E — CI gate (conditional):** Only if STEP C ran. Check CI, wait if in progress, report failures.
7. **STEP F — Chain or stop:** Apply §10 decision table for next step.

After all 6 runbooks created: run L1 (`scripts/ci/test-L1.ps1 -BaseRef HEAD`). Fix until green (max 2 attempts). Then proceed to checkpoint pause.

---

### Prompt 4 — P3: Two .instructions.md context files

**Pre-written** · Target: P3-A, P3-B · **Status: CONSUMED** (P3 complete ✅ `6d75946c`)

Create directory `.github/instructions/` if it doesn't exist. Each file uses `.instructions.md` extension with YAML front matter containing `applyTo` glob pattern. These files are passive context — VS Code auto-injects them when the matching file is open. Keep them short and declarative (rules, not procedures).

**P3-A — `plan-files.instructions.md`**

```yaml
---
applyTo: "**/plans/PLAN_*.md"
---
```

Content (declarative rules for agents editing plan files):
- Each step is an atomic unit. Never mix scope between steps.
- Mark `[x]` with commit SHA on completion: `- [x] F?-? — Description — ✅ \`<sha>\``.
- If no code change: `✅ \`no-commit (<reason>)\``.
- Mark `⏳ IN PROGRESS (<agent>, <date>)` before starting a step.
- At `📌` checkpoints: pause, propose commit, wait for user.
- Every step close requires evidence block: Step, Code commit SHA, Plan commit SHA.
- Plan-file updates go in the same commit as the implementation they track.
- Never amend the plan-start snapshot commit.

**P3-B — `backlog-files.instructions.md`**

```yaml
---
applyTo: "**/Backlog/*.md"
---
```

Content (declarative rules for agents editing backlog items):
- Status lifecycle: `Planned` → `In Progress` → `Done`.
- Set `In Progress` when plan execution starts (first step marked in-progress).
- Set `Done` only during closeout, before moving to `completed/`.
- Naming: `<TYPE>-<NUMBER>-<slug>.md` where TYPE is `US`, `IMP`, `ARCH`, or project-specific.
- Link format for plans: `[PLAN_<date>_<slug>.md](../plans/PLAN_<date>_<slug>.md)`.
- When moving to `completed/`: update all relative links in surrounding docs.

After both P3-A and P3-B: run L1 (`scripts/ci/test-L1.ps1 -BaseRef HEAD`). Fix until green (max 2 attempts). Then proceed to checkpoint pause.

---

### Prompt 5 — P4: Dry-run validation

**Pre-written (just-in-time, now resolved)** · Target: P4-A through P4-D

Each dry-run simulates a real agent interaction using the artifacts created in P1-P3. The goal is to verify the runbooks produce deterministic, correct behavior from a cold start. Document each result as a markdown section in a single validation log entry below the step.

**P4-A — Dry-run: plan creation**

1. Open a new chat (or simulate cold context — no prior conversation state).
2. Invoke `.github/prompts/plan-create.prompt.md` via the VS Code prompt picker (type `#plan-create` or use `/` command).
3. Provide a synthetic backlog item as input: "IMP-99 — Test validation item" (do not create a real backlog file).
4. Verify the agent produces a plan skeleton containing ALL required sections from `plan-creation.md` §1:
   - Title, Operational rules pointer, Metadata (with PENDING placeholders), Context, Objective, Scope Boundary, Execution Status (with Phase 0), Prompt Queue, Active Prompt, Acceptance criteria, How to test, Documentation task (DOC-1).
5. Verify Phase 0 contains the 5 mandatory preflight steps (branch, worktree, execution mode, model assignment, snapshot).
6. Record result: `PASS` if all sections present and correctly structured, `FAIL` with specific missing/malformed sections.
7. Do NOT commit the synthetic plan — delete it after validation.

**P4-B — Dry-run: plan-start with unresolved metadata**

1. Create a temporary test plan file in `plans/` with all 4 metadata fields set to `PENDING PLAN-START RESOLUTION` / `PENDING USER SELECTION`.
2. Run `python scripts/dev/plan-start-check.py` → verify exit code 1 and all 4 fields flagged as `❌ unresolved`.
3. Invoke `.github/prompts/plan-start.prompt.md` via the VS Code prompt picker, with the test plan file attached.
4. Verify the agent:
   - Detects all 4 unresolved fields.
   - Auto-resolves Branch (current branch) and Worktree (current workspace).
   - Presents Execution Mode and Model Assignment as interactive choices (or numbered options).
   - Does NOT skip any field or proceed to implementation.
5. Run `python scripts/dev/plan-start-check.py` again after simulated resolution → verify exit code 0 and all `✅ resolved`.
6. Record result: `PASS` / `FAIL` with details.
7. Delete the temporary test plan file.

**P4-C — Dry-run: plan resume**

1. Use this plan file (IMP-13 PR-1) as the test subject — it has completed steps and pending P4 steps.
2. Invoke `.github/prompts/plan-resume.prompt.md` via the VS Code prompt picker, with this plan file attached.
3. Verify the agent:
   - Reads Execution Status and correctly identifies the first `[ ]` step (should be P4-A or whichever is current).
   - Checks Prompt Queue for a matching prompt.
   - Applies the decision table correctly (prompt exists + no hard-gate → auto-chain; hard-gate → STOP).
   - Marks the step `⏳ IN PROGRESS` before starting.
4. Record result: `PASS` if the agent follows the checklist deterministically, `FAIL` with the deviation.
5. Revert any changes the agent made to this plan file during the dry-run (the dry-run is observational, not a real execution).

**P4-D — Hard-gate: user review**

This is a 🚧 hard-gate. After P4-A, P4-B, and P4-C are complete:
1. Present the three dry-run results to the user in a summary table:

   | Dry-run | Target runbook | Result | Notes |
   |---|---|---|---|
   | P4-A | plan-create.prompt.md | PASS/FAIL | details |
   | P4-B | plan-start.prompt.md + plan-start-check.py | PASS/FAIL | details |
   | P4-C | plan-resume.prompt.md | PASS/FAIL | details |

2. Ask the user: "Fase A dry-runs complete. Do you confirm Fase A is done?"
3. If all PASS and user confirms: Fase A is complete → proceed to checkpoint commit.
4. If any FAIL: report failures, ask user whether to fix and retry or accept with noted limitations.

---

### Prompt 6 — DOC-1: Documentation task

**Pre-written** · Target: DOC-1

This step is pre-closed as `no-doc-needed`. The `.prompt.md` and `.instructions.md` files created in P2 and P3 are themselves the documentation deliverables — no separate wiki page or doc update is required.

Action:
1. Mark DOC-1 as `[x]` with `✅ \`no-commit (no-doc-needed)\``.
2. No files to create, modify, or commit.

---

## Active Prompt

None — all prompts consumed. DOC-1 closable via Prompt 6.

---

## Acceptance criteria

1. `scripts/dev/plan-start-check.py` deterministically detects unresolved plan-start fields and outputs structured next-action text.
2. All six `.prompt.md` runbooks exist under `.github/prompts/`, each under 50 lines, each self-contained.
3. Both `.instructions.md` files exist under `.github/instructions/` with correct `applyTo` patterns.
4. Unit tests for `plan-start-check.py` pass.
5. Dry-runs confirm the new artifacts work from a cold chat.
6. No existing files were modified (additive only).

## How to test

1. **Script enforcement:** Run `python scripts/dev/plan-start-check.py` against a plan with unresolved fields → verify it reports missing fields and outputs structured next-action.
2. **Prompt dry-run:** Open a new VS Code chat, invoke `plan-start.prompt.md` via the prompt picker → verify the agent follows the checklist deterministically.
3. **Instructions auto-load:** Open a `PLAN_*.md` file in VS Code → verify `plan-files.instructions.md` appears in Copilot context panel.
4. **L2 green:** Run `scripts/ci/test-L2.ps1 -BaseRef main` → all tests pass.
