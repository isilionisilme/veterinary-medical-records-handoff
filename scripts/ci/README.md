# scripts/ci

Scripts de preflight local y hooks de Git.

## Qué hace cada script

| Script | Qué hace |
|---|---|
| `preflight-ci-local.ps1` | Motor principal de preflight. Ejecuta checks por alcance de diff (ruff/pytest/npm/doc guards/pip-audit/docker/e2e según modo y flags). |
| `preflight-ci-local.bat` | Wrapper CMD para lanzar `preflight-ci-local.ps1`. |
| `test-L1.ps1` | Preset rápido (`Mode Quick`) para pre-commit. |
| `test-L1.bat` | Wrapper CMD de `test-L1.ps1`. |
| `test-L2.ps1` | Preset de push (`Mode Push`) para pre-push. |
| `test-L2.bat` | Wrapper CMD de `test-L2.ps1`. |
| `test-L3.ps1` | Preset completo (`Mode Full`) para validación previa a PR. |
| `test-L3.bat` | Wrapper CMD de `test-L3.ps1`. |
| `install-pre-commit-hook.ps1` | Instala `.githooks/pre-commit` en `.git/hooks/pre-commit` (usa L1). |
| `install-pre-push-hook.ps1` | Instala `.githooks/pre-push` en `.git/hooks/pre-push` (usa L2). |
| `validate-branch-name.ps1` | Valida formato de rama (`<worktree>/<category>/<slug>`; permite legacy con warning). |

## Notas rápidas

- Los hooks de Git (`.githooks/*`) invocan scripts PowerShell.
- Los `.bat` existen como comodidad para terminal CMD.
