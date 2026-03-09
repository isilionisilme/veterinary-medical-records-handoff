# ARCH-24 — Replace Wildcard Re-export with Explicit Imports

**Status:** Planned

**Type:** Architecture Improvement (code quality)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (DC-1)

**Severity:** LOW  
**Effort:** XS (30min)

**Problem Statement**
`document_service.py` uses `from backend.app.application.documents import *`, making dependencies opaque.

**Action**
Replace with explicit named imports.

**Acceptance Criteria**
- No wildcard imports remain in `document_service.py`
- All tests pass
- Import list explicitly names each used symbol

**Dependencies**
- None.
