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

- Plan folder naming convention: `PLAN_<YYYY-MM-DD>_<SLUG>`
- Active plan location: `docs/projects/veterinary-medical-records/04-delivery/plans/<plan-folder>/`
- Canonical root file inside the plan folder: `PLAN_<YYYY-MM-DD>_<SLUG>.md` (must match the folder name)
- Legacy compatibility: plans that still use the legacy root-file naming remain readable during the transition period. New plans MUST use the folder-matching name.
- Optional per-PR annex files: `PR-1.md`, `PR-2.md`, ...
- Completed plans location: `docs/projects/veterinary-medical-records/04-delivery/plans/completed/<plan-folder>/`

### Required plan template

Every new plan MUST include:

1. Create plan folder: `plans/<plan-folder>/`.
2. Create root file: `plans/<plan-folder>/PLAN_<YYYY-MM-DD>_<SLUG>.md` (matching the folder name).
3. Title: `# Plan: <name>`
4. Operational rules pointer: `> **Operational rules:** See [plan-execution-protocol.md](...)`
5. Metadata:
   - `**Branch:**`
   - `**PR:**` — Use `Pending (PR created on explicit user request)` as placeholder.
   - `**User Story:**`
   - `**Prerequisite:**`
   - `**Worktree:**`
   - `**CI Mode:**`
   - `**Automation Mode:**` — one of `Supervisado`, `Semiautomatico`, `Automatico`
6. `## Context`
7. `## Objective`
8. `## Scope Boundary`
9. `## Execution Status`
10. `## Prompt Queue`
11. `## Active Prompt`
12. `## Acceptance criteria`
13. `## How to test`

Optional sections:

- `## Design decisions`
- `## PR Roadmap` (mandatory when a plan spans multiple PRs)
- `## Risks and limitations`

When `## PR Roadmap` is present:
- The section lives in the plan root file.
- Each phase and each execution-status step must include a `**[PR-X]**` tag.
- If a PR requires implementation detail that would bloat the plan root file, create/update `PR-X.md` annex files in the same folder and link them from the roadmap.

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
  - More than `400` changed lines, or
  - More than `15` changed files.

If uncertainty remains, default to smaller PR slices and document dependencies in `## PR Roadmap`.

#### PR partition gate (mandatory procedure)

Before finalizing a plan, the planning agent MUST run this gate and record the result in `## PR Roadmap`:

1. **Project scope per planned PR**
   - Estimate changed files and changed lines for each planned PR slice from planned phases/steps.
2. **Evaluate semantic risk axes**
   - Check whether each planned PR mixes high-risk axes (backend+frontend, migration+feature behavior, contract+broad refactor).
3. **Evaluate size guardrails**
   - Check whether projected scope exceeds `400` changed lines or `15` changed files for any planned PR.
4. **Open decision gate with user (hard gate)**
   - If semantic or size thresholds are exceeded, the planning agent MUST present two options:
     - `Option A`: keep a single PR with explicit rationale (for example, mechanical/cohesive low-risk changes).
     - `Option B`: split into multiple PRs with proposed boundaries and dependencies.
   - The user must explicitly choose A or B before plan approval.
5. **Record evidence in roadmap**
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

