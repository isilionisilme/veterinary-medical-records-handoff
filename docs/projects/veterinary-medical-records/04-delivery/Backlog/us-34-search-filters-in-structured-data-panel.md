# US-34 — Search & filters in Structured Data panel

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to quickly narrow down structured fields using search and simple filters so that I can focus on the most relevant data during review.

**Acceptance Criteria**
- A compact control bar is available under the `Datos estructurados` header.
- The control bar includes:
  - Search input with a magnifying-glass icon.
  - Confidence filter chips: `Baja`, `Media`, `Alta`.
  - Toggles: `Solo CRÍTICOS`, `Solo con valor`.
- Filtering applies to rendered Global Schema fields in fixed order.
- Search is case-insensitive and matches field label, schema key, and rendered value (when present).
- Confidence bucket semantics are:
  - `Baja` when confidence < 0.50
  - `Media` when confidence is 0.50–0.75
  - `Alta` when confidence >= 0.75
- Filters combine with logical AND.
- Repeatable fields:
  - Match search when at least one item matches.
  - Match `Solo con valor` when list length is > 0.
- Section behavior:
  - Without filters/search, all sections are shown.
  - With any filter/search active, sections with 0 matches are hidden/collapsed.
- If no fields match, the panel shows: `No hay resultados con los filtros actuales.`
- Search uses debounce between 150 and 250 ms.

**Scope Clarification**
- This story does not change Global Schema keys or ordering.
- This story does not add or modify endpoints.
- This story does not change interpretation persistence semantics.
- Changes should remain localized to the review panel UI and related filtering logic.

**Authoritative References**
- Product: Canonical field authority and order: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md) section **Global Schema (Canonical Field List)**.
- UX: Review rendering baseline and deterministic missing/empty behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) section **Review UI Rendering Rules (Global Schema Template)**.
- Brand: UI controls and visual consistency: [`docs/shared/01-product/brand-guidelines.md`](../../../../shared/01-product/brand-guidelines.md).
- Frontend context: review rendering backbone: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../../02-tech/frontend-implementation.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Unit tests cover search matching behavior (label/key/rendered value).
- Unit tests cover confidence bucket classification boundaries.
- Review panel keeps Global Schema order deterministic while filters are applied.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
