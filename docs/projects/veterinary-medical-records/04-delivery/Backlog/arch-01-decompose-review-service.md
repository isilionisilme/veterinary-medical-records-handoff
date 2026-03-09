# ARCH-01 — Decompose `review_service.py`

**Status:** Planned

**Type:** Architecture Improvement (code quality)

**Target release:** Release 19 — Critical architecture remediation

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (P-1), Phase 3 (§3.1)

**Severity:** CRITICAL  
**Effort:** L (8-16h)

**Problem Statement**
`review_service.py` is a God Module: 1,532 LOC, 9 distinct responsibilities, max CC 99, 15 commits since Feb baseline. It is the single largest maintainability risk in the codebase.

**Action**
Extract into 4+ focused modules:
1. `VisitAssignmentEngine` — visit scoping, segment extraction, clause parsing
2. `SegmentParser` + `ClauseClassifier` — replace CC-99 function with strategy-based classification
3. `AgeNormalizer` — consolidate 5 age-related functions
4. `ReviewPayloadProjector` — decouple review shape from canonical form

**Acceptance Criteria**
- No file > 400 LOC
- No function CC > 20
- All existing tests pass without modification (refactor, not rewrite)
- Public API (`review_document`, `get_canonical_review`) unchanged

**Dependencies**
- ARCH-03 (CI complexity gates) should be in place first to prevent re-accretion.
