# Structured interpretation schema 
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix D (Structured Interpretation Schema visit-grouped canonical contract).

Alignment note:
- Interpretation output may be partial with respect to the full Global Schema key universe.
- Backend does not backfill missing keys for presentation; frontend materializes the full schema view per Product Design authority.

## Storage contract
Authority:
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix D3 (Relationship to Persistent Model)
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B2.4 (InterpretationVersion)
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A3 (Interpretation & Versioning Invariants)

Implementation responsibility:
- Store the structured interpretation JSON as `InterpretationVersion.data`.
- Any edit creates a new `InterpretationVersion` (append-only).
- Exactly one active interpretation version per run.

## Critical keys
`StructuredField.is_critical` MUST be derived from `key ∈ CRITICAL_KEYS`.
Source of truth: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md).

Backend responsibility:
- Apply deterministic derivation at write-time (or validate on write).
- Do not allow the model to decide criticality.

## Tooltip breakdown data sourcing (MVP)

- Backend provides tooltip breakdown values when available.
- `text_extraction_reliability` comes from run/extraction diagnostics; if unavailable, expose `null`.
- `field_review_history_adjustment` comes from calibration aggregates for (`context_key`, `field_key`, `mapping_id`) under active `policy_version`; when no history exists, expose deterministic `0`.
- Frontend must not compute these values.
