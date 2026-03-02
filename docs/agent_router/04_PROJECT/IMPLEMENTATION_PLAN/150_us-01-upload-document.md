# US-01 — Upload document

**User Story**
As a user, I want to upload a document so that it is stored and available for processing.

**Acceptance Criteria**
- I can upload a supported document type.
- I receive immediate confirmation that the document was uploaded (without waiting on processing).
- The document appears in the system with the initial derived status.

**Scope Clarification**
- This story does not start processing.
- Background processing is introduced later (US-05).
- This story supports the upload types defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3; format expansion is introduced via later user stories.
- This story delivers the backend ingestion capability; user-facing upload UI/UX (including feedback copy) is introduced later (US-21).

**Authoritative References**
- Tech: API surface + upload requirements + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3/B3.2
- Tech: Derived document status: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A1.2
- Tech: Filesystem rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B5

**Test Expectations**
- Uploading a supported type succeeds and persists the document.
- Uploading an unsupported type fails with the normative error contract.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
