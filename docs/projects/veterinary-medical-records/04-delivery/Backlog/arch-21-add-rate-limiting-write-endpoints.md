# ARCH-21 — Add Rate Limiting to Write Endpoints

**Status:** Planned

**Type:** Architecture Improvement (security)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (S-4)

**Severity:** LOW  
**Effort:** S (1-2h)

**Problem Statement**
Write endpoints (review, reprocess, edit) have no rate limiting.

**Action**
Add rate limits to review, reprocess, and edit endpoints. Follow existing `slowapi` pattern.

**Acceptance Criteria**
- Rate limits applied to all write endpoints
- Follows existing `slowapi` pattern in the codebase
- Returns appropriate 429 responses when exceeded

**Dependencies**
- None.
