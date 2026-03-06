# Plan: Worktree-Prefixed Branch Naming Convention

> **Operational rules:** See [execution-rules.md](../../03-ops/execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `improvements/improvement/branch-naming-rules-update`
**PR:** pendiente (draft)
**Prerequisito:** `main` estable con tests verdes y router generator operativo (`python scripts/docs/generate-router-files.py`).
**Iteracion:** 1
**Modo CI:** `3) End-of-plan gate`

---

## Context

### Problema operativo

Los nombres de rama actuales no identifican explicitamente el worktree de origen. Con multiples worktrees activos, esto complica:

- identificar de un vistazo de que worktree viene cada rama,
- evitar colisiones de nombres entre agentes/worktrees,
- filtrar ramas por contexto operativo.

### Estado actual

- Convencion vigente documentada: `<category>/<slug>`.
- No hay validacion automatica de branch naming en hooks o CI.
- Los worktrees activos comparten el mismo repositorio: `veterinary-medical-records`, `veterinary-medical-records-golden-loop`, `golden-2`, `docs`.

### Regla funcional adoptada

- Nuevo formato canonico: `<worktree>/<category>/<slug>`.
- `worktree` usa el nombre de carpeta tal cual.
- Categorias permitidas: `feature`, `fix`, `docs`, `chore`, `refactor`, `ci`, `improvement`.
- Exenciones: `main` y detached HEAD.
- Transicion: formato antiguo (`<category>/<slug>`) permitido temporalmente con warning.

---

## Objective

1. Establecer la convencion canonica `<worktree>/<category>/<slug>` en la documentacion operativa.
2. Regenerar router docs para mantener sincronia canonical -> router.
3. Implementar validacion automatica en pre-push (via L2/preflight) con mensajes claros.
4. Mantener compatibilidad temporal con ramas antiguas (warning, no bloqueo).
5. Garantizar verificabilidad con pruebas manuales del hook + check de drift del router.
6. Forzar que el agente cree ramas nuevas en formato canonico desde `Starting New Work` (no solo validacion al push).
7. Mantener enforcement operativo en L2 (pre-push) para evitar ejecuciones frecuentes durante iteracion local.

## Scope Boundary (strict)

- **In scope:** `way-of-working.md` (branching + starting new work), regeneracion de router files, nuevo validador de nombre de rama, integracion en `preflight-ci-local.ps1` (L2), contrato de propagacion router para START_WORK/BRANCHING, pruebas manuales de enforcement.
- **Out of scope:** migracion/rename de ramas historicas, enforcement en CI remoto, cambios de categorias de rama, refactors no relacionados.

---

## Commit Task Definitions

| ID | After Steps | Scope | Commit Message | Push |
|---|---|---|---|---|
| CT-1 | P1-A, P1-B | Convencion canonica + router regenerado | `docs(plan-p1): adopt worktree-prefixed branch naming convention` | Inmediato |
| CT-2 | P2-A, P2-B | Validador + integracion preflight L2 | `ci(plan-p2): enforce worktree-prefixed branch naming on pre-push` | Inmediato |
| CT-3 | P3-A, P3-B | Evidencia de validacion + cierre del plan | `docs(plan-p3): document branch naming validation evidence` | Inmediato |
| CT-4 | P4-A, P4-B, P4-C | Creacion de rama guiada para agentes + contrato de propagacion + evidencia | `docs(plan-p4): enforce agent branch creation with canonical naming` | Inmediato |

---

## Estado de ejecucion

**Leyenda**
- 🔄 auto-chain — ejecutable por Codex
- 🚧 hard-gate — revision/decision de usuario

### Phase 1 — Convencion y router

- [x] P1-A 🔄 — Actualizar `docs/shared/03-ops/way-of-working.md` seccion 2 para formalizar `<worktree>/<category>/<slug>`, exenciones y politica de transicion. (GPT-5.3-Codex)
- [x] P1-B 🔄 — Regenerar router docs y verificar que `docs/agent_router/03_SHARED/WAY_OF_WORKING/30_branching-strategy.md` y `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md` reflejan la nueva convencion. (GPT-5.3-Codex)
- [x] CT-1 🔄 — Commit task: scope P1-A + P1-B -> `docs(plan-p1): adopt worktree-prefixed branch naming convention` -> push. (GPT-5.3-Codex)

### Phase 2 — Enforcement pre-push

- [x] P2-A 🔄 — Crear `scripts/ci/validate-branch-name.ps1` con validacion de formato nuevo, exenciones, fallback legacy con warning y error blocking para formatos invalidos. (GPT-5.3-Codex)
- [x] P2-B 🔄 — Integrar validacion en `scripts/ci/preflight-ci-local.ps1` para que aplique en L2 (`Mode Push`) y bloquee push cuando corresponda. (GPT-5.3-Codex)
- [x] CT-2 🔄 — Commit task: scope P2-A + P2-B -> `ci(plan-p2): enforce worktree-prefixed branch naming on pre-push` -> push. (GPT-5.3-Codex)

### Phase 3 — Validacion y cierre

- [x] P3-A 🔄 — Ejecutar validacion manual de escenarios (nuevo formato, legacy permitido, invalido bloqueado, worktree-prefijo incorrecto bloqueado). (GPT-5.3-Codex)
- [x] P3-B 🔄 — Ejecutar `python scripts/docs/generate-router-files.py --check` y consolidar evidencia final para PR. (GPT-5.3-Codex)
- [x] CT-3 🔄 — Commit task: scope P3-A + P3-B -> `docs(plan-p3): document branch naming validation evidence` -> push. (GPT-5.3-Codex)

### Phase 4 — Creacion correcta por agente + feedback temprano

- [x] P4-A 🔄 — Actualizar `docs/shared/03-ops/way-of-working.md` seccion 1 (`Starting New Work`) para exigir que al crear rama nueva el agente derive `<worktree>/<category>/<slug>` y use mapeo de categoria por tipo de trabajo (`feature`, `improvement`, `fix`, `docs`, `chore`, `refactor`, `ci`). (GPT-5.3-Codex) — ✅ `c0467eda`
- [x] P4-B 🔄 — Regenerar router docs y verificar que `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md` y `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md` reflejan explicitamente la creacion de rama canonica por el agente. (GPT-5.3-Codex) — ✅ `c0467eda`
- [x] P4-C 🔄 — Mantener enforcement en L2 (sin mover branch naming a L1) y agregar/actualizar contrato en `backend/tests/unit/test_doc_router_contract.py` para fijar la propagacion START_WORK/BRANCHING. (GPT-5.3-Codex) — ✅ `c0467eda`
- [x] CT-4 🔄 — Commit task: scope P4-A + P4-B + P4-C -> `docs(plan-p4): enforce agent branch creation with canonical naming` -> push. (GPT-5.3-Codex) — ✅ `c0467eda`

---

## Acceptance criteria

1. La convencion oficial queda documentada como `<worktree>/<category>/<slug>` en `way-of-working.md`.
2. Los router files derivados de branching reflejan la nueva convencion sin drift.
3. El push falla para ramas fuera de formato y pasa para formato nuevo valido.
4. Ramas legacy `<category>/<slug>` no bloquean push durante transicion y muestran warning.
5. Ramas con prefijo de worktree incorrecto se bloquean en pre-push.
6. `main` y detached HEAD permanecen exentos.
7. Al pedir al agente "crea una rama para ...", la rama propuesta/creada cumple `<worktree>/<category>/<slug>` desde START_WORK.
8. L2 (Push) mantiene bloqueo para ramas invalidas sin requerir ejecucion adicional en L1.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `docs/shared/03-ops/way-of-working.md` | Fuente canonica de convencion de ramas |
| `docs/agent_router/03_SHARED/WAY_OF_WORKING/30_branching-strategy.md` | Router derivado para branching strategy |
| `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md` | Entrada routing para intent de branch naming |
| `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md` | Entrada routing para creacion de rama por agente |
| `scripts/ci/validate-branch-name.ps1` | Validador de branch naming (nuevo) |
| `scripts/ci/preflight-ci-local.ps1` | Punto de integracion enforcement en L2 |
| `backend/tests/unit/test_doc_router_contract.py` | Contrato de propagacion source -> router (START_WORK/BRANCHING) |
| `.githooks/pre-push` | Hook que dispara L2 antes del push |

---

## Politicas de sesion

- No editar router files manualmente (son auto-generated).
- Cualquier cambio en docs canonicos de branching debe regenerar router antes de cerrar.
- No cambiar categorias de rama fuera del alcance de este plan.

---

## Cola de prompts

### P1-A — Canonical branching update

```text
Contexto: estamos ejecutando el plan WORKTREE-PREFIXED-BRANCH-NAMING en la rama `improvements/improvement/branch-naming-rules-update`.

Actualiza `docs/shared/03-ops/way-of-working.md` en la seccion de Branching Strategy para adoptar como formato canonico:

<worktree>/<category>/<slug>

Requisitos:
1) Mantener categorias vigentes: feature, fix, docs, chore, refactor, ci, improvement.
2) Explicitar exenciones: main y detached HEAD.
3) Definir transicion: permitir temporalmente el formato legacy <category>/<slug> con warning.
4) Incluir ejemplos concretos para worktrees: veterinary-medical-records, veterinary-medical-records-golden-loop, golden-2, docs.
5) No modificar secciones no relacionadas.

```

### P1-B — Router regeneration and verification

```text
Regenera los router files tras el cambio canonico de branching:

1) Ejecutar: python scripts/docs/generate-router-files.py
2) Verificar que cambiaron:
	- docs/agent_router/03_SHARED/WAY_OF_WORKING/30_branching-strategy.md
	- docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md
3) Validar drift limpio con:
	- python scripts/docs/generate-router-files.py --check

```

### P2-A — Branch name validator script

```text
Crea `scripts/ci/validate-branch-name.ps1` con esta logica:

1) Detectar rama actual con `git branch --show-current`.
2) Si rama vacia (detached) o `main`: exit 0.
3) Detectar worktree esperado con `git rev-parse --show-toplevel` + `Split-Path -Leaf`.
4) Validar formato nuevo:
	^<worktree>/(feature|fix|docs|chore|refactor|ci|improvement)/[a-z0-9][a-z0-9-]*[a-z0-9]$
5) Si no matchea formato nuevo pero si legacy (`^(feature|fix|docs|chore|refactor|ci|improvement)/`): warning + exit 0.
6) Si no matchea ninguno: error + exit 1.
7) Mensajes claros con formato esperado y worktree detectado.

NO toques el archivo PLAN. NO hagas commit.
```

### P2-B — Integrate validation into L2 preflight

```text
Integra el validador en `scripts/ci/preflight-ci-local.ps1` para que corra en modo Push (L2):

1) Invocar `scripts/ci/validate-branch-name.ps1` temprano en el flujo de Mode Push.
2) Si la validacion falla, abortar con exit code no-cero.
3) No ejecutar la validacion en mode Quick (L1), salvo que ya exista patron central reutilizable.
4) Mantener sin cambios el resto de checks L1/L2/L3.

NO toques el archivo PLAN. NO hagas commit.
```

### P3-A — Manual validation matrix

```text
Ejecuta y documenta esta matriz manual:

1) Rama valida nueva: <worktree>/chore/test-branch-naming -> push permitido.
2) Rama legacy: chore/test-old-format -> warning y push permitido.
3) Rama invalida: random-branch -> push bloqueado.
4) Prefijo worktree incorrecto: golden-2/chore/test desde worktree veterinary-medical-records -> push bloqueado.

Registrar comandos y resultado de cada caso.

NO toques el archivo PLAN. NO hagas commit.
```

### P3-B — Final quality checks and PR evidence

```text
Preparar evidencia final:

1) Ejecutar: python scripts/docs/generate-router-files.py --check
2) Consolidar resultados de la matriz de validacion del hook.
3) Preparar resumen para PR body:
	- formato nuevo,
	- compatibilidad legacy temporal,
	- casos bloqueados,
	- archivos modificados.

NO toques el archivo PLAN. NO hagas commit.
```

### P4-A — Starting New Work canonical branch creation behavior

```text
Actualiza `docs/shared/03-ops/way-of-working.md` en la seccion `1. Starting New Work (Branch First)` para que la creacion de rama por agente quede explicitamente en formato canonico.

Requisitos:
1) En el paso de crear rama, indicar que el nombre DEBE construirse como `<worktree>/<category>/<slug>`.
2) Documentar que `worktree` se deriva del nombre de carpeta del repo actual (top-level).
3) Definir mapeo de categoria por tipo de solicitud: user story -> `feature`; mejora user-facing -> `improvement`; tecnico -> `fix|docs|chore|refactor|ci`.
4) Mantener consistencia con la seccion 2 (Branching Strategy), sin duplicar reglas innecesarias.

NO toques el archivo PLAN. NO hagas commit.
```

### P4-B — Router regeneration for START_WORK + BRANCHING behavior

```text
Regenera los router files tras el cambio en `Starting New Work`:

1) Ejecutar: python scripts/docs/generate-router-files.py
2) Verificar que cambiaron:
	- docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md
	- docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md
3) Validar drift limpio con:
	- python scripts/docs/generate-router-files.py --check

NO toques el archivo PLAN. NO hagas commit.
```

### P4-C — L2-only enforcement + propagation contract

```text
Implementa enforcement en L2 y contrato de propagacion:

1) Mantener `scripts/ci/validate-branch-name.ps1` unicamente en modo Push (L2) en `scripts/ci/preflight-ci-local.ps1`.
2) Mantener exenciones (`main`, detached HEAD) y compatibilidad legacy con warning.
3) Agregar/actualizar test en `backend/tests/unit/test_doc_router_contract.py` para asegurar que la instruccion de creacion canonica de rama aparece propagada en START_WORK/BRANCHING.
4) Ejecutar L2 y pruebas unitarias del contrato doc-router afectado.

NO toques el archivo PLAN. NO hagas commit.
```
