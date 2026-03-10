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
5. If `**Branch:**` was missing in the plan file, the agent must have already created and recorded it in STEP 0. Verify the field is populated before proceeding.

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
4. **Move plan file to completed archive** — `git mv plans/<plan-file> plans/completed/<plan-file>`.
  Keep the file name unchanged to preserve links.
5. **DOC_UPDATES normalization** — For qualifying `.md` files only.
6. **Commit + push** — `docs(closeout): archive <plan-slug> and backlog artifacts` on the feature branch.
7. **Wait for CI green** on the close-out commit.
8. **Mirror to docs repository** — If applicable.

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

### Merge (Automatic, After Close-Out)

Only after close-out is committed and CI is green:
1. Confirm PR is mergeable (CI green, no conflicts).
2. Squash merge: `gh pr merge <number> --squash --delete-branch`.
3. Switch to main, pull, delete local branch, clean stashes.

---
