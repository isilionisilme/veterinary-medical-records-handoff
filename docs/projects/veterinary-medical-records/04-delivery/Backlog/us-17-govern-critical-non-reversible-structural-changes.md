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
- Product: Critical concept policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md) Section 4
- Tech: Critical derivation rule: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix D7.4
- UX: Sensitive changes never add veterinarian friction: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Section 6

**Test Expectations**
- Critical designation affects reviewer prioritization only; it does not block veterinarian workflows.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
