# PRODUCT_DESIGN — Modules

This content was split into smaller modules for token-optimized assistant reads.

Start with `AGENTS.md` (repo root) and `docs/agent_router/00_AUTHORITY.md` for intent routing.

## Index
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/10_preamble.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/20_note-for-readers.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/30_high-level-product-approach.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/40_1-core-product-strategy.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/50_2-human-in-the-loop-philosophy-product-level.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/60_3-structural-signals-pending-review.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/70_4-critical-concepts.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/75_4-4-critical-non-reversible-changes-policy.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/76_conceptual-model-local-schema-global-schema-and-mapping.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/77_global-schema-canonical-field-list.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/78_global-schema-medical-record-mvp-field-list.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/80_5-separation-of-responsibilities-product-level.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/90_6-learning-governance.md`
- `docs/agent_router/04_PROJECT/PRODUCT_DESIGN/100_7-final-product-rule.md`

## Propagated updates
- Conceptual-model ownership includes explicit separation of `candidate_confidence` (diagnostic) and `field_mapping_confidence` (context stability).
- Context, learnable-unit (`mapping_id`), and confidence-propagation calibration semantics are maintained in this module set.
- Global Schema historical/canonical ownership remains in `docs/projects/veterinary-medical-records/01-product/product-design.md`; router modules are derived convenience shards only.
