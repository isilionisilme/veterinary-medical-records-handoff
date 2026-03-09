# ARCH-15 — Explicitly Declare pydantic in requirements.txt

**Status:** Planned

**Type:** Architecture Improvement (dependencies)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (D-1)

**Severity:** LOW  
**Effort:** XS (5min)

**Problem Statement**
`pydantic` is used but only installed transitively through FastAPI. Not explicitly declared.

**Action**
Add `pydantic` with pinned version to `requirements.txt`.

**Acceptance Criteria**
- `pydantic` appears in `requirements.txt` with a pinned version
- No new dependency conflicts introduced

**Dependencies**
- None.
