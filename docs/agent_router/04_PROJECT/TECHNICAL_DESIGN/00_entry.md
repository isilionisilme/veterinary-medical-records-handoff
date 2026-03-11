# TECHNICAL_DESIGN — Modules

This content was split into smaller modules for token-optimized assistant reads.

Start with `AGENTS.md` (repo root) and `docs/agent_router/00_AUTHORITY.md` for intent routing.

## Index
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/10_preamble.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/20_purpose.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/30_1-system-overview-technical.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/40_1-1-deployment-model-intent.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/50_1-2-logical-pipeline-conceptual.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/60_1-3-domain-model-overview-conceptual.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/70_1-4-persistence-strategy-intent.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/80_1-5-safety-design-guardrails.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/90_2-architecture.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/100_3-processing-model.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/110_4-reprocessing-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/120_5-review-editing-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/130_6-data-persistence-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/140_7-confidence-technical-contract.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/150_8-error-handling-states.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/160_9-observability.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/170_10-api-notes.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/180_11-scope-ownership.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/190_12-data-lifecycle.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/195_13-security-boundary.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/197_14-known-limitations.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/200_13-final-instruction.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/210_a1-state-model-source-of-truth.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/220_a2-processing-run-invariants.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/230_a3-interpretation-versioning-invariants.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/240_a4-confidence-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/250_a5-api-contract-principles.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/260_a6-concurrency-idempotency-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/270_a7-governance-invariants.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/280_a8-audit-observability-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/290_a10-final-rule.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/300_b1-asynchronous-in-process-processing-model-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/310_b2-minimal-persistent-data-model-textual-erd.md`

Canonical project references routed here include:
- `docs/projects/veterinary-medical-records/02-tech/technical-design.md`
- `docs/projects/veterinary-medical-records/02-tech/extraction-quality.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/320_b3-minimal-api-endpoint-map-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/330_b3-2-endpoint-error-semantics-error-codes-normative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/340_b4-idempotency-safe-retry-rules-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/350_b5-filesystem-management-rules.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/360_b6-blocking-rules-normative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/370_b7-testability-expectations.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/380_final-rule.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/390_c1-processing-step-model-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/400_c2-run-state-derivation-from-steps-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/410_c3-error-codes-and-failure-mapping-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/420_c4-relationship-between-step-artifacts-and-logs-normative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/430_d1-scope-and-design-principles.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/440_d2-versioning.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/450_d3-relationship-to-persistent-model-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/460_d4-top-level-object-structuredinterpretation-json.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/470_d5-structuredfield-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/480_d6-evidence-approximate-by-design.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/490_d7-semantics-rules-authoritative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/500_d8-example-multiple-fields.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/505_d9-structured-interpretation-schema-visit-grouped-normative.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/510_e1-pdf-text-extraction.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/520_e2-language-detection.md`
- `docs/agent_router/04_PROJECT/TECHNICAL_DESIGN/530_e3-dependency-justification-repository-requirement.md`

## Propagated updates
- Context deterministic keying, `mapping_id` learnable-unit identity, and policy thresholds/hysteresis contracts are maintained in technical-design modules.
- Reviewed signal semantics and calibration observability requirements remain authoritative within this module family.
- Security Boundary (§13) and Known Limitations (§14) sections added from CTO verdict iteration 2 (F8-D). Auth scope, production path, and limitation table propagated.
- Naming clarification propagated: architecture layer naming uses `infra (infrastructure)` to stay aligned with `backend/app/infra/`.
- Known Limitations propagation note refreshed: `routes.py` concentration is now marked resolved (Iteration 6), `AppWorkspace.tsx` baseline is updated to ~2,200 LOC, and pending hardening gaps include API rate limiting and FK index coverage.
- Iteration 10 propagation (F16-K): Security Boundary now documents active rate limiting (`slowapi`), UUID path validation, and CI security audit gates; Known Limitations marks rate limiting and FK index gaps as resolved.
- Iteration 11 propagation (F18-T): Known Limitations updated to reflect repository aggregate split and refreshed AppWorkspace sizing; technical notes now include benchmark evidence and frontend error UX mapping references.
- Canonical TECHNICAL_DESIGN refresh synchronized on 2026-02-28 (classification: clarification/navigation in this cycle).
- Canonical EXTRACTION_QUALITY reference is now tracked under this module family for doc-router parity and doc/test sync ownership.
- Canonical EXTRACTION_QUALITY wording now uses neutral extraction-tracking artifact references (no direct `docs/agent_router/*` path literals).
- Canonical TECHNICAL_DESIGN sync on 2026-03-09: E2E limitation wording aligned to `65 tests / 21 specs` and related architecture-link corrections propagated.
- Canonical EXTRACTION_QUALITY sync on 2026-03-09: governance wording and navigation refresh propagated under TECHNICAL_DESIGN ownership.
- Canonical TECHNICAL_DESIGN sync on 2026-03-11 (ARCH-09): B2 now includes a Mermaid ER diagram for the five core entities (`Document`, `ProcessingRun`, `Artifacts`, `InterpretationVersion`, `FieldChangeLog`) with FK/cardinality annotations.
