<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 1. Starting New Work (Branch First)

Before making any new changes (code, docs, config, etc.), create a new branch off the appropriate base (default: `main`) using the branch naming conventions defined below.

**STOP** and ask for confirmation only if the repository state is unsafe or ambiguous (examples: uncommitted changes, merge/rebase in progress, conflicts, or it is unclear whether the current branch already corresponds to the intended work item).

### Procedure

1. Confirm repository state is safe:
   - Working tree is clean (no uncommitted changes).
   - No merge/rebase in progress.
   - If not safe, STOP and ask before proceeding.
2. Ensure the correct base branch:
   - Default base is `main` unless the user explicitly specifies another base.
   - Switch to base and update it (`git switch main` then `git pull origin main`).
3. Create the branch before editing any files:
   - If already on a correctly named branch for the same work item, proceed.
   - Otherwise, build `<branch-name>` using the canonical format `codex/<worktree>/<category>/<slug>` and create it from the updated base (`git switch -c <branch-name>`).
   - Derive `worktree` from the current repository top-level folder name.
   - category mapping defined in Section 1.
   - user story -> `feature`
   - user-facing improvement -> `improvement`
   - technical work -> `fix`, `docs`, `chore`, `refactor`, or `ci`
   - If it is ambiguous whether the current branch is the correct work branch, STOP and ask.

---
