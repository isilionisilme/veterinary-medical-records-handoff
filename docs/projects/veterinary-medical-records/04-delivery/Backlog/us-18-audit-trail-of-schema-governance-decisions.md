# US-18 — Audit trail of schema governance decisions

**User Story**
As a reviewer, I want to see an audit trail of schema governance decisions so that structural evolution is transparent and traceable.

**Acceptance Criteria**
- I can see a chronological list of governance decisions.
- Each entry shows decision type, reviewer identity, and timestamp.
- The audit trail is read-only, immutable, and append-only.

**Scope Clarification**
- This story provides visibility only.

**Authoritative References**
- Tech: Governance decision log persistence: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B2.9
- Tech: Audit trail endpoint: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3
- Tech: Audit immutability and separation: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A8

**Test Expectations**
- Audit trail ordering is chronological and records are immutable.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
