# US-33 — PDF Viewer Zoom

**Status**: Implemented (2026-02-13)

**User Story**
As a veterinarian reviewer, I want to zoom in/out the PDF viewer so I can read small text without losing context.

**Acceptance Criteria**
- Zoom controls (`+`, `-`, and `reset`) are visible in the PDF viewer toolbar.
- Zoom level persists while navigating pages within the same document.
- Zoom enforces reasonable limits (50%–200%).
- Zoom does not affect extracted text tab behavior or structured data layout.

**Scope Clarification**
- This story only covers in-viewer zoom controls and in-document persistence.
- Out of scope: pan/hand tool, multi-page thumbnails, and fit-to-width vs fit-to-page refinements.

**Authoritative References**
- UX: Review workflow and side-by-side behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)
- Tech: Existing review/document surface boundaries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md)

**Test Expectations**
- Users can change zoom with toolbar controls and reset to default.
- Zoom persists across page navigation for the active document and resets when changing document.
- Extracted text tab and structured data rendering remain unaffected by zoom changes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
