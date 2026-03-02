# US-02 — View document status

**User Story**
As a user, I want to see the current status of a document so that I understand its processing state.

**Acceptance Criteria**
- I can view the current derived status of a document at any time.
- I can see whether processing has succeeded, failed, or timed out.
- If processing fails, the UI can explain the failure category in non-technical terms.
- Pending review and schema governance concepts never block veterinarians and are not exposed in veterinarian UI.

**Scope Clarification**
- This story does not start or control processing.
- This story does not expose run history or per-step details (US-11 covers history).

**Authoritative References**
- Tech: Derived status rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A1.2
- Tech: Failure types and mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix C3
- UX: Separation of responsibilities: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../UX_DESIGN/00_entry.md) Sections 1 and 8

**Test Expectations**
- Derived status matches the latest run state across all states.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
