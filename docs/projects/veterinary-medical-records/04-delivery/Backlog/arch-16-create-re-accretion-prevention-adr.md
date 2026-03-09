# ARCH-16 — Create Re-accretion Prevention ADR

**Status:** Planned

**Type:** Architecture Improvement (architecture governance)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 3 (§5.3)

**Severity:** HIGH  
**Effort:** S (1-2h)

**Problem Statement**
Decomposed files tend to grow back into hotspots without documented governance thresholds.

**Action**
Document architectural decision: maximum file LOC (500), maximum function CC (20), enforcement via CI gates (ARCH-03). Record rationale based on observed regression pattern.

**Acceptance Criteria**
- ADR exists documenting complexity thresholds and enforcement strategy
- References the re-accretion pattern observed in the codebase
- Links to ARCH-03 CI gates as the enforcement mechanism

**Dependencies**
- ARCH-03 (CI complexity gates) for enforcement reference.
