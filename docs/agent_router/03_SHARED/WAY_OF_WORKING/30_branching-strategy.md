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

**User stories:**
   - `feature/<ID>-<short-representative-slug>`
      - El slug debe ser conciso y describir el propósito de la historia de usuario.

**User-facing improvements (to previous implementations):**
   - `improvement/<short-slug>`

**Technical non-user-facing work:**
   - `refactor/<short-slug>`
   - `chore/<short-slug>`
   - `ci/<short-slug>`
   - `docs/<short-slug>`
   - `fix/<short-slug>`

Slug rules:
   - Usar solo minúsculas, números y guiones.
   - Mantenerlo conciso y representativo del trabajo.

Exemptions:
   - `main` está exenta de esta convención.
   - Detached HEAD está exenta de esta convención.

La convención antigua elimina el segmento `codex/<worktree>/` y solo requiere el patrón por categoría:
   - Ejemplo: `feature/us-42-pet-owner-export`, `improvement/prescription-print-layout`, `chore/preflight-branch-name-hook`, `docs/branching-convention-refresh`

Las ramas deben ser **cortas** y enfocadas en una sola historia de usuario o un solo tema técnico.

---
