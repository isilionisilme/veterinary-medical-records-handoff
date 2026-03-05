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

**User stories:**
- `feature/<ID>-<short-representative-slug>`
- The slug must be concise and describe the purpose of the user story.

**User-facing improvements (to previous implementations):**
- `improvement/<short-slug>`

**Technical non-user-facing work:**
- `refactor/<short-slug>`
- `chore/<short-slug>`
- `ci/<short-slug>`
- `docs/<short-slug>`
- `fix/<short-slug>`

Branches must be **short-lived** and focused on a single user story or a single technical concern.

---
