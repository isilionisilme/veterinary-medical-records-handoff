# ARCH-27 — Regression Tests for Visit Scoping & Projection Pipeline

**Status:** Planned

**Type:** Architecture Improvement (test coverage)

**Target release:** Release 20 — Architecture hardening

**Origin:** [PR #291 AI Code Review](https://github.com/isilionisilme/veterinary-medical-records/pull/291) — Must-fix: contract-level regression tests for extracted scoping/projection pipeline

**Severity:** HIGH  
**Effort:** S (1-2h)

**Problem Statement**
The ARCH-01 decomposition moved the behavior-critical visit scoping/projection path into three new modules (`visit_scoping`, `visit_helpers`, `visit_population`) without adding end-to-end tests that lock down the final canonical payload. Direct coverage is low (visit_scoping 15%, visit_helpers 7%, visit_population 10%). Failures in this path are silent data drift: wrong visit assignment, missing `reason_for_visit`, or wrong derived document-level `weight`.

**Action**
Add fixture-style regression tests through `normalize_canonical_review_scoping()` covering:
1. Repeated same-day visits → separate visit objects created
2. Ambiguous/unassigned field placement → field lands in `unassigned` visit
3. Latest-weight derivation from raw text → `derived-weight-current` field correct
4. Single visit default assignment → all fields absorbed
5. Document-level weight from visit weights → most recent visit's weight wins

**Acceptance Criteria**
- 5+ regression tests covering the edge cases above
- All tests pass through the public orchestrator entry point (no internal function testing)
- Coverage of `visit_scoping.py`, `visit_helpers.py`, `visit_population.py` increases measurably
- All existing tests pass
- L3 green

**Dependencies**
- ARCH-01 (Done) — decomposition must be merged first.

**Plan**
[PLAN_2026-03-12_ARCH-01-REGRESSION-TESTS.md](../plans/PLAN_2026-03-12_ARCH-01-REGRESSION-TESTS.md)
