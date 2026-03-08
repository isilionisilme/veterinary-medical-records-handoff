# US-24 — Support global drag-and-drop PDF upload across relevant screens

**User Story**
As a user, I want to drag and drop a PDF from multiple relevant screens so that I can upload documents without navigating back to a specific dropzone.

**Acceptance Criteria**
- I can drop supported PDFs from any approved upload-capable surface (including list view, document review screen, and relevant empty states).
- Drag-over/drop feedback is visually consistent across those surfaces.
- Upload validation and error messaging are consistent with existing upload behavior.
- Keyboard and non-drag alternatives remain available and equivalent.

**Scope Clarification**
- Already partially covered by US-21 (upload UX), but this story expands drag-and-drop coverage beyond existing dropzones.
- This story does not add support for new file types.

**Authoritative References**
- Tech: Existing upload contract and validation behavior: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- UX: Upload interaction consistency and fallbacks: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Drag-and-drop succeeds from each approved screen and follows the same success/failure feedback contract.
- Non-drag upload path remains fully functional.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
