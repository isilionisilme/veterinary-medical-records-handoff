# Plan: Autocalculo de edad desde fecha de nacimiento

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for execution protocol and hard-gates.

**Branch:** `codex/veterinary-medical-records/docs/age-autocalc-plan`
**PR:** Pending (PR created on explicit user request)
**User Story:** N/A — standalone derivation improvement (no parent user story)
**Prerequisite:** None
**Worktree:** `D:/Git/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** Planning agent + Execution agent
**Automation Mode:** `Supervisado`
**Iteration:** 1
**Mode:** feature with backend normalization + frontend UX hint.

---

## Context

Hoy el esquema mantiene `age` y `dob` como campos separados. La edad se puede editar manualmente y no se deriva de forma automatica, lo que permite inconsistencias cuando existe fecha de nacimiento valida.

Decisiones cerradas para este plan:

1. Fecha de referencia para el calculo: **ultima `visit_date` valida**.
2. Prioridad: **la edad manual prevalece** sobre la autocalculada.
3. UX: `age` permanece **autorrelleno y editable**.

---

## Objective

1. Derivar `age` desde `dob` cuando corresponda, usando la ultima visita como fecha de referencia.
2. Mantener trazabilidad del origen (`human` vs `derived`) y evitar sobrescribir correcciones humanas.
3. Conservar compatibilidad de API y contrato actual de review/interpretation.
4. Exponer en UI una indicacion clara cuando `age` sea derivada.

## Scope Boundary (strict)

- **In scope:** normalizacion backend en lectura/proyeccion de interpretacion, preservacion de prioridad manual, ajuste de UI para hint de campo derivado, tests unitarios/integracion asociados.
- **Out of scope:** nuevos endpoints, cambios de contrato global schema, recalculo historico masivo de artefactos existentes, cambios de logica clinica fuera de `age`/`dob`.

---

## Steps

### F1 - Backend derivation rules

| Step | Task | Agent | Gate |
|------|------|-------|------|
| F1-A | Implementar helper para calcular edad en anos completos desde `dob` y fecha de referencia | 🔄 auto | - |
| F1-B | Resolver fecha de referencia con prioridad: ultima `visit_date` valida -> `document_date` valida -> fecha actual del sistema | 🔄 auto | - |
| F1-C | Aplicar derivacion de `age` durante normalizacion de review payload solo cuando no exista `age` manual no vacia | 🔄 auto | - |
| F1-D | Marcar origen `derived` para `age` autocalculada y reflejar valor en `fields` + `global_schema` | 🔄 auto | - |

### F2 - Frontend UX behavior

| Step | Task | Agent | Gate |
|------|------|-------|------|
| F2-A | Mantener `age` editable en dialogo de campo sin bloquear guardado manual | 🔄 auto | - |
| F2-B | Mostrar hint contextual cuando `age` venga con origen `derived` | 🔄 auto | - |
| F2-C | Verificar que edicion manual de `age` sigue teniendo prioridad tras refrescos/recarga del review | 🔄 auto | - |

### F3 - Validation and hard-gates

| Step | Task | Agent | Gate |
|------|------|-------|------|
| F3-A | Tests unitarios backend: calculo, fallbacks, DOB invalida/futura, no-overwrite de valor manual | 🔄 auto | - |
| F3-B | Test de integracion backend: `get_document_review` proyecta `age` derivada y respeta `age` manual | 🔄 auto | - |
| F3-C | Tests frontend: render de hint derivado y persistencia de edicion manual | 🔄 auto | - |
| F3-D | Documentation task: no-doc-needed (internal derivation logic, no new API surface or user-facing docs) | 🔄 auto | - |
| F3-E | 🚧 Validacion funcional de usuario en documento con multiples visitas y DOB presente | 🚧 hard-gate | User approval |

---

## Execution Status

**Legend**

- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — requires user review/decision

- [ ] F1-A — Helper de calculo de edad
- [ ] F1-B — Resolucion de fecha de referencia
- [ ] F1-C — Derivacion condicionada por prioridad manual
- [ ] F1-D — Persistencia de origen `derived` en proyeccion
- [ ] F2-A — Edad editable sin bloqueo
- [ ] F2-B — Hint visual de campo derivado
- [ ] F2-C — Prioridad manual tras refresco
- [ ] F3-A — Unit tests backend
- [ ] F3-B — Integration test backend
- [ ] F3-C — Tests frontend
- [ ] F3-D — Documentation task (no-doc-needed)
- [ ] F3-E — 🚧 Validacion funcional del usuario

---

## Prompt Queue

1. F1-A/F1-B: implementar helper de calculo y politica de fecha de referencia.
2. F1-C/F1-D: integrar derivacion condicionada y trazabilidad de origen.
3. F2-A/F2-B/F2-C: mantener UX editable y agregar hint de derivacion.
4. F3-A/F3-B/F3-C: completar bateria de tests backend/frontend.
5. F3-D: cerrar documentation task (no-doc-needed).
6. F3-E: ejecutar validacion funcional con usuario.

## Active Prompt

Pending activation.

---

## Acceptance Criteria

1. Con `dob` valida y sin `age` manual, el sistema muestra `age` derivada correctamente.
2. Con `age` manual no vacia, el sistema no la sobrescribe por derivacion automatica.
3. La fecha de referencia para el calculo sigue la prioridad definida (ultima visita -> fecha documento -> hoy).
4. Si `dob` es invalida o futura, no se deriva `age`.
5. La UI muestra indicacion de campo derivado y permite edicion manual.
6. Suite de pruebas objetivo en verde sin regresiones.

---

## PR Roadmap

### PR partition gate assessment

- **Projected scope:** ~8 changed files, ~150–250 changed lines.
- **Semantic risk axes:** backend + frontend in same PR (mixed axis flagged).
- **Size guardrails:** within 400 lines / 15 files thresholds.
- **Decision:** `Option A` — single PR. Rationale: changes are cohesive (one derivation feature), backend changes are small normalization logic, frontend changes are limited to a hint label. Risk is low and reviewable in isolation.

| PR | Scope | Steps | Status |
|----|-------|-------|--------|
| PR-1 | Age auto-calc: backend derivation + frontend hint + tests | F1-A → F3-E | Pending |

---

## Key Files

| File | Role |
|------|------|
| `backend/app/application/documents/review_service.py` | Proyeccion/normalizacion de payload para derivar `age` |
| `backend/app/application/documents/edit_service.py` | Preservacion de prioridad en ediciones manuales |
| `frontend/src/components/structured/FieldEditDialog.tsx` | UX de edicion y hint de campo derivado |
| `frontend/src/hooks/useFieldEditing.ts` | Flujo de guardado y prioridad de cambios manuales |

---

## How to test

- `python -m pytest backend/tests/unit -v --no-cov`
- `python -m pytest backend/tests/integration -v --no-cov`
- `npm --prefix frontend run test -- --run`
