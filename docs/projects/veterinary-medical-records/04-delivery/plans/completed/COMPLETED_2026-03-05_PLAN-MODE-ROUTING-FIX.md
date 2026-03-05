# Plan: Plan-Mode Routing Fix

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit-task schema, and handoff rules.

**Branch:** `docs/plan-mode-routing-fix`
**PR:** `#207`
**Prerequisite:** `main` estable.
**Worktree:** `D:/Git/veterinary-medical-records`
**CI Mode:** 2 — Pipeline depth-1 gate
**Agents:** Codex 5.3

## Context

When an agent executes a plan and the user issues an ad-hoc git command ("commit y push"), the agent may skip SCOPE BOUNDARY because `AGENTS.md` only triggers the plan execution protocol on continuation intent ("Continúa", "continue", etc.). The agent follows the generic commit discipline route instead of loading `plan-execution-protocol.md`, so it never sees SCOPE BOUNDARY, EVIDENCE BLOCK, STEP-LOCK, or PLAN-UPDATE-IMMEDIATE.

Root cause: the routing layer (`AGENTS.md`) has a narrow trigger — continuation intent only. Ad-hoc git commands during active plan execution fall through to generic WAY_OF_WORKING modules.

## Objective

- Any git operation request during active plan execution triggers the plan execution protocol.
- SCOPE BOUNDARY §13 and Atomic Iterations §2 explicitly state they govern all git operations during plan mode.
- Zero new rules added; only activation signals and governance clarifications.

## Scope Boundary (strict)

- **In scope:** `AGENTS.md` trigger expansion, `plan-execution-protocol.md` §2 and §13 activation signals.
- **Out of scope:** `way-of-working.md`, `MANIFEST.yaml`, router files (regenerated automatically), golden-loop worktree.

## Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Where to fix | Routing layer (`AGENTS.md`) + protocol internals (§2, §13) | The routing gap is the primary failure; internal signals are defense-in-depth |
| New rules? | No — activation signals only | Adding more rules to solve non-compliance of existing rules is counterproductive |
| `way-of-working.md` changes | None | Plan execution rules belong in the protocol, not in the general workflow doc |

## Commit plan

| # | Commit message | Files touched | Step |
|---|---|---|---|
| C1 | `docs(ops): widen plan-execution trigger in AGENTS.md and add activation signals` | `AGENTS.md`, `docs/projects/.../03-ops/plan-execution-protocol.md` | F1-A |

## Operational override steps

### CT-1 — Commit implementation

- `type`: `commit-task`
- `trigger`: after F1-A is `[x]`
- `preconditions`: L1 preflight green, router drift check passes
- `commands`:
  - `git add AGENTS.md docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`
  - `git commit -m "docs(ops): widen plan-execution trigger in AGENTS.md and add activation signals"`
  - `git push origin docs/plan-mode-routing-fix`
- `approval`: `auto`
- `fallback`: if commit fails, re-run formatters and retry once

## Execution Status

### Phase 1 — Routing fix

- [x] F1-A 🔄 — **Apply 3 edits** — (1) Widen `AGENTS.md` plan execution trigger to cover ad-hoc git operations, (2) Add plan-mode governance hard rule to §2 Atomic Iterations, (3) Add activation rule callout to §13 SCOPE BOUNDARY. Single commit. — ✅ `6846a9fc`
- [x] F1-B 🔄 — **Commit-task CT-1** — Execute CT-1 per SCOPE BOUNDARY. — ✅ `0299c3a4`
- [x] F1-C 🔄 — **Regenerate router files** — Run `python scripts/docs/generate-router-files.py` and verify with `--check`. Commit if files changed. — ✅ `no-commit (router files unchanged after regeneration)`

## Prompt Queue

### F1-A — Apply 3 edits

```text
Apply exactly these 3 edits to fix the plan-mode routing gap:

1. In `AGENTS.md`, section `## Plan execution (`Continúa`)`:
   - Change heading from `## Plan execution (`Continúa`)` to `## Plan execution`
   - Replace the first bullet:
     OLD: `- Load: `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`.`
     NEW:
     ```
     - **Trigger:** continuation intent ("Continúa", "continue", "go", "proceed", "resume") OR any git operation request (commit, push, branch, merge) while a `PLAN_*.md` is attached or referenced in the conversation.
     - Load: `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`.
     ```

2. In `plan-execution-protocol.md`, section `## 2. Atomic Iterations`, append after the existing paragraph:

   ```
   **Plan-mode governance (hard rule):** While a plan is active, all git operations (commit, push, branch) are governed by this protocol. Ad-hoc user requests that imply git operations are interpreted through the lens of the active plan step and routed to SCOPE BOUNDARY (§13). There is no "just commit and push" shortcut.
   ```

3. In `plan-execution-protocol.md`, section `## 13. SCOPE BOUNDARY Procedure`, insert before "Execute these steps **IN THIS EXACT ORDER**:":

   ```
   > **Activation rule:** Any commit or push during active plan execution MUST go through this procedure. If the user requests "commit", "push", or any git operation while a plan step is active, treat it as a SCOPE BOUNDARY trigger — not as an isolated command.
   ```

Validation:
- Run `scripts/ci/test-L1.ps1 -BaseRef HEAD` to verify formatting/linting.
- Run `python scripts/docs/generate-router-files.py --check` to verify no unexpected router drift.

Do NOT edit any other files.
```

⚠️ AUTO-CHAIN → F1-B (commit-task CT-1)

### F1-B — Commit-task CT-1

Execute CT-1 per SCOPE BOUNDARY (§13 of plan-execution-protocol.md).

⚠️ AUTO-CHAIN → F1-C

### F1-C — Regenerate router files

```text
Run the router regeneration script and verify no drift:

1. `python scripts/docs/generate-router-files.py`
2. `python scripts/docs/generate-router-files.py --check`
3. If files changed, commit: `docs(router): regenerate after plan-mode routing fix`
4. If no files changed (expected — plan-execution-protocol.md is loaded via reference pointer, not extracted), confirm and note in evidence.
```

## Active Prompt

_Empty._

## Acceptance criteria

1. An agent receiving "commit y push" while a `PLAN_*.md` is in conversation context will load `plan-execution-protocol.md` before acting.
2. §2 explicitly states all git ops during plan mode are governed by the protocol.
3. §13 explicitly states it activates on any commit/push request during active plan execution.
4. No changes to `way-of-working.md`, `MANIFEST.yaml`, or router files (beyond regeneration).
5. Router drift check passes.

## How to test

1. Open a new chat with a `PLAN_*.md` attached.
2. Write "commit y push" (without "Continúa").
3. Verify the agent loads `plan-execution-protocol.md` and routes to SCOPE BOUNDARY instead of executing a bare commit.
