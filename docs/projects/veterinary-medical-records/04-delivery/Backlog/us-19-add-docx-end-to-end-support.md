# US-19 — Add DOCX end-to-end support

**User Story**
As a user, I want to upload, access, and process DOCX documents so that the same workflow supported for PDFs applies to Word documents.

**Acceptance Criteria**
- I can upload supported `.docx` documents.
- I can download the original DOCX at any time without blocking on processing.
- DOCX documents are processed in the same step-based, non-blocking pipeline as PDFs (extraction → interpretation), producing the same visibility and artifacts.
- Review-in-context and editing behave the same as for PDFs once extracted text exists.

**Scope Clarification**
- This story changes format support only; the processing pipeline, contracts, versioning rules, and review workflow semantics remain unchanged.
- This story does not require preview for DOCX; if preview is unavailable, the UI must clearly fall back to download-only without blocking workflows.
- This story requires updating the authoritative format support contract in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) (supported upload types and any related filesystem rules).

**Authoritative References**
- Tech: Endpoint surface and error semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix C
- UX: Review flow guarantees and rendering contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) sections **Confidence — UX Definition**, **Veterinarian Review Flow**, **Review-in-Context Contract**, and **Review UI Rendering Rules (Global Schema Template)**.

**Story-specific technical requirements**
- Add server-side type detection for DOCX based on server-side inspection.
- Add DOCX text extraction using a minimal dependency surface (choose one library during implementation and document the choice; candidates include `python-docx` or `mammoth`).
- Store the original under the deterministic path rules with the appropriate extension (e.g., `original.docx`).

**Test Expectations**
- DOCX inputs behave like PDFs for upload/download/status visibility.
- Extraction produces a raw-text artifact for DOCX runs, enabling the same review/edit endpoints once processing completes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
