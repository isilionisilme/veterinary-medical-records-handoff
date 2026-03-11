<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 2. Branching Strategy

- The default branching strategy is **Feature Branching**.
- Work is developed in **short-lived branches** on top of a stable `main` branch.
- `main` always reflects a **runnable, test-passing state**.
- **No direct commits to `main`.** All changes must go through a feature branch and a pull request.
- Each change is implemented in a dedicated branch.
- Branches are merged once the change is complete and reviewed.

### Branch Naming Conventions

Branch names must follow category-specific patterns:

Canonical format:

- `codex/<worktree>/<category>/<slug>`

Category-specific branch patterns:

- Creation-time rule:
- During `Starting New Work`, the agent must derive and create branch names in canonical format.
- Use the category mapping defined in Section 1.
- Canonical branch naming uses the category segment from the patterns listed below.
- Legacy format `<worktree>/<category>/<slug>` is temporarily allowed during migration.
- Legacy format `<category>/<slug>` is temporarily allowed during migration.

**User stories:**

- `feature/<ID>-<short-representative-slug>`
- The slug must be concise and describe the user story purpose.

**User-facing improvements (to previous implementations):**

- `improvement/<short-slug>`

**Technical non-user-facing work:**

- `refactor/<short-slug>`
- `chore/<short-slug>`
- `ci/<short-slug>`
- `docs/<short-slug>`
- `fix/<short-slug>`

Slug rules:

- Use lowercase letters, numbers, and hyphens.
- Keep it concise and representative of the work item.

Exemptions:

- `main` is exempt from this convention.
- Detached HEAD is exempt from this convention.

This convention removes the `codex/<worktree>/` segment and only requires the category pattern:

- Example: `feature/us-42-pet-owner-export`, `improvement/prescription-print-layout`,
  `chore/preflight-branch-name-hook`, `docs/branching-convention-refresh`

Branches must be **short-lived** and focused on a single user story or a single technical concern.

---
