# Plan: ARCH-02 Decompose candidate_mining

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary template, commit conventions, and handoff behavior.

**Branch:** `refactor/arch-02-implement-candidate-mining`
**PR:** Pending (PR created on explicit user request)
**Backlog item:** [arch-02-decompose-candidate-mining.md](../../Backlog/arch-02-decompose-candidate-mining.md)
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

## Execution Status

**Legend**
- `🔄` auto-chain — executable by agent
- `🚧` hard-gate — user review or decision required

### Phase 1 - Baseline and extraction scaffolding

- [ ] A1 ⏳ IN PROGRESS (agent, 2026-03-11) 🔄 — Confirm baseline callers/import graph for `_mine_interpretation_candidates()`, `_map_candidates_to_global_schema()`, and `_candidate_sort_key()`.
- [ ] A2 🔄 — Create `backend/app/application/processing/field_patterns.py` and move module-level compiled regex patterns from `candidate_mining.py` into it without behavior change.
- [ ] A3 🔄 — Create `backend/app/application/processing/extractors/` package scaffolding and shared extractor contracts/helpers.

### Phase 2 - Move ranking and schema mapping responsibilities

- [ ] B1 🔄 — Create `backend/app/application/processing/candidate_ranking.py` with `_candidate_sort_key()` and `_map_candidates_to_global_schema()`.
- [ ] B2 🔄 — Update imports in `interpretation.py`, tests, and `processing_runner.py` re-export list to use `candidate_ranking.py`.
- [ ] B3 🔄 — Run targeted tests that cover ranking behavior and schema mapping.

### Phase 3 - Extract candidate mining by domain group

- [ ] C1 🔄 — Implement `extractors/identifiers.py` for `microchip_id` and `clinical_record_number` extraction plus validations.
- [ ] C2 🔄 — Implement `extractors/persons.py` for `owner_name` and `vet_name` extraction plus validations.
- [ ] C3 🔄 — Implement `extractors/locations.py` for `clinic_name`, `clinic_address`, and `owner_address` extraction plus disambiguation helpers.
- [ ] C4 🔄 — Implement `extractors/clinical.py` for diagnosis/treatment/procedure/vaccination/lab/imaging/line_item/language extraction.
- [ ] C5 🔄 — Implement `extractors/physical.py` for pet identity and physical attributes (`pet_name`, `species`, `breed`, `sex`, `weight`, etc.).

### Phase 4 - Recompose orchestrator and verify parity

- [ ] D1 🔄 — Refactor `candidate_mining.py` into thin orchestration flow (line preprocessing, external date parsing calls, modular extractor composition).
- [ ] D2 🔄 — Ensure helper utilities are either retained in orchestrator only when cross-domain or moved to owning extractor modules.
- [ ] D3 🔄 — Verify public API compatibility and output shape parity against current tests/regression fixtures.

### Phase 5 - Validation and closeout

- [ ] E1 🔄 — Run targeted unit tests: `test_interpretation_schema.py`, `test_golden_extraction_regression.py`, `test_clinic_name_normalization.py`, `test_microchip_normalization.py`.
- [ ] E2 🔄 — Run broader backend test suite for regression confidence.
- [ ] E3 🔄 — Run architecture metrics checks and confirm ARCH-02 thresholds (function LOC <= 100, CC <= 20).
- [ ] E4 🚧 — Hard-gate: present final evidence and request explicit user approval before any commit/PR workflow.

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

Pending execution approval.

---

## Acceptance Criteria

From [ARCH-02 backlog item](../../Backlog/arch-02-decompose-candidate-mining.md):

1. No function exceeds 100 LOC.
2. No function exceeds CC 20.
3. All existing tests pass.
4. `mine_candidates()` public API remains unchanged.

---

## Validation Checklist

- [ ] `field_patterns.py` exists and owns moved regex patterns from `candidate_mining.py`.
- [ ] Extractor modules exist and own domain-specific extraction + validation logic.
- [ ] `_candidate_sort_key()` and `_map_candidates_to_global_schema()` are isolated in `candidate_ranking.py`.
- [ ] `candidate_mining.py` is reduced to orchestration and remains easy to navigate.
- [ ] All targeted tests pass.
- [ ] Architecture metrics confirm no function over LOC/CC acceptance thresholds.
- [ ] Public API behavior remains stable for current callers.

---

## How to Test

1. Run `pytest backend/tests/unit/test_interpretation_schema.py -v`.
2. Run `pytest backend/tests/unit/test_golden_extraction_regression.py -v`.
3. Run `pytest backend/tests/unit/test_clinic_name_normalization.py -v`.
4. Run `pytest backend/tests/unit/test_microchip_normalization.py -v`.
5. Run `pytest backend/tests/ -v`.
6. Run `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 20 --max-loc 100` and verify no failures in modified areas.
