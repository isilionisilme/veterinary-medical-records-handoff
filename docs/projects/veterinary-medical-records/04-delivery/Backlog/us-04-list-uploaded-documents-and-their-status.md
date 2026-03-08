# US-04 — List uploaded documents and their status

**Status**: Implemented (2026-02-16)

**User Story**
As a user, I want to list uploaded documents and see their status so that I can navigate my work.

**Acceptance Criteria**
- I can see a stable list of documents.
- Each item includes basic metadata and derived status.
- The list remains accessible regardless of processing state.

**Scope Clarification**
- This story does not add filtering/search (future concern).

**Authoritative References**
- Tech: Listing semantics and run resolution: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.1
- Tech: Derived status rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A1.2

**Test Expectations**
- Documents with no runs show the correct derived status.
- Documents with queued/running/latest terminal runs show the correct derived status.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
