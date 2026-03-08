# US-40 — Implement field-level confidence tooltip breakdown

**Status**: Implemented (2026-02-18)

**User Story**
As a veterinarian, I want to understand why a field confidence looks the way it does so I can triage and review faster.

**Acceptance Criteria**
- Tooltip renders consistently for all fields that expose confidence dot/band.
- Tooltip is implemented with the shared wrapper and is keyboard accessible on focus/hover.
- Tooltip shows overall confidence percentage, explanatory copy, and breakdown lines for candidate confidence and review history adjustment.
- Adjustment semantic styling follows positive/negative/zero rules using existing tokens/classes.
- Edge cases are rendered deterministically: no history shows adjustment `0`; missing extraction reliability shows `No disponible`.
- Dot/band behavior remains unchanged and continues to use `field_mapping_confidence` as the primary visible signal.
- Confidence computation/propagation behavior is unchanged.
- Tooltip copy and structure align with [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) section **4.3 Confidence Tooltip Breakdown (Veterinarian UI)**.

**Scope Clarification**
- Implements the confidence tooltip pattern defined in UX + Design System for veterinarian review fields.
- `field_mapping_confidence` remains the primary visible signal (dot + band); tooltip is explanatory.
- Frontend consumes backend-provided breakdown values as render-only input.
- This story does not change confidence computation or propagation.
- This story does not add analytics/chart views, document-level confidence policy UI, recalibration mechanics, field reordering, layout shifts, or governance terminology in veterinarian-facing copy.

**Data Assumptions / Dependencies**
- Review payload includes field-level `field_mapping_confidence` (0–1).
- Review payload may include `text_extraction_reliability` (0–1, nullable); it must not be inferred from `candidate_confidence`.
- Review payload includes deterministic `field_review_history_adjustment` (signed percentage points), with `0` when no history is available.
- Exact payload shape and sourcing are governed by the authoritative technical docs referenced below.

**Out of Scope**
- Calibration/policy management UI.
- Document-level confidence policy UI.
- Charts, analytics, or historical dashboards.
- Recalibration logic changes or any confidence algorithm change.

**Authoritative References**
- UX tooltip contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) section **4.3 Confidence Tooltip Breakdown (Veterinarian UI)**.
- Design system tooltip pattern: [`docs/projects/veterinary-medical-records/01-product/design-system.md`](../../01-product/design-system.md).
- Technical contract and visibility invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md).
- Backend sourcing responsibilities: [`docs/projects/veterinary-medical-records/02-tech/backend-implementation.md`](../../02-tech/backend-implementation.md).
- Frontend rendering responsibilities: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](../../02-tech/frontend-implementation.md).

**Test Expectations**
- Confidence tooltip appears on all confidence-bearing fields with consistent structure and accessibility behavior.
- Positive/negative/zero adjustment styling uses existing semantic tokens/classes with no new color system.
- No-history and missing-extraction edge cases render as defined without fallback computation in frontend.
- No regressions to existing dot/band behavior, field ordering, or review interaction flow.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
