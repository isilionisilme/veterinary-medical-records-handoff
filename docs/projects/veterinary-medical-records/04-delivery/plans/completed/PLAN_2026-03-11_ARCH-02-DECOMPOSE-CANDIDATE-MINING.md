# Plan: ARCH-02 Decompose candidate_mining

> **Operational rules:** See [plan-execution-protocol.md](../../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary template, commit conventions, and handoff behavior.

**Branch:** `refactor/arch-02-implement-candidate-mining`
**PR:** See `## PR Roadmap`
**Backlog item:** [arch-02-decompose-candidate-mining.md](../../../Backlog/completed/arch-02-decompose-candidate-mining.md)
**Review artifact:** [PLAN_2026-03-11_ARCH-02-CORRECTNESS-FIXES.md](./PLAN_2026-03-11_ARCH-02-CORRECTNESS-FIXES.md)
**Prerequisite:** ARCH-03 completed (CI complexity gates)
**Worktree:** `D:\Git\worktrees\arch02-impl`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** Planning agent (plan authoring) -> Execution agent (implementation)
**Execution Mode:** `Autonomous`
**Model Assignment:** `Uniform`
**Automation Mode:** `Autonomous`
**Iteration:** pending

---

## Agent Instructions

1. Mark each task as completed as soon as it is finished in `Execution Status`.
2. Do not commit or push without explicit user approval (`Automation Mode: Supervisado`).
3. Keep scope strictly limited to ARCH-02 decomposition goals and acceptance criteria.
4. Preserve public API behavior: `_mine_interpretation_candidates()` contract and outputs must remain stable.

---

## Context

`backend/app/application/processing/candidate_mining.py` is a critical complexity hotspot:

- File size is around 1,100 LOC.
- `_mine_interpretation_candidates()` spans around 767 LOC.
- Cyclomatic complexity peaks at 163.
- The function currently mixes pattern registry, extraction orchestration, validation rules, heuristics, and ranking concerns.

ARCH-02 requires decomposition into maintainable architecture components while preserving runtime behavior and test compatibility.

---

## Objective

1. Reduce complexity by decomposing candidate mining into cohesive modules.
2. Separate regex pattern ownership from extraction logic.
3. Ensure no function exceeds 100 LOC and no function exceeds CC 20.
4. Keep `mine_candidates()` public behavior unchanged and pass all existing tests.

---

## Scope Boundary

- **In scope:** candidate mining decomposition, extraction modularization, validation relocation, pattern registry extraction, ranking extraction, import rewiring, regression verification.
- **Out of scope:** new extraction features, schema contract changes, behavior-altering heuristic tuning, unrelated processing module refactors.

---

## Design Decisions

### DD-1: Extract by field domain groups
Use field-group modules (identifiers, persons, locations, clinical, physical) rather than per-field files to balance cohesion, readability, and reviewability.

### DD-2: Introduce dedicated field pattern registry
Create `field_patterns.py` for regex patterns currently embedded in `candidate_mining.py` so pattern evolution and extractor logic evolve independently.

### DD-3: Keep validation close to extractor ownership
Validation logic is co-located with each extractor module (instead of a central validator class) to reduce indirection and improve maintainability.

### DD-4: Move ranking into standalone module
Move `_candidate_sort_key()` and `_map_candidates_to_global_schema()` into `candidate_ranking.py` to isolate scoring/ranking policy from extraction mechanics.

### DD-5: Keep candidate_mining as thin orchestrator
`candidate_mining.py` becomes an orchestration layer that composes external parsing helpers plus modular extractors and returns the same candidate bundle shape.

---

## PR Roadmap

Delivery published as 1 effective PR.

| PR | Branch | Steps | Scope | Status | URL |
|---|---|---|---|---|---|
| PR-1 | `refactor/arch-02-implement-candidate-mining` | A1-E4 | Candidate mining decomposition + parity restoration + validation + plan traceability | Ready to open | — |

**Merge strategy:** single PR. A multi-PR split was considered during execution, but the documentation closeout was absorbed into the same branch after validation and publication.

---

## Execution Status

**Legend**
- `🔄` auto-chain — executable by agent
- `🚧` hard-gate — user review or decision required

### Phase 1 - Baseline and extraction scaffolding

- [x] [PR-1] A1 🔄 — Confirm baseline callers/import graph for `_mine_interpretation_candidates()`, `_map_candidates_to_global_schema()`, and `_candidate_sort_key()`. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] A2 🔄 — Create `backend/app/application/processing/field_patterns.py` and move module-level compiled regex patterns from `candidate_mining.py` into it without behavior change. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] A3 🔄 — Create `backend/app/application/processing/extractors/` package scaffolding and shared extractor contracts/helpers. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`

### Phase 2 - Move ranking and schema mapping responsibilities

- [x] [PR-1] B1 🔄 — Create `backend/app/application/processing/candidate_ranking.py` with `_candidate_sort_key()` and `_map_candidates_to_global_schema()`. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] B2 🔄 — Update imports in `interpretation.py`, tests, and `processing_runner.py` re-export list to use `candidate_ranking.py`. — ✅ `no-commit (compatibility preserved via candidate_mining wrappers; no caller breakage introduced)`
- [x] [PR-1] B3 🔄 — Run targeted tests that cover ranking behavior and schema mapping. — ✅ `no-commit (pytest --no-cov targeted suite green)`

### Phase 3 - Extract candidate mining by domain group

- [x] [PR-1] C1 🔄 — Implement `extractors/identifiers.py` for `microchip_id` and `clinical_record_number` extraction plus validations. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] C2 🔄 — Implement `extractors/persons.py` for `owner_name` and `vet_name` extraction plus validations. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] C3 🔄 — Implement `extractors/locations.py` for `clinic_name`, `clinic_address`, and `owner_address` extraction plus disambiguation helpers. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] C4 🔄 — Implement `extractors/clinical.py` for diagnosis/treatment/procedure/vaccination/lab/imaging/line_item/language extraction. — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] C5 🔄 — Implement `extractors/physical.py` for pet identity and physical attributes (`pet_name`, `species`, `breed`, `sex`, `weight`, etc.). — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`

### Phase 4 - Recompose orchestrator and verify parity

- [x] [PR-1] D1 🔄 — Refactor `candidate_mining.py` into thin orchestration flow (line preprocessing, external date parsing calls, modular extractor composition). — ✅ `no-commit (implemented in working tree; awaiting user approval before commit workflow)`
- [x] [PR-1] D2 🔄 — Ensure helper utilities are either retained in orchestrator only when cross-domain or moved to owning extractor modules. — ✅ `no-commit (shared collection/validation moved to extractor common helpers; domain heuristics moved to owner modules)`
- [x] [PR-1] D3 🔄 — Verify public API compatibility and output shape parity against current tests/regression fixtures. — ✅ `no-commit (targeted and broad backend suites green)`

### Phase 5 - Validation and closeout

- [x] [PR-1] E1 🔄 — Run targeted unit tests: `test_interpretation_schema.py`, `test_golden_extraction_regression.py`, `test_clinic_name_normalization.py`, `test_microchip_normalization.py`. — ✅ `no-commit (73 targeted tests green)`
- [x] [PR-1] E2 🔄 — Run broader backend test suite for regression confidence. — ✅ `no-commit (847 passed, 2 xfailed)`
- [x] [PR-1] E3 🔄 — Run architecture metrics checks and confirm ARCH-02 thresholds (function LOC <= 100, CC <= 20). — ✅ `no-commit (refactored modules verified by AST LOC scan + radon CC)`
- [x] [PR-1] E4 🚧 — Hard-gate cleared: final validation completed, code committed, and branch pushed after explicit user approval. — ✅ `2a7d1114`

- [x] [PR-1] E5 🔄 — Reconcile plan/traceability updates after split analysis and keep delivery on a single effective PR. — ✅ `4d786db8`
- [x] [PR-1] E6 🔄 — Retrofit PR split notes in-place, then reconcile back to one effective PR after user decision. — ✅ `cb2b8fa0`

---

## Prompt Queue

### Prompt 1 - A1 to B3 (safe extraction setup)

1. Baseline current import/call graph and tests touching candidate mining and ranking.
2. Create `field_patterns.py` with extracted compiled patterns and migrate imports.
3. Create `candidate_ranking.py`, move ranking/mapping functions, and update import sites.
4. Run targeted ranking and interpretation tests and report parity.

### Prompt 2 - C1 to C5 (domain extractor implementation)

1. Build domain extractor modules under `extractors/`.
2. Port extraction and validation logic from monolithic function into owner modules.
3. Keep candidate payload schema identical (value, confidence, evidence, anchor metadata).
4. Add concise module-level comments only where logic is not self-explanatory.

### Prompt 3 - D1 to E4 (orchestrator + full validation)

1. Replace monolith body in `candidate_mining.py` with orchestration pipeline.
2. Re-run targeted and broad tests.
3. Run complexity metrics and capture evidence for acceptance checklist.
4. Present final status and stop at hard-gate for explicit user decision.

---

## Active Prompt

Execution complete through E6. Branch is pushed and ready for PR creation on explicit user request.

---

## Acceptance Criteria

From [ARCH-02 backlog item](../../../Backlog/completed/arch-02-decompose-candidate-mining.md):

1. No function exceeds 100 LOC.
2. No function exceeds CC 20.
3. All existing tests pass.
4. `mine_candidates()` public API remains unchanged.

---

## Validation Checklist

- [x] `field_patterns.py` exists and owns moved regex patterns from `candidate_mining.py`.
- [x] Extractor modules exist and own domain-specific extraction + validation logic.
- [x] `_candidate_sort_key()` and `_map_candidates_to_global_schema()` are isolated in `candidate_ranking.py`.
- [x] `candidate_mining.py` is reduced to orchestration and remains easy to navigate.
- [x] All targeted tests pass.
- [x] Architecture metrics confirm no function over LOC/CC acceptance thresholds in the refactored candidate-mining modules.
- [x] Public API behavior remains stable for current callers.

---

## Validation Evidence

- Plan-start gate: `scripts/ci/test-L1.ps1 -BaseRef HEAD` — PASS.
- Targeted functional tests: `pytest --no-cov backend/tests/unit/test_microchip_normalization.py backend/tests/unit/test_clinic_name_normalization.py backend/tests/unit/test_interpretation_schema.py -q` — `60 passed`.
- Golden extraction regression: `pytest --no-cov backend/tests/unit/test_golden_extraction_regression.py -q` — `13 passed`.
- Broad backend suite: `pytest --no-cov backend/tests -q` — `847 passed, 2 xfailed`.
- Final preflight: `scripts/ci/test-L2.ps1 -BaseRef main` — PASS.
- Final gate before commit/push: `scripts/ci/test-L3.ps1 -BaseRef main` — PASS.
- Focused ARCH-02 complexity check: `radon cc backend/app/application/processing/candidate_mining.py backend/app/application/processing/candidate_ranking.py backend/app/application/processing/extractors backend/app/application/processing/field_patterns.py -s` — max observed complexity `C (20)` in `extractors/clinical.py`; no refactored function exceeded `CC 20`.
- Focused ARCH-02 function LOC check: AST scan over `candidate_mining.py`, `candidate_ranking.py`, `field_patterns.py`, and `extractors/*.py` — no function exceeded `100 LOC`.

📋 Evidence:
- Step: E4-E6
- Code commit: `2a7d1114`
- Plan commit: `cb2b8fa0`

---

## How to Test

1. Run `pytest backend/tests/unit/test_interpretation_schema.py -v`.
2. Run `pytest backend/tests/unit/test_golden_extraction_regression.py -v`.
3. Run `pytest backend/tests/unit/test_clinic_name_normalization.py -v`.
4. Run `pytest backend/tests/unit/test_microchip_normalization.py -v`.
5. Run `pytest backend/tests/ -v`.
6. Run `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 20 --max-loc 100` and verify no failures in modified areas.
