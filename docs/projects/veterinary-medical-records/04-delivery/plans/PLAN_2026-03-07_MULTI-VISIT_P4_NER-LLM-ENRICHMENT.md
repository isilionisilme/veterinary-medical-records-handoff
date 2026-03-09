# Plan: NER/LLM Enrichment of Pre-Categorized Visit Fields

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** pendiente
**PR:** pendiente
**Prerequisite:** `main` con Plan 2 (observations/actions) y Plan 3 (metricas de cobertura) mergeados.
**Backlog item:** N/A (conditional spike; tracked via multi-visit macro-plan)
**Worktree:** `d:/Git/veterinary-medical-records-golden-loop`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** pendiente de seleccion explicita del usuario antes de Step 1
**Automation Mode:** `Supervisado` (default hasta seleccion explicita del usuario)
**Iteration:** 26 (propuesta)

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Continuation Context

Este plan es la **Parte 4 de 4** del macro-plan de multi-visit scoping:

| Parte | Plan | Scope | Estado |
|---|---|---|---|
| **1** | [COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md](completed/COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md) | Deteccion de boundaries de visitas desde raw text | Completado (PR #216) |
| **2** | [PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md](PLAN_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md) | Extraccion de campos clinicos por segmento + observations/actions | En progreso |
| **3** | [COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md](completed/COMPLETED_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md) | Observabilidad, metricas de cobertura y documentacion de cierre | Completado |
| **4 (esta)** | [PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md](PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md) | NER/LLM sobre observations/actions → campos granulares | Pendiente (condicional) |

---

## Context

### Activacion condicional

Este plan **solo se ejecuta** si se toma una decision de negocio de invertir en extraccion granular de campos clinicos mas alla del nivel de cobertura alcanzado con `observations`/`actions` (Plan 2). Requiere que P2 y P3 esten mergeados para disponer de:

1. Campos `observations` y `actions` poblados por visita (input pre-categorizado).
2. Metricas baseline de cobertura de campos por visita (P3) para medir delta.

### Problema funcional

Los campos clinicos granulares (`symptoms`, `diagnosis`, `medication`, `procedure`, `treatment_plan`) tienen recall muy bajo con heurísticas regex sobre texto clinico veterinario no estructurado. Las notas veterinarias mezclan observaciones y acciones en lenguaje natural sin etiquetas explicitas, haciendo imposible una clasificacion fina sin comprension semantica.

### Estrategia pre-categorizada

Plan 2 resuelve la cobertura con `observations` (hallazgos/signos/diagnostico) y `actions` (tratamiento/medicacion/procedimientos). Este plan aprovecha esa pre-categorizacion para que el NER/LLM reciba input acotado y con contexto:

- `observations` → extraer: `symptoms`, `diagnosis`
- `actions` → extraer: `medication`, `procedure`, `treatment_plan`

Ventajas:
1. **Reduccion de coste**: el modelo procesa solo el texto pre-categorizado, no el documento completo.
2. **Mayor precision**: el contexto "esto son observaciones" / "esto son acciones" reduce ambiguedad.
3. **Fallback garantizado**: si el NER/LLM falla, `observations`/`actions` siguen mostrando el texto completo.

### Opciones de modelo a evaluar

| Opcion | Peso | Dominio | Trade-off |
|---|---|---|---|
| spaCy + PlanTL-GOB-ES (bio-ehr-es) | ~2 GB | HCE humanas españolas | Offline, pero entrenado en medicina humana, no veterinaria |
| GLiNER (zero-shot NER) | ~400 MB | Generalista multilingue | Flexible, precision media |
| LLM via API (GPT/Claude) | 0 MB local | Generalista | Maxima flexibilidad, dependencia externa + coste |
| LLM local (Ollama/llama.cpp) | Variable | Generalista | Sin dependencia externa, requiere GPU o CPU potente |

---

## Objective

1. Evaluar y seleccionar modelo NER/LLM para extraccion granular desde `observations`/`actions`.
2. Implementar pipeline que enriquezca campos granulares a partir de campos pre-categorizados.
3. Medir delta de precision/recall vs baseline heuristico (metricas de P3).
4. Mantener `observations`/`actions` como fallback — los campos granulares son refinamiento, nunca reemplazo.

## Scope Boundary

- **In scope:** evaluacion de modelo, PoC offline, pipeline de enriquecimiento NER/LLM, tests de precision/recall, actualizacion de Docker image si procede.
- **Out of scope:** cambios en deteccion de boundaries (P1), cambios en observations/actions (P2), cambios en UI mas alla de mostrar campos granulares ya existentes.

---

## Commit recommendations (inline, non-blocking)

- After `P0-A + P0-B`: recommend `spike(plan-p0): evaluate NER/LLM model for clinical field enrichment`.
- After `P1-A + P1-B`: recommend `feat(plan-p1): NER/LLM enrichment pipeline for visit fields`.
- After `P2-B`: recommend `docs(plan-p2): NER/LLM validation evidence and rollout decision`.
- In `Supervisado`, each commit requires explicit user confirmation.
- Push remains manual in all modes.
- PR creation/update is user-triggered only and requires pre-PR commit-history review.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain - ejecutable por agente
- 🚧 hard-gate - revision/decision de usuario

### Phase 0 - Evaluacion de modelo

- [ ] P0-A 🚧 - Seleccion de modelo: evaluar opciones (spaCy + PlanTL-GOB-ES, GLiNER, LLM API, LLM local) considerando: precision en dominio veterinario español, peso/dependencias, coste operativo, latencia. Decision documentada.
- [ ] P0-B 🔄 - PoC offline: ejecutar modelo seleccionado sobre `observations` y `actions` de docB. Medir precision/recall vs campos granulares esperados (ground truth manual). Documentar resultados.

### Phase 1 - Integracion

- [ ] P1-A 🔄 - Implementar pipeline: `observations` → NER/LLM → `symptoms`, `diagnosis`; `actions` → NER/LLM → `medication`, `procedure`, `treatment_plan`. Campos granulares se inyectan aditivamente (no reemplazan `observations`/`actions` ni campos ya asignados por fuentes de mayor prioridad).
- [ ] P1-B 🔄 - Tests: unit tests del pipeline, integracion con metricas delta vs baseline P3.

### Phase 2 - Validacion y merge

- [ ] P2-A 🚧 - Hard-gate: mejora medible sobre heuristicas solas. Criterio GO: precision >70% y recall >60% en campos granulares sobre corpus de test.
- [ ] P2-B 🔄 - Consolidar evidencia final (precision/recall, riesgos, recomendacion de adopcion) para decision de rollout.
- [ ] P2-C 🚧 - Documentacion wiki: actualizar documentacion tecnica del pipeline NER/LLM o cerrar con `no-doc-needed` justificado.

---

## Prompt Queue

1. `P0-A`: evaluar opciones de modelo NER/LLM para dominio veterinario español.
2. `P0-B`: PoC offline con modelo seleccionado sobre docB observations/actions.
3. `P1-A`: implementar pipeline de enriquecimiento NER/LLM.
4. `P1-B`: tests de precision/recall con metricas delta.
5. `P2-A`: hard-gate de validacion de mejora.
6. `P2-B`: consolidar evidencia final y recomendacion de rollout.
7. `P2-C`: documentacion wiki o `no-doc-needed`.

## Active Prompt

Pendiente de activacion condicional tras Plan 2 + Plan 3.

---

## Acceptance criteria

1. Modelo seleccionado y decision documentada con justificacion.
2. Pipeline de enriquecimiento integrado aditivamente (no rompe observations/actions).
3. Precision >70% y recall >60% en campos granulares sobre corpus de test.
4. Metricas delta positivas vs baseline heuristico de P3.
5. Docker image actualizado si se añade dependencia pesada.
6. CI verde, payload determinista e idempotente.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `backend/app/application/documents/review_service.py` | Integracion del pipeline NER/LLM en scoping canonical |
| `backend/app/application/processing/candidate_mining.py` | Logica de extraccion existente (baseline) |
| `shared/global_schema_contract.json` | Schema con campos granulares y pre-categorizados |
| `Dockerfile.backend` | Imagen Docker (actualizacion si se añade modelo) |
| `backend/requirements.txt` | Dependencias Python (actualizacion si se añade modelo) |

---

## How to test

- `python -m pytest backend/tests/ -v --no-cov`
- PoC offline: script de evaluacion sobre docB con metricas precision/recall.
- Revision manual de campos granulares extraidos vs ground truth.
