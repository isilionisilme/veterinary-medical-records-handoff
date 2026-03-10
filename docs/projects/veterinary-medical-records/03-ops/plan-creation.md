# Plan Creation

> Project-specific operational document.
> Defines how plans are authored and structured in the `veterinary-medical-records` project.
> Execution-time behavior is defined in [plan-execution-protocol.md](plan-execution-protocol.md).

---

## 1. How to Create a Plan

Create a plan when work requires coordinated multi-step delivery, multiple checkpoints, explicit hard-gates, or multi-agent handoffs.

### Ownership

- The planning agent owns plan authoring and plan updates.
- Execution agents consume and execute the plan; they do not redefine authoring rules.

### Naming and location

- Plan file naming convention: `PLAN_<YYYY-MM-DD>_<SLUG>.md`
- Active plan location: `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`
- Completed plans location: `docs/projects/veterinary-medical-records/04-delivery/plans/completed/PLAN_<YYYY-MM-DD>_<SLUG>.md`
- Plans are **single files** — no plan folders, no annex files (`PR-X.md`). All plan content lives in the root `.md` file.

### Required plan template

Every new plan MUST include:

1. Create plan file: `plans/PLAN_<YYYY-MM-DD>_<SLUG>.md`.
2. Title: `# Plan: <name>`
3. Operational rules pointer: `> **Operational rules:** See [plan-execution-protocol.md](...)`
4. Metadata:
   - `**Branch:**`
   - `**PR:**` — Use `Pending (PR created on explicit user request)` as placeholder.
   - `**User Story:**`
   - `**Prerequisite:**`
   - `**Worktree:**`
   - `**Execution Mode:**` — one of `Supervised`, `Semi-supervised`, `Autonomous`
   - `**Model Assignment:**` — one of `Default`, `Uniform`, `Custom`
5. `## Context`
6. `## Objective`
7. `## Scope Boundary`
8. `## Execution Status`
9. `## Prompt Queue`
10. `## Active Prompt`
11. `## Acceptance criteria`
12. `## How to test`

Optional sections:

- `## Design decisions`
- `## PR Roadmap` (mandatory when a plan spans multiple PRs)
- `## Risks and limitations`

When `## PR Roadmap` is present:
- The section lives in the plan root file.
- Each phase and each execution-status step must include a `**[PR-X]**` tag.

#### Integration strategy table (mandatory)

The roadmap MUST open with:
1. A one-line summary stating the total number of PRs.
2. A **Merge strategy** declaration.
3. An integration table with these exact columns:

| Column | Content |
|---|---|
| PR | PR identifier (`PR-1`, `PR-2`, ...) |
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
   > | PR-1 | P1-A through P2-C | ... | ... |
   > | PR-2 | P3-A through P5-A | ... | ... |
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

### Plan-start requirement

- The plan must receive explicit go/no-go from the user before execution.
- On first execution, mandatory plan-start choices defined in `plan-execution-protocol.md` apply.

---

## 2. Plan Scope Principle (Hard Rule)

Plans contain only product/engineering/documentation outcomes.
Operational actions are never executable plan steps.

| Valid plan step | Invalid plan step |
|---|---|
| "Implement owner_address normalization and tests" | "Commit and push" |
| "Run benchmark and record delta evidence" | "Create PR" |
| "Document feature behavior in wiki (or no-doc-needed rationale)" | "Merge PR" |

### Operational actions policy

- `commit`, `push`, `create/update PR`, `merge`, and post-merge cleanup are execution protocol behavior, not plan tasks.
- A plan may include commit recommendations inline, but these are guidance, not checkboxes.

### Required inline commit recommendation format

When relevant, include commit guidance under the implementation step:

- **When:** after which concrete step(s).
- **Scope:** intended files/areas.
- **Suggested message:** proposed commit message.
- **Expected validation:** minimum checks expected before commit.

This recommendation must not be represented as `CT-*`, `commit-task`, `create-pr`, or `merge-pr` checklist items.

### Commit checkpoint blockquote format

When a plan includes commit checkpoint recommendations, use this blockquote format:

> 📌 **Commit checkpoint — <Phase/group> complete.** Suggested message: `<type>(<scope>): <description>`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

Rules:
- Checkpoint blockquotes are guidance, not executable checklist items (consistent with the Plan Scope Principle).
- Place checkpoints after the last step of a logical group or phase.
- The suggested commit message must follow [way-of-working.md §3](../../shared/03-ops/way-of-working.md) conventions.
- The L2 reference is `scripts/ci/test-L2.ps1 -BaseRef main`.

---

## 3. Plan Documentation Task (Hard Rule)

Every active plan MUST include an explicit documentation task.

- If documentation is needed: create/update wiki docs.
- If not needed: close the task with `no-doc-needed` and a brief rationale.

When documentation is required, enforce:

- clear structure and readability,
- table of contents when the page is long enough to need one,
- Mermaid diagrams when they improve comprehension,
- applicable documentation skills/workflows available in the project.

---

## 4. Plan-File Commit Policy

- Do not create plan-only commits for routine status telemetry (checkbox toggles, in-progress markers).
- Plan updates during execution are allowed only for substantive scope/decision changes.
- The canonical plan archive commit is a single close-out commit when the plan moves to `completed/`.

---

## 5. Pull Request Policy in Plans

- A PR is required before merge.
- PR creation/update is user-triggered only.
- Plans must not include automatic PR creation tasks.
- During plan creation, the planning agent MUST estimate the required number of PRs and record that decision in `## PR Roadmap`.
- **PR-first planning order (hard rule):** When a plan may span multiple PRs, determine PR boundaries and record them in `## PR Roadmap` **before** writing `## Execution Status` and commit checkpoints. Post-hoc PR partitioning risks misaligned checkpoints and step-to-PR tag inconsistencies.

### PR sizing and split criteria (hard rule)

Thresholds are mandatory risk signals, not automatic split commands by themselves.

#### "Good PR" criteria

- One dominant objective (user story slice or technical concern).
- Risk remains bounded and reviewable in isolation.
- No mixed high-risk axes without explicit justification.

#### Mandatory mixed threshold assessment

Flag the plan for PR partition decision when any of these apply:

- Semantic threshold:
  - Significant backend and frontend changes in the same PR.
  - Schema/data migration in the same PR as feature behavior changes.
  - Public API/contract changes mixed with broad refactor.
  - Large structural refactor mixed with unrelated product behavior.
- Size guardrail threshold (approximate per PR diff):
   - **Code risk signal (partition trigger):** more than `400` code lines, or more than `15` code files.
   - **Review load signal (informational):** more than `800` total reviewable lines (code + docs + config). This does not trigger partitioning by itself.
   - Docs-only and config-only changes do not count toward the code risk signal.

If uncertainty remains, default to smaller PR slices and document dependencies in `## PR Roadmap`.

#### PR partition gate (mandatory procedure)

Before finalizing a plan, the planning agent MUST run this gate and record the result in `## PR Roadmap`:

1. **Project scope per planned PR**
   - Estimate changed files and changed lines for each planned PR slice from planned phases/steps.
2. **Evaluate semantic risk axes**
   - Check whether each planned PR mixes high-risk axes (backend+frontend, migration+feature behavior, contract+broad refactor).
3. **Classify projected changes by bucket**
   - Estimate **code lines/files**, **doc lines**, and **config lines** for each planned PR slice.
4. **Evaluate size guardrails**
   - Check whether projected scope exceeds the **code risk signal** (`400` code lines or `15` code files).
   - If projected total reviewable lines exceed `800`, note high review load in the roadmap rationale without forcing partition by size alone.
5. **Open decision gate with user (hard gate)**
   - If semantic or size thresholds are exceeded, the planning agent MUST present two options:
     - `Option A`: keep a single PR with explicit rationale (for example, mechanical/cohesive low-risk changes).
     - `Option B`: split into multiple PRs with proposed boundaries and dependencies.
   - The user must explicitly choose A or B before plan approval.
6. **Record evidence in roadmap**
   - Add a short note per PR with projected size/risk, selected option, and rationale.

Execution-time safeguard:
- Before opening or updating a PR, re-evaluate the same thresholds using the real branch diff.
- If exceeded, open the same hard gate with the user (Option A single-PR exception or Option B split) and proceed only after explicit confirmation.

---

## 6. Prompt Strategy

### Prompt types

- Pre-written prompts (Prompt Queue): authored at iteration start for tasks that do not depend on prior outputs.
- Just-in-time prompts (Active Prompt): authored when a task depends on earlier results.

### Prompt creation lifecycle

| Operation | Who | When |
|---|---|---|
| Create (pre-written) | Planning agent | At iteration start, in Prompt Queue |
| Create (just-in-time) | Planning agent | Before the dependent step, in Active Prompt |

