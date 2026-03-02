# 7. Confidence (Technical Contract)

- Each structured field MUST carry a `confidence` number in range 0–1 (see Appendix D).
- Confidence is a stored **attention signal** only.
- The meaning/governance of confidence in veterinarian workflows is defined in [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../PRODUCT_DESIGN/00_entry.md).

## Tooltip breakdown visibility contract (MVP)

- `field_mapping_confidence` remains the primary veterinarian-facing confidence signal.
- Optional tooltip diagnostics:
  - `text_extraction_reliability` (`number|null`) for per-run/per-document extraction quality.
    - Unit/scale: ratio in `[0,1]` when present.
  - `field_review_history_adjustment` (`number`) for cross-document/system-level explanatory adjustment.
    - Unit: signed percentage points (`+7` -> `+7%`, `-4` -> `-4%`, `0` -> `0%`).
- `text_extraction_reliability` is not `candidate_confidence`.
- Tooltip breakdown is explanatory only; no document-level policy UI is exposed.

---
