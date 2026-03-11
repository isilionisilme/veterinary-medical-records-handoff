---
agent: agent
description: Create or update a pull request using the canonical PR workflow.
---

1. Run this workflow only when the user explicitly requests Pull Request creation or update.
2. Confirm repository state first: current branch, base branch, and working tree. Every user story or technical change requires at least one Pull Request, but PR creation or update is always user-triggered.
3. Use the canonical title conventions: `Story <ID> — <Full User Story Title>` for user stories, and `<type>: <short description>` for technical work.
4. Write Pull Request title, body, and review comments in English. When using CLI, pass real multiline body content via `--body-file` or a PowerShell here-string; never use escaped `\n` sequences.
5. Classify the Pull Request by file type before proceeding:

| Type | File patterns |
|---|---|
| **Docs-only** | `docs/**`, `*.md`, `*.txt`, `*.rst`, `*.adoc` only |
| **Code** | Any `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.css`, `*.scss`, `*.html`, `*.sql` |
| **Non-code, non-doc** | `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.env` |

6. Before opening or updating the PR, run the Pre-PR Commit History Review: inspect the feature-branch history, ensure commits are coherent and scoped, messages follow conventions, and no unrelated refactors or accidental changes appear. If history is messy, fix it before the PR.
7. Run the PR partition gate with real diff evidence: compute size against base, classify code/doc/config lines, assess semantic risk axes, and open a user decision gate if code lines exceed `400`, code files exceed `15`, or a high-risk axis mix lacks split rationale.
8. If the partition threshold is exceeded, present `Option A`: keep a single PR with explicit rationale, and `Option B`: split into additional PRs with proposed boundaries and dependencies. Without explicit user selection, STOP.
9. When the user requests PR creation or update, follow the procedure: create or update the PR targeting `main`, apply required preflight before PR work, check CI status, include end-user validation steps when applicable, and update an existing PR instead of creating a duplicate.
10. For Pull Requests that change `frontend/**` or user-visible behavior, review canonical UX and brand guidance first and add a `UX/Brand compliance` section to the PR description.
11. Before requesting merge, if the PR contains code changes and no code review has been performed, ask whether review should be done and include a recommended review depth with brief justification.
12. After the Pull Request is merged, run post-merge cleanup automatically: ensure the working tree is clean, clean related stashes where safe, switch to `main` and pull latest changes, delete the local branch safely, and attempt remote branch deletion while reporting non-fatal failures.