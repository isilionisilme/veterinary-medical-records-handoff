# Pull Requests
- A pull request is opened for each user story or each technical non user-facing change (refactors, chores, CI, docs, fixes).
- Pull requests are opened once the change is fully implemented and all automated tests are passing.
- Each pull request must be small enough to be reviewed comfortably in isolation and should focus on a single user story or a single technical concern.

## Plan-level PR Roadmap

When a plan (`PLAN_*.md`) spans work large enough to require more than one Pull Request, the plan must include a **PR Roadmap** section that maps execution phases to PRs.

Rules:

- Add a `## PR Roadmap` section after the Scope Boundary and before the Estado de ejecución.
- The roadmap is a table with columns: **PR** (identifier or link), **Rama** (branch name), **Fases** (which plan phases it covers), **Alcance** (short description), **Depende de** (prerequisite PR).
- Each phase belongs to exactly one PR. A phase must **not** be split across PRs.
- Each execution step in the Estado de ejecución must carry a `**[PR-X]**` tag indicating which PR it belongs to.
- A PR is merged only when all its assigned phases pass CI and user review.
- The roadmap is written when the plan is created or when scope grows beyond a single PR. It may be updated as phases are completed.

## Pull Request Automation (AI Assistants)

When an AI coding assistant or automation tool is used to create or update a Pull Request in this repository, it must follow this procedure automatically. This operational rule complements the existing Pull Request and Code Review policies and does not replace them.

## Local preflight levels (operational default)

Apply these levels automatically at the corresponding moments:

- **L1 — Quick (before commit):** `scripts/ci/test-L1.ps1` (or `.bat`)
- **L2 — Push (before every push):** `scripts/ci/test-L2.ps1` (or `.bat`), enforced by `.githooks/pre-push`
- **L3 — Full (before PR creation/update):** `scripts/ci/test-L3.ps1` (or `.bat`)

Operational defaults:
- L2 and L3 are path-scoped for frontend: run frontend checks only when frontend-impact paths changed.
- `-ForceFrontend` forces frontend checks when no frontend-impact paths changed.
- `-ForceFull` forces full backend/frontend/docker scope for L3.
- Before merge to `main`, verify CI is green. Local L3 is not required when CI has already passed (CI runs a superset of L3 checks).

If the required level fails, STOP and resolve issues before continuing.

Auto-fix policy when preflight fails:
- Attempt focused fixes automatically before continuing.
- Keep fixes within current scope; avoid unrelated refactors.
- Maximum automatic remediation loop: 2 attempts (fix + rerun the failed level).
- Never bypass gates (`--no-verify`, disabled tests/checks, weakened assertions).
- If still failing after the limit, STOP and report root cause and next actions.

## Manual trigger only: Code reviews (precedence gate)

Code review execution is manual trigger only.
- Do not initiate code review steps from PR events/context unless the user explicitly asks.
- Explicit trigger examples: "Do a code review for PR #...", "Review the diff for ...", "Run a code review now".
- Starting a code review includes fetching PR review context, reading diffs for review, generating formal review output/comments, suggesting review commits, or running any multi-step review flow.
- If a review may be useful, you may propose it, but stop and wait for explicit user instruction.
- This gate overrides any automatic-review interpretation in this document.

## Pull Request Procedure

1) Confirm repository state before creating the PR:
   - Current branch name
   - Base branch (main)
   - Working tree status (report if not clean)

2) Create or update the Pull Request to `main` using the standard branching and naming conventions already defined in this document.
   - PR title, body, and review comments must be written in English.
   - When setting the PR description/body from CLI, use real multiline content (heredoc or file input), not escaped `\n` sequences.
   - Do not submit PR bodies that contain literal `\n`.
   - Preferred patterns:
     - `gh pr create --body-file <path-to-markdown-file>`
     - PowerShell here-string (`@' ... '@`) assigned to a variable and passed to `--body`

2.1) Run local L3 preflight before creating/updating the PR:
   - Use `scripts/ci/test-L3.ps1` (or `.bat`).
    - If L3 fails, STOP and fix or explicitly justify any accepted exception.

3) Check CI status (if configured):
   - Report whether CI is pending, passing, or failing.
   - Include end-user validation steps in the PR description when applicable; if not applicable, state why and provide alternative verification steps.

4) Classify the PR by file types (use changed file paths; do not require reading full diff content):
   - **Docs-only PR**: the diff contains **only**:
     - `docs/**`
     - `*.md`, `*.txt`, `*.rst`, `*.adoc`
   - **Code PR**: the diff contains **any** code file, such as:
     - `*.py`
     - `*.ts`, `*.tsx`
     - `*.js`, `*.jsx`
     - `*.css`, `*.scss`
     - `*.html`
     - `*.sql`
   - **Non-code, non-doc PR**: the diff contains files that are neither docs nor code (examples: `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.env`).

5) For PRs that change `frontend/**` or user-visible behavior/copy:
   - Load `docs/agent_router/02_PRODUCT/USER_VISIBLE/00_entry.md` before implementation/review.
   - Add a `UX/Brand compliance` section to the PR description with concrete evidence.

6) Code review gate:
   - Do not ask by default on every PR.
   - Run a review only when explicitly requested by the user.
   - For docs-only PRs, review remains skipped by policy unless the user explicitly requests one.

7) Perform a maintainability-focused code review of the PR diff (when user-approved):
   - Use `git diff main...HEAD` as the review input.
   - Apply all rules from:
     "Code Review Guidelines (Maintainability-Focused, Take-Home Pragmatic)"

## Pull Request review visibility

After producing a PR code review, the AI assistant must publish the review output as a comment in the Pull Request (or update an existing “AI Code Review” comment), using the mandatory review output format.

For `frontend/**` or user-visible changes, that PR review comment must include a dedicated `UX/Brand Compliance` section.

If one or more review findings are addressed in subsequent commits, the AI assistant must add a brief follow-up comment summarizing which findings were addressed.

If the PR changes after review (new commits that materially affect the diff), the AI assistant must add a follow-up comment summarizing what changed and whether the previous findings are still applicable.

If the AI assistant cannot post a comment to the Pull Request (for example due to missing PR reference, missing GitHub CLI access, or authentication), STOP and ask the user before proceeding. Do not treat chat-only output as satisfying the “publish to PR” requirement.

For docs-only PRs, no review comment is required (review is skipped by policy).

## Merge Execution + Post-merge Cleanup (AI Assistants)

This section supports two entry points:
- User already merged the PR manually and asks for cleanup.
- User asks the assistant to merge the PR (for example: "merge this PR").

If the user asks the assistant to merge the PR, execute merge and cleanup end-to-end in one flow.

Only STOP and ask for confirmation if the repository state is unsafe or ambiguous (examples: uncommitted changes, rebase/merge in progress, conflicts, or unclear stash purpose/ownership).

### When user asks "merge this PR"

1) Preconditions (must pass before merge):
   - Run local L3 preflight (`scripts/ci/test-L3.ps1` or `.bat`) and stop on failures.
   - Ensure working tree is clean (`git status`).
   - Sync refs and prune (`git fetch --prune`).
   - Verify PR is mergeable without bypassing protections:
     - required checks/CI are green,
     - required approvals are present,
     - no merge conflicts.

2) Merge strategy:
   - Default to squash merge unless user requests another strategy.
   - Use GitHub CLI merge command for the target PR.
   - If merge queue or pending-check flow requires auto-merge, use auto-merge mode.

3) Branch deletion authorization:
   - A direct user request to merge a PR is implicit authorization to delete that PR head branch as part of the merge flow.
   - Delete the PR head branch on remote and local after merge (for that PR only).
   - Do not delete any branch that is not the PR head branch.

4) Continue with the post-merge cleanup checklist below.

### Post-merge cleanup checklist

1) Ensure the working tree is clean:
   - If there are uncommitted changes, STOP and ask before proceeding.
   - If a merge/rebase is in progress, STOP and ask before proceeding.

2) Check for existing stashes:
   - List stashes (`git stash list`).
   - If a stash is clearly related to the merged branch and no longer needed, delete it (`git stash drop ...`).
   - If there is any ambiguity about a stash (purpose unclear, potentially still needed), STOP and ask before deleting it.

3) Switch to `main`.

4) Pull the latest changes from `origin/main` into local `main`.

5) Delete the branch used for the merged PR:
   - If the branch is currently checked out, switch to `main` first.
   - If this flow started from "merge this PR", delete remote and local PR head branch.
   - If this flow started after user-reported manual merge, default to deleting local branch only.
   - For local deletion, try safe deletion first: `git branch -d <branch>`.
   - If deletion fails due to "not fully merged" (common with squash merges):
     - Verify the branch has **no unique commits** relative to `main` (for example: `git log <branch> --not main`).
     - If there are no unique commits, it is safe to force delete: `git branch -D <branch>`.
     - If unique commits exist, STOP and ask what to do.
