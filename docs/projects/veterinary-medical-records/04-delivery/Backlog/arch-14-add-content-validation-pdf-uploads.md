# ARCH-14 — Add Content Validation for PDF Uploads

**Status:** Planned

**Type:** Architecture Improvement (security)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (S-3)

**Severity:** MEDIUM  
**Effort:** S (2-4h)

**Problem Statement**
No content-type validation for uploaded files beyond extension check.

**Action**
Add content-type validation (magic bytes check). Consider ClamAV integration for production deployments.

**Acceptance Criteria**
- Uploaded files are validated by magic bytes, not just extension
- Non-PDF files with .pdf extension are rejected
- Validation runs before processing starts

**Dependencies**
- None.
