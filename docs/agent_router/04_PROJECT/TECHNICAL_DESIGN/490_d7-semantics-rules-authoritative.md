# D7. Semantics & Rules (Authoritative)

## D7.1 Confidence
- Confidence never blocks: editing, marking reviewed, or accessing data.
- UI may render qualitatively (e.g., low / medium / high).

## D7.2 Multiple Values
Repeated concepts (e.g., medications) are represented by multiple fields with the same `key` and different `field_id`s.

## D7.3 Governance (Future-Facing)
Structural changes (new keys, key remapping) may later be marked as pending review for schema evolution.
This is never exposed or actionable in veterinarian-facing workflows.

## D7.4 Critical Concepts (Authoritative)

Derivation (authoritative):
- `StructuredField.is_critical = (StructuredField.key ∈ CRITICAL_KEYS)`

Rules (technical, authoritative):
- `is_critical` MUST be derived from the field key (not model-decided).
- `CRITICAL_KEYS` is a closed set (no heuristics, no model output).
- This designation MUST NOT block workflows; it only drives UI signaling and internal flags.

Source of truth for `CRITICAL_KEYS`:
- Defined in [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md) (product authority).
- The complete Global Schema key list, fixed ordering, section grouping, repeatability rules, and cross-key fallback rules (including `document_date` fallback to `visit_date`) are also governed by [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md).

---
