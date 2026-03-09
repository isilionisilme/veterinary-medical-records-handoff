# ARCH-22 — Parameterize PRAGMA table_info Call

**Status:** Planned

**Type:** Architecture Improvement (security)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (S-2)

**Severity:** LOW (MEDIUM pattern risk)  
**Effort:** XS (30min)

**Problem Statement**
`f"PRAGMA table_info({table})"` uses string interpolation for a SQL-adjacent call, creating a pattern risk even if current usage is safe.

**Action**
Replace with assertion that table is in a known allowlisted set, or use allowlisted table names directly.

**Acceptance Criteria**
- No f-string interpolation in PRAGMA calls
- Table names validated against an allowlist before use
- All existing tests pass

**Dependencies**
- None.
