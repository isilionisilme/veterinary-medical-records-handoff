# US-03 — Download / preview original document

**User Story**
As a user, I want to download and preview the original uploaded document so that I can access the source material.

**Acceptance Criteria**
- I can access the original uploaded file for a document.
- Preview is supported for PDFs.
- If the stored file is missing, the system returns the normative missing-artifact behavior.
- Accessing the original file is non-blocking and does not depend on processing success.

**Scope Clarification**
- This story does not implement evidence overlays or highlighting.

**Authoritative References**
- Tech: API surface + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3/B3.2
- Tech: Filesystem artifact rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B5

**Test Expectations**
- Successful download works for an uploaded document.
- Missing artifact behavior matches the Technical Design contract.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
