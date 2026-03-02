# US-13 — Review aggregated pending structural changes

**User Story**
As a reviewer, I want to review aggregated pending structural changes so that I can validate or reject schema-level evolution based on recurring patterns.

**Acceptance Criteria**
- I can see pending structural change candidates grouped by pattern, not by individual documents.
- Each candidate includes summary, occurrence counts, and representative evidence.
- This review flow never blocks veterinarians or document processing.
- This flow is reviewer-facing only and not exposed in veterinarian UI.

**Scope Clarification**
- No retroactive changes to past documents.

**Authoritative References**
- Product: Separation of responsibilities and governance boundary: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) Sections 5 and 4.3
- Tech: Governance invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A7
- Tech: Governance persistence + endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B2.8–B2.9 + Appendix B3.1

**Test Expectations**
- Candidates are isolated from document workflows and apply prospectively only.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
