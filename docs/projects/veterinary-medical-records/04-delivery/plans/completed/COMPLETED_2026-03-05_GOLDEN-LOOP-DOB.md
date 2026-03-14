# Plan: Golden Loop — `dob` (Fecha de nacimiento del paciente)

> **Operational rules:** See [execution-rules.md](../../03-ops/execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `feat/golden-loop-paciente-dob`
**PR:** [#203](https://github.com/isilionisilme/veterinary-medical-records/pull/203)
**User Story:** [US-61](../implementation-plan.md)
**Prerequisito:** `main` estable con tests verdes.
**Iteración:** 20
**Modo CI:** `3) End-of-plan gate`

## Context

`dob` (Fecha de nacimiento del paciente) ya existe en el contrato global (`shared/global_schema_contract.json`, sección `Paciente`, `value_type: date`, `optional: true`) y tiene una regex etiquetada en `_LABELED_PATTERNS`. Sin embargo, faltan las piezas clave del patrón golden loop:

- **No conectado al normalizador de fechas** — `normalize_canonical_fields()` llama `_normalize_date_value()` para `visit_date`, `document_date`, `admission_date`, `discharge_date`, pero **NO para `dob`**.
- **No en `DATE_TARGET_KEYS`** — el mining por anchors de fecha ignora `dob` completamente.
- **No en `MVP_COVERAGE_DEBUG_KEYS`** — no aparece en la lista de campos debug.
- **No dedicated fixtures** — no existe `backend/tests/fixtures/synthetic/dob/`.
- **No benchmark test** — no existe `backend/tests/benchmarks/test_dob_extraction_accuracy.py`.
- **No dedicated normalization unit tests** — falta suite específica para `dob`.
- **No dob-specific observability/triage** — no flags de sospecha dedicados.
- **No guardrails documentados** — `dob` no aparece en el Field Guardrails Catalog de `extraction-quality.md`.
- **No listado como Golden Field** — falta en § 6 Golden Fields status.

### Desafíos específicos de `dob`

- **Desambiguación con `visit_date`:** las fechas de nacimiento NO deben capturarse como visita y viceversa (ya existe guard en `visit_date`, falta el recíproco para `dob`).
- **Formatos de fecha en español:** `DD/MM/AAAA`, `D/M/AA`, separadores variados (`/`, `-`, `.`).
- **Año de 2 dígitos para nacimiento:** un animal nacido en `15` → 2015; rango plausible de nacimiento ≠ rango de visita.
- **Variaciones de etiqueta en español:** "Fecha de nacimiento", "F. Nac.", "F/Nto", "Nacimiento", "Nac.", "DOB", "Fecha nac", "F Nac".
- **Null cases:** documentos sin fecha de nacimiento (muy común — campo optional).
- **False-positive traps:** fecha de visita/alta/documento capturada como dob.

## Objective

- Alcanzar ≥ 85 % exact match en benchmark sintético de `dob`.
- Evitar regresiones en los golden loops existentes y en el resto del schema canónico.
- Añadir evidencia reproducible (fixtures + benchmark + tests unit/golden + observability).

## Scope Boundary (strict)

- **In scope:** extracción, normalización, ranking y observabilidad de `dob`; fixtures sintéticos; benchmark y tests focalizados del campo; documentación de guardrails.
- **Out of scope:** cambios de UX/frontend, rediseño del contrato global, refactors no relacionados, cambios de reglas en otros campos.

---

## Commit Task Definitions

| ID | After Steps | Scope | Commit Message | Push |
|---|---|---|---|---|
| CT-1 | P0-A, P0-B | Fixtures + benchmark (baseline) | `test(plan-p0): dob golden-loop baseline fixtures and benchmark` | Inmediato |
| CT-2 | P1-A, P1-B, P1-C, P1-D | Normalizador + anchors + regex + unit tests | `feat(plan-p1): dob extraction hardening — normalizer, anchors, labels, unit tests` | Inmediato |
| CT-3 | P2-A | Observability flags + tests | `feat(plan-p2): dob observability flags` | Inmediato |
| CT-4 | P3-A, P3-B | Golden regression + validation evidence | `test(plan-p3): dob golden regression and validation evidence` | Inmediato |
| CT-5 | P3-D | Threshold lock + extraction-quality doc | `docs(plan-p3): dob threshold lock and extraction-quality update` | Inmediato |

---

## Estado de ejecución

**Leyenda**
- 🔄 auto-chain — ejecutable por Codex
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Baseline and fixtures

- [x] P0-A 🔄 — Crear fixtures sintéticos de `dob` con casos positivos/negativos/ruido OCR bajo `backend/tests/fixtures/synthetic/dob/` (GPT-5.3-Codex) — ✅ `7d94b07d`
- [x] P0-B 🔄 — Crear benchmark `backend/tests/benchmarks/test_dob_extraction_accuracy.py` y medir baseline inicial (GPT-5.3-Codex) — ✅ `7d94b07d` — baseline: 11/18 (61.1%), null_misses=6, false_positives=0
- [x] CT-1 🔄 — Commit task: scope P0-A + P0-B → `test(plan-p0): dob golden-loop baseline fixtures and benchmark` → push (GPT-5.3-Codex) — ✅ `7d94b07d`

### Phase 1 — Extraction improvements (`dob` only)

- [x] P1-A 🔄 — Conectar `dob` al normalizador de fechas en `normalize_canonical_fields()` y añadir a `MVP_COVERAGE_DEBUG_KEYS` (GPT-5.3-Codex) — ✅ `a19d6f73`
- [x] P1-B 🔄 — Añadir `dob` a `DATE_TARGET_KEYS` con anchors de nacimiento y guards contra contexto visit/discharge/document; ampliar variantes de label en `_LABELED_PATTERNS` (GPT-5.3-Codex) — ✅ `a19d6f73`
- [x] P1-C 🔄 — Añadir tests unitarios dedicados de normalización de `dob`: formatos válidos (DD/MM/AAAA, D/M/AA, AAAA-MM-DD), años de 2 dígitos, inválidos, None/vacío (GPT-5.3-Codex) — ✅ `a19d6f73` (42 passed)
- [x] P1-D 🔄 — Medir delta de benchmark vs baseline; ajustar confidence/ranking de candidates de `dob` si es necesario (GPT-5.3-Codex) — ✅ `a19d6f73` — **16/18 (88.9%)** (+27.8 pp, 2 null misses: dash separator + embedded pipes)
- [x] CT-2 🔄 — Commit task: scope P1-A + P1-B + P1-C + P1-D → `feat(plan-p1): dob extraction hardening — normalizer, anchors, labels, unit tests` → push (GPT-5.3-Codex) — ✅ `a19d6f73`

### Phase 2 — Observability and quality gates

- [x] P2-A 🔄 — Añadir señales de observabilidad/triage para `dob` sospechoso (fecha futura, implausiblemente antigua > 40 años, coincidencia con visit_date) + tests (GPT-5.3-Codex) — ✅ `c62f6586` (3 tests passed)
- [x] CT-3 🔄 — Commit task: scope P2-A → `feat(plan-p2): dob observability flags` → push (GPT-5.3-Codex) — ✅ `c62f6586`

### Phase 3 — Tests, validation, and closure

- [x] P3-A 🔄 — Añadir/ajustar assertions golden para `dob` en `test_golden_extraction_regression.py` y ejecutar suite focalizada (benchmark dob + unit normalización + observability + regresión golden) (GPT-5.3-Codex) — ✅ `f0fd5398`
- [x] P3-B 🔄 — Ejecutar suite completa y preparar evidencia reproducible para body de PR (totales, pass/fail, EM, null misses, false positives, delta vs baseline) (GPT-5.3-Codex) — ✅ `f0fd5398` — evidencia: EM 16/18 (88.9%), null_misses=2, false_positives=0; golden docB dob visible tras reprocess/build
- [x] CT-4 🔄 — Commit task: scope P3-A + P3-B → `test(plan-p3): dob golden regression and validation evidence` → push (GPT-5.3-Codex) — ✅ `f0fd5398`
- [x] P3-C 🚧 — Hard-gate: validación de usuario con evidencia y decisión go/no-go (Claude Opus 4.6) — ✅ GO (88.9% EM, 0 FP, 2 null misses)
- [x] P3-D 🔄 — Post-gate: ajustar `MIN_EXACT_MATCH_RATE` al valor alcanzado menos 5 pp, actualizar guardrails de `dob` en `extraction-quality.md`, añadir a Golden Fields status (GPT-5.3-Codex) — ✅ `fb4644c4`
- [x] CT-5 🔄 — Commit task: scope P3-D → `docs(plan-p3): dob threshold lock and extraction-quality update` → push (GPT-5.3-Codex) — ✅ `fb4644c4`

---

## Acceptance criteria

1. `dob` alcanza ≥ 85 % exact match en benchmark sintético.
2. No hay regresiones en tests golden existentes (`pet_name`, `clinic_name`, `clinic_address`, `microchip_id`, otros campos).
3. `dob` conectado al normalizador de fechas (`_normalize_date_value`) en `normalize_canonical_fields()`.
4. `dob` en `DATE_TARGET_KEYS` con anchors de nacimiento y guards de desambiguación.
5. Flags de observabilidad (`dob_future_date`, `dob_implausibly_old`, `dob_matches_visit_date`) implementados con tests.
6. Guardrails de `dob` documentados en `extraction-quality.md` § 2.
7. `dob` listado como Golden Field completado en `extraction-quality.md` § 6.
8. Cambios limitados al path de `dob`.

---

## Cola de prompts

### P0-A — Synthetic fixtures

```text
Contexto: estamos ejecutando el golden loop para el campo `dob` (fecha de nacimiento del paciente). La rama es `feat/golden-loop-paciente-dob` en el worktree `d:\Git\veterinary-medical-records-golden-loop`. Crea la rama desde `origin/main` si no existe.

Crea fixtures sintéticos para `dob`.

Bajo `backend/tests/fixtures/synthetic/dob/dob_cases.json` incluye al menos 15 casos:

**Positivos (con label explícito):**
- "Fecha de nacimiento: 15/03/2018"
- "F. Nac.: 3/7/15" (formato corto, año 2 dígitos)
- "F/Nto: 2020-01-10" (formato ISO)
- "Nacimiento: 08.12.2019" (separador punto)
- "Nac.: 22-06-2017" (separador guión)
- "DOB: 01/11/2021"
- "Fecha nac: 5/1/20"
- "F Nac - 30/04/2016"

**Positivos con ruido OCR:**
- Label con espacios extra o errores tipográficos ("Fcha nacimiento", "Fecha  de nacimiento")
- Fecha embebida en bloque de datos del paciente con múltiples campos

**Null cases (expected_dob = null):**
- Documento sin ninguna fecha de nacimiento
- Documento solo con fecha de visita
- Documento con fecha de alta y fecha de documento pero sin dob

**False-positive traps (expected_dob = null o el valor correcto de dob, no la fecha trampa):**
- Documento con "Fecha de visita: 10/02/2024" y "Fecha de nacimiento: 15/03/2018" — expected_dob = "15/03/2018"
- Documento solo con "Consulta: 22/01/2025" sin dob — expected_dob = null
- Documento con "Alta: 05/03/2024" sin dob — expected_dob = null

Formato: `{"cases": [{"id": "...", "text": "...", "expected_dob": "..." | null}]}`

Añade también un `README.md` describiendo la estructura del fixture.

NO toques el archivo PLAN. NO hagas commit. Solo crea los fixtures.
```

⚠️ AUTO-CHAIN → P0-B

### P0-B — Baseline benchmark

```text
Crea `backend/tests/benchmarks/test_dob_extraction_accuracy.py` siguiendo el patrón exacto de `test_microchip_extraction_accuracy.py`, adaptado a `dob`:

1. Carga fixtures de `dob_cases.json`.
2. Extrae `dob` vía `_build_interpretation_artifact()`.
3. Normaliza para comparación usando `normalize_canonical_fields()`.
4. Test parametrizado por caso (`test_dob_extraction_case[<id>]`).
5. Test summary de accuracy (`test_dob_accuracy_summary`).
6. `MIN_EXACT_MATCH_RATE = 0.0` (baseline — se ajustará post hard-gate).

Ejecuta el benchmark y reporta accuracy inicial — exact matches, null misses, false positives.

NO toques el archivo PLAN. NO hagas commit todavía.
```

⚠️ AUTO-CHAIN → CT-1

### CT-1 — Commit task Phase 0

```text
Ejecuta el commit task CT-1 según SCOPE BOUNDARY:

**STEP 0 — Branch Verification:**
- Rama esperada: `feat/golden-loop-paciente-dob`
- Si no existe, créala desde `origin/main`.

**STEP A — Commit Code:**
- Format pre-flight: formatters + L1.
- Stage todo excepto PLAN: `git add -A -- . ':!docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-04_GOLDEN-LOOP-DOB.md'`
- Commit: `test(plan-p0): dob golden-loop baseline fixtures and benchmark`

**STEP B — Commit Plan Update:**
- Marca P0-A, P0-B, CT-1 como `[x]` en Estado de ejecución (con SHA del code commit).
- Limpia Prompt activo.
- Stage y commit solo el PLAN.

**STEP C — Push:**
- `git push origin feat/golden-loop-paciente-dob`
- Primera vez: crear draft PR con `gh pr create --draft`.

**STEP D — Update PR description.**

**STEP E — CI Gate** (según modo CI seleccionado).

**STEP F — Chain or Handoff.**
```

⚠️ AUTO-CHAIN → P1-A

### P1-A — Connect dob to date normalizer

```text
Conecta `dob` al pipeline de normalización y debug:

1. En `backend/app/application/field_normalizers.py` → `normalize_canonical_fields()`:
   - Añade `normalized["dob"] = _normalize_date_value(normalized.get("dob"))` junto a las otras fechas.

2. En `backend/app/application/processing/constants.py`:
   - Añade `"dob"` a `MVP_COVERAGE_DEBUG_KEYS`.

3. Amplía la regex de `dob` en `_LABELED_PATTERNS` para cubrir más variantes de label:
   - Actual: `(?:f(?:echa)?\s*(?:de\s*)?(?:nacimiento|nac\.|nac)|dob|birth\s*date)`
   - Añadir soporte para: `f/nto`, `f\.?\s*nac`, `nacimiento`, `fecha\s*nac`, formatos donde el año va primero (`AAAA-MM-DD`), y la variante `fnto`.

Ejecuta tests existentes para confirmar que no hay regresiones.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → P1-B

### P1-B — Date anchor mining for dob

```text
Añade `dob` al sistema de mining por anchors de fecha:

1. En `backend/app/application/processing/constants.py`:
   - Añade `"dob"` a `DATE_TARGET_KEYS`.
   - Añade entrada en `_DATE_TARGET_ANCHORS`: `"dob": ("nacimiento", "nac.", "nac", "f. nac", "f/nto", "fnto", "dob", "birth", "fecha de nacimiento")`.
   - Añade entrada en `_DATE_TARGET_PRIORITY`: `"dob": 1` (prioridad baja vs visit_date para evitar colisión).

2. Confirma que los guards existentes en `visit_date` (reject birthdate context) sean recíprocos: si `dob` tiene anchor de nacimiento, no debe ser promovido como visit_date y viceversa.

3. Ejecuta el benchmark de `dob` y reporta delta vs baseline.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → P1-C

### P1-C — Normalization unit tests

```text
Crea `backend/tests/unit/test_dob_normalization.py` con tests unitarios dedicados:

**Formatos válidos → esperado DD/MM/YYYY o DD/MM/YY:**
- "15/03/2018" → "15/03/2018"
- "3/7/15" → "03/07/15"
- "2020-01-10" → "10/01/2020"
- "08.12.2019" → "08/12/2019"
- "22-06-2017" → "22/06/2017"
- "5/1/20" → "05/01/20"

**Inválidos → None:**
- None, "", "texto sin fecha", "99/99/9999", "00/00/0000"

**Edge cases:**
- Fecha con label residual: "Nac.: 15/03/2018" (el normalizador debe extraer la fecha)
- Año de 2 dígitos en rango animal (00-25 → 2000-2025 es plausible)

Ejecuta tests y reporta resultados.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → P1-D

### P1-D — Benchmark delta and confidence tuning

```text
Ejecuta el benchmark de `dob` completo y reporta delta vs baseline:
- Exact match rate actual vs baseline
- Null misses (esperado no-null pero obtuvo null)
- False positives (esperado null pero obtuvo valor)

Si el EM rate es < 85%, investiga los casos fallidos e intenta ajustes mínimos en:
- Confidence/ranking de candidates
- Labels o anchors
- Normalizador

Re-ejecuta benchmark tras cada ajuste. El objetivo es ≥ 85% EM.

Ejecuta también los benchmarks existentes (pet_name, clinic_name, clinic_address, microchip_id) para confirmar 0 regresiones.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → CT-2

### CT-2 — Commit task Phase 1

```text
Ejecuta el commit task CT-2 según SCOPE BOUNDARY:

**STEP A — Commit Code:**
- Format pre-flight: formatters + L1.
- Stage todo excepto PLAN.
- Commit: `feat(plan-p1): dob extraction hardening — normalizer, anchors, labels, unit tests`

**STEP B — Commit Plan Update:**
- Marca P1-A, P1-B, P1-C, P1-D, CT-2 como `[x]` con SHA.
- Limpia Prompt activo.

**STEP C — Push.**
**STEP D — Update PR.**
**STEP E — CI Gate.**
**STEP F — Chain or Handoff.**
```

⚠️ AUTO-CHAIN → P2-A

### P2-A — Observability flags

```text
Añade señales de observabilidad/triage para `dob` sospechoso:

1. **`dob_future_date`** — flag si la fecha de nacimiento es posterior a hoy.
2. **`dob_implausibly_old`** — flag si la fecha implica un animal de más de 40 años.
3. **`dob_matches_visit_date`** — flag si `dob` == `visit_date` (posible confusión de campos).

Implementa en el módulo de observability/triage existente, siguiendo el patrón de `microchip_phone_context` / `microchip_document_id_context`.

Incluye tests unitarios para cada flag.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → CT-3

### CT-3 — Commit task Phase 2

```text
Ejecuta el commit task CT-3 según SCOPE BOUNDARY:

**STEP A — Commit Code:**
- Format pre-flight: formatters + L1.
- Commit: `feat(plan-p2): dob observability flags`

**STEP B — Commit Plan Update:**
- Marca P2-A, CT-3 como `[x]` con SHA.

**STEP C — Push.**
**STEP D — Update PR.**
**STEP E — CI Gate.**
**STEP F — Chain or Handoff.**
```

⚠️ AUTO-CHAIN → P3-A

### P3-A — Golden regression and focused suite

```text
Añade/ajusta assertions golden para `dob` en `test_golden_extraction_regression.py`:
- Al menos 2 casos: uno con label explícito, uno con formato variante.
- Ejecuta suite focalizada:
  - `pytest backend/tests/benchmarks/test_dob_extraction_accuracy.py -q`
  - `pytest backend/tests/unit/test_dob_normalization.py -q`
  - `pytest backend/tests/unit/test_golden_extraction_regression.py -k dob -q`
  - Observability tests de dob

Reporta resultados reproducibles.

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ AUTO-CHAIN → P3-B

### P3-B — Validation run

```text
Ejecuta suite focalizada completa (unit + golden + benchmark + observability) y resume para body de PR:
- Total tests, pass/fail
- Exact match rate vs baseline
- Null misses y false positives
- Delta vs threshold (≥ 85%)
- Benchmarks de otros campos: 0 regresiones

NO toques el archivo PLAN. NO hagas commit.
```

⚠️ HARD-GATE → P3-C (Claude)

### P3-C — Hard-gate

```text
P3-C 🚧 — Hard-gate: validación de usuario con evidencia y decisión go/no-go (Claude Opus 4.6).

Claude revisa:
1. Benchmark results (EM rate, null misses, false positives)
2. Coherencia de fixtures (variedad, edge cases)
3. Regresiones en otros campos
4. Observability flags correctos
5. Guardrails propuestos para extraction-quality.md

Decisión: GO / NO-GO con justificación.
```

### P3-D — Post-gate closure

```text
Tras aprobación explícita de Claude/usuario en P3-C:

1. En `backend/tests/benchmarks/test_dob_extraction_accuracy.py`:
   - Ajusta `MIN_EXACT_MATCH_RATE` al valor alcanzado menos 5 puntos porcentuales.

2. En `docs/projects/veterinary-medical-records/02-tech/extraction-quality.md`:
   - § 2 Field Guardrails Catalog: añade sección `### dob` con tabla de guardrails:
     | Aspect | Rule |
     | Business meaning | Patient date of birth |
     | Accept | Valid calendar date in DD/MM/YYYY, D/M/YY, YYYY-MM-DD. Plausible age (0–40 years). |
     | Reject | Future dates, implausibly old (> 40 years), non-date strings. |
     | Common failures | visit_date promoted as dob, unlabeled date captured as dob. |
     | Implementation | `field_normalizers.py`, `constants.py` (DATE_TARGET_KEYS + anchors). |
     | Tests | `test_dob_extraction_accuracy.py`, `test_dob_normalization.py`, golden regression. |
   - § 6 Golden Fields — Current Status: añade `dob` como ✅.

3. Actualiza PR body con evidencia final.

NO toques el archivo PLAN hasta STEP B del SCOPE BOUNDARY.
```

⚠️ AUTO-CHAIN → CT-5

### CT-5 — Commit task Phase 3 closure

```text
Ejecuta el commit task CT-5 según SCOPE BOUNDARY:

**STEP A — Commit Code:**
- Format pre-flight: formatters + L1.
- DOC NORMALIZATION si hay .md modificados.
- Commit: `docs(plan-p3): dob threshold lock and extraction-quality update`

**STEP B — Commit Plan Update:**
- Marca P3-D, CT-5 como `[x]` con SHA.

**STEP C — Push.**
**STEP D — Update PR.**
**STEP E — CI Gate.**
**STEP F — Chain or Handoff** (iteration complete → stop).
```

---

## Prompt activo

_(vacío — se poblará dinámicamente)_
