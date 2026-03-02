# US-46 — Deterministic Visit Assignment Coverage MVP (Schema)

**Status:** Planned  
**Owner:** Platform / Backend (contract-driven)

## Context
- US-43: UI renders `visits[]` contract-driven (no client-side grouping).
- US-45 (implemented): backend can create assigned VisitGroups when sufficient deterministic evidence exists, with safe fallback to `unassigned`.
- Current problem: even when multiple visits exist, relevant clinical information still appears as “unassigned/not associated to a visit”, reducing coherence and increasing cognitive load.

## Objective
Improve clinical coherence per visit by safely increasing the proportion of visit-scoped clinical information shown under the correct visit **when evidence is consistent**, without weakening safety.

## User Story
As a veterinarian reviewer,  
I want to see visit-scoped clinical fields (per TECHNICAL_DESIGN Appendix D9; e.g., diagnosis/medication/procedure when present) within the correct visit when evidence allows it,  
so I can review each episode with clear clinical context and lower cognitive load.

## Scope (MVP)

**In scope**
- Improve deterministic assignment of visit-scoped clinical fields to **existing** VisitGroups (created by US-45), only when evidence is consistent.
- Preserve the possibility that some information remains in the `unassigned` bucket when evidence is insufficient.

**Out of scope**
- Creating new VisitGroups or changing how they are created (owned by US-45).
- Advanced ambiguity resolution beyond the deterministic criteria documented in TECHNICAL_DESIGN.
- ML/LLM.
- UI changes (beyond contract-driven rendering already covered by US-43).

## Acceptance Criteria (testable)

**User-facing**
1) **Per-visit coherence**
- Given a document with multiple visits and an assigned VisitGroup present,
- When I open the “Visits” section,
- Then I see visit-scoped clinical fields (per D9; e.g., diagnosis/medication/procedure when present) inside specific visits when evidence supports it, instead of all being shown under the unassigned bucket.

2) **Transparency when evidence is insufficient**
- If some visit-scoped fields cannot be clearly associated to a visit,
- Then they remain shown under the unassigned bucket (label/copy as defined in `docs/projects/veterinary-medical-records/01-product/ux-design.md`), without forcing doubtful assignments.

3) **Measurable improvement (fixture-bound + frozen baseline)**
- Define a stable fixture `mixed_multi_visit_assignment` and a versioned baseline expected-output snapshot.
- On that fixture, increase by **≥ +2** the number of visit-scoped fields moved from unassigned to assigned visits (vs the frozen baseline).
- Ensure at least **1** key clinical field (diagnosis/medication/procedure when present with sufficient evidence) is assigned to a **non-unassigned** VisitGroup.

4) **Reproducibility**
- Reprocessing the same fixture yields the same VisitGroups and the same field→visit assignments.

**Non-user-facing guardrails (testable)**
5) **No new visits created**
- For the agreed fixture, the set of VisitGroups (visit_ids/dates and ordering) must remain unchanged vs the frozen baseline snapshot.

6) **No leakage**
- Visit-scoped keys (per D9) must not appear in top-level `data.fields[]`; they must appear only in `visits[].fields[]` or in the unassigned bucket.

7) **Safety guardrail**
- Administrative/non-visit dates (DOB, report/invoice emission, microchip/admin identifiers, etc.) must not force visit assignment.

8) **Regression guardrail**
- Integration test fails if:
  - there is no improvement vs baseline, or
  - new visits are created for the fixture, or
  - leakage occurs to `data.fields[]`, or
  - administrative contexts force assignment.

## Documentation Requirement
- Document the deterministic assignment criteria in `docs/projects/veterinary-medical-records/02-tech/technical-design.md` (Appendix D9 or an adjacent note). This story references the contract; it does not redefine it.

## Authoritative References
- `docs/projects/veterinary-medical-records/02-tech/technical-design.md` — Appendix D9 (visit grouping + visit-scoped keys + ordering rules)
- `docs/projects/veterinary-medical-records/01-product/ux-design.md` — unassigned label/copy and any relevant empty-state or wording

---
