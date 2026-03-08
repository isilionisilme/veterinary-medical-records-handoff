# US-35 — Resizable splitter between PDF Viewer and Structured Data panel

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian reviewer, I want to resize the PDF and structured-data panels so that I can optimize my workspace for reading the document or validating fields.

**Objective**
- Make side-by-side review adaptable to desktop monitor sizes and reviewer tasks without introducing new workflow modes.

**Acceptance Criteria**
- A vertical splitter handle allows pointer drag resizing between the PDF Viewer and Structured Data panels.
- The splitter has a generous hit area and resize cursor.
- Sane width constraints are enforced:
  - PDF panel has a minimum width that preserves readability.
  - Structured panel has a minimum width that preserves field readability.
  - Neither panel can be resized to fully collapse the other.
- Default layout can be restored via double-click on the splitter handle.
- Reset behavior is provided via double-click on the splitter handle (without an additional reset button).
- Preferred behavior: persist split ratio in local storage so it survives page refresh on the same device.
- Resizing keeps Global Schema rendering deterministic (field order/position remains canonical).
- Resizing does not break panel scroll/focus behavior and does not interfere with PDF interactions or structured data filtering/search.
- Any icon-only control introduced for splitter actions includes an accessible name.

**Scope Clarification**
- This story keeps the existing three-area layout (documents sidebar, PDF Viewer, structured data panel).
- This story is limited to review-layout resizing behavior and local persistence.
- This story does not change endpoint contracts, persistence schema, or interpretation semantics.

**Out of Scope**
- New review modes, alternate workflows, or additional panel types.
- Reordering/redefining Global Schema fields.
- Non-desktop-specific layout redesign.

**UX Notes**
- The splitter should be subtle at rest and more visible on hover/focus.
- Dragging must feel stable and avoid jitter or layout jumps.
- Interaction should remain fast and tool-like.

**Edge Cases**
- Very narrow container widths should gracefully clamp to a safe split.
- Loading/empty/error states must keep layout integrity and not break splitter behavior.
- Pinned source panel mode must keep splitter behavior stable for PDF vs Structured Data.

**Authoritative References**
- UX: Side-by-side review interaction baseline: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Sections 2–4.
- Product: Global Schema canonical ordering invariants: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md) section **Global Schema (Canonical Field List)**.
- Frontend context: review rendering backbone and deterministic structure: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../../02-tech/frontend-implementation.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Splitter drag updates panel widths while honoring min/max constraints.
- Default reset behavior restores baseline split.
- Stored split ratio is restored on reload when available and valid.
- Structured panel keeps deterministic Global Schema order under resize and existing filters.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
