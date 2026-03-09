# ARCH-08 — Expose `_shared` Functions Publicly

**Status:** Planned

**Type:** Architecture Improvement (code principles)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 3 (encapsulation warning), Phase 2 (P-3)

**Severity:** MEDIUM  
**Effort:** XS (30min)

**Problem Statement**
`api/routes_review.py` imports from a `_`-prefixed (private) module in the application layer, breaking encapsulation conventions.

**Action**
Re-export `_locate_visit_date_occurrences_from_raw_text` through `application/documents/__init__.py`. Update import in `api/routes_review.py`.

**Acceptance Criteria**
- No imports from `_shared` or `_`-prefixed modules in api/ layer
- All tests pass

**Dependencies**
- None.
