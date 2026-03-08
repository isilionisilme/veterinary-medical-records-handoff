# IMP-04 — Active Plan Migration and Global Index Cleanup

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (active plan docs + global/index references only)

**Technical Outcome**
Bring all active plan files into full compliance with the updated operational model while cleaning global/index references that still point to legacy semantics, without rewriting historical completed plan content.

**Problem Statement**
Even with updated canonical policy and guardrails, active plans can remain inconsistent (legacy operational step patterns, stale metadata, inconsistent documentation tasks), and global index pages can still route readers to outdated references.

**Scope**
- Migrate active plans to the agreed policy:
  - no operational actions as executable checklist steps,
  - commit guidance inline and non-blocking,
  - explicit wiki documentation task with `no-doc-needed` fallback and rationale,
  - normalized automation mode metadata and role-neutral agent wording.
- Ensure active plan naming/structure conventions remain consistent with current operational standards.
- Clean global/index/reference docs that still expose legacy operational pointers.
- Keep references coherent across `implementation-plan`, release overviews, and project-level index pages.

**Out of Scope**
- No modifications to files under `plans/completed/` body content.
- No new CI/script enforcement logic (owned by IMP-03).
- No canonical policy redesign (owned by IMP-01).
- No router/maps contract propagation (owned by IMP-02).
- No product API or UI changes.

**Acceptance Criteria**
- All active plans comply with the updated operational policy model.
- No active plan includes operational checklist steps (`commit`, `push`, `create/update PR`, `merge`) as executable tasks.
- Every active plan includes explicit documentation handling (update wiki or justified `no-doc-needed`).
- Active plan metadata uses normalized automation mode semantics and role-neutral agent terminology.
- Global/index-level references no longer direct users to obsolete operational semantics.
- No `plans/completed/` content body is modified.

**Validation Checklist**
- Manual scan across active plan files confirms policy conformance.
- Search confirms no active plan contains legacy operational-step checklist patterns.
- Search confirms documentation task presence in every active plan.
- Search confirms global/index references to deprecated operational pointers are removed or updated.
- Verify changed docs remain internally link-valid and contextually coherent.

**Risks and Mitigations**
- Risk: accidental edit of completed plan history.
  - Mitigation: enforce strict path scope; exclude `plans/completed/` from edits.
- Risk: over-editing low-value historical references in unrelated docs.
  - Mitigation: limit cleanup to active navigation/index surfaces only.
- Risk: migration drift between active plans.
  - Mitigation: apply a single migration checklist to every active plan.

**Dependencies**
- Depends on IMP-01 policy being stable.
- Best sequenced after IMP-02 so mappings/parity logic are already aligned before active-plan cleanup finalization.

---
