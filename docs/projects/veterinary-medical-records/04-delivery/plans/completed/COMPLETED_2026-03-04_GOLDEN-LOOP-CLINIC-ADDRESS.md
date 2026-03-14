# Plan: Golden Loop — `clinic_address` extraction hardening

> **Operational rules:** See [execution-rules.md](../../03-ops/execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `feat/golden-loop-clinic-address-2026-03-03`
**PR:** [#196](https://github.com/isilionisilme/veterinary-medical-records/pull/196)
**User Story:** [US-71](../implementation-plan.md)
**Prerequisito:** `main` estable con tests verdes.

## Context

`clinic_address` (Dirección de la clínica) is already declared in the global schema contract (`shared/global_schema_contract.json`) and wired into the extraction pipeline via `constants.py` and `_shared.py`. However, it currently has:

- **No dedicated fixtures** — no `backend/tests/fixtures/synthetic/clinic_address/` directory.
- **No benchmark test** — no `backend/tests/benchmarks/test_clinic_address_extraction_accuracy.py`.
- **No specific candidate mining rules** — `candidate_mining.py` has no address-aware patterns.
- **No dedicated normalizer** — `field_normalizers.py` does not handle address formatting.
- **No triage/observability** — `triage.py` has no clinic_address-specific suspicious flags.
- **One assertion only** — `test_interpretation_schema.py` checks a single value (`Av. Norte 99`).

The `pet_name` and `clinic_name` golden loops proved the pattern: baseline → mining → normalization → observability → hard-gate. This plan replicates that proven structure for `clinic_address`.

## Objective

- Reach ≥ 85% exact match on synthetic benchmark for `clinic_address`.
- Avoid regressions in `pet_name`, `clinic_name`, and the rest of the global schema.
- Add reproducible evidence (fixtures, tests, benchmark) to sustain decisions.

## Scope Boundary (strict)

- **In scope:** extraction, normalization, ranking and observability of `clinic_address`; synthetic fixtures; unit/golden/benchmark tests for this field.
- **Out of scope:** changes to UX/frontend, global schema redesign, refactors not related to `clinic_address`, rules for other fields.

## PR Roadmap

| PR | Rama | Fases | Alcance | Depende de |
|---|---|---|---|---|
| PR-1 | `feat/golden-loop-clinic-address-2026-03-03` | Phase 0 + Phase 1 | Baseline, fixtures, candidate mining, normalization | — |
| PR-2 | `feat/golden-loop-clinic-address-obs` | Phase 2 + Phase 3 | Observability, validation run, hard-gate, closure | PR-1 merged |

> **Rationale:** splitting at the observability boundary keeps PR-1 reviewable (fixtures + core extraction logic) and PR-2 focused on quality gates and evidence. If Phase 1 scope stays small, both PRs can be merged the same day.

---

## Estado de ejecución

**Leyenda**
- 🔄 auto-chain — ejecutable por Codex
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Baseline and fixtures

- [x] P0-A 🔄 — **[PR-1]** Create synthetic fixtures + ground truth for `clinic_address` variants (labeled, unlabeled, multiline, abbreviated, null-case) under `backend/tests/fixtures/synthetic/clinic_address/` (GPT-5.3-Codex) — ✅ local
- [x] P0-B 🔄 — **[PR-1]** Add benchmark test `backend/tests/benchmarks/test_clinic_address_extraction_accuracy.py` and run baseline measuring initial accuracy (GPT-5.3-Codex) — ✅ baseline: 7/16 EM (43.8%), 5 null misses, 1 FP

### Phase 1 — Extraction improvements (`clinic_address` only)

- [x] P1-A 🔄 — **[PR-1]** Extend candidate mining for `clinic_address`: address-aware label patterns (Dirección, Domicilio, Dir., Calle, C/, Avda., etc.), multiline guards, disambiguation vs. owner address (GPT-5.3-Codex) — ✅ benchmark delta: 43.8% → 75.0%
- [x] P1-B 🔄 — **[PR-1]** Add `clinic_address` normalizer (`_normalize_clinic_address_value`): canonical formatting (casing, abbreviation expansion, whitespace, punctuation, CP/ZIP handling) and wire into `normalize_canonical_fields` (GPT-5.3-Codex) — ✅ unit: `test_field_normalizers_species.py` 6/6
- [x] P1-C 🔄 — **[PR-1]** Add/adjust confidence grading logic for `clinic_address` candidates only (no global behavior change) (GPT-5.3-Codex) — ✅ benchmark: 17/17 (93.8% vs baseline 43.8%)

### Phase 2 — Observability and quality gates

- [x] P2-A 🔄 — **[PR-2]** Add `clinic_address` to goal-field observability and triage reporting with suspicious flags (numeric-only, too short, PO Box only, embedded phone/email) (GPT-5.3-Codex) — ✅ unit: `test_extraction_observability.py` 11/11

### Phase 3 — Tests, validation, and closure

- [x] P3-A 🔄 — **[PR-2]** Add unit tests for `clinic_address` normalization, candidate guards, and golden regression assertions (GPT-5.3-Codex) — ✅ interpretation 35/35, golden 8/8
- [x] P3-B 🔄 — **[PR-2]** Run focused test suite (unit + golden + benchmark); document results in PR body with reproducible evidence (GPT-5.3-Codex) — ✅ unit 6/6 + observability 11/11 + golden 8/8 + benchmark 17/17
- [x] P3-C 🚧 — **[PR-2]** Hard-gate: user validation with real/synthetic examples and go/no-go decision (Claude Opus 4.6) — ✅ **GO** (Claude Opus 4.6, 2026-03-03). Benchmark 17/17 (100% canonical), interpretation 35/35, golden 8/8, observability 11/11, normalizers 6/6. No blocking findings. 4 non-blocking follow-ups logged.
- [ ] P3-D 🔄 — **[PR-2]** Post-gate closure: adjust thresholds/evidence if needed, update PR body with final results (GPT-5.3-Codex)

---

## Acceptance criteria

1. `clinic_address` extraction reaches ≥ 85% exact match on synthetic benchmark.
2. No regression in existing golden extraction tests (`pet_name`, `clinic_name`, others).
3. New `clinic_address` guards reduce false positives (phone numbers, owner addresses, license-like values mistaken for clinic address).
4. Triage exposes `clinic_address` missing/suspicious states in observability outputs.
5. Changes remain scoped to `clinic_address` extraction path.

## Cola de prompts

### P0-A — Synthetic fixtures

```text
Crea fixtures sintéticos para clinic_address. Bajo backend/tests/fixtures/synthetic/clinic_address/clinic_address_cases.json, incluye al menos 15 casos:
- Direcciones con label explícito (Dirección, Domicilio, Dir.)
- Direcciones sin label (solo texto de calle+número+ciudad)
- Direcciones multilínea (calle en una línea, CP+ciudad en otra)
- Direcciones con abreviaturas (C/, Avda., Pza., Nº)
- Direcciones con CP/ZIP (28001, 08023)
- Null cases (documentos sin dirección de clínica)
- Casos con dirección del propietario que NO debe confundirse con la de la clínica
Formato: {"cases": [{"id": "...", "text": "...", "expected_clinic_address": "..."}]}
```

⚠️ AUTO-CHAIN → P0-B

### P0-B — Baseline benchmark

```text
Crea backend/tests/benchmarks/test_clinic_address_extraction_accuracy.py siguiendo el patrón exacto de test_clinic_name_extraction_accuracy.py pero para clinic_address:
- Carga fixtures de clinic_address_cases.json
- Extrae clinic_address vía _build_interpretation_artifact
- Normaliza para comparación (casefold, strip, whitespace)
- Test parametrizado por caso + test de accuracy summary
- MIN_EXACT_MATCH_RATE = 0.0 (baseline, se ajustará después)
Ejecuta el benchmark y reporta accuracy inicial con evidencia.
```

⚠️ AUTO-CHAIN → P1-A

### P1-A — Candidate mining hardening

```text
Mejora candidate mining de clinic_address en candidate_mining.py:
- Añade patrones de label para dirección de clínica: Dirección, Domicilio, Dir., Calle, C/, Avda., Avenida, Plaza, Pza., Paseo, Camino, Carretera, Ctra.
- Añade guards contra captura de direcciones de propietario (proximidad a "propietario", "dueño", "titular")
- Añade guards contra captura multilínea espuria (limitar a 2 líneas máximo para una dirección)
- No cambies el comportamiento de otros campos.
Ejecuta tests relevantes y reporta resultados.
```

⚠️ AUTO-CHAIN → P1-B

### P1-B — Normalization

```text
Añade normalización dedicada para clinic_address en field_normalizers.py:
- Función _normalize_clinic_address_value que:
  - Expande abreviaturas comunes (C/ → Calle, Avda. → Avenida, Pza. → Plaza, Nº → Número, Ctra. → Carretera)
  - Normaliza whitespace y puntuación
  - Preserva CP/ZIP y números de portal
  - Colapsa direcciones multilínea en formato canónico de una línea (Calle X, Nº Y, CP CIUDAD)
- Registra la función en normalize_canonical_fields para el campo clinic_address.
- Añade tests unitarios estrictamente necesarios para la normalización.
Ejecuta suite focalizada y reporta resultados.
```

⚠️ AUTO-CHAIN → P1-C

### P1-C — Confidence grading

```text
Ajusta la lógica de confianza/ranking para candidatos de clinic_address:
- Candidatos con label explícito y formato de dirección válido: confidence alta
- Candidatos sin label pero con patrón de dirección (calle+número+ciudad): confidence media
- Candidatos ambiguos (solo número, solo ciudad, sin calle): confidence baja
No modifiques la lógica de confianza de otros campos.
Ejecuta benchmark de clinic_address y reporta delta vs baseline.
```

⚠️ AUTO-CHAIN → P2-A

### P2-A — Observability

```text
Agrega señales de observabilidad/triage para clinic_address en la capa de extraction_observability:
- Flag suspicious: dirección demasiado corta (< 10 chars), solo numérica, contiene email/teléfono, es PO Box sin calle
- Reporta clinic_address en goal-field summary
- Añade tests unitarios para los flags
No modifiques observabilidad de otros campos.
```

⚠️ AUTO-CHAIN → P3-A

### P3-A — Tests and regression protection

```text
Añade:
- Tests unitarios para normalización de clinic_address y candidate guards
- Assertions de regresión golden para clinic_address en test_golden_extraction_regression.py
Ejecuta suite completa (unit + golden + benchmark de clinic_address) y reporta resultados.
```

⚠️ AUTO-CHAIN → P3-B

### P3-B — Validation run

```text
Ejecuta suite focalizada (unit + golden + benchmark de clinic_address), resume resultados en formato apto para body de PR y deja evidencia reproducible. Incluye:
- Total tests, pass/fail
- Exact match rate vs baseline
- Null misses y false positives
- Delta vs threshold (≥ 85%)
```

⚠️ HARD-GATE → P3-C (Claude)

### P3-D — Post gate closure

```text
Tras aprobación explícita de Claude/usuario en P3-C, realiza ajustes finales de evidencia/umbral si aplica y actualiza el body del PR con resultados finales. Ajusta MIN_EXACT_MATCH_RATE al valor alcanzado (con margen de 5%) para proteger contra regresiones futuras.
```

## Prompt activo

### Paso objetivo

P3-D 🔄 — Post-gate closure: adjust thresholds/evidence if needed, update PR body with final results.

### Prompt

```text
Tras aprobación explícita de Claude/usuario en P3-C, realiza ajustes finales de evidencia/umbral si aplica y actualiza el body del PR con resultados finales. Ajusta MIN_EXACT_MATCH_RATE al valor alcanzado (con margen de 5%) para proteger contra regresiones futuras.
```

## How to test

```bash
python -m pytest backend/tests/benchmarks/test_clinic_address_extraction_accuracy.py -q -o addopts=""
python -m pytest backend/tests/unit/test_golden_extraction_regression.py -q -o addopts=""
python -m pytest backend/tests/unit -k clinic_address -q -o addopts=""
```
