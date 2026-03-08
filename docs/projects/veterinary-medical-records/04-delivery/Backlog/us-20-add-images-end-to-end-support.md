# US-20 — Add Images end-to-end support

**User Story**
As a user, I want to upload, access, and process image documents so that scans and photographs can be handled in the same workflow.

**Acceptance Criteria**
- I can upload supported image types (at minimum PNG and JPEG).
- I can download and preview the original image at any time without blocking on processing.
- Image documents are processed in the same step-based, non-blocking pipeline as PDFs, producing the same visibility and artifacts.
- Extraction for images uses OCR to produce raw text suitable for downstream interpretation and review.
- Review-in-context and editing behave the same as for PDFs once extracted text exists.

**Scope Clarification**
- This story changes format support only; the processing pipeline, contracts, versioning rules, and review workflow semantics remain unchanged.
- This story requires updating the authoritative format support contract in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) (supported upload types and any related filesystem rules).

**Authoritative References**
- Tech: Endpoint surface and error semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix C
- Tech: Extraction library decisions (appendix): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E
- UX: Review flow guarantees and rendering contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) sections **Confidence — UX Definition**, **Veterinarian Review Flow**, **Review-in-Context Contract**, and **Review UI Rendering Rules (Global Schema Template)**.

**Story-specific technical requirements**
- Add server-side type detection for images based on server-side inspection.
- Define the OCR extraction approach in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E during this story, then implement it.
- Store the original under the deterministic path rules with the appropriate extension (e.g., `original.png`, `original.jpg`).

**Test Expectations**
- Image inputs behave like PDFs for upload/download/status visibility.
- OCR extraction produces a raw-text artifact for image runs, enabling the same review/edit endpoints once processing completes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
