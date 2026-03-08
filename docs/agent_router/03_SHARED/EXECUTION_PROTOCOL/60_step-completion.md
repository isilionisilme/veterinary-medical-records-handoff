<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 8. Step Completion Integrity (Hard Rules)

### NO-BATCH
**Prohibited: batching unrelated plan steps in a single commit.**

Commits must remain coherent to the currently closed implementation step(s) and their validated scope.

### CI Mode 2 — Pipeline Execution (Depth-1)

**Core principle:** Do not wait for CI between auto-chain steps. After pushing the commit bundle defined by the active implementation step scope, immediately start the next implementation step. CI is checked *before starting* step N+2, keeping a maximum pipeline depth of 1.

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
4. **Always run the targeted preflight level** for the active step scope before committing.
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
