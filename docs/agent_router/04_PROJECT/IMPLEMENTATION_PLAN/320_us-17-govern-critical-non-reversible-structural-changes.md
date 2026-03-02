# US-17 — Govern critical (non-reversible) structural changes

**User Story**
As a reviewer, I want stricter handling for critical structural changes so that high-risk evolutions require deliberate review.

**Acceptance Criteria**
- Critical candidates are clearly distinguished from non-critical candidates.
- Critical candidates are not auto-promoted.
- Critical decisions are explicitly recorded and auditable.
- Critical governance is isolated from veterinarian workflows.

**Scope Clarification**
- No veterinarian friction is introduced.

**Authoritative References**
- Product: Critical concept policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) Section 4
- Tech: Critical derivation rule: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix D7.4
- UX: Sensitive changes never add veterinarian friction: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../UX_DESIGN/00_entry.md) Section 6

**Test Expectations**
- Critical designation affects reviewer prioritization only; it does not block veterinarian workflows.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
