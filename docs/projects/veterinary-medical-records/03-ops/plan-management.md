# Plan Management

> **Project-specific operational document.**
> Defines how plans are created, structured, and executed in the `veterinary-medical-records` project.
> For step-level execution mechanics, see [`plan-execution-protocol.md`](plan-execution-protocol.md).

---

## 1. How to Create a Plan

Create a plan when work requires coordinated multi-step delivery, multiple commits, explicit hard-gates, or assignment between planning and execution roles. A trivial one-step change with no sequencing or gating does not require a `PLAN_*.md` file.

### Ownership

- The planning agent owns plan authoring and plan updates.
- Execution agents consume the plan and implement steps; they do not redefine authoring rules.

### Naming and location

- Naming convention: `PLAN_<YYYY-MM-DD>_<SLUG>.md`
- Location: `docs/projects/veterinary-medical-records/04-delivery/plans/`

### Required plan template

Every new plan MUST include:

1. Title: `# Plan: <name>`
2. Operational rules pointer: `> **Operational rules:** See [plan-execution-protocol.md](...)`
3. Metadata:
	- `**Branch:**`
	- `**PR:**` — Use `Pending (branch PR not created yet)` as placeholder until the PR exists.
	- `**User Story:**` — Markdown link to the related US in `implementation-plan.md` (e.g., `[US-78](../implementation-plan.md#us-78)`). If the plan covers multiple stories, list all of them.
	- `**Prerequisite:**`
	- `**Worktree:**`
	- `**CI Mode:**`
	- `**Agents:**`
4. `## Context`
5. `## Objective`
6. `## Scope Boundary`
7. `## Commit plan`
8. `## Operational override steps`
9. `## Execution Status`
10. `## Prompt Queue`
11. `## Active Prompt`
12. `## Acceptance criteria`
13. `## How to test`

Optional sections:

- `## Design decisions`
- `## PR Roadmap` (mandatory when a plan spans multiple PRs)
- `## Risks and limitations`

### Approval to start execution

- The plan must receive explicit go/no-go from the user before execution.
- On first execution, mandatory plan-start choices defined in `plan-execution-protocol.md` still apply.

---

## 2. How to Execute a Plan

Execution rules live exclusively in [`plan-execution-protocol.md`](plan-execution-protocol.md).

This file intentionally contains no execution-time behavior, chaining logic, CI gating behavior, or handoff procedures.

---

## 3. Task Chaining Policy

Task chaining policy is part of execution behavior and is defined in [`plan-execution-protocol.md`](plan-execution-protocol.md).

---

## 5. Plan Scope Principle (Hard Rule)

**Plans contain ONLY product/engineering tasks and well-defined operational override steps.** Generic or unscoped operational mentions are NEVER plan steps.

| Valid plan step | Operational Override Step (allowed) | NOT a plan step (generic) |
|---|---|---|
| "Add Playwright smoke test for upload flow" | `commit-task`: Commit F1-1 + F1-2 (scope, message, push defined) | "Commit and push" (unscoped) |
| "Configure CI job for E2E tests" | `create-pr`: Create draft PR for iteration branch | "Create PR" (unscoped) |
| "Add data-testid attributes to components" | `merge-pr`: Squash-merge PR #42 after user approval | "Merge PR" (unscoped) |

### Operational Override Steps

Certain operational actions (commits, PRs, merges) are allowed as plan steps only when they follow the strict schema below. Generic mentions without the required fields are rejected.

#### Required schema

Each operational override step in `PLAN_*.md` MUST include:

| Field | Description | Required |
|---|---|---|
| `type` | One of: `commit-task`, `create-pr`, `merge-pr` | Yes |
| `trigger` | When this step executes (e.g., "after F1-1 and F1-2") | Yes |
| `preconditions` | What must be true before execution (e.g., "CI green for all prior steps") | Yes |
| `commands` | Exact command set to execute | Yes |
| `approval` | `auto` or `explicit-user-approval` | Yes |
| `fallback` | What to do if execution fails | Yes |

#### Approval rules

- `commit-task`: approval value MUST be `auto`.
- `create-pr`: approval value MUST be `auto`.
- `merge-pr`: approval value MUST be `explicit-user-approval`.

#### Validation

At authoring time, the planning agent MUST ensure every operational override step includes all required fields before the plan is handed off for execution.

### Commit Task Specification (Mandatory at Plan Creation)

When generating `PLAN_*.md`, the planning agent MUST define explicit commit tasks as first-class plan steps.

Each commit task MUST include:

1. **Trigger point** - when the commit task is executed (for example: after steps `F1-1` and `F1-2`).
2. **Scope** - exact files and/or step IDs included in that commit.
3. **Commit message** - exact message to use.
4. **Push expectation** - whether the commit is pushed immediately or grouped with a later plan-update commit.

Authoring constraint:

- The planning agent MUST define commit tasks explicitly before execution starts.
- If commit scope/message must change, the planning agent updates the plan first, then execution continues from the updated plan.

---

## 6. Prompt Strategy

### Prompt types

- **Pre-written prompts** (Prompt Queue): written by the planning agent at iteration start for tasks whose content does not depend on prior results.
- **Just-in-time prompts** (Active Prompt): written by the planning agent when a task depends on a prior task's result.

### Prompt creation lifecycle

| Operation | Who | When |
|---|---|---|
| **Create** (pre-written) | Planning agent | At iteration start, in Prompt Queue |
| **Create** (just-in-time) | Planning agent | Before the step that needs it, in Active Prompt |
