---
agent: agent
description: Resolve plan-start choices and record snapshot.
---

1. Read the plan file and inspect `Branch`, `Worktree`, `Execution Mode`, and `Model Assignment`. If any field is blank or still contains `PENDING PLAN-START RESOLUTION`, `PENDING USER SELECTION`, `Pending`, or equivalent unresolved wording, suspend normal execution and complete plan-start first.
2. Until the snapshot commit exists, do only plan-start work: read the plan/protocol, inspect repository safety state, list or resolve worktrees, create/select the execution branch, ask mandatory plan-start questions, update the plan file, run L1, and commit the snapshot. Do not edit implementation files or run implementation-targeted tests.
3. Resolve `Branch` automatically only when it has a single unambiguous answer from the current execution context; otherwise ask. Resolve `Worktree` automatically only when the current active workspace makes it unambiguous; otherwise list all worktrees first and offer using an existing worktree or creating a new one.
4. `Execution Mode` always requires explicit user selection unless already recorded. Present these options and do not start step 1 without a choice:

| Mode | Per-task gate | Per-checkpoint gate | Commit | Push | Hard-gates (🚧) | Max retries |
|---|---|---|---|---|---|---|
| **Supervised** | L2 | L3 | Manual (user approval) | Manual | User decides | 2 |
| **Semi-supervised** | L1 | L2 | Manual (user approval) | Manual | User decides | 2 |
| **Autonomous** | L2 | L3 | Automatic | Automatic | Agent decides (documented) | 10 |

5. Apply the selected mode exactly:
	- `Supervised`: after each task run `scripts/ci/test-L2.ps1 -BaseRef main`; at `📌` checkpoints run `scripts/ci/test-L3.ps1 -BaseRef main`; commit and push require explicit user approval.
	- `Semi-supervised`: after each task run `scripts/ci/test-L1.ps1 -BaseRef HEAD`; at `📌` checkpoints run `scripts/ci/test-L2.ps1 -BaseRef main`; commit and push require explicit user approval.
	- `Autonomous`: after each task run `scripts/ci/test-L2.ps1 -BaseRef main`; at `📌` checkpoints run `scripts/ci/test-L3.ps1 -BaseRef main`; commit and push are automatic after tests pass; hard-gates are agent-decided unless marked `🚧🔒 NEVER-SKIP`.
6. `Model Assignment` always requires explicit user selection unless already recorded. Present these options and record exactly one:
	- `Default` — Planning agent uses the most-capable available model; Execution agent uses the standard-cost model.
	- `Uniform` — Both roles use the standard-cost model.
	- `Custom` — User specifies which model to use for each role.
7. Keep execution in the current chat by default. Recommend a chat switch only for significant token-efficiency benefit or a hard capability blocker, and wait for explicit user decision. If context exhaustion appears, stop cleanly at the current step and hand off.
8. Record all resolved values in the plan file. If any placeholder remains after editing, STOP. Use the exact record formats `**Execution Mode:** <selected-mode>` and `**Model Assignment:** <selected-mode>`.
9. Before the snapshot commit, verify that `**Branch:**`, `**Worktree:**`, `**Execution Mode:**`, and `**Model Assignment:**` all contain resolved non-placeholder values. Then run `scripts/ci/test-L1.ps1 -BaseRef HEAD`.
10. If the required L1 preflight fails, fix within plan-start scope and retry up to the active mode limit; on exceeding the retry limit, STOP and report.
11. Commit with `docs(plan): record plan-start choices for <plan-slug>`. Never amend the plan-start snapshot; it is the execution baseline.
12. Tell the user plan-start is complete, report the chosen `Execution Mode` and `Model Assignment`, and continue in the same chat unless a justified switch was approved.
