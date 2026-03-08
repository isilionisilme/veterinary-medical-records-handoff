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
- Product: Critical keys policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md) CRITICAL_KEYS
- Tech: Critical concept derivation: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix D7.4
- Tech: Governance endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3

**Test Expectations**
- Filters do not change underlying candidate data; they only change views.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
