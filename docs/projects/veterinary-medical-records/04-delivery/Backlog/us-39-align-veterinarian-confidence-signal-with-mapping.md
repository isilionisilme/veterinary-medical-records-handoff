# US-39 — Align veterinarian confidence signal with mapping confidence policy

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want confidence dots/colors in the review UI to reflect mapping confidence policy so that the signal is consistent, explainable, and reliable for triage.

**Acceptance Criteria**
- Existing confidence dots/colors in veterinarian UI represent `field_mapping_confidence` (not candidate/legacy confidence).
- Low/medium/high confidence bands are derived from backend-provided `policy_version` + confidence band cutoffs.
- The UI does not use hardcoded confidence thresholds.
- If `policy_version` or confidence band cutoffs are missing, UI does not crash, explicitly indicates missing policy configuration (degraded mode), and emits a diagnostic/telemetry event without inventing fallback thresholds.

**Scope Clarification**
- This story aligns veterinarian-facing confidence semantics and display only.
- This story does not redefine policy contracts, persistence shape, or backend threshold logic.
- This story depends on the backend exposing `policy_version` + confidence band cutoffs in the document/schema payload per [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md).

**Authoritative References**
- Product: Confidence meaning and veterinarian-facing signal intent: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](../../01-product/product-design.md).
- UX: Confidence visualization behavior in review surfaces: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md).
- Tech: Policy-provided confidence configuration and response semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md).
- Frontend context: Confidence rendering implementation points: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../../02-tech/frontend-implementation.md).

**Test Expectations**
- Confidence dot/color mapping uses `field_mapping_confidence` with backend-provided confidence band cutoffs.
- Missing policy configuration triggers explicit degraded-mode UI behavior and a diagnostic/telemetry event without app crash.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
