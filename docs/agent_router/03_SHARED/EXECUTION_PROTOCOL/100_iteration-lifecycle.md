<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 14. Iteration Lifecycle Protocol

```
Branch creation → Plan steps → PR readiness → User approval → Close-out → Merge
  [automatic]     [SCOPE BOUNDARY]  [automatic]   [hard-gate]   [automatic]  [automatic]
```

### Branch Creation (Before Any Plan Step)
1. Read `**Branch:**` from the plan.
2. `git fetch origin`
3. Create from latest main: `git checkout -b <branch> origin/main`.
4. If branch exists remotely: checkout and pull.

### PR Creation (User-Triggered)
PR creation remains mandatory for delivery through review, but it is **not automatic**. The agent creates or updates a PR only when the user explicitly requests it. When created, record the PR number in the plan. If a PR already exists for the branch, update it instead of creating a new one.

### PR Readiness (Automatic)
When all steps are `[x]` and CI is green:
1. If a PR exists: update title/body/classification and report PR number + URL to user.
2. If no PR exists: STOP and ask the user whether to create it now (PR is required before merge).
3. **Hard-gate:** user decides when to merge.

### Iteration Close-Out Procedure (Pre-Merge)

> **Hard rule:** Close-out runs BEFORE the merge, on the feature branch itself. This avoids creating artificial close-out branches and PRs.

When user says "merge", execute close-out first:

1. **Verify clean working tree** and `git fetch --prune`.
2. **Plan reconciliation** — If any steps are `[ ]`, present each to user: Defer / Drop / Mark complete.
3. **Update IMPLEMENTATION_HISTORY.md** — Add timeline row and cumulative progress.
4. **Rename plan → completed archive** — `git mv` from active to `completed/`.
5. **DOC_UPDATES normalization** — For qualifying `.md` files only.
6. **Commit + push** — `docs(iter-close): iteration <N> close-out` on the feature branch.
7. **Wait for CI green** on the close-out commit.
8. **Mirror to docs repository** — If applicable.

### Merge (Automatic, After Close-Out)

Only after close-out is committed and CI is green:
1. Confirm PR is mergeable (CI green, no conflicts).
2. Squash merge: `gh pr merge <number> --squash --delete-branch`.
3. Switch to main, pull, delete local branch, clean stashes.

---
