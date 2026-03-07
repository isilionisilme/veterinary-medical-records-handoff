# Plan: Golden Loop — Pet Name extraction hardening

> **Operational rules:** See `docs/projects/veterinary-medical-records/ops/EXECUTION_RULES.md` for execution protocol, handoff rules, and step completion integrity.

**Rama:** `feature/golden-loop-pet-name`
**PR:** [#182](https://github.com/isilionisilme/veterinary-medical-records/pull/182)
**Prerequisito:** Branch created from `main` in isolated worktree.

## Context

`pet_name` is currently a critical field with weak extraction coverage:

- One labeled regex (`Paciente|Nombre del paciente|Patient`)
- One fragile heuristic (uppercase single word near species/chip tokens)
- No dedicated normalization for `pet_name`
- No golden regression assertions for `pet_name`
- No explicit triage flags for suspicious `pet_name` values

Goal: implement an end-to-end golden loop for one field (`pet_name`) as a reusable blueprint.

## Scope boundary (strict)

- **In scope:** `pet_name` extraction path only (candidate mining, normalization, confidence behavior for this field, observability/triage for this field, tests/fixtures for this field).
- **Out of scope:** LLM integration, OCR, schema-wide confidence redesign, other field extraction behavior.
- **Out of scope:** frontend feature work (except existing validation updates if strictly needed for `pet_name`).

---

## Estado de ejecución — actualizar al completar cada paso

**Leyenda**
- 🔄 auto-chain — ejecutable por Codex
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Baseline and fixtures

- [x] P0-A 🔄 — Create synthetic fixtures + ground truth for `pet_name` variants (labeled, unlabeled, noisy, null-case) under `backend/tests/fixtures/synthetic/pet_name/` (GPT-5.3-Codex) — ✅ `3523af93`
- [x] P0-B 🔄 — Add benchmark test `backend/tests/benchmarks/test_pet_name_extraction_accuracy.py` (GPT-5.3-Codex) — ✅ `df091939`
- [x] P0-C 🔄 — Run baseline benchmark and capture current pass/fail profile (GPT-5.3-Codex) — ✅ baseline: 8/15 EM (53.3%), 4 null misses (26.7%), 2 FP (13.3%)

### Phase 1 — Extraction improvements (`pet_name` only)

- [x] P1-A 🔄 — Extend labeled regex patterns for `pet_name` (animal/mascota/name variants) — ✅ `bd4a6e92` → 73.3% EM
- [x] P1-B 🔄 — Improve heuristic fallback for mixed-case and multi-token names with strong guards against address/license/phone false positives — ✅ `bca05887` → 80.0% EM
- [x] P1-C 🔄 — Add conservative `pet_name` normalization (`_normalize_pet_name_value`) and wire into `normalize_canonical_fields` — ✅ `7f3e18f1` → 100.0% EM
- [x] P1-D 🔄 — Add/adjust confidence grading logic for `pet_name` candidates only (no global behavior change) — ✅ `a3510ca4`

### Phase 2 — Observability and quality gates

- [x] P2-A 🔄 — Add `pet_name` to goal-field observability and triage reporting — ✅ `8f78ae2d`
- [x] P2-B 🔄 — Add suspicious flags for `pet_name` (numeric-only, too short, stopword, embedded date) — ✅ `8f78ae2d`

### Phase 3 — Tests and regression protection

- [x] P3-A 🔄 — Add unit tests for `pet_name` normalization and candidate guards — ✅ `d2187e82` (29 tests)
- [x] P3-B 🔄 — Add golden regression assertions for `pet_name` in `test_golden_extraction_regression.py` — ✅ `4b591420`
- [x] P3-C 🔄 — Run focused tests + benchmark; set minimum non-regression threshold in benchmark test — ✅ 442/442 green, `MIN_EXACT_MATCH_RATE=1.0`

### Phase 4 — Wrap-up

- [x] P4-A 🚧 — User review of extraction deltas and acceptable precision/recall tradeoff — ✅ approved ("Ahora sí sale bien")
- [x] P4-B 🔄 — Create PR with benchmark delta summary and rollback notes — ✅ PR #182 updated

---

## Acceptance criteria

1. `pet_name` extraction improves versus baseline on synthetic benchmark.
2. No regression in existing golden extraction tests.
3. New `pet_name` guards reduce false positives (addresses/phones/license-like values).
4. Triage exposes `pet_name` missing/suspicious states in observability outputs.
5. Changes remain scoped to `pet_name` path.

## How to test

- `python -m pytest backend/tests/benchmark/test_pet_name_extraction_accuracy.py -q -o addopts=""`
- `python -m pytest backend/tests/unit/test_golden_extraction_regression.py -q -o addopts=""`
- `python -m pytest backend/tests/unit -k pet_name -q -o addopts=""`

## Prompt activo

### Paso objetivo

_Completed._

### Prompt

`Continúa`