# Plan: Multi-Visit Detection via Raw Text Boundaries

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
**PR:** [#216](https://github.com/isilionisilme/veterinary-medical-records/pull/216)
**User Story:** [US-64](../implementation-plan.md)
**Prerequisite:** `main` estable con tests verdes y baseline reproducible en `test_document_review.py`.
**Worktree:** `d:/Git/veterinary-medical-records-golden-loop`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** `Codex 5.3` (single-agent execution)
**Iteration:** 23 (propuesta)

---

## Continuation Context

Este plan es la **Parte 1 de 4** del macro-plan de multi-visit scoping:

| Parte | Plan | Scope | Estado |
|---|---|---|---|
| **1 (esta)** | [COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md](COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md) | Deteccion de boundaries de visitas desde raw text | Completado (PR #216) |
| **2** | [PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md](../PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md) | Extraccion de campos clinicos por segmento de visita + observations/actions | En progreso |
| **3** | [COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md](COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md) | Observabilidad, metricas de cobertura y documentacion de cierre | Completado |
| **4** | [PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md](../PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md) | NER/LLM sobre observations/actions -> campos granulares | Pendiente (condicional) |

---

## Context

### Problema funcional

La deteccion de visitas en review scoping depende hoy de:

1. Campos explicitos `visit_date`.
2. Fechas detectadas en snippets de evidencia que contienen keywords de visita.

Esto provoca fallos en documentos con multiples visitas cuando la fecha existe en el texto crudo pero no esta presente en snippets de campos visit-scoped. Caso objetivo: `docB` mostrando una sola visita cuando el documento contiene varias.

### Estado actual relevante

- `_extract_visit_date_candidates_from_text()` en `_shared.py` solo opera sobre snippets.
- `_normalize_canonical_review_scoping()` en `review_service.py` no consume `raw_text`.
- Existe guard de contexto no-visita (`_NON_VISIT_DATE_CONTEXT_PATTERN`), pero solo aplicado al snippet.

### Decision de implementacion

Se incorpora una fuente adicional de deteccion de visitas basada en `raw_text` completo, en modo incremental:

- Fase inicial: deteccion por fechas + contexto de visita desde `raw_text` (sin asignacion por offsets).
- Fase posterior condicional: offsets posicionales solo si la fase inicial no resuelve `docB`.

---

## Objective

1. Detectar multiples visitas cuando las fechas aparecen en `raw_text` aunque no esten en snippets.
2. Mantener comportamiento determinista/idempotente del payload canonical.
3. Evitar falsos positivos de fechas no clinicas (factura, emision, nacimiento, etc.).
4. Resolver `docB` sin regresiones en golden loops existentes.

## Scope Boundary

- **In scope:** deteccion de visitas desde `raw_text`, merge/deduplicacion con fuentes existentes, guards de contexto no-visita, tests de integracion y benchmark focalizado de visit count.
- **Out of scope:** cambios UX/frontend, cambios de prompt/LLM, soporte de otros idiomas, refactors no relacionados.

---

## Commit plan

| ID | After Steps | Scope | Commit Message | Push |
|---|---|---|---|---|
| CT-1 | P0-A, P0-B | Baseline y fixtures multi-visita | `test(plan-p0): multi-visit raw-text baseline and fixtures` | Inmediato |
| CT-2 | P1-A0, P1-A, P1-B | Plumbing raw_text + deteccion fuente 3 + dedupe | `feat(plan-p1): detect multi-visit boundaries from raw text` | Inmediato |
| CT-3 | P2-A, P2-B | Guards anti-false-positive + determinismo | `fix(plan-p2): harden raw-text visit detection guards` | Inmediato |
| CT-4 | P3-A, P3-B | Benchmark + suite focalizada + evidencia | `test(plan-p3): validate multi-visit raw-text detection` | Inmediato |
| CT-5 | P3-D | Post-gate docs update | `docs(plan-p3): document raw-text multi-visit detection` | Inmediato |
| CT-6 | P4-A, P4-B | Offset assignment (solo si aplica) | `feat(plan-p4): positional visit assignment by raw-text offsets` | Inmediato |

---

## Operational override steps

### CT-1

- `type`: `commit-task`
- `trigger`: after `P0-A` and `P0-B`
- `preconditions`: cambios de `P0-A` y `P0-B` completos; preflight L1/L2 verde; sin archivos fuera de scope
- `commands`: `git add <scope-files> && git commit -m "test(plan-p0): multi-visit raw-text baseline and fixtures" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

### CT-2

- `type`: `commit-task`
- `trigger`: after `P1-A0`, `P1-A`, and `P1-B`
- `preconditions`: plumbing `raw_text` y deteccion fuente 3 listos; preflight L1/L2 verde
- `commands`: `git add <scope-files> && git commit -m "feat(plan-p1): detect multi-visit boundaries from raw text" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

### CT-3

- `type`: `commit-task`
- `trigger`: after `P2-A` and `P2-B`
- `preconditions`: guards anti-false-positive y pruebas de determinismo completas; preflight L1/L2 verde
- `commands`: `git add <scope-files> && git commit -m "fix(plan-p2): harden raw-text visit detection guards" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

### CT-4

- `type`: `commit-task`
- `trigger`: after `P3-A` and `P3-B`
- `preconditions`: benchmark y suite focalizada en verde
- `commands`: `git add <scope-files> && git commit -m "test(plan-p3): validate multi-visit raw-text detection" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

### CT-5

- `type`: `commit-task`
- `trigger`: after `P3-D`
- `preconditions`: hard-gate `P3-C` aprobado por usuario y docs post-gate actualizadas
- `commands`: `git add <scope-files> && git commit -m "docs(plan-p3): document raw-text multi-visit detection" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

### CT-6

- `type`: `commit-task`
- `trigger`: after `P4-A` and `P4-B`
- `preconditions`: `P4-A` habilitado (decision gate GO) y offsets implementados
- `commands`: `git add <scope-files> && git commit -m "feat(plan-p4): positional visit assignment by raw-text offsets" && git push origin veterinary-medical-records-golden-loop/fix/multi-visit-rawtext-detection`
- `approval`: `auto`
- `fallback`: si falla commit/push, corregir causa, reintentar una vez; si persiste, marcar paso `🚫 BLOCKED` y escalar

---

## Execution Status

**Leyenda**
- 🔄 auto-chain - ejecutable por Codex
- 🚧 hard-gate - revision/decision de usuario

### Phase 0 - Baseline y diagnostico

- [x] P0-A 🔄 - Verificar que el test baseline existente reproduce el bug de `docB` (raw text con multiples visitas -> sistema detecta una sola). Extender si la cobertura es insuficiente. No cambiar logica productiva.
- [x] P0-B 🔄 - Verificar que `visit_detection_cases.json` contiene las 7 variantes (a)-(g). Extender si faltan variantes o ajustar expected values. Asegurar que fixtures tienen campo `raw_text` consumible por la nueva funcion.
- [x] CT-1 🔄 - Commit task P0.

### Phase 1 - Deteccion desde raw text (sin offsets)

- [x] P1-A0 🔄 - Propagar `raw_text` al flujo canonical: leer contenido en `get_document_review()` via `storage.resolve_raw_text()`, inyectar bajo key `_raw_text` en `structured_data`, preservar a traves del pipeline hasta `_normalize_canonical_review_scoping()` donde sera consumida y eliminada del output.
- [x] P1-A 🔄 - Implementar `_detect_visit_dates_from_raw_text(raw_text: str) -> list[str]` en `_shared.py` con estrategia de ventana de contexto (±150 chars por fecha tokenizada). Evaluar `_VISIT_CONTEXT_PATTERN` (extendido con `cita|atencion|exploracion`) y `_NON_VISIT_DATE_CONTEXT_PATTERN` solo sobre la ventana, NO sobre el texto completo. Deduplicar por fecha normalizada.
- [x] P1-B 🔄 - Integrar como tercera fuente **aditiva** en `_normalize_canonical_review_scoping()`: despues de fuentes 1 y 2, llamar a `_detect_visit_dates_from_raw_text()` con `_raw_text` del dict. Solo añadir fechas no presentes en `seen_detected_visit_dates`. Prioridad: fuente 1 > 2 > 3.
- [x] CT-2 🔄 - Commit task P1.

### Phase 2 - Guards y robustez

- [x] P2-A 🔄 - Añadir terminos faltantes a `_NON_VISIT_DATE_CONTEXT_PATTERN` (los existentes ya cubren nacimiento/factura/emision). Nuevos: `registro`, `certificado`, `recibo`, `prescripcion`, `expediente`, `identificacion`, `numero de`, `nº`. Verificar que no interfieran con contextos clinicos validos.
- [x] P2-B 🔄 - Verificar determinismo e idempotencia del payload canonical con tests (misma entrada, misma salida/orden).
- [x] CT-3 🔄 - Commit task P2.

### Phase 3 - Validacion y cierre

- [x] P3-A 🔄 - Ejecutar benchmark completo + delta, sin regresiones en golden loops.
- [x] P3-B 🔄 - Ejecutar suite focalizada de visit detection incluyendo assert duro `detected_visits == expected_visits` para cada fixture.
- [x] CT-4 🔄 - Commit task P3-A + P3-B. — ✅ `c070040a`
- [x] P3-C 🚧 - Hard-gate: validacion manual de `docB` en entorno dev. Criterio GO: multiples visitas detectadas correctamente. — ✅ `no-commit (GO user confirmation in chat, 2026-03-06)`
- [x] P3-D 🔄 - Post-gate: actualizacion de documentacion tecnica y umbrales aplicables. — ✅ `45284d0c`
- [x] CT-5 🔄 - Commit task P3-D. — ✅ `45284d0c`

### Phase 4 - Extension condicional (solo si Phase 1 no alcanza)

- [x] P4-A 🚫 NO-GO - La deteccion por fechas desde raw text resolvio docB sin necesidad de offsets posicionales. No se habilita esta fase.
- [ ] P4-B ⏭️ SKIPPED - Dependia de P4-A GO.
- [ ] CT-6 ⏭️ SKIPPED - Dependia de P4-A GO.

### Phase 5 - Merge y cierre de PR

- [ ] P5-A 🔄 - Merge PR a `main` tras CT-5. Verificar CI verde.
- [x] P5-B 🔄 - Crear plan separado para nueva PR: extraccion de campos clinicos por segmento de visita (scope: `reason_for_visit`, `diagnosis`, `symptoms`, `medication`, etc.). — ✅ `6ea7781c`

---

## Prompt Queue

1. `P0-A`: verificar que el test baseline existente (`test_document_review_docb_raw_text_multi_visit_status_quo_detects_single_assigned_visit`) reproduce el bug de `docB` correctamente. Si no cubre el escenario objetivo (raw text con multiples visitas → sistema detecta una sola), extenderlo. No cambiar logica productiva.
2. `P0-B`: verificar que `visit_detection_cases.json` ya contiene las 7 variantes (a)-(g). Si falta alguna variante o los expected values necesitan ajuste para la nueva fuente raw_text, extender. Los fixtures deben tener campo `raw_text` consumible por la nueva funcion.
3. `P1-A0`: propagar `raw_text` al flujo de normalizacion canonical. Concretamente: (a) en `get_document_review()`, leer el contenido via `storage.resolve_raw_text()` cuando `exists_raw_text()` sea True; (b) inyectar `raw_text` en el dict `structured_data` bajo una key reservada (e.g. `_raw_text`) antes de llamar a `_normalize_review_interpretation_data()`; (c) preservar esa key a traves de `_project_review_payload_to_canonical()` hasta `_normalize_canonical_review_scoping()`, donde sera consumida y eliminada del output.
4. `P1-A`: implementar `_detect_visit_dates_from_raw_text(raw_text: str) -> list[str]` en `_shared.py`. Estrategia: (a) tokenizar todas las fechas con `_VISIT_DATE_TOKEN_PATTERN`; (b) para cada fecha, extraer una **ventana de contexto** (±150 chars o hasta salto de linea/seccion) alrededor del match; (c) evaluar `_VISIT_CONTEXT_PATTERN` y `_NON_VISIT_DATE_CONTEXT_PATTERN` solo sobre la ventana, NO sobre el texto completo; (d) extender `_VISIT_CONTEXT_PATTERN` con keywords adicionales (`cita`, `atencion`, `exploracion`) manteniendo los existentes (`visita`, `consulta`, `control`, `revision`, `seguimiento`, `ingreso`, `alta`); (e) deduplicar por fecha normalizada.
5. `P1-B`: integrar como tercera fuente **aditiva** en `_normalize_canonical_review_scoping()`: despues de recolectar fechas de fuente 1 (campos `visit_date`) y fuente 2 (snippets de evidencia), llamar a `_detect_visit_dates_from_raw_text()` con el `_raw_text` del dict. Solo añadir fechas que NO esten ya en `seen_detected_visit_dates`. Orden de prioridad: fuente 1 > fuente 2 > fuente 3 (raw_text nunca contradice, solo complementa).
6. `P2-A`: añadir terminos faltantes a `_NON_VISIT_DATE_CONTEXT_PATTERN`. Terminos NUEVOS a agregar (los demas ya existen): `registro`, `certificado`, `recibo`, `prescripcion`, `expediente`, `identificacion`, `numero de`, `nº`. Verificar que no interfieran con contextos clinicos validos.
7. `P2-B`: asegurar determinismo/idempotencia con tests dedicados: misma entrada → misma salida (orden de visitas, IDs, fechas). Ejecutar cada test 3 veces para confirmar estabilidad.
8. `P3-A`: ejecutar benchmark completo y validar no regresiones en golden loops.
9. `P3-B`: ejecutar suite focalizada con asserts duros de visit count para cada fixture de `visit_detection_cases.json`.
10. `P3-C`: hard-gate de validacion manual de `docB`.
11. `P3-D`: documentar cambios y umbrales post-gate.
12. `P4-A`: 🚫 NO-GO — resuelto sin offsets.
13. `P4-B`: ⏭️ SKIPPED.
14. `P5-A`: merge PR a `main`.
15. `P5-B`: crear plan para nueva PR de extraccion de campos por segmento de visita.

## Active Prompt

Siguiente paso ejecutable: `P5-A` (merge PR a `main`, verificar CI verde).

---

## Post-Gate Notes (P3-D)

- Confirmacion hard-gate (`P3-C`): `GO` del usuario para `docB` en entorno dev (multiples visitas detectadas).
- Suite focalizada de review integration: `47 passed` (`python -m pytest backend/tests/integration/test_document_review.py -v --no-cov`).
- Benchmark suite: `116 passed, 2 xfailed` (`python -m pytest backend/tests/benchmarks/ -v --no-cov`), sin regresiones blocking.
- Umbral operativo de cierre: CI de PR en verde para commit de evidencia y commit de plan-update antes de continuar.

## Acceptance criteria

1. `docB` pasa de una visita detectada a multiples visitas detectadas correctamente.
2. No se introducen visitas fantasma en casos single-visit.
3. Fechas no clinicas no generan visitas (factura/emision/nacimiento/disclaimer).
4. Dedupe correcto de fechas equivalentes (`dd/mm/yyyy` y `yyyy-mm-dd`).
5. Payload canonical determinista e idempotente.
6. Suites de regresion y benchmark relevantes en verde.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `backend/app/application/documents/_shared.py` | Deteccion de fechas de visita desde snippet/raw text y patrones de contexto |
| `backend/app/application/documents/review_service.py` | Integracion de fuentes de visita y scoping canonical |
| `backend/tests/integration/test_document_review.py` | Casos de integracion multi-visita |
| `backend/tests/fixtures/synthetic/` | Fixtures sinteticos de visit detection |
| `backend/tests/benchmarks/` | Benchmark/regresion de extraccion |

---

## How to test

- `python -m pytest backend/tests/integration/test_document_review.py -v --no-cov`
- `python -m pytest backend/tests/benchmarks/ -v --no-cov`
- `python -m pytest backend/tests/unit/test_golden_extraction_regression.py -v --no-cov`
- Validacion manual: cargar `docB` y confirmar multiples visitas detectadas.

---

## Continuation — Multi-Visit Implementation Roadmap

Este plan es la **Parte 1 de 3** de la implementacion completa de multi-visit scoping. La funcionalidad se divide en PRs independientes para mantener diffs manejables (<400 LOC de logica productiva por PR) y facilitar code review, siguiendo la recomendacion de la [AI Code Review de PR #216](https://github.com/isilionisilme/veterinary-medical-records/pull/216#issuecomment-4013104012).

| Parte | Plan | Scope | PR |
|---|---|---|---|
| **1 (esta)** | [COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md](COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md) | Deteccion de boundaries de visitas desde raw text | [#216](https://github.com/isilionisilme/veterinary-medical-records/pull/216) |
| **2** | [PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md](../PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md) | Extraccion de campos clinicos por segmento de visita | Pendiente |
| **3 (condicional)** | [COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md](COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md) | Observabilidad, debug tooling y documentacion de cierre | Completado |
