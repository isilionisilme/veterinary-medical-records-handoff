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
