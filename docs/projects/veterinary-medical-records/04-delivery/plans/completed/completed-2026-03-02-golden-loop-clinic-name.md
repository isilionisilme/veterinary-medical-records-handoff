# Plan: Iteration 16 — Golden loop for `clinic_name`

> **Operational rules:** See [execution-rules.md](../03-ops/execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Iteración:** 16  
**Rama:** `feature/golden-loop-clinic-name`  
**PR:** _(pending)_  
**Prerequisito:** `main` estable con tests verdes.

## Context

Se inicia un nuevo golden loop para mejorar la extracción del campo `clinic_name` (nombre del centro/clinica) en documentos veterinarios reales. El objetivo es aumentar exactitud y robustez ante variaciones de OCR, layouts y encabezados heterogéneos, manteniendo estabilidad de los demás campos.

## Objective

- Mejorar la precisión de `clinic_name` en casos reales y sintéticos.
- Evitar regresiones en `pet_name` y en el contrato de salida actual.
- Añadir evidencia reproducible (tests/fixtures/benchmark) para sostener decisiones.

## Scope Boundary (strict)

- **In scope:** extracción, normalización, ranking y observabilidad de `clinic_name`; fixtures sintéticos; tests unitarios/golden/benchmark del campo.
- **Out of scope:** cambios de UX/frontend, rediseño de schema global, refactors no relacionados, reglas de campos no afectados.

## Estado de ejecución

- [x] P0-A 🔄 — Baseline de `clinic_name`: crear/ajustar fixtures sintéticos + benchmark específico y medir accuracy inicial (GPT-5.3-Codex) — ✅ `3aa44550`
- [x] P0-B 🔄 — Añadir regresiones mínimas (positivas/negativas) para patrones reales de encabezado y OCR ruidoso (GPT-5.3-Codex) — ✅ `43105d8d`
- [x] P1-A 🔄 — Mejorar candidate mining para `clinic_name` (labels, delimitadores, guards multilinea/ruido) (GPT-5.3-Codex) — ✅ `573b9612`
- [x] P1-B 🔄 — Ajustar normalización/ranking de `clinic_name` sin afectar otros campos (GPT-5.3-Codex) — ✅ `c2a5cace`
- [x] P2-A 🔄 — Añadir observabilidad/triage para candidatos sospechosos de `clinic_name` (GPT-5.3-Codex) — ✅ `8fd1b51b`
- [x] P3-A 🔄 — Ejecutar tests focalizados + benchmark y documentar resultados en PR (GPT-5.3-Codex) — ✅ `e2c61fec`
- [x] P4-A 🚧 — Hard-gate: validación de usuario con ejemplos reales y decisión go/no-go (Claude Opus 4.6) — ✅ GO: 340/340 tests green, 11/11 benchmark, 0 regressions
- [x] P4-B 🔄 — Cierre técnico: ajustar umbral/evidencia final y actualizar cuerpo de PR (GPT-5.3-Codex) — ✅ `c5027cf0`

## Cola de prompts

### P0-A — Baseline benchmark

```text
Establece el baseline de clinic_name. Crea/ajusta fixtures sintéticos para clinic_name y un benchmark específico en backend/tests/benchmarks para medir accuracy inicial del campo.
Ejecuta solo tests/benchmarks relevantes y reporta accuracy inicial con evidencia.
```

⚠️ AUTO-CHAIN → P0-B

### P0-B — Regression seeds

```text
Añade regresiones mínimas para clinic_name (casos positivos y negativos) incluyendo encabezados multilinea y OCR ruidoso. Mantén cobertura focalizada sin ampliar alcance.
```

⚠️ AUTO-CHAIN → P1-A

### P1-A — Candidate mining hardening

```text
Mejora candidate mining de clinic_name: nuevos patrones de label, delimitadores y guards contra capturas multilinea espurias o ruido típico de OCR.
No cambies comportamiento de campos no relacionados.
```

⚠️ AUTO-CHAIN → P1-B

### P1-B — Normalization + ranking

```text
Ajusta normalización y ranking de clinic_name para priorizar candidatos plausibles y reducir falsos positivos. Agrega tests unitarios/golden estrictamente necesarios.
```

⚠️ AUTO-CHAIN → P2-A

### P2-A — Observability

```text
Agrega señales de observabilidad/triage para clinic_name sospechoso en la capa de extraction observability, con criterios concretos y testeables.
```

⚠️ AUTO-CHAIN → P3-A

### P3-A — Validation run

```text
Ejecuta suite focalizada (unit + golden + benchmark de clinic_name), resume resultados en formato apto para body de PR y deja evidencia reproducible.
```

⚠️ HARD-GATE → P4-A (Claude)

### P4-B — Post gate closure

```text
Tras aprobación explícita de Claude/usuario en P4-A, realiza ajustes finales de evidencia/umbral si aplica y actualiza el body del PR con resultados finales.
```

## Prompt activo

```text
P4-A 🚧 — Hard-gate: validación de usuario con ejemplos reales y decisión go/no-go (Claude Opus 4.6).
```
