<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 5. Pull Request Workflow

- Every user story or technical change requires **at least one Pull Request**. A single story or change may be split across multiple Pull Requests when the scope justifies it.
- Pull Requests are opened once the change (or the slice covered by that Pull Request) is **fully implemented** and **all automated tests are passing**.
- Each Pull Request must be small enough to be reviewed comfortably in isolation and should focus on a **single user story or a single technical concern**.

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

### Pull Request Procedure

1. Confirm repository state (branch, base, working tree).
2. Create/update the Pull Request targeting `main`.
3. Apply the preflight rules from Section 4 before Pull Request creation and for subsequent updates.
4. Check CI status (pending, passing, or failing).
5. For Pull Requests that change `frontend/**` or user-visible behavior:
   - Review canonical UX/brand sources before implementation/review.
   - Add a `UX/Brand compliance` section to the Pull Request description.
6. Include end-user validation steps when applicable.
7. Before requesting merge, if the Pull Request includes code changes and no code review has been performed, ask the user whether a review should be done. Include a recommended review depth (see Section 6 — Review Depth) with a brief justification.

### Plan-Level Pull Request Roadmap

Compatibility note: this section is also referenced as **Plan-level PR Roadmap** in legacy router contracts.

When a plan spans multiple Pull Requests, it must include a **Pull Request Roadmap** section:
- Table with columns: **Pull Request**, **Branch**, **Phases**, **Scope**, **Depends on**.
- Each phase belongs to exactly one Pull Request.
- Each phase belongs to exactly one PR.
- Each execution step carries a `**[PR-X]**` tag.
- Each execution step in the Execution Status must carry a `**[PR-X]**` tag.
- A Pull Request is merged only when all its assigned phases pass CI and user review.

### Post-Merge Cleanup Procedure

After a Pull Request is merged into `main`:
1. Ensure the working tree is clean.
2. Check for stashes related to the merged branch; clean up where safe.
3. Switch to `main` and pull latest changes.
4. Delete the local branch (safe deletion first; force-delete only if verified no unique commits).
5. Do NOT delete remote branches unless explicitly requested.

---
