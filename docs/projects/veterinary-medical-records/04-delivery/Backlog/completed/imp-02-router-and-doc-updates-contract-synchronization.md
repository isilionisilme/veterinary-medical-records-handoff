# IMP-02 — Router and DOC_UPDATES Contract Synchronization

**Status:** Done

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (derived docs and contract maps only)

**Technical Outcome**
Propagate canonical policy updates into router modules and DOC_UPDATES contract maps so assistants and guardrails evaluate the same source-of-truth semantics with no legacy drift.

**Problem Statement**
After canonical policy changes, derived router files and DOC_UPDATES mappings can remain stale (for example, legacy references to `execution-rules.md`), causing inconsistent assistant behavior or false pass/fail conditions in documentation guardrails.

**Scope**
- Regenerate router files from canonical sources.
- Update DOC_UPDATES `test_impact_map.json` and `router_parity_map.json` so owner-backed mappings reflect current canonical sources (`plan-execution-protocol.md`, `plan-creation.md`, and current implementation-plan owner modules).
- Remove/replace stale legacy mapping references that are no longer authoritative.
- Ensure project owner modules for Implementation Plan remain synchronized with `implementation-plan.md`.

**Out of Scope**
- No new execution guard implementation in `scripts/ci`.
- No migration of active plan files.
- No backend/frontend product changes.
- No historical rewrite of completed plans.

**Acceptance Criteria**
- `python scripts/docs/generate-router-files.py --check` passes.
- `python scripts/docs/check_doc_test_sync.py --base-ref <base>` passes with no unmapped or owner propagation gaps.
- `python scripts/docs/check_doc_router_parity.py --base-ref <base>` passes with required terms present.
- `python scripts/docs/check_router_directionality.py --base-ref <base>` passes.
- No DOC_UPDATES mapping rule references deprecated canonical ownership paths.

**Validation Checklist**
- Confirm changed canonical sources have explicit and correct router parity mappings.
- Confirm changed canonical sources have explicit and correct doc/test impact mappings.
- Confirm IMPLEMENTATION_PLAN owner module files were propagated when `implementation-plan.md` changed.
- Confirm no stale reference remains that could route assistants to obsolete policy semantics.

**Risks and Mitigations**
- Risk: map edits become over-broad and weaken fail-closed behavior.
  - Mitigation: keep mappings source-specific and preserve strict required-term checks.
- Risk: router regeneration introduces unrelated drift.
  - Mitigation: regenerate once and review only touched owner families before merge.

**Dependencies**
- Depends on IMP-01 canonical policy alignment being merged or at least finalized in branch scope.

---
