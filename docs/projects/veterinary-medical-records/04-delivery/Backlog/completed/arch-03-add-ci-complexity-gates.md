# ARCH-03 — Add CI Complexity Gates

**Status:** Planned

**Type:** Architecture Improvement (build & CI)

**Target release:** Release 19 — Critical architecture remediation

**Origin:** [Architecture Review 2026-03-09](../../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 3 (§6), Phase 2 (Q-2)

**Severity:** HIGH  
**Effort:** S (2-4h)

**Problem Statement**
Re-accretion pattern — decomposed files grow back into hotspots without automated guardrails.

**Action**
1. Add `radon cc --min C` check to CI (warn on CC 11-20)
2. Add `radon cc --min E` check to CI (fail on CC > 30)
3. Add LOC gate: fail if any Python file exceeds 500 LOC
4. Document thresholds in an ADR

**Acceptance Criteria**
- CI fails on new functions with CC > 30
- CI warns on new functions with CC > 10
- CI fails on new files > 500 LOC
- Gate runs in < 30s

**Authoritative References**
- Tech: Architecture review findings and hotspot rationale: [Architecture Review 2026-03-09](../../../02-tech/audits/architecture-review-2026-03-09.md)
- Tech: Enforcement thresholds and changed-file CI scope: [ADR-ARCH-0005](../../../02-tech/adr/ADR-ARCH-0005-complexity-gate-thresholds.md)

**Dependencies**
- None. This should be implemented first to protect subsequent decomposition work.
