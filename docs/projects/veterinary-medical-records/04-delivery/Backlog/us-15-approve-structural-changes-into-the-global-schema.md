# US-15 — Approve structural changes into the global schema

**User Story**
As a reviewer, I want to approve structural changes so that future interpretations use an updated canonical schema.

**Acceptance Criteria**
- I can approve a candidate.
- Approval creates a new canonical schema contract snapshot.
- Approved changes apply prospectively to new runs only.
- Past documents and past runs remain unchanged.
- Approval does not trigger implicit reprocessing.

**Scope Clarification**
- No automatic promotion without explicit reviewer action.

**Authoritative References**
- Tech: Schema contract persistence and current schema rule: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B2.7
- Tech: `schema_contract_used` persisted per run: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B2.2
- Tech: Governance invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A7

**Test Expectations**
- Approval creates a new schema contract snapshot and new runs use it.
- Existing runs retain their historical schema association.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
