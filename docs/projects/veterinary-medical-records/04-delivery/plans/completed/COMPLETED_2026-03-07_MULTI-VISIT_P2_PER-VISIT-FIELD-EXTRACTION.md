# Plan: Per-Visit Field Extraction from Segment Text

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `veterinary-medical-records-golden-loop/feat/per-visit-field-extraction`
**PR:** pendiente (draft)
**User Story:** [US-65](../implementation-plan.md)
**Prerequisite:** `main` con PR #216 mergeada (multi-visit raw text boundaries).
**Worktree:** `d:/Git/veterinary-medical-records-golden-loop`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** pendiente de seleccion explicita del usuario antes de Step 1
**Iteration:** 24 (propuesta)

---

## Continuation Context

Este plan es la **Parte 2 de 4** del macro-plan de multi-visit scoping:

| Parte | Plan | Scope | Estado |
|---|---|---|---|
| **1** | [COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md](completed/COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md) | Deteccion de boundaries de visitas desde raw text | Completado (PR #216) |
| **2 (este)** | [COMPLETED_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md](completed/COMPLETED_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md) | Extraccion de campos clinicos por segmento + observations/actions | Completado |
| **3** | [COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md](COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md) | Observabilidad, metricas de cobertura y documentacion de cierre | Completado |
| **4** | [PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md](PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md) | NER/LLM sobre observations/actions -> campos granulares | Pendiente (condicional) |

---

## Context

### Problema funcional

Tras PR #216, las visitas se detectan y segmentan correctamente desde raw text — cada visita tiene su `visit_date` y el texto del segmento correspondiente. Sin embargo, los campos clinicos de cada visita (`reason_for_visit`, `diagnosis`, `symptoms`, `medication`, `procedure`, etc.) estan vacios porque la extraccion actual opera a nivel de documento completo, no por segmento de visita.

### Estado actual relevante

- Visitas generadas en `_normalize_canonical_review_scoping()` con `"fields": []` y metadata (`visit_date`) correcta.
- `_locate_visit_boundary_offsets_from_raw_text()` proporciona offsets para segmentar raw text por visita.
- `_mine_interpretation_candidates()` en `candidate_mining.py` ya extrae campos clinicos con patrones regex bien probados, pero opera sobre el documento completo.
- La asignacion de campos a visitas existente se basa en snippets de evidencia del LLM — no cubre campos que no estan en la interpretacion original.

### Decision de implementacion

Re-utilizar `_mine_interpretation_candidates()` sobre el texto de cada segmento de visita para poblar campos clinicos. Enfoque iterativo campo a campo, empezando por los de mayor valor/menor riesgo. Deteccion **aditiva** — nunca reemplazar campos ya asignados por fuentes de mayor prioridad (LLM > snippet > raw-text mining).

### Principios de diseno (de AI Code Review PR #216)

1. **<400 LOC de logica productiva por PR.**
2. **No mezclar logica core + endpoints debug + docs en la misma PR.**
3. **Un test de regresion focalizado por commit que pruebe su delta comportamental.**
4. **Preservar determinismo/idempotencia del payload canonical.**
5. **Deteccion aditiva; no reemplazar prioridades de fuentes existentes.**

---

## Objective

1. Visitas detectadas desde raw text pasan de `fields: []` a tener campos clinicos extraidos de su segmento de texto.
2. Orden de campos por iteracion: `reason_for_visit` → `diagnosis`/`symptoms` → `medication` → `procedure`.
3. Nuevos campos pre-categorizados `observations` (hallazgos/signos/sintomas/diagnostico) y `actions` (tratamiento/medicacion/procedimientos/seguimiento) que capturan el texto clinico del segmento con alta cobertura.
4. No introducir regresiones en golden loops ni en campos ya asignados por fuentes de mayor prioridad.
5. Payload canonical determinista e idempotente.

## Scope Boundary

- **In scope:** extraccion de campos clinicos por segmento de visita, integracion aditiva en `_normalize_canonical_review_scoping()`, tests focalizados por campo; nuevos campos pre-categorizados `observations`/`actions` (schema + backend heuristica + frontend + tests).
- **Out of scope:** NER/LLM (Plan 4), debug endpoints y metricas de cobertura (Plan 3), soporte de otros idiomas, refactors no relacionados.

---

## Commit plan

| ID | After Steps | Scope | Commit Message | Push |
|---|---|---|---|---|
| CT-1 | P0-A, P0-B | Baseline fixtures con visitas vacias | `test(plan-p0): per-visit field extraction baseline` | Inmediato |
| CT-2 | P1-A, P1-B | reason_for_visit extraction | `feat(plan-p1): extract reason_for_visit from visit segment text` | Inmediato |
| CT-3 | P2-A, P2-B | diagnosis + symptoms extraction | `feat(plan-p2): extract diagnosis and symptoms from visit segment text` | Inmediato |
| CT-4 | P3-A, P3-B | medication + procedure extraction | `feat(plan-p3): extract medication and procedure from visit segment text` | Inmediato |
| CT-5 | P4-A, P4-B | Validacion final + benchmark | `test(plan-p4): validate per-visit field extraction end-to-end` | Inmediato |
| CT-6 | P5-A, P5-B, P5-C | observations/actions schema + backend + frontend + tests | `feat(plan-p5): add observations and actions pre-categorized fields` | Inmediato |
| CT-7 | P6-A | Cierre de hard-gate y actualizacion de estado del plan | `chore(plan-p6): close observations-actions validation gate` | Inmediato |

---

## Execution Status

**Leyenda**
- 🔄 auto-chain - ejecutable por agente
- 🚧 hard-gate - revision/decision de usuario

### Phase 0 - Baseline

- [x] P0-A 🔄 - Crear/extender fixtures de integracion con documentos multi-visita que tengan texto clinico rico (sintomas, diagnosticos, medicacion) en cada segmento. Asegurar que el baseline actual produce `fields: []` para visitas detectadas desde raw text.
- [x] P0-B 🔄 - Crear tests focalizados que asserten el estado vacio actual como baseline. Estos tests evolucionaran para verificar campos poblados en phases siguientes.
- [x] CT-1 🔄 - Commit task P0.

### Phase 1 - reason_for_visit

- [x] P1-A 🔄 - Implementar extraccion de `reason_for_visit` desde el segmento de texto de cada visita. Estrategia: primera linea/clausula significativa del segmento (excluyendo la fecha y prefijos de visita como "Consulta", "Control", "Revision"). Inyectar en el campo `reason_for_visit` de la visita cuando este `None`.
- [x] P1-B 🔄 - Tests focalizados: verificar que `reason_for_visit` se extrae correctamente para docB y fixtures sinteticos. Assert de no-regresion en visitas con `reason_for_visit` ya asignado.
- [x] CT-2 🔄 - Commit task P1.

### Phase 2 - diagnosis + symptoms

- [x] P2-A 🔄 - Implementar extraccion de `diagnosis` y `symptoms` por segmento de visita. Estrategia: re-usar logica de `_mine_interpretation_candidates()` ejecutada sobre el texto del segmento. Campos extraidos se añaden a `visit["fields"]` solo si no hay campos con esa key ya asignados por fuentes de mayor prioridad.
- [x] P2-B 🔄 - Tests focalizados: verificar extraccion correcta en fixtures multi-visita. Assert de deduplicacion (no duplicar campos ya presentes). Assert de determinismo.
- [x] CT-3 🔄 - Commit task P2.

### Phase 3 - medication + procedure

- [x] P3-A 🔄 - Implementar extraccion de `medication` y `procedure` por segmento de visita, misma estrategia que P2. Incluir patrones de medicacion ya existentes (nombres de farmacos, dosis, frecuencia).
- [x] P3-B 🔄 - Tests focalizados con fixtures que contengan lineas de medicacion y procedimientos en distintos segmentos de visita.
- [x] CT-4 🔄 - Commit task P3.

### Phase 4 - Validacion y cierre

- [x] P4-A 🔄 - Ejecutar benchmark completo + delta. Verificar no regresiones en golden loops existentes.
- [x] P4-B 🔄 - Ejecutar suite de integracion completa. Verificar payload determinista e idempotente.
- [x] CT-5 🔄 - Commit task P4. — ✅ `67ea55d8`
- [x] P4-C 🚧 — **CLOSED (pivot).** Hard-gate de deteccion granular: la extraccion por keyword tiene recall muy bajo en texto clinico no estructurado. Decision: mantener campos granulares como best-effort y pivotar a campos pre-categorizados `observations`/`actions` en Phase 5. Validacion de cobertura redefinida en P6-A.
- [x] P4-D 🔄 — **DEFERRED.** Merge removido del plan; se ejecutara solo con instruccion explicita del usuario.

### Phase 5 - Campos pre-categorizados (observations / actions)

> **Contexto del pivot:** La extraccion granular (symptoms, diagnosis, medication, procedure) por keyword tiene precision/recall insuficiente en texto clinico veterinario no estructurado. Se añaden dos campos amplios que pre-categorizan el texto del segmento: `observations` (hallazgos, signos, sintomas, impresiones clinicas) y `actions` (tratamiento, medicacion, procedimientos, seguimiento). Esto garantiza alta cobertura y prepara el input para un futuro NER/LLM (Plan 4) que distribuya la informacion en campos granulares.

- [x] P5-A 🔄 - **Schema + Backend:** Añadir `observations` y `actions` a `global_schema_contract.json` (section "Visita / episodio", `repeatable: false`, `value_type: "string"`). Implementar heuristica en `review_service.py` que divida `segment_text` en observaciones vs. acciones (separador: verbos de accion/prescripcion como "se recomienda", "se prescribe", "se administra", "se aplica", "tratamiento", "cita para", etc.). Inyectar en `visit["fields"]` como campos aditivos. — ✅ `no-commit (batched into CT-6)`
- [x] P5-B 🔄 - **Frontend:** Añadir `observations` y `actions` a `CANONICAL_VISIT_SCOPED_FIELD_KEYS` y `FIELD_LABELS` en `appWorkspace.ts`. Renderizar como campos de texto largo en las episode cards, antes de los campos granulares existentes. — ✅ `no-commit (batched into CT-6)`
- [x] P5-C 🔄 - **Tests:** Unit tests para la heuristica de particion (casos: texto mixto, texto solo-observaciones, texto solo-acciones, texto vacio). Integracion: verificar que docB produce observations/actions con ≥80% cobertura del segmento. — ✅ `no-commit (batched into CT-6)`
- [x] CT-6 🔄 - Commit task P5. — ✅ `6979b03b`, ✅ `4296bb14`

### Phase 6 - Validacion post-gate

- [x] P6-A 🚧 - Hard-gate: revision de observations/actions en docB. Criterio GO: ≥80% del texto clinico del segmento clasificado en uno de los dos campos. Campos granulares best-effort se valoran como bonus. ✅ APPROVED by user (2026-03-07).
- [x] CT-7 🔄 - Commit task P6 (cierre documental del gate, sin merge). — ✅ `6a219348`

---

## Prompt Queue

1. `P0-A`: crear/extender fixtures de integracion multi-visita con texto clinico rico por segmento. Verificar que baseline produce `fields: []` en visitas generadas desde raw text.
2. `P0-B`: crear tests que asserten el estado vacio como baseline. Estos tests se actualizaran en phases siguientes.
3. `P1-A`: implementar extraccion de `reason_for_visit` desde texto de segmento de visita. Usar primera clausula significativa. Solo cuando `reason_for_visit is None`.
4. `P1-B`: tests focalizados de `reason_for_visit`. No-regresion en visitas con valor ya asignado.
5. `P2-A`: implementar extraccion de `diagnosis`/`symptoms` por segmento via re-uso de `_mine_interpretation_candidates()`. Solo aditivo.
6. `P2-B`: tests de deduplicacion y determinismo para `diagnosis`/`symptoms`.
7. `P3-A`: implementar extraccion de `medication`/`procedure` por segmento. Misma estrategia.
8. `P3-B`: tests focalizados de `medication`/`procedure`.
9. `P4-A`: benchmark completo + delta.
10. `P4-B`: suite de integracion + verificacion de determinismo.
11. `P5-A`: schema + backend heuristica observations/actions.
12. `P5-B`: frontend — render observations/actions en episode cards.
13. `P5-C`: tests unitarios + integracion de observations/actions.
14. `P6-A`: hard-gate validacion de observations/actions en docB.
15. `P6-B`: reservado; merge fuera de este plan y sujeto a instruccion explicita del usuario.

## Active Prompt

Plan completado. No hay pasos pendientes.

---

## Acceptance criteria

1. Visitas detectadas desde raw text tienen `reason_for_visit` poblado cuando el segmento contiene contexto de motivo de consulta.
2. Al menos `diagnosis` o `symptoms` extraido por visita cuando el segmento contiene informacion clinica (best-effort).
3. Campos pre-categorizados `observations` y `actions` capturan ≥80% del texto clinico de cada segmento.
4. No se introducen campos duplicados en visitas que ya tenian campos asignados por el LLM.
5. Payload canonical determinista e idempotente.
6. Suites de regresion y benchmark en verde.
7. LOC de logica productiva <400.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `backend/app/application/documents/_shared.py` | Constantes de visit-scoped keys, patrones de contexto |
| `backend/app/application/documents/review_service.py` | Integracion de campos en visitas durante scoping canonical |
| `backend/app/application/processing/candidate_mining.py` | Logica de extraccion de candidatos reutilizable por segmento |
| `frontend/src/constants/appWorkspace.ts` | Constantes de campos visit-scoped, labels UI |
| `shared/global_schema_contract.json` | Schema canonical con observations/actions |
| `backend/tests/integration/test_document_review.py` | Casos de integracion multi-visita |
| `backend/tests/fixtures/raw_text/docB.txt` | Fixture principal de validacion |
| `backend/tests/benchmarks/` | Benchmark/regresion de extraccion |

---

## How to test

- `python -m pytest backend/tests/integration/test_document_review.py -v --no-cov`
- `python -m pytest backend/tests/benchmarks/ -v --no-cov`
- `python -m pytest backend/tests/unit/test_golden_extraction_regression.py -v --no-cov`
- Validacion manual: cargar docB y confirmar campos clinicos poblados por visita.
