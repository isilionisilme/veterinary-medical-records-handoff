# scripts/ci — Local preflight system

## Architecture

```
Hook (sh)  ──→  test-L{1,2,3}.ps1  ──→  preflight-ci-local.ps1  (engine)
Human (PS) ──→  test-L{1,2,3}.ps1  ──→  preflight-ci-local.ps1  (engine)
```

All validation logic lives in a single engine: **`preflight-ci-local.ps1`** (~480 lines).
The `test-L*.ps1` files are thin wrappers (presets) that call the engine with the right flags.

## Files

| File | Role |
|------|------|
| `preflight-ci-local.ps1` | Engine — runs ruff, pytest, npm, doc guards, pip-audit, docker, e2e (path-scoped) |
| `preflight-ci-local.bat` | CMD launcher for the engine |
| `test-L1.ps1` / `.bat` | **L1 — Quick** preset (`-Mode Quick`). Pre-commit gate. |
| `test-L2.ps1` / `.bat` | **L2 — Push** preset (`-Mode Push -SkipDocker -ForceFrontend`). Pre-push gate. |
| `test-L3.ps1` / `.bat` | **L3 — Full** preset (`-Mode Full -SkipDocker -SkipE2E -ForceFrontend -ForceFull`). Pre-PR gate. |
| `install-pre-commit-hook.ps1` | Installs `.githooks/pre-commit` (runs L1) |
| `install-pre-push-hook.ps1` | Installs `.githooks/pre-push` (runs L2) |

## Why PowerShell?

- Git hooks (`.githooks/*`) are `sh` scripts. They invoke `pwsh` to run the `.ps1` wrappers.
- `.bat` files exist as a convenience for CMD terminals; they just call the `.ps1` via `powershell`.
- The engine uses PowerShell for diff parsing, conditional execution, and cross-platform compatibility.

A `.bat` cannot replace the `.ps1` wrappers because:
1. Hooks are `sh` and call `pwsh` directly — they cannot invoke `.bat`.
2. A `.bat` would still need to launch PowerShell to reach the engine anyway (extra layer, no benefit).

## When to run each level

| Level | When | Enforced by |
|-------|------|-------------|
| L1 | Before every commit | `.githooks/pre-commit` |
| L2 | Before every push | `.githooks/pre-push` |
| L3 | Before PR creation/update | Manual (documented in engineering playbook) |

## Common flags

Pass these to any wrapper or directly to the engine:

| Flag | Effect |
|------|--------|
| `-BaseRef <ref>` | Compare against a specific ref instead of `main` (L1 uses `HEAD`) |
| `-ForceFrontend` | Run frontend checks even if no frontend paths changed |
| `-ForceFull` | Run all scopes regardless of diff |
| `-SkipDocker` | Skip docker build check |
| `-SkipE2E` | Skip end-to-end tests |
