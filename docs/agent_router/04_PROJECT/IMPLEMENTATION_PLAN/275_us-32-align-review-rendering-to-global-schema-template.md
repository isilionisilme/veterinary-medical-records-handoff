# US-32 — Align review rendering to Global Schema template

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want the review view to always use the full Global Schema template so that scanning is consistent across documents.

**Acceptance Criteria**
- The UI renders the complete Global Schema in fixed order and by sections, regardless of how many fields were extracted.
- Non-extracted keys render explicit placeholders (no blank gaps).
- While structured data is loading, the UI shows a loading state and does not render missing placeholders yet.
- Repeatable fields render as lists and show an explicit empty-list state when no items are present.
- Extracted keys outside Global Schema are rendered in a separate section named `Other extracted fields`.
- Veterinarian-facing copy does not expose governance terminology such as `pending_review`, `reviewer`, or `governance`.

**Scope Clarification**
- This story does not introduce new endpoints.
- This story does not change persistence schema.
- This story does not redefine error codes.
- This story does not change run semantics; it defines review rendering behavior only.
- Confidence payload naming follows the hard-rename contract: `field_mapping_confidence`, `text_extraction_reliability`, and `field_review_history_adjustment`.

**Authoritative References**
- Product: Global schema authority and field list: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) section **Global Schema (Canonical Field List)**.
- UX: Rendering and placeholder behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../UX_DESIGN/00_entry.md) section **Review UI Rendering Rules (Global Schema Template)**.
- Tech: Structured interpretation schema and partial payload boundary: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix D.
- Frontend implementation notes: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../FRONTEND_IMPLEMENTATION/00_entry.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Review screens always show the same section/key structure, independent of extraction completeness.
- Missing scalar values, missing repeatable values, and loading states are visually distinguishable and deterministic.
- Non-schema extracted keys are visible under `Other extracted fields`.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
