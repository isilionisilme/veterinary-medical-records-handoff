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
| `validate-branch-name.ps1` | Valida formato de rama (`<category>/<slug>`; categorias: feature, improvement, refactor, chore, ci, docs, fix). |
| `check_plan_execution_guard.py` | Valida invariantes del plan activo por rama (resolucion de plan activo, `Execution Status` y unicidad de `IN PROGRESS`). |
| `plan-close-step.ps1` | Cierra un step `IN PROGRESS` de un plan de forma determinista y exige evidencia antes del cierre. |

## Guard de ejecucion de plan

Script: `scripts/ci/check_plan_execution_guard.py`

Que valida:
- Resolucion determinista de plan activo por branch (`PLAN_*.md` fuera de `completed/`).
- `## Execution Status` presente en plan activo.
- Maximo un step activo (`IN PROGRESS`).
- Ningun step cerrado puede conservar el label `IN PROGRESS`.

Ejecucion manual:

```powershell
python scripts/ci/check_plan_execution_guard.py
python scripts/ci/check_plan_execution_guard.py --branch "feature/us-3-plan-execution-guard"
python scripts/ci/check_plan_execution_guard.py --branch "my-branch" --plan-root "docs/projects/veterinary-medical-records/04-delivery/plans"
```

Exit codes:
- `0`: PASS (incluye modo no-plan: sin plan activo para la branch).
- `1`: FAIL (ambiguedad o invariante violado).

Integracion:
- Local: se ejecuta en `preflight-ci-local.ps1` en modos `Push` y `Full`.
- CI: job `plan_execution_guard` en `.github/workflows/ci.yml` para eventos `pull_request`.

## Helper de cierre de step

Script: `scripts/ci/plan-close-step.ps1`

Que hace:
- Busca el step por `StepId` en estado `- [ ] ... IN PROGRESS`.
- Valida evidencia en lineas siguientes (por ejemplo linea con `✅`) antes de cerrar.
- Cierra step (`- [x]`) y elimina label `IN PROGRESS`.

Uso:

```powershell
./scripts/ci/plan-close-step.ps1 -PlanPath "docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-09_IMP-03-PLAN-EXECUTION-GUARD.md" -StepId "P1-A"
```

## Notas rápidas

- Los hooks de Git (`.githooks/*`) invocan scripts PowerShell.
- Los `.bat` existen como comodidad para terminal CMD.
- In `Mode Push`, `preflight-ci-local.ps1` runs a remote-base sync guard that executes `git fetch origin <base>` and fails if `HEAD` does not contain `origin/<base>`.
