# US-21 — Upload medical documents (end-user UI)

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to upload medical documents through a proper application interface — without needing Swagger, curl, or any developer tool — so that the system can start processing them.

**Acceptance Criteria**
- The UI provides a clear upload affordance (dropzone / file picker) accessible to non-technical users.
- The UI clearly communicates which document formats are supported (PDF only for the current scope).
- After submitting a document, the UI provides clear success/failure feedback without exposing internal technical details.
- The UI communicates that processing is assistive and may be incomplete, without blocking the user.
- When automatic processing-on-upload is enabled (US-05), uploading via the UI triggers that flow non-blockingly; the UI relies only on the API response and derived status rules.

**Scope Clarification**
- This story is **frontend-only**: it builds the end-user upload experience on top of the API delivered by US-01. No new endpoints or backend ingestion logic.
- Sequenced in Release 2 (after US-05) so the UI can show processing feedback states that depend on the processing pipeline existing.
- Limited to PDFs; additional formats are introduced only via dedicated format expansion stories.
- Does not add preview/rendering, raw-text visibility, or review/edit experiences.

**Authoritative References**
- UX: Global upload experience and feedback heuristics: [`docs/shared/01-product/ux-guidelines.md`](../../../../shared/01-product/ux-guidelines.md)
- UX: Project interaction contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Sections 1–4
- UX: User-facing copy tone: [`docs/shared/01-product/brand-guidelines.md`](../../../../shared/01-product/brand-guidelines.md)
- Tech: API contract consumed by the UI: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2

**Test Expectations**
- Upload via the UI succeeds for supported PDFs and shows the expected feedback states.
- Upload failure cases render user-friendly messages without leaking internal details.
- Upload triggers background processing without blocking the UI (per the processing model).

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
