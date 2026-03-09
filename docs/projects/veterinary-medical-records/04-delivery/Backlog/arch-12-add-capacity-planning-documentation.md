# ARCH-12 — Add Capacity Planning Documentation

**Status:** Planned

**Type:** Architecture Improvement (documentation)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 1 (GAP-007)

**Severity:** HIGH  
**Effort:** S (2-4h)

**Problem Statement**
No capacity planning information is documented.

**Action**
Document expected data volumes, storage growth projections, SQLite row limits, concurrent processing limits, maximum document count.

**Acceptance Criteria**
- Capacity planning section or document exists
- Covers storage growth, SQLite limits, and concurrency constraints
- References ADR-0001 single-process decision

**Dependencies**
- None.
