# US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal

**Status**: Implemented (2026-02-19)

**User Story**
As a veterinarian reviewer, I want to see a small list of alternative extracted candidates when editing a field, so that I can correct values faster by selecting a suggestion while still being able to type any manual correction.

**Acceptance Criteria**
Data contract (standard review payload)
- The standard review payload includes optional per-field `candidate_suggestions` as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) section **Field Candidate Suggestions (standard review payload)**.
- Backwards compatible: clients MAY ignore `candidate_suggestions`.

UI (existing edit modal only)
- In the existing field edit modal, when `candidate_suggestions` exist for the field (and there is at least one alternative different from the current displayed value; trimmed string equality), show a section:
  - Title: `Sugerencias (N)`
  - Subtitle: `Selecciona una sugerencia o escribe tu propia corrección.`
- Show up to 5 candidates in a compact clickable list (per Technical Design; current max length is 5).
- The top-1 candidate is labeled `Sugerido`.
- Clicking a candidate copies its value into the input (does not auto-save).
- The input remains fully editable; manual typing overrides any prior selection.
- Validation behavior remains unchanged: Save remains disabled unless existing `validateFieldValue(...)` is OK.
- If there are no candidates (or only the current value), the `Sugerencias` section is not shown.

No layout disruption
- Global Schema layout remains stable; do not add inline expansion in the report view. Only the edit modal changes.

**Scope Clarification**
- Does not change confidence computation logic, confidence tooltip breakdown, or `mapping_confidence` semantics.
- Does not add new review modes or new screens.
- Does not add new validation rules; reuses existing validators/normalizers.
- Candidates may be derived from existing debug candidate logic, but must be surfaced via the standard payload contract referenced above (not gated by debug env flag).

**Authoritative References**
- [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)
- [`docs/projects/veterinary-medical-records/01-product/design-system.md`](../../01-product/design-system.md)
- [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md)
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) section **Field Candidate Suggestions (standard review payload)**

**Test Expectations**
Backend:
- Unit tests verify ordering, truncation to max length 5, and optional presence (per Technical Design contract).
Frontend:
- Tests verify suggestions render only when present, click copies value, manual typing works, and validation/save-disable remains unchanged.

**Definition of Done (DoD)**
- Acceptance criteria met.
- No regressions in report-like density (no new always-visible blocks).
- Backend + frontend tests added/updated per repo conventions.

---
