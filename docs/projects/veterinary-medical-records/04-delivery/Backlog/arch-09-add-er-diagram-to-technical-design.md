# ARCH-09 — Add ER Diagram to technical-design.md

**Status:** Planned

**Type:** Architecture Improvement (documentation)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 1 (GAP-006)

**Severity:** HIGH  
**Effort:** S (1-2h)

**Problem Statement**
No visual data model exists in the technical documentation.

**Action**
Add Mermaid ER diagram to `technical-design.md` showing: Document, ProcessingRun, Artifacts, InterpretationVersion, FieldChangeLog. Include relationship cardinality and foreign keys.

**Acceptance Criteria**
- ER diagram renders correctly in Mermaid
- Shows all 5 core entities with relationships
- Includes cardinality and foreign key annotations

**Dependencies**
- None.
