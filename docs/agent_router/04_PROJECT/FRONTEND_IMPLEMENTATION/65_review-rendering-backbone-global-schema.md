# Review Rendering Backbone (Global Schema)

Rendering authority for the full key universe, ordering, section grouping, repeatability, and fallback rules is
[`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) (Global Schema).

Frontend implementation guidance:
- Use Global Schema as the review rendering backbone.
- Render all keys in stable order, grouped by the same sections (A-G), even when values are missing.
- Show explicit empty states/placeholders for missing values; do not hide keys only because the model omitted them.
- If `document_date` is missing, display the Product Design fallback to `visit_date`.

Repeatable keys: `medication`, `diagnosis`, `procedure`, `lab_result`, `line_item`, `symptoms`, `vaccinations`, `imaging`.
- Always render the repeatable field container.
- Render an explicit empty-list state when there are no items.
- Scope note: payloads may include billing repeatables (for example `line_item`) even when Medical Record MVP UI scope excludes non-clinical concepts.

Value typing:
- Respect the existing contract value types: `string | date | number | boolean | unknown`.
- For ambiguous or unit-bearing values, default to `string`.
- Do not introduce new parsing obligations beyond existing backend/frontend contracts.
