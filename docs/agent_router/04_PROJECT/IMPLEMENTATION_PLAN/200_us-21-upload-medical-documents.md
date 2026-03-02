# US-21 — Upload medical documents

**User Story**
As a user, I want to upload a medical document so that the system can start processing it.

**Acceptance Criteria**
- I can upload a medical document using the application.
- The UI clearly communicates which document formats are supported (PDF only for the current scope).
- After submitting a document, I receive clear feedback indicating whether the upload was successful.
- If the upload fails, I receive a clear and user-friendly error message (without exposing internal technical details).
- The UI communicates that processing is assistive and may be incomplete, without blocking the user.
- When automatic processing-on-upload is enabled (introduced in US-05), uploading a document via the UI starts that existing processing flow in a non-blocking way; the UI relies only on the API response and derived status rules.
- I do not need to use technical tools or interfaces to upload documents.
- I am not shown document previews, extracted text, or review functionality as part of this story.

**Scope Clarification**
- This story is limited to the user-facing upload experience and feedback states; it reuses the existing upload contract and does not introduce new endpoint surface area.
- This story does not implement or modify backend ingestion logic; it consumes the existing upload capability (US-01) and respects backend validation rules.
- This story does not introduce new workflow states, reprocessing semantics, or observability contracts.
- This story is limited to PDFs; additional formats are introduced only via the dedicated format expansion stories.
- This story does not add preview/rendering, raw-text visibility, or review/edit experiences.

**Authoritative References**
- Tech: API surface + upload requirements + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3/B3.2
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Sections 3–4 + Appendix A2
- UX: Global upload experience and feedback heuristics: [`docs/shared/01-product/ux-guidelines.md`](../../03_SHARED/UX_GUIDELINES/00_entry.md)
- UX: Project interaction contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../UX_DESIGN/00_entry.md) Sections 1–4
- UX: User-facing copy tone: [`docs/shared/01-product/brand-guidelines.md`](../../03_SHARED/BRAND_GUIDELINES/00_entry.md)

**Story-specific technical requirements**
- Reuse the existing upload contract and backend validation rules as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3/B3.2.
- Do not introduce new ingestion endpoints, domain logic, or workflow states; rely only on the API response for UI behavior.
- Preserve existing observability contracts (events/metrics/log taxonomy) as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md).
- Follow implementation conventions in [`docs/projects/veterinary-medical-records/02-tech/backend-implementation.md`](../BACKEND_IMPLEMENTATION/00_entry.md) and [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../FRONTEND_IMPLEMENTATION/00_entry.md).

**Test Expectations**
- Upload succeeds for supported PDFs and provides the expected user-facing feedback states.
- Upload failure cases map to user-friendly messages without leaking internal details.
- Upload triggers background processing without blocking the request (per the processing model).

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
