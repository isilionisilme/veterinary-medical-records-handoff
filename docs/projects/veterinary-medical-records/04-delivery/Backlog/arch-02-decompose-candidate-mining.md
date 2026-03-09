# ARCH-02 — Decompose `candidate_mining.py`

**Status:** Planned

**Type:** Architecture Improvement (code quality)

**Target release:** Release 19 — Critical architecture remediation

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (P-2), Phase 3 (§3.2)

**Severity:** CRITICAL  
**Effort:** L (8-16h)

**Problem Statement**
`candidate_mining.py` has 1,013 LOC, a 767-LOC single function (`_mine_interpretation_candidates`), CC 163 (highest in codebase), and an inner closure with 25+ field-specific validation blocks.

**Action**
1. Split into per-entity-type `FieldCandidateExtractor` strategies (labeled, heuristic, microchip, address, date)
2. Extract `CandidateValidator` with per-field validation rules
3. Move 40+ compiled regex patterns into `FieldPattern` registry
4. Replace multi-pass line iteration with single `MedicalDocumentParser`

**Acceptance Criteria**
- No function > 100 LOC
- No function CC > 20
- All existing tests pass
- `mine_candidates()` public API unchanged

**Dependencies**
- ARCH-03 (CI complexity gates) should be in place first to prevent re-accretion.
