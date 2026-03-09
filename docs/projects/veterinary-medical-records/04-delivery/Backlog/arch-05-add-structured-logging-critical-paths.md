# ARCH-05 — Add Structured Logging to Critical Paths

**Status:** Planned

**Type:** Architecture Improvement (observability)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (O-1)

**Severity:** MEDIUM  
**Effort:** S (2-4h)

**Problem Statement**
22 log statements across 317 functions (7% coverage). `review_service.py` and `candidate_mining.py` have zero logging.

**Action**
1. Add entry/exit logging to `review_document()`, `get_canonical_review()`
2. Add extraction-start/extraction-complete logging to `mine_candidates()`
3. Add error logging with context for all exception handlers in hotspot files
4. Follow existing `logging.getLogger(__name__)` pattern

**Acceptance Criteria**
- Every public function in hotspot files has at least entry-level logging
- Error handlers include contextual information (document_id, run_id)
- Log format consistent with existing codebase pattern

**Dependencies**
- Best done after ARCH-01 and ARCH-02 (decomposition) to avoid logging in files that will be restructured.
