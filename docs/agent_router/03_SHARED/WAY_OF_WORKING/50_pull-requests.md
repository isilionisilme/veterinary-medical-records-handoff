<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 4. Local Preflight Levels

Use the local preflight system with three levels before pushing changes.

### L1 — Quick (before commit)

- Entry points: `scripts/ci/test-L1.ps1` / `scripts/ci/test-L1.bat`
- Purpose: catch obvious lint/format/doc guard failures with minimal delay.

### L2 — Push (before every push)

- Entry points: `scripts/ci/test-L2.ps1` / `scripts/ci/test-L2.bat`
- Frontend checks run only when frontend-impact paths changed, unless `-ForceFrontend` is provided.
- Enforced by git hook: `.githooks/pre-push`.

### L3 — Full (before Pull Request creation)

- Entry points: `scripts/ci/test-L3.ps1` / `scripts/ci/test-L3.bat`
- Runs path-scoped backend/frontend/docker checks by default.
- Use `-ForceFull` to execute full backend/frontend/docker scope regardless of diff.
- Use `-ForceFrontend` to force frontend checks even when frontend-impact paths did not change.
- E2E runs only for frontend-impact changes, unless `-ForceFrontend` or `-ForceFull` is provided.

### Preflight Rules

- For interactive local commits, run **L1** by default.
- Before every `git push`, **L2** must run (automatically via pre-push hook).
- Before opening a Pull Request, run **L3**.
- Before PR creation/update, run **L3**.
- After the Pull Request exists, rely on its CI for subsequent updates unless an explicit local rerun is requested.
- L3 runs path-scoped by default for day-to-day development branches.
- Before merge to `main`, verify CI is green.
- If a level fails, **STOP** and resolve failures (or explicitly document why a failure is unrelated/pre-existing).

### Preflight Auto-Fix Policy

Auto-fix policy when preflight fails: apply focused fixes and rerun the same level.
Maximum automatic remediation loop: 2 attempts.

When a preflight level (L1/L2/L3) fails:

- AI assistants must attempt focused fixes automatically before proceeding.
- Auto-fixes must stay within the current change scope and avoid unrelated refactors.
- Maximum automatic remediation loop: **2 attempts** (fix + rerun the failed level).
- **Never bypass quality gates** (`--no-verify`, disabling tests/checks, weakening assertions) to force a pass.
- If failures persist after the limit, STOP and report root cause, impacted files, and next-action options.

---

## 5. Pull Request Workflow

- Every user story or technical change requires **at least one Pull Request**. A single story or change may be split across multiple Pull Requests when the scope justifies it.
- Pull Requests are opened once the change (or the slice covered by that Pull Request) is **fully implemented** and **all automated tests are passing**.
- Each Pull Request must be small enough to be reviewed comfortably in isolation and should focus on a **single user story or a single technical concern**.
- Pull Request creation/update is always explicit user-triggered.

### Pull Request Title Conventions

**User stories:**
- `Story <ID> — <Full User Story Title>`

**Technical work:**
- `<type>: <short description>`

### Pull Request Body Requirements

- Pull Request title, body, and review comments must be written in **English**.
- When setting the Pull Request description/body from CLI, use real multiline content (heredoc or file input), not escaped `\n` sequences.
- Preferred patterns:
  - `gh pr create --body-file <path-to-markdown-file>`
  - PowerShell here-string assigned to a variable and passed to `--body`

### Pull Request Classification

Classify the Pull Request by file types:

| Type | File patterns |
|------|--------------|
| **Docs-only** | `docs/**`, `*.md`, `*.txt`, `*.rst`, `*.adoc` only |
| **Code** | Any `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.css`, `*.scss`, `*.html`, `*.sql` |
| **Non-code, non-doc** | `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.env` |

### Pre-PR Commit History Review (Hard Rule)

Before opening or updating a Pull Request, the agent MUST review the commit history on the feature branch to ensure:

- Commits are coherent and scoped to single logical changes.
- Commit messages follow conventions (`Story <ID>: ...` or `<type>: ...`).
- No unrelated refactors or accidental changes appear in any commit.
- Commit history is readable and supports reasoning and review.

If issues are found, amend, reorder, or squash commits before opening the PR.

### Pull Request Procedure

When the user explicitly requests Pull Request creation or update, an AI coding assistant or automation tool must follow this procedure automatically:

1. Confirm repository state (branch, base, working tree).
2. Create/update the Pull Request targeting `main`.
3. Apply the preflight rules from Section 4 before Pull Request creation and for subsequent updates.
4. Check CI status (pending, passing, or failing).
5. For Pull Requests that change `frontend/**` or user-visible behavior:
   - Review canonical UX/brand sources before implementation/review.
   - Add a `UX/Brand compliance` section to the Pull Request description.
6. Include end-user validation steps when applicable.
7. Before requesting merge, if the Pull Request includes code changes and no code review has been performed, ask the user whether a review should be done. Include a recommended review depth (see Section 6 — Review Depth) with a brief justification.

### PR Partition Gate (hard rule)

Before creating or updating a Pull Request, the agent MUST run the partition gate with real diff evidence:

1. Compute diff size against PR base:
   - `git diff --shortstat <base_ref>...HEAD`
   - `git diff --name-only <base_ref>...HEAD`
2. Evaluate semantic risk axes in the pending PR scope:
   - significant backend + frontend in one PR,
   - migration + feature behavior in one PR,
   - public contract changes + broad refactor in one PR.
3. Classify changed lines into buckets using the **Pull Request Classification** table:
    - **Code lines**: files matching the `Code` type.
    - **Doc lines**: files matching the `Docs-only` type.
    - **Config lines**: files matching the `Non-code, non-doc` type.
4. Apply thresholds using two independent signals:
    - **Code risk signal (partition trigger):** exceeded when code lines > `400` or code files > `15`. Doc-only and config-only lines are excluded.
    - **Review load signal (informational):** when total reviewable lines (code + docs + config) exceed `800`, note high review load in the PR description. Does NOT trigger the partition gate.
    - **Semantic threshold:** exceeded if any high-risk axis mix is present without explicit split rationale.
5. Open user decision gate when thresholds are exceeded:
   - Present `Option A`: keep single PR with explicit rationale.
   - Present `Option B`: split into additional PRs with proposed boundaries/dependencies.
   - Require explicit user selection before proceeding.
6. Enforce selected outcome:
   - If user selects `Option A`, proceed with one PR and include rationale.
   - If user selects `Option B`, split and proceed with the agreed PR set.
   - Without explicit selection, STOP.
7. Record evidence:
   - Include size metrics, semantic assessment, selected option, and rationale in plan `PR Roadmap` notes or PR description rationale.

### Plan-Level Pull Request Roadmap

Compatibility note: this section is also referenced as **Plan-level PR Roadmap** in legacy router contracts.

When a plan spans multiple Pull Requests, it must include a **Pull Request Roadmap** section:
- Table with columns: **Pull Request**, **Branch**, **Phases**, **Scope**, **Depends on**.
- The planning agent must estimate PR count during plan creation and record it in the roadmap before execution starts.
- Each phase belongs to exactly one Pull Request.
- Each phase belongs to exactly one PR.
- Each execution step carries a `**[PR-X]**` tag.
- Each execution step in the Execution Status must carry a `**[PR-X]**` tag.
- A Pull Request is merged only when all its assigned phases pass CI and user review.

PR split threshold (mandatory, mixed model):
- Semantic and size thresholds are mandatory risk signals.
- Exceeding a threshold triggers the user decision gate above; it does not force automatic split without user confirmation.
- If uncertain, default to smaller PR slices and declare dependencies in the roadmap.

### Post-Merge Cleanup Procedure

After a Pull Request is merged into `main`, the AI assistant must run this cleanup automatically:
1. Ensure the working tree is clean.
2. Check for stashes related to the merged branch; clean up where safe.
3. Switch to `main` and pull latest changes.
4. Delete the local branch (safe deletion first; force-delete only if verified no unique commits).
5. Attempt to delete the remote branch (`git push origin --delete <branch-name>`). If it fails because the branch is missing, protected, or you lack permissions, report it and continue cleanup.

---
