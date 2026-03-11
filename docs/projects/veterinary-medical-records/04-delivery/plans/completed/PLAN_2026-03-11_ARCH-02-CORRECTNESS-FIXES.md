# Plan: ARCH-02 Correctness Fixes

> **Operational rules:** See [plan-execution-protocol.md](../../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary template, commit conventions, and handoff behavior.

**Branch:** `refactor/arch-02-post-pr1-correctness-fixes`
**PR:** Not planned as separate PR (absorbed into parent branch)
**Related plan:** [PLAN_2026-03-11_ARCH-02-DECOMPOSE-CANDIDATE-MINING.md](./PLAN_2026-03-11_ARCH-02-DECOMPOSE-CANDIDATE-MINING.md)
**Worktree:** `D:\Git\worktrees\arch02-post-pr1`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** Review agent (findings) -> Execution agent (fixes)
**Execution Mode:** `Autonomous`
**Model Assignment:** `Uniform`
**Automation Mode:** `Supervisado` (no commit/push without explicit user approval)
**Iteration:** pending

---

## Agent Instructions

1. Mark each task complete in `Execution Status` immediately after completion.
2. Do not commit or push without explicit user approval.
3. Keep scope limited to the two accepted correctness findings from the regression-safety review.
4. Preserve external behavior and public API contracts.

---

## Context

After ARCH-02 decomposition, a correctness/regression-safety review found two real drifts that must be fixed before PR-1:

1. Missing code path: owner-header inline address extraction dropped during extraction split.
2. Pattern substitution drift in `_extract_owner_address_block()`:
   - `_ADDRESS_LIKE_PATTERN` was replaced with `_CLINIC_ADDRESS_START_RE`.
   - `_CLINIC_ADDRESS_CONTEXT_RE` was replaced with `_CLINIC_OR_HOSPITAL_CONTEXT_RE`.

Finding 3 (extractor execution order and dedup metadata priority) is accepted as non-blocking and out of scope for this fix plan.

This plan is intentionally retained as a review artifact recording the correctness findings and the accepted fix scope.
Its scoped fixes were absorbed into the parent ARCH-02 implementation commit, so no separate branch or PR will be opened from this document.

---

## Objective

1. Restore missing owner inline-address extraction path.
2. Re-align pattern usage in owner-address block to original monolith semantics.
3. Validate no regression through targeted and broad backend tests.

---

## Scope Boundary

- **In scope:** `locations.py` behavioral parity fixes, import cleanup required by those fixes, and regression validation.
- **Out of scope:** new heuristics, ranking policy changes, extractor order changes, schema contract changes.

---

## Execution Status

**Legend**
- `🔄` auto-chain — executable by agent
- `🚧` hard-gate — user review or decision required

### Phase 1 - Behavioral parity fixes

- [x] A1 🔄 — Add `_extract_owner_header_inline_address(context, collector)` in `backend/app/application/processing/extractors/locations.py` to restore owner-header inline address extraction behavior from the original monolith. — ✅ `2a7d1114`
- [x] A2 🔄 — Wire `_extract_owner_header_inline_address()` into `extract_location_candidates()` before labeled address extraction to preserve original sequencing. — ✅ `2a7d1114`
- [x] A3 🔄 — In `_extract_owner_address_block()`, replace `_CLINIC_ADDRESS_START_RE.search(address_line)` with `_ADDRESS_LIKE_PATTERN.search(address_line)`. — ✅ `2a7d1114`
- [x] A4 🔄 — In `_extract_owner_address_block()`, replace `_CLINIC_OR_HOSPITAL_CONTEXT_RE.search(context_text)` with `_CLINIC_ADDRESS_CONTEXT_RE.search(context_text)` and clean unused imports. — ✅ `2a7d1114`
- [x] A5 🔄 — Run formatter/lint preflight for touched file(s). — ✅ `2a7d1114`

### Phase 2 - Regression validation

- [x] B1 🔄 — Run targeted tests: `pytest backend/tests/unit/test_golden_extraction_regression.py backend/tests/unit/test_interpretation_schema.py -v`. — ✅ `2a7d1114`
- [x] B2 🔄 — Run full backend suite: `pytest backend/tests/ -v`. — ✅ `2a7d1114`
- [x] B3 🔄 — Run L1 gate: `scripts/ci/test-L1.ps1`. — ✅ `2a7d1114`
- [x] B4 🚧 — Hard-gate cleared indirectly: fixes were validated by `scripts/ci/test-L3.ps1 -BaseRef main` before code commit and push. — ✅ `2a7d1114`

---

## Relevant Files

### Core (modify)
- `backend/app/application/processing/extractors/locations.py`

### Read-only references
- `backend/app/application/processing/field_patterns.py`
- `backend/app/application/processing/constants.py`
- `backend/app/application/processing/candidate_mining.py` (original monolith reference via `git show HEAD:...`)

---

## Verification

1. Missing owner-header inline address path is restored and covered by current regression suite.
2. Pattern parity in owner-address block matches original monolith logic.
3. Targeted tests pass.
4. Full backend tests pass.
5. L1 gate passes.

---

## Validation Evidence

- Targeted regression validation: `pytest backend/tests/unit/test_golden_extraction_regression.py backend/tests/unit/test_interpretation_schema.py -v` — PASS.
- Broad backend validation: `pytest backend/tests/ -v` — PASS (`847 passed, 2 xfailed`).
- Final gate before commit/push: `scripts/ci/test-L3.ps1 -BaseRef main` — PASS.

📋 Evidence:
- Step: A1-A5, B1-B4
- Code commit: `2a7d1114`
- Plan commit: pending

---

## Decisions

- Accepted: Finding 3 (execution order and dedup metadata priority) remains unchanged in this plan.
- Required: Findings 1 and 2 must be fixed before PR-1 commit boundary.
