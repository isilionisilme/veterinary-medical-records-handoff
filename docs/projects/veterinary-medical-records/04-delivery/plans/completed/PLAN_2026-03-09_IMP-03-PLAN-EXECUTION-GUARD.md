# Plan: IMP-03 — Plan Execution Guard Enforcement (Local + CI)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-03-plan-execution-guard-enforcement-local-ci.md](../../Backlog/completed/imp-03-plan-execution-guard-enforcement-local-ci.md)
**Branch:** `codex/veterinary-medical-records/ci/plan-execution-guard`
**PR:** pendiente
**Prerequisite:** `main` actualizado y tests verdes
**Worktree:** `C:/Users/ferna/.codex/worktrees/8420/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** pendiente de selección explícita del usuario antes de Step 1
**Automation Mode:** `Supervisado` (default hasta selección explícita del usuario)

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

Las reglas del plan-execution-protocol existen en docs, pero no hay enforcement automatizado.
Un agente puede olvidar transiciones de estado (dejar steps sin cerrar, abrir dos steps simultáneamente) y nada lo bloquea técnicamente.

Infraestructura existente:

- `scripts/ci/preflight-ci-local.ps1` — orquestador local con patrón `Invoke-Step` y modos Quick/Push/Full.
- `.github/workflows/ci.yml` — CI con jobs independientes por guard (doc canonical, doc parity, brand, etc.).
- `scripts/ci/test-L1|L2|L3.ps1` — wrappers de modos Quick/Push/Full.
- No existe script de guard de plan ni helper `plan-close-step`.

---

## Objective

1. Crear un script Python `scripts/ci/check_plan_execution_guard.py` que valide los invariantes de estado de plan activo.
2. Crear un helper PowerShell `scripts/ci/plan-close-step.ps1` para cerrar steps de forma determinista.
3. Integrar el guard en `preflight-ci-local.ps1` (modos Push/Full).
4. Añadir un job CI en `.github/workflows/ci.yml` para PRs.
5. Cubrir con tests unitarios el guard Python.

## Scope Boundary

- **In scope:** `scripts/ci/check_plan_execution_guard.py`, `scripts/ci/plan-close-step.ps1`, integración en `preflight-ci-local.ps1`, job en `ci.yml`, tests unitarios del guard.
- **Out of scope:** cambios de política canonical (IMP-01), sincronización router/maps (IMP-02), migración de planes activos (IMP-04/05), cambios de backend/frontend product.

---

## Commit recommendations (inline, non-blocking)

| After steps | Recommended message |
|---|---|
| P1-A .. P1-D | `ci(plan-guard): add plan execution guard script with invariant checks` |
| P2-A .. P2-C | `test(plan-guard): unit tests for plan execution guard invariants` |
| P3-A .. P3-B | `ci(plan-guard): add plan-close-step helper` |
| P4-A .. P4-B | `ci(plan-guard): integrate guard into preflight and CI workflow` |
| P5-A          | `ci(plan-guard): add validation checklist evidence` |

En modo Supervisado, cada commit requiere confirmación explícita del usuario.
Push permanece manual en todos los modos.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain — ejecutable por agente
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Análisis y diseño

- [x] P0-A 🔄 — Analizar estructura de planes existentes en `docs/.../plans/` para definir parsing: detectar `**Branch:**`, `## Execution Status`, checkboxes, labels `IN PROGRESS` / `STEP LOCKED`. — ✅ `no-commit (pattern audit on active PLAN_*.md)`
- [x] P0-B 🔄 — Documentar en este plan la especificación del guard: inputs, outputs, exit codes, mensajes de error. — ✅ `no-commit (spec documented below)`
- [x] P0-C 🚧 — Hard-gate: usuario valida diseño del guard antes de implementar. — ✅ `no-commit (user approval in chat: Go)`

#### P0-B Guard Specification (formal)

- Inputs:
  - `--branch <name>`: branch objetivo para resolver plan activo.
  - `--plan-root <path>`: raíz de búsqueda de planes (default `docs/projects/veterinary-medical-records/04-delivery/plans`).
  - Si `--branch` no se pasa: resolver con `git rev-parse --abbrev-ref HEAD`.
- Active plan resolution algorithm:
  - Hacer glob recursivo `PLAN_*.md` bajo `plan-root`.
  - Excluir cualquier archivo bajo `completed/`.
  - Para cada plan candidato, extraer branch con regex: `\*\*Branch:\*\*\s*`([^`]+)`.
  - Comparar branch extraido con branch objetivo de manera exacta.
  - `0` matches: modo no-plan, PASS (exit `0`).
  - `1` match: ese es el plan activo, continuar validaciones.
  - `>1` matches: FAIL por ambiguedad con lista de paths y remediacion (dejar un solo plan activo por branch).
- Invariants enforced on active plan:
  - `## Execution Status` debe existir.
  - At-most-one estado activo: entre checkboxes abiertos `- [ ]`, no puede haber mas de una linea con `IN PROGRESS` o `STEP LOCKED`.
  - Prohibicion de inicio con lock activo: si existe alguna linea `STEP LOCKED`, no puede coexistir otra linea `IN PROGRESS`.
  - Inconsistencia adicional: un checkbox cerrado `- [x]` no debe conservar labels activos (`IN PROGRESS` o `STEP LOCKED`); si aparece, FAIL con remediacion.
- Output format:
  - Cada violacion imprime una linea con prefijo `ERROR: `.
  - Sin errores: `plan-execution-guard: PASS`.
  - Con errores: `plan-execution-guard: FAIL (<n> invariant(s) violated)`.
- Exit codes:
  - `0`: PASS (incluye modo no-plan).
  - `1`: FAIL (cualquier invariante roto o ambiguedad de plan activo).

### Phase 1 — Script guard Python

- [x] P1-A 🔄 — Crear `scripts/ci/check_plan_execution_guard.py` con función de resolución de plan activo: buscar `PLAN_*.md` fuera de `completed/`, filtrar por branch match, 0 → pass, >1 → fail con mensaje de ambigüedad. — ✅ `no-commit (implemented; pending commit point)`
- [x] P1-B 🔄 — Implementar validación de que `## Execution Status` existe en plan activo. — ✅ `no-commit (implemented; pending commit point)`
- [x] P1-C 🔄 — Implementar validación de at-most-one `IN PROGRESS` o `STEP LOCKED` simultáneo. — ✅ `no-commit (implemented; pending commit point)`
- [x] P1-D 🔄 — Implementar validación de que no se puede iniciar step nuevo con `STEP LOCKED` activo. Definir exit code 0 (pass) / 1 (fail) con mensajes accionables. — ✅ `no-commit (implemented; pending commit point)`

> **Commit point →** `ci(plan-guard): add plan execution guard script with invariant checks`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 2 — Tests unitarios del guard

- [x] P2-A 🔄 — Crear `backend/tests/unit/test_plan_execution_guard.py` con fixtures Markdown para los escenarios: happy-path (1 step in progress), no-plan (pass), ambiguity (2 plans → fail), no execution-status (fail). — ✅ `no-commit (implemented; pending commit point)`
- [x] P2-B 🔄 — Test: `STEP LOCKED` presente + nuevo step → fail; step cerrado clean `[x]` → pass. — ✅ `no-commit (implemented; pending commit point)`
- [x] P2-C 🔄 — Test: 0 plans activos para branch → exit 0 (no-plan pass mode). — ✅ `no-commit (implemented; pending commit point)`

> **Commit point →** `test(plan-guard): unit tests for plan execution guard invariants`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 3 — Helper `plan-close-step`

- [x] P3-A 🔄 — Crear `scripts/ci/plan-close-step.ps1`: acepta plan path + step ID, valida que step está `IN PROGRESS`, reemplaza por `[x]`, elimina label `IN PROGRESS`. — ✅ `no-commit (implemented; pending commit point)`
- [x] P3-B 🔄 — Añadir validación de evidencia requerida: el step debe tener al menos un `✅` o línea de evidencia tras el checkbox antes de aceptar cierre. — ✅ `no-commit (implemented; pending commit point)`

> **Commit point →** `ci(plan-guard): add plan-close-step helper`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 4 — Integración preflight + CI

- [x] P4-A 🔄 — Integrar `check_plan_execution_guard.py` en `preflight-ci-local.ps1` como `Invoke-Step "Plan execution guard"` en bloque Push/Full, tras el bloque de doc guards existente. Condición: ejecutar siempre (la detección no-plan ya es pass-through). — ✅ `no-commit (implemented; pending commit point)`
- [x] P4-B 🔄 — Añadir job `plan_execution_guard` en `.github/workflows/ci.yml`: condición `github.event_name == 'pull_request'`, checkout con `fetch-depth: 0`, Python 3.11, ejecutar `python scripts/ci/check_plan_execution_guard.py --branch "${{ github.head_ref }}"`. — ✅ `no-commit (implemented; pending commit point)`

> **Commit point →** `ci(plan-guard): integrate guard into preflight and CI workflow`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 5 — Validation & closure

- [x] P5-A 🔄 — Ejecutar validation checklist completa del backlog item: happy path, locked path, ambiguity path, no-plan path. Documentar evidencia en este plan. — ✅ `no-commit (implemented; pending commit point)`
- [x] P5-B 🚧 — Hard-gate: usuario valida resultados y aprueba para PR. — ✅ `no-commit (user approval in chat to continue with commit + L3 + push + PR)`
- [x] P5-C 🚧 — Documentación: actualizar `scripts/ci/README.md` con descripción del guard y helper, o cerrar con `no-doc-needed` justificado. — ✅ `no-commit (README updated)`

#### P5-A Validation Evidence

- Happy path:
  - Fixture: branch `branch/happy` con 1 step `IN PROGRESS`.
  - Resultado guard local: `plan-execution-guard: PASS`, `exit=0`.
  - Cobertura CI path: job agregado `plan_execution_guard` en `.github/workflows/ci.yml` para PR con `--branch "${{ github.head_ref }}"`.
- Locked path:
  - Fixture: branch `branch/locked` con `STEP LOCKED` + `IN PROGRESS`.
  - Resultado guard local: FAIL (`exit=1`) con errores accionables:
    - `Multiple active steps found...`
    - `Cannot start step while STEP LOCKED is active. Resolve the locked step first.`
- Ambiguity path:
  - Fixtures: dos `PLAN_*.md` con branch `branch/ambiguous` fuera de `completed/`.
  - Resultado guard local: FAIL (`exit=1`) con mensaje de remediacion:
    - `Ambiguous active plan resolution... Keep exactly one active plan per branch outside completed/.`
- No-plan path:
  - Branch `branch/no-plan` sin plan activo asociado en `plan-root`.
  - Resultado guard local: `plan-execution-guard: PASS`, `exit=0`.
- Robustez de salida en Windows:
  - Fix aplicado en `check_plan_execution_guard.py` para evitar `UnicodeEncodeError` en consolas cp1252 al imprimir lineas con emojis de estado; fallback seguro con escape ASCII.

---

## Prompt Queue

### P0-A — Analizar estructura de planes existentes

```
Lee los archivos PLAN_*.md activos (fuera de completed/) en docs/projects/veterinary-medical-records/04-delivery/plans/.
Analiza los patrones de:
- Línea **Branch:** y su formato.
- Sección ## Execution Status con checkboxes.
- Labels usados: IN PROGRESS, STEP LOCKED, 🔄, 🚧.
- Formato de checkbox abierto `- [ ]` vs cerrado `- [x]`.
Documenta un resumen de patrones encontrados en P0-B.
```

### P0-B — Especificación del guard

```
Usando los patrones de P0-A, escribe en este plan la especificación formal:
- Algoritmo de resolución de plan activo (glob, exclusión de completed/, match de branch).
- Invariantes que se validan y su mensaje de error.
- CLI interface: argumentos (--branch, --plan-root), exit codes (0=pass, 1=fail), formato de output.
Actualiza la sección P0-B de este plan con la especificación.
```

### P0-C — Validación de diseño (hard-gate)

```
Presenta al usuario el diseño del guard (especificación de P0-B).
Espera aprobación antes de continuar a Phase 1.
```

### P1-A — Crear guard: resolución de plan activo

```
Crea scripts/ci/check_plan_execution_guard.py.
Implementa la función resolve_active_plan(branch, plan_root):
- Glob PLAN_*.md recursivo bajo plan_root, excluyendo completed/.
- Leer cada archivo, buscar línea que match regex r'\*\*Branch:\*\*\s*`([^`]+)`'.
- Comparar branch extraído con branch actual.
- 0 matches → return None (no-plan mode, exit 0).
- 1 match → return path.
- >1 matches → print error con lista de matches y exit 1.
Usa argparse con --branch (default: resultado de git rev-parse --abbrev-ref HEAD) y --plan-root (default: docs/projects/veterinary-medical-records/04-delivery/plans).
Haz el script ejecutable como __main__.
```

### P1-B — Validar Execution Status existe

```
Añade a check_plan_execution_guard.py la función validate_execution_status(plan_content):
- Buscar '## Execution Status' en el contenido.
- Si no existe, return error "Plan {path} is missing '## Execution Status' section."
Integra esta validación en el flujo main después de resolver el plan activo.
```

### P1-C — Validar at-most-one IN PROGRESS / STEP LOCKED

```
Añade la función validate_single_active_step(plan_content):
- Regex: buscar líneas de checkbox (r'- \[ \].*') que contengan 'IN PROGRESS' o 'STEP LOCKED'.
- También buscar en líneas ya marcadas [x] que aún tengan esos labels (estado inconsistente).
- Contar occurrencias de 'IN PROGRESS' + 'STEP LOCKED' en checkboxes abiertos.
- Si count > 1 → error "Multiple active steps found: {list}. At most one step may be IN PROGRESS or STEP LOCKED."
```

### P1-D — Validar no-new-step con STEP LOCKED

```
Añade la función validate_no_start_while_locked(plan_content):
- Si existe algún checkbox con 'STEP LOCKED', verificar que no hay otro con 'IN PROGRESS'.
- Si STEP LOCKED + IN PROGRESS coexisten → error "Cannot start step while STEP LOCKED is active. Resolve the locked step first."
Definir exit codes: 0 (pass, sin errores), 1 (fail, al menos un invariante roto).
Output format: cada error en línea propia, prefijo "ERROR: ".
Al final, si 0 errores: "plan-execution-guard: PASS"
Si >0: "plan-execution-guard: FAIL ({n} invariant(s) violated)" y exit 1.

Tras completar P1-A..P1-D → LANZAR L2.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### P2-A — Tests: happy-path, no-plan, ambiguity, no-execution-status

```
Crea backend/tests/unit/test_plan_execution_guard.py.
Importa las funciones del guard (ajustar sys.path si necesario para scripts/ci/).
Fixtures como strings Markdown:
- HAPPY_PLAN: un plan con Branch correcto, Execution Status, un step - [ ] IN PROGRESS.
- NO_EXEC_STATUS_PLAN: un plan sin ## Execution Status.
- AMBIGUOUS: dos plan contents con mismo branch.
Tests:
- test_resolve_no_plan: mock glob retornando vacío → None.
- test_resolve_single_match: mock glob retornando 1 plan → path.
- test_resolve_ambiguous: mock glob retornando 2 plans con mismo branch → exit error.
- test_validate_execution_status_present: HAPPY_PLAN → pass.
- test_validate_execution_status_missing: NO_EXEC_STATUS_PLAN → error.
```

### P2-B — Tests: STEP LOCKED y clean [x]

```
Añade tests a test_plan_execution_guard.py:
- LOCKED_PLAN fixture: plan con un step STEP LOCKED y otro IN PROGRESS.
- CLEAN_PLAN fixture: plan con todos steps [x] limpios (sin labels activos).
Tests:
- test_locked_plus_in_progress_fails: LOCKED_PLAN → error de coexistencia.
- test_all_closed_passes: CLEAN_PLAN → pass (0 active steps ok).
- test_single_in_progress_passes: HAPPY_PLAN → pass (exactly 1 active ok).
```

### P2-C — Test: no-plan pass mode

```
Añade test:
- test_no_plan_branch_passes: resolve_active_plan con branch que no matchea ningún plan → None → guard pass (exit 0).
Ejecutar todos los tests del guard: pytest backend/tests/unit/test_plan_execution_guard.py -v.

Tras completar P2-A..P2-C → LANZAR L2.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### P3-A — Crear plan-close-step helper

```
Crea scripts/ci/plan-close-step.ps1 con parámetros:
  -PlanPath (obligatorio): ruta al PLAN_*.md.
  -StepId (obligatorio): identificador del step (ej: "P1-A").
Lógica:
1. Leer contenido del plan.
2. Buscar línea que contenga el StepId y `- [ ]` y `IN PROGRESS`.
3. Si no encontrado → error "Step {StepId} not found or not IN PROGRESS in {PlanPath}."
4. Reemplazar `- [ ]` por `- [x]` y eliminar 'IN PROGRESS' del label.
5. Escribir archivo modificado.
6. Print "Step {StepId} closed successfully in {PlanPath}."
```

### P3-B — Validación de evidencia en cierre

```
Modifica plan-close-step.ps1:
Después de encontrar la línea del step y antes de cerrarla:
1. Buscar en las líneas siguientes (hasta el próximo checkbox o fin de sección) alguna evidencia: línea con '✅' o '— ✅' o que empiece con evidencia textual.
2. Si no hay evidencia → error "Step {StepId} cannot be closed: no evidence found. Add a ✅ evidence line after the step before closing."
3. Si hay evidencia → proceder con cierre.

Tras completar P3-A..P3-B → LANZAR L2.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### P4-A — Integrar en preflight-ci-local.ps1

```
Edita scripts/ci/preflight-ci-local.ps1:
Tras el bloque de doc guards (después de "Doc/router parity guard"), añadir:

    if ($Mode -eq "Push" -or $Mode -eq "Full") {
        Invoke-Step "Plan execution guard" {
            & $python "scripts/ci/check_plan_execution_guard.py"
        }
    }

Esto ejecuta el guard solo en Push/Full (no en Quick).
La resolución de branch usa el default de git rev-parse internamente.
```

### P4-B — Añadir job CI

```
Edita .github/workflows/ci.yml:
Añadir después del último doc guard job (doc_router_directionality_guard o brand_guard):

  plan_execution_guard:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: 3.11
      - name: Run plan execution guard
        run: |
          python scripts/ci/check_plan_execution_guard.py --branch "${{ github.head_ref }}"

Tras completar P4-A..P4-B → LANZAR L2.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### P5-A — Validation checklist

```
Ejecutar la validation checklist del backlog item:
1. Happy path: crear plan temporal con 1 step IN PROGRESS → guard pasa local + CI.
2. Locked path: plan temporal con STEP LOCKED + nuevo step → guard falla.
3. Ambiguity path: dos planes temporales para mismo branch → guard falla.
4. No-plan path: branch sin plan activo → guard pasa.
5. Verificar que mensajes de error incluyen guía de remediación.
Documentar evidencia en la sección de este step.
```

### P5-B — Validación de usuario (hard-gate)

```
Presenta al usuario:
- Resumen de todos los invariantes implementados.
- Evidencia de validation checklist.
- Archivos modificados/creados.
Espera aprobación para PR.
```

### P5-C — Documentación

```
Actualizar scripts/ci/README.md añadiendo secciones para:
- check_plan_execution_guard.py: qué valida, cómo ejecutar, exit codes.
- plan-close-step.ps1: qué hace, parámetros, ejemplo de uso.
O cerrar con no-doc-needed justificado si README.md ya cubre el patrón por convención.
```

---

## Active Prompt

Pendiente de activación por usuario.

---

## Acceptance criteria

1. Guard detecta plan activo por branch match determinista (0 → pass, 1 → validate, >1 → fail).
2. `Execution Status` ausente en plan activo → bloqueo.
3. >1 step `IN PROGRESS` o `STEP LOCKED` simultáneo → bloqueo.
4. `STEP LOCKED` + nuevo `IN PROGRESS` → bloqueo.
5. Branches sin plan activo → pasan sin bloqueo.
6. Helper `plan-close-step.ps1` cierra steps con validación de evidencia.
7. Guard integrado en preflight (Push/Full) y CI (PRs).
8. Tests unitarios cubren todos los escenarios de la validation checklist.

---

## How to test

```powershell
# Unit tests del guard
pytest backend/tests/unit/test_plan_execution_guard.py -v

# Guard manual
python scripts/ci/check_plan_execution_guard.py
python scripts/ci/check_plan_execution_guard.py --branch "codex/veterinary-medical-records/ci/plan-execution-guard"

# Helper manual
./scripts/ci/plan-close-step.ps1 -PlanPath "docs/.../PLAN_xxx.md" -StepId "P1-A"

# Preflight L2 (incluye guard)
./scripts/ci/test-L2.ps1
```
