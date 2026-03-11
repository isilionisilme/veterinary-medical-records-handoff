---
agent: agent
description: Start new work on a dedicated branch before editing files.
---

1. Use this workflow when the user starts new work, asks to create a branch, or when plan execution requires branch creation before edits.
2. Confirm repository state is safe before any new change: working tree clean, no merge or rebase in progress, no conflicts, and no ambiguity about whether the current branch already matches the intended work item. If unsafe or ambiguous, STOP and ask.
3. Ensure the correct base branch: default base is `main` unless the user explicitly names another base. Switch to the base branch and update it before creating a new work branch.
4. Create the branch before editing files. If already on the correctly named branch for the same work item, proceed; otherwise build `<category>/<slug>` and create it from the updated base.
5. Use this category mapping when choosing the branch prefix:

| Work type | Branch pattern |
|---|---|
| User story | `feature/<ID>-<short-representative-slug>` |
| User-facing improvement | `improvement/<short-slug>` |
| Technical work | `refactor/<short-slug>`, `chore/<short-slug>`, `ci/<short-slug>`, `docs/<short-slug>`, or `fix/<short-slug>` |

6. Apply slug rules exactly: lowercase letters, numbers, and hyphens only; concise and representative of the work item.
7. Respect branch strategy: use short-lived dedicated branches, keep `main` runnable and test-passing, and never commit directly to `main`.
8. If it is unclear whether the current branch is the right one, STOP and ask rather than guessing.