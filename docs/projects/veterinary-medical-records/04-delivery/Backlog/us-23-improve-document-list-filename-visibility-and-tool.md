# US-23 — Improve document list filename visibility and tooltip details

**User Story**
As a user, I want document names to be more readable in the list so that I can identify files quickly without opening each document.

**Acceptance Criteria**
- In the document list, long filenames use the available horizontal space before truncation.
- When a filename is truncated, hover and keyboard focus reveal a tooltip with the full filename and key metadata shown in the row.
- Tooltip behavior is accessible: focus-triggered, dismissible with keyboard, and available on desktop and touch alternatives (for example, tap/long-press fallback).
- The list remains usable on mobile widths without overlapping status/actions.

**Scope Clarification**
- Already partially covered by US-04 (list visibility and metadata), but this story adds readability and accessibility refinements.
- This story does not introduce search/filtering/sorting.

**Authoritative References**
- UX: Document list behavior and responsive interaction principles: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)
- UX: Accessibility and interaction consistency: [`docs/shared/01-product/ux-guidelines.md`](../../../../shared/01-product/ux-guidelines.md)

**Test Expectations**
- Long filenames are easier to scan due to increased visible text before truncation.
- Tooltip content matches source metadata and is accessible via keyboard focus.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
