# Plan: Golden Loop - `weight` (fuentes mixtas global + visitas)

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `codex/veterinary-medical-records/improvement/golden-loop-weight`  
**PR:** pendiente  
**Prerequisite:** `main` actualizado y tests verdes  
**Worktree:** `D:/Git/veterinary-medical-records`  
**CI Mode:** `2) Pipeline depth-1 gate` (default)  
**Agents:** pendiente de seleccion explicita del usuario antes de Step 1  
**Automation Mode:** `Supervisado` (default hasta seleccion explicita del usuario)  
**Iteration:** 27 (propuesta)

---

## Context

El campo `weight` puede aparecer en dos fuentes:

1. Como dato global en cabecera (`fields` document-scoped / `global_schema`).
2. Como dato visit-scoped en entradas de `visits`.

Regla funcional objetivo:

- Si hay pesos en visitas, el peso document-level debe derivarse del peso de la visita mas reciente/actualizada.
- Si solo hay peso global (sin pesos de visita), se mantiene el peso global.
- Si hay conflicto entre peso global y peso de visita, debe prevalecer el de visita para el document-level derivado.

Estado actual observado en `main`:

- Ya existe derivacion document-level de `weight` desde visitas (ordenada por `visit_date`).
- Ya hay tests de baseline para casos single-visit, multi-visit por fecha, global-only, ambiguo y ausencia.
- Falta robustecer el criterio de "mas actualizado" en empates de fecha y cerrar cobertura de tests para conflictos mixtos global+visita y desempate determinista intra-fecha.

---

## Objective

1. Formalizar y estabilizar la regla de precedencia de `weight` en fuentes mixtas.
2. Hacer determinista el desempate cuando hay multiples pesos con la misma `visit_date`.
3. Cubrir con tests de integracion los casos frontera que ahora no estan explicitamente protegidos.
4. Validar que no hay regresion en el flujo de review/canonical payload.

## Scope Boundary

- **In scope:** `review_service.py` (post-procesado de weight), tests de integracion de document review, evidencia de validacion.
- **Out of scope:** cambios de UX, cambios de schema, cambios de procesamiento ajenos a `weight`.

---

## Commit recommendations (inline, non-blocking)

- After `P1-A..P1-B`: recommend `feat(weight): deterministic precedence for mixed global/visit weight`.
- After `P2-A..P2-B`: recommend `test(weight): cover mixed-source and same-date tie-break behavior`.
- In `Supervisado`, each commit requires explicit user confirmation.
- Push remains manual in all modes.
- PR creation/update is user-triggered only and requires pre-PR commit-history review.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain - ejecutable por agente
- 🚧 hard-gate - revision/decision de usuario

### Phase 0 - Baseline & contract check

- [x] P0-A 🔄 - Confirmar comportamiento actual en `main`: weight derivado desde visitas, fallback global-only y tests baseline existentes. — ✅ `analisis en chat (2026-03-08)`
- [x] P0-B 🔄 - Confirmar que no existe plan activo de `weight` en `docs/.../plans` y recrear plan operativo. — ✅ `PLAN_2026-03-08_GOLDEN-LOOP-WEIGHT-MIXED-SOURCES.md`

### Phase 1 - Rule hardening (logic)

- [x] P1-A 🔄 - Implementar criterio de desempate determinista para pesos en misma `visit_date` (priorizar evidencia mas tardia/actualizada; fallback estable por orden de visita/campo). — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`
- [x] P1-B 🔄 - Mantener precedencia de visita sobre peso global cuando ambas fuentes coexisten en el mismo payload. — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`

### Phase 2 - Test coverage expansion

- [x] P2-A 🔄 - Añadir test de integracion: `weight` mixto global+visita debe derivar valor de visita. — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`
- [x] P2-B 🔄 - Añadir test de integracion: misma `visit_date` con varios pesos debe elegir ganador determinista (ultima evidencia). — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`
- [x] P2-C 🔄 - Ejecutar subset focalizado de tests de review y confirmar no regresiones. — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`

### Phase 3 - Validation & closure

- [x] P3-A 🚧 - Hard-gate: validacion de usuario sobre el criterio "mas actualizado" y resultados en payload final. — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`
- [x] P3-B 🔄 - Preparar evidencia final para PR (casos cubiertos, before/after, comandos de test). — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`
- [x] P3-C 🚧 - Documentacion wiki: actualizar documentacion tecnica o cerrar con `no-doc-needed` justificado. — ✅ `no-commit (user-directed close-out reconciliation 2026-03-09)`

---

## Prompt Queue

1. `P1-A`: reforzar algoritmo de seleccion de `weight` document-level para empates de fecha.
2. `P1-B`: garantizar precedencia de visita frente a global en escenarios mixtos.
3. `P2-A`: test integracion mixed global+visit.
4. `P2-B`: test integracion same-date tie-break.
5. `P2-C`: corrida focalizada de tests y resumen.
6. `P3-A`: hard-gate de usuario.
7. `P3-B`: evidencia final para PR.
8. `P3-C`: doc update o `no-doc-needed`.

## Active Prompt

Pendiente de activacion por usuario.

---

## Acceptance criteria

1. Si existe al menos un `weight` visit-scoped valido, el document-level `weight` deriva de visitas (no del global).
2. El desempate para misma fecha es determinista y estable.
3. Los dos nuevos escenarios frontera quedan cubiertos por tests de integracion.
4. Los tests focalizados de review quedan en verde.
5. No hay regresion en casos baseline ya existentes.

---

## How to test

- `pytest backend/tests/integration/test_document_review.py -k \"weight\" -v`
- `pytest backend/tests/integration/test_document_review.py -k \"mixed_global_and_visit or same_date\" -v`
