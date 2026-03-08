# US-01 — Upload document (API)

**Status**: Implemented (2026-02-16)

**User Story**
As a developer, I want an API endpoint that accepts and persists a document so that it is stored and available for processing.

**Acceptance Criteria**
- A supported document type can be uploaded via the API (e.g. Swagger UI, curl, or developer tools).
- The API returns immediate confirmation that the document was persisted (without waiting on processing).
- The document appears in the system with the initial derived status.

**Scope Clarification**
- This story delivers the **backend ingestion API only** — no end-user UI. Verification is done through Swagger UI, curl, or equivalent developer tools.
- This story does not start processing. Background processing is introduced later (US-05).
- This story supports the upload types defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3; format expansion is introduced via later user stories.
- The end-user upload experience (dropzone, feedback copy, error messages) is introduced in US-21.

**Authoritative References**
- Tech: API surface + upload requirements + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- Tech: Derived document status: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A1.2
- Tech: Filesystem rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B5

**Test Expectations**
- Uploading a supported type succeeds and persists the document.
- Uploading an unsupported type fails with the normative error contract.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
