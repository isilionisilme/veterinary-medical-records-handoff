# US-28 — Delete uploaded document from list (soft-delete/archive)

**User Story**
As a user, I want to remove an uploaded document from my active list so that I can keep my workspace clean.

**Acceptance Criteria**
- Each eligible document includes a delete/remove action from the list/detail context.
- The delete flow requires explicit user confirmation before completing.
- Deleting a document removes it from the default active list without breaking historical auditability expectations.
- If soft-delete/archive semantics are used, the behavior is explicit in UI copy and reversible behavior (if available) is clearly communicated.

**Scope Clarification**
- Recommended default is soft-delete/archive semantics; irreversible hard-delete behavior requires explicit policy confirmation before implementation.
- This story does not redefine audit/governance contracts.

**Authoritative References**
- Tech: Existing document listing/status contracts: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.1
- UX: Destructive action confirmation and recoverability patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Delete confirmation prevents accidental deletion.
- Deleted/archived documents follow defined visibility semantics consistently.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
