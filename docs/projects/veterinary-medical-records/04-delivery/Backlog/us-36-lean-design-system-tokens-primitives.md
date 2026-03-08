# US-36 — Lean design system (tokens + primitives)

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian reviewing claims, I want a consistent UI foundation (tokens and reusable primitives) so that interactions remain predictable and future editable-field work does not introduce visual drift.

**Objective**
Introduce a minimal, consistent UI foundation to prevent ad-hoc styling and enable editable structured fields without UI drift.

**Acceptance Criteria**
- All UI work touched in this story uses design tokens (no scattered hex values in implementation files).
- Icon-only interactive controls are implemented via `IconButton` with required `label`; raw icon-only `<button>` / `<Button>` are forbidden unless documented as explicit allowlisted exceptions.
- Tooltip behavior is standardized (top placement + portal rendering to avoid clipping) and remains keyboard-accessible.
- At least one key review area adopts the primitives and wrappers (viewer toolbar icon actions + one structured-data section).
- Document status indicators are unified through a reusable `DocumentStatusCluster`, with the primary signal in the document list/sidebar and no redundant duplicate status surfaces.
- `docs/projects/veterinary-medical-records/01-product/design-system.md` exists and is linked from project docs navigation.
- Design-system guidance is reflected consistently in operational assistant modules.
- CI/local design-system check exists and runs.

**Scope Clarification**
- Define and wire a lean token set (surfaces/backgrounds, text, borders, spacing, radius, subtle shadow, semantic statuses for confidence/critical/missing).
- Ensure shadcn/ui + Radix-based primitives are available and used for button, tooltip, tabs, separator, input, toggle-group, and scroll-area.
- Add lightweight app wrappers: `IconButton`, `Section` / `SectionHeader`, `FieldRow` / `FieldBlock`, `ConfidenceDot`, `CriticalBadge`, `RepeatableList`.
- Add and adopt `DocumentStatusCluster` for consistent document status rendering in sidebar/list as the primary status signal.
- Migrate only touched review areas needed to prove adoption.

**Out of Scope**
- Full UI redesign.
- Broad re-theming beyond the minimum token setup.
- Large refactors of unrelated screens.

**Authoritative References**
- UX: Review interaction contract and confidence behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Sections 2–4 and section **Review UI Rendering Rules (Global Schema Template)**.
- Shared UX boundaries: [`docs/shared/01-product/ux-guidelines.md`](../../../../shared/01-product/ux-guidelines.md).
- Brand constraints and tokenization requirement: [`docs/shared/01-product/brand-guidelines.md`](../../../../shared/01-product/brand-guidelines.md).
- Design system implementation contract: [`docs/projects/veterinary-medical-records/01-product/design-system.md`](../../01-product/design-system.md).

**Test Expectations**
- Design-system guard script flags forbidden patterns and passes on compliant code.
- Viewer toolbar icon actions and structured-data field rendering continue to function with wrappers.
- Tooltips remain keyboard accessible and visible without clipping.
- Unified Document Status Cluster renders consistent status semantics in sidebar/list without redundant duplicate status messaging.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Lint/tests pass for touched frontend scope.
- Docs updated and normalized.
- PR summary verifies each acceptance criterion.

---
