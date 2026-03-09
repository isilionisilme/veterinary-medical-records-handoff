# ARCH-17 — Simplify extraction_observability/ Subsystem

**Status:** Planned

**Type:** Architecture Improvement (code quality)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (P-4)

**Severity:** MEDIUM  
**Effort:** M (4-8h)

**Problem Statement**
`triage.py` has CC 64 — `_suspicious_accepted_flags` may be over-engineered.

**Action**
Review `triage.py` and consider simplifying classification logic or extracting into data-driven rules.

**Acceptance Criteria**
- `triage.py` CC reduced to < 30
- All existing tests pass
- Triage behavior unchanged (same inputs → same outputs)

**Dependencies**
- None, but lower priority than ARCH-01 and ARCH-02.
