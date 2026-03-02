# US-14 — Filter and prioritize pending structural changes

**User Story**
As a reviewer, I want to filter and prioritize pending structural changes so I can focus on the most impactful candidates.

**Acceptance Criteria**
- I can filter candidates by status and basic attributes.
- I can prioritize candidates by frequency and criticality.
- Filtering/prioritization never blocks veterinarians.

**Scope Clarification**
- This story does not introduce automatic decisions.

**Authoritative References**
- Product: Critical keys policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) CRITICAL_KEYS
- Tech: Critical concept derivation: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix D7.4
- Tech: Governance endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3

**Test Expectations**
- Filters do not change underlying candidate data; they only change views.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
