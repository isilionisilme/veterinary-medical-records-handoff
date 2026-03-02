# US-04 — List uploaded documents and their status

**User Story**
As a user, I want to list uploaded documents and see their status so that I can navigate my work.

**Acceptance Criteria**
- I can see a stable list of documents.
- Each item includes basic metadata and derived status.
- The list remains accessible regardless of processing state.

**Scope Clarification**
- This story does not add filtering/search (future concern).

**Authoritative References**
- Tech: Listing semantics and run resolution: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3/B3.1
- Tech: Derived status rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A1.2

**Test Expectations**
- Documents with no runs show the correct derived status.
- Documents with queued/running/latest terminal runs show the correct derived status.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
