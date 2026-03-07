# Plan: Visit Scoping Observability & Documentation

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `veterinary-medical-records-golden-loop/feat/visit-scoping-observability`
**PR:** pendiente
**User Story:** [US-66](../implementation-plan.md)
**Prerequisite:** `main` con Plan 2 (per-visit field extraction) mergeado.
**Worktree:** `d:/Git/veterinary-medical-records-golden-loop`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** pendiente de seleccion explicita del usuario antes de Step 1
**Iteration:** 25 (propuesta)

---

## Continuation Context

Este plan es la **Parte 3 de 3** de la implementacion de multi-visit scoping:

| Parte | Plan | Scope | Estado |
|---|---|---|---|
| **1** | [COMPLETED_2026-03-06_MULTI-VISIT-RAWTEXT-BOUNDARIES.md](completed/COMPLETED_2026-03-06_MULTI-VISIT-RAWTEXT-BOUNDARIES.md) | Deteccion de boundaries de visitas desde raw text | Completado (PR #216) |
| **2** | [PLAN_2026-03-07_PER-VISIT-FIELD-EXTRACTION.md](PLAN_2026-03-07_PER-VISIT-FIELD-EXTRACTION.md) | Extraccion de campos clinicos por segmento de visita | Pendiente |
| **3 (este)** | [PLAN_2026-03-07_VISIT-SCOPING-OBSERVABILITY.md](PLAN_2026-03-07_VISIT-SCOPING-OBSERVABILITY.md) | Observabilidad, debug tooling y documentacion de cierre | Pendiente / Condicional |

---

## Context

### Activacion condicional

Este plan **solo se ejecuta** si tras completar Plan 2 se identifica alguna de las siguientes necesidades:

1. El debug endpoint existente (`/documents/{id}/review/debug/visits`) no cubre las necesidades de diagnostico post-extraction.
2. Se necesitan metricas de cobertura de campos por visita para monitorear calidad.
3. La documentacion tecnica del ciclo multi-visit requiere actualizacion significativa.

Si ninguna de estas condiciones se cumple, este plan se cierra como **NO-GO** y la documentacion minima se incluye en Plan 2.

### Scope

- Debug tooling de visit scoping (extension del endpoint existente o nuevos endpoints).
- Metricas/logging de cobertura de campos por visita.
- Documentacion tecnica de cierre del ciclo completo de multi-visit.

---

## Objective

1. Proporcionar herramientas de diagnostico para validar extraccion de campos por visita en produccion.
2. Documentar el ciclo completo de multi-visit scoping con decisiones de arquitectura.
3. Mantener LOC <200.

## Scope Boundary

- **In scope:** debug endpoints, metricas de cobertura, documentacion tecnica.
- **Out of scope:** logica de extraccion de campos (Plan 2), cambios UX/frontend, cambios de prompt/LLM.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain - ejecutable por agente
- 🚧 hard-gate - revision/decision de usuario

### Phase 0 - Decision gate

- [ ] P0-A 🚧 - Evaluar si el debug endpoint existente cubre las necesidades post-Plan-2. Decision: GO (continuar plan) / NO-GO (cerrar plan, documentacion minima en Plan 2).

### Phase 1 - Observabilidad (solo si GO)

- [ ] P1-A 🔄 - Extender debug endpoint o crear metricas de cobertura de campos por visita segun necesidad identificada en P0-A.
- [ ] P1-B 🔄 - Tests de integracion para observabilidad.
- [ ] CT-1 🔄 - Commit task P1.

### Phase 2 - Documentacion de cierre

- [ ] P2-A 🔄 - Documentar decisiones de arquitectura del ciclo multi-visit completo (Partes 1-3). Actualizar docs tecnicos relevantes.
- [ ] CT-2 🔄 - Commit task P2.
- [ ] P2-B 🔄 - Merge PR a `main`. Verificar CI verde.

---

## Prompt Queue

1. `P0-A`: evaluar necesidades de debug/observabilidad post-Plan-2.
2. `P1-A`: extender debug tooling segun necesidad.
3. `P1-B`: tests de integracion.
4. `P2-A`: documentacion de cierre del ciclo multi-visit.
5. `P2-B`: merge PR.

## Active Prompt

Pendiente de activacion condicional tras Plan 2.

---

## Acceptance criteria

1. Debug tooling cubre diagnostico de campos por visita (si GO).
2. Documentacion tecnica del ciclo multi-visit completa.
3. LOC <200.
4. CI verde.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `backend/app/api/routes_review.py` | Debug endpoint de visitas |
| `docs/projects/veterinary-medical-records/` | Documentacion tecnica |
| `backend/tests/integration/test_document_review.py` | Tests de debug endpoint |

---

## How to test

- `python -m pytest backend/tests/integration/test_document_review.py -k "debug" -v --no-cov`
- Revision manual de documentacion generada.
