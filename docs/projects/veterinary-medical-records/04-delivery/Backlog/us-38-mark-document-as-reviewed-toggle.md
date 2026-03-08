# US-38 — Mark document as reviewed (toggle)

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian reviewer, I want to mark a document as reviewed and unmark it later so that I can manage my review queue without losing my corrections.

**Acceptance Criteria**
- In document view, I can use a single action button labeled `Mark as reviewed`.
- When a document is marked reviewed:
  - The left sidebar item status indicator changes from the current dot to a checkmark.
  - The sidebar status label changes to `Reviewed` (instead of `Ready`).
  - Reviewed documents remain visible in the sidebar, visually separated (e.g., grouped under a `Reviewed` label/section) and visually muted.
- When a document is marked as Reviewed, structured data is rendered in read-only mode.
- Reopening is only possible from the document view using the explicit `Reopen` action.
- The sidebar checkmark is a visual indicator only and is not interactive.
- While Reviewed, structured data is read-only (no editing), safe interactions (e.g., text selection/copy) remain available without toasts, and a non-blocking informational toast is shown only on edit attempts.
- Visual styling clearly indicates non-editable state (e.g., muted text styling, no edit affordances).
- When reopened from the document view, the document returns to the non-reviewed state and re-enters the to-review subset.
- Toggling reviewed/reopened status does not remove or reset extracted/corrected field values.
- Reviewed status is independent from processing status.
- Reprocessing does not change review status.

**Scope Clarification**
- In scope: veterinarian-facing reviewed toggle behavior in document view and sidebar list status representation.
- In scope: reversible reviewed state transitions (`to_review` ↔ `reviewed`) from document view only, without field-value loss.
- In scope: reviewed documents remain discoverable in the sidebar via visual separation from the to-review subset.
- In scope: reviewed documents are non-editable until explicitly reopened.

**Out of Scope**
- Automatic reopening triggered by edits.
- Reopen interactions from the sidebar list/checkmark.
- Implicit state transitions from field interaction while reviewed.
- Reviewer/governance workflows or schema evolution behavior.

**UX Behavior**
- Primary action in document view: `Mark as reviewed`.
- Reviewed state is represented in sidebar list by non-interactive checkmark + `Reviewed` label, visually separated from the to-review subset and visually muted.
- While reviewed, structured data appears visually muted/non-editable and does not show edit affordances.
- Safe interactions (e.g., text selection/copy) do not show toasts; an edit attempt is any interaction that would enter edit mode or change a field value; only edit attempts show a non-blocking informational toast; reopening requires explicit `Reopen` in document view.
- Reopen from document view returns the document to the non-reviewed state and re-enters the to-review subset.
- Future enhancement (not required in this story): add a `Show reviewed` toggle to reveal reviewed items inline.

**Data / State Notes**
- Persist review state via `review_status` (`to_review` or `reviewed`).
- Persist `reviewed_at` timestamp when entering reviewed state.
- `reviewed_by` is optional and recorded when user identity is available.
- Reopen clears or updates reviewed-state metadata per authoritative contract while preserving extracted/corrected field content.

**Authoritative References**
- UX: Veterinarian review flow and status visibility: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Sections 1, 4, and section **Review UI Rendering Rules (Global Schema Template)**.
- Product: Human-in-the-loop and non-blocking workflow principles: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md) Sections 2 and 5.
- Tech: Review status model and transition rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A1.3 + Appendix B4.

**Test Expectations**
- Sidebar status icon/label switches correctly between non-reviewed and reviewed states.
- Mark reviewed keeps the document visible in the sidebar, visually separated from the to-review subset and visually muted.
- Reopen from document view returns the document to the non-reviewed state and re-enters the to-review subset.
- While reviewed, fields are non-editable; safe interactions (e.g., text selection/copy) do not show toasts; edit attempts trigger a non-blocking informational toast.
- Repeated toggle actions are idempotent and do not lose field edits/corrections.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
