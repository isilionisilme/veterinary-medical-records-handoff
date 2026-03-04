# Plan: Golden Loop — `microchip_id` extraction hardening

> **Operational rules:** See [execution-rules.md](../../03-ops/execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `feat/golden-loop-paciente-microchip`
**PR:** _(pending)_
**Prerequisito:** `main` estable con tests verdes.

## Context

`microchip_id` (Microchip del paciente) ya existe en el contrato global (`shared/global_schema_contract.json`) y está conectado al pipeline de extracción/normalización. Actualmente hay cobertura parcial, pero faltan piezas clave del patrón golden loop reciente (`pet_name`, `clinic_name`, `clinic_address`):

- **No dedicated fixtures** — no `backend/tests/fixtures/synthetic/microchip/`.
- **No benchmark test** — no `backend/tests/benchmarks/test_microchip_extraction_accuracy.py`.
- **No dedicated normalization unit tests** — falta suite específica para `_normalize_microchip_id` y `normalize_microchip_digits_only`.
- **No microchip-specific observability/triage** — no flags de sospecha dedicados.
- **No hard-gate evidence package** — falta corrida focalizada con evidencia reproducible en formato PR.

## Objective

- Alcanzar ≥ 85% exact match en benchmark sintético de `microchip_id`.
- Evitar regresiones en los golden loops existentes y en el resto del schema canónico.
- Añadir evidencia reproducible (fixtures + benchmark + tests unit/golden + observability).

## Scope Boundary (strict)

- **In scope:** extracción, normalización, ranking y observabilidad de `microchip_id`; fixtures sintéticos; benchmark y tests focalizados del campo.
- **Out of scope:** cambios de UX/frontend, rediseño del contrato global, refactors no relacionados, cambios de reglas en otros campos.

---

## Estado de ejecución

**Leyenda**
- 🔄 auto-chain — ejecutable por Codex
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Baseline and fixtures

- [x] P0-A 🔄 — Crear fixtures sintéticos de `microchip_id` con casos positivos/negativos/ruido OCR bajo `backend/tests/fixtures/synthetic/microchip/` (GPT-5.3-Codex) — ✅ `microchip_cases.json` + `README.md` creados (18 casos)
- [x] P0-B 🔄 — Crear benchmark `backend/tests/benchmarks/test_microchip_extraction_accuracy.py` y medir baseline inicial (GPT-5.3-Codex) — ✅ baseline: 14/18 EM (77.8%), null_misses=4, false_positives=0

### Phase 1 — Extraction improvements (`microchip_id` only)

- [x] P1-A 🔄 — Hardening de candidate mining para `microchip_id` (labels, guards de falsos positivos numéricos) sin afectar otros campos (GPT-5.3-Codex) — ✅ soporte para `identificación electrónica`, `transponder`, prefijo OCR `N-` y dígitos con separadores
- [x] P1-B 🔄 — Añadir tests unitarios dedicados de normalización de `microchip_id` y ajustar normalizador solo si el benchmark lo requiere (GPT-5.3-Codex) — ✅ `test_microchip_normalization.py` + robustez en normalizador para evidencia extendida y dígitos con separadores
- [x] P1-C 🔄 — Ajustar confidence/ranking de candidatos de `microchip_id` y medir delta vs baseline (GPT-5.3-Codex) — ✅ delta benchmark: 77.8% (14/18) → 100% (18/18), null_misses: 4 → 0, false_positives: 0 → 0

### Phase 2 — Observability and quality gates

- [x] P2-A 🔄 — Añadir señales de observabilidad/triage para `microchip_id` sospechoso (longitud inválida, contaminación no numérica, patrones de teléfono/NIF) + tests (GPT-5.3-Codex) — ✅ flags: `microchip_phone_context`, `microchip_document_id_context`, `microchip_phone_like_digits`; suite focalizada verde

### Phase 3 — Tests, validation, and closure

- [x] P3-A 🔄 — Añadir/ajustar regresiones golden de `microchip_id` y ejecutar suite focalizada (unit + golden + benchmark + observability) (GPT-5.3-Codex) — ✅ regresiones añadidas: `transponder` y dígitos con separadores en `test_golden_extraction_regression.py`
- [x] P3-B 🔄 — Preparar evidencia reproducible para body de PR (totales, pass/fail, EM, null misses, false positives, delta vs threshold) (GPT-5.3-Codex) — ✅ suite focalizada: 53 passed; benchmark: 18/18 (100%), baseline previo 14/18 (77.8%), null_misses: 4→0, false_positives: 0→0
- [x] P3-C 🚧 — Hard-gate: validación de usuario con ejemplos reales/sintéticos y decisión go/no-go (Claude Opus 4.6) — ✅ GO aprobado: 18/18 EM (100%), 0 FP, 0 null misses, 72 benchmarks verdes, doc real validado
- [x] P3-D 🔄 — Post-gate closure: actualizar umbral `MIN_EXACT_MATCH_RATE` con margen de 5% y cerrar evidencia final de PR (GPT-5.3-Codex) — ✅ threshold=0.95 (100%-5pp), benchmark microchip 19/19, benchmark global 72/72, `7e32e946`

---

## Acceptance criteria

1. `microchip_id` alcanza ≥ 85% exact match en benchmark sintético.
2. No hay regresiones en tests golden existentes (`pet_name`, `clinic_name`, `clinic_address`, otros campos).
3. Falsos positivos numéricos relevantes (teléfono, NIF/documento, códigos no-chip) quedan mitigados por guards/ranking.
4. Triage reporta estados missing/suspicious de `microchip_id` en salidas de observabilidad.
5. Cambios limitados al path de `microchip_id`.

## Cola de prompts

### P0-A — Synthetic fixtures

```text
Crea fixtures sintéticos para microchip_id.
Bajo backend/tests/fixtures/synthetic/microchip/microchip_cases.json incluye al menos 15 casos:
- Labels explícitos ("Microchip", "Nº chip", "Identificación electrónica")
- Casos sin label con contexto clínico válido
- OCR ruidoso (espacios, guiones, prefijos tipo N-)
- Límites de longitud válidos (9 y 15 dígitos)
- Null cases (sin chip)
- False-positive traps (teléfonos, NIF/documento, códigos no-chip)
Formato: {"cases": [{"id": "...", "text": "...", "expected_microchip_id": "..."}]}
```

⚠️ AUTO-CHAIN → P0-B

### P0-B — Baseline benchmark

```text
Crea backend/tests/benchmarks/test_microchip_extraction_accuracy.py siguiendo el patrón exacto de test_pet_name_extraction_accuracy.py, adaptado a microchip_id:
- Carga fixtures de microchip_cases.json
- Extrae microchip_id vía _build_interpretation_artifact
- Normaliza para comparación (whitespace/case cuando aplique)
- Test parametrizado por caso + summary de accuracy
- MIN_EXACT_MATCH_RATE = 0.0 (baseline)
Ejecuta benchmark y reporta accuracy inicial con evidencia.
```

⚠️ AUTO-CHAIN → P1-A

### P1-A — Candidate mining hardening

```text
Mejora candidate mining de microchip_id en candidate_mining.py:
- Refuerza labels válidos de microchip en español/variantes OCR
- Añade guards contra números ajenos (teléfono, NIF, IDs administrativos)
- Mantén alcance estricto: no cambiar comportamiento de otros campos
Ejecuta tests relevantes y reporta resultados.
```

⚠️ AUTO-CHAIN → P1-B

### P1-B — Normalization unit coverage

```text
Añade tests unitarios dedicados para _normalize_microchip_id y normalize_microchip_digits_only:
- Válidos: dígitos limpios, con espacios/guiones/prefijos
- Inválidos: vacío, None, sin secuencia 9-15 dígitos
- Guardas de contaminación alfanumérica
Ajusta normalizador solo si hay evidencia de fallo en benchmark/tests.
```

⚠️ AUTO-CHAIN → P1-C

### P1-C — Confidence/ranking

```text
Ajusta confianza/ranking de candidatos microchip_id:
- Label explícito + longitud válida: alta
- Contexto compatible sin label: media
- Ambiguo o patrón de documento/teléfono: baja
No modifiques la lógica de otros campos.
Ejecuta benchmark y reporta delta vs baseline.
```

⚠️ AUTO-CHAIN → P2-A

### P2-A — Observability

```text
Agrega señales de observabilidad/triage para microchip_id:
- suspicious por longitud fuera de 9-15
- suspicious por residuos no numéricos tras normalización
- suspicious por coincidencia con patrones de teléfono/NIF
Incluye tests unitarios para cada flag.
```

⚠️ AUTO-CHAIN → P3-A

### P3-A — Tests and regression protection

```text
Añade/ajusta assertions golden para microchip_id en test_golden_extraction_regression.py y ejecuta suite focalizada:
- benchmark microchip
- tests unitarios de normalización microchip
- tests de observability
- regresión golden
Reporta resultados reproducibles.
```

⚠️ AUTO-CHAIN → P3-B

### P3-B — Validation run

```text
Ejecuta suite focalizada (unit + golden + benchmark + observability), y resume para body de PR:
- Total tests, pass/fail
- Exact match rate vs baseline
- Null misses y false positives
- Delta vs threshold (≥ 85%)
```

⚠️ HARD-GATE → P3-C (Claude)

### P3-D — Post gate closure

```text
Tras aprobación explícita de Claude/usuario en P3-C, ajusta MIN_EXACT_MATCH_RATE al valor alcanzado con margen de 5% y actualiza el body del PR con evidencia final.
```

## Prompt activo

```text
P3-C 🚧 — Hard-gate: validación de usuario con ejemplos reales/sintéticos y decisión go/no-go (Claude Opus 4.6).
```
