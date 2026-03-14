# US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement)

**Status:** Implemented (2026-02-21)

### Context / Problem
With US-43, the UI is strictly contract-driven: it renders `active_interpretation.data.visits[]` when `canonical contract`, without inferring or grouping visits client-side.

Current issue: in documents that visually contain multiple episodes/visits, the backend often returns only:
- `visits = [{ visit_id: "unassigned", ... }]`
or an empty grouping, making “Extracted Data > Visits” operationally unhelpful.

This is a backend grouping coverage issue, not a UI issue.

### Objective
Improve coverage of the `Structured Interpretation Schema (visit-grouped)` contract so that:

When there is sufficient deterministic evidence of distinct clinical episodes, the backend produces real VisitGroups (`visit_id != "unassigned"`) with `visit_date` populated when appropriate, preserving determinism and safety.

This story does NOT guarantee “≥1 visit” for all documents.
If evidence is insufficient, it is correct for everything to remain in `unassigned`.

### User Story
As a veterinarian reviewer,
I want the Visits section to show clinical episodes grouped when the document contains clear evidence of multiple visits,
so I can review and edit information per episode with lower cognitive load and better clinical context.

### Scope (MVP)

In scope
1) Deterministic visit detection (backend)
- If the document contains sufficient evidence of at least one identifiable clinical episode:
  - Backend produces `visits[]` with ≥ 1 group where `visit_id != "unassigned"`.
  - `visit_date` is populated when supported by the “sufficient evidence” definition in TECHNICAL_DESIGN.
- If evidence is insufficient:
  - Everything remains in `unassigned`.

2) Assignment of visit-scoped fields
- Visit-scoped fields (per TECHNICAL_DESIGN Appendix D9) should be placed into `visits[].fields[]` when assignment is consistent.
- If a field cannot be associated with sufficient evidence or is ambiguous:
  - it falls into `unassigned`.

3) Determinism (same input → same output)
- Same input yields the same `visits[]` structure (IDs, ordering, assignments), except for intentional pipeline changes.
- `visits[]` ordering follows the rules documented in TECHNICAL_DESIGN Appendix D9.

Out of scope
- High-coverage grouping of all visits.
- Complex ambiguity resolution beyond contract-defined basic rules.
- ML/LLM inference for visits.
- UI changes (contract-driven rendering is covered by US-43).

### Contractual rules / Non-negotiables
- UI does not invent visits or regroup data.
- Anything not assignable with sufficient evidence → `unassigned`.
- `visit_date` is VisitGroup metadata (not a field in `fields[]`).
- This story references (does not redefine) the canonical visit-grouped contract in TECHNICAL_DESIGN Appendix D9.

### Acceptance Criteria (testable)

1) Agreed multi-visit fixture
- Given a stable fixture (PDF or equivalent) with multiple visits and clear clinical dates,
- When processed,
- Then `active_interpretation.data.visits[]` contains at least one group with:
  - `visit_id != "unassigned"`,
  - and `visit_date` populated when supported by the “sufficient evidence” definition in TECHNICAL_DESIGN.

2) No structural scoping regression
- No visit-scoped keys appear in `data.fields[]` (per TECHNICAL_DESIGN Appendix D9).
- Visit-scoped keys appear in `visits[].fields[]` or in `unassigned` (based on evidence/assignment).

3) UI outcome
- In Visits, the user sees at least one “Visit <date>” block when the contract produces an assigned VisitGroup, plus the “Unassigned” block if applicable.

4) Determinism
- Reprocessing the same fixture yields the same `visits[]` structure (IDs, order, assignments).

5) Regression guardrail
- A backend integration test fails if, for the agreed fixture, everything ends up in `unassigned`.

### Dependencies
- Define and version a stable multi-visit fixture.
- TECHNICAL_DESIGN must document what constitutes “sufficient evidence” to create a VisitGroup and populate `visit_date` (do not define it in this US).

### Risks / Watch-outs
- False positives by confusing dates (DOB, report issue date, invoice date) with clinical visit dates.
- Documents with multiple dates but a single clinical episode (over-segmentation).
- Extraction/canonicalization changes causing regressions; guardrail must catch it.

---
