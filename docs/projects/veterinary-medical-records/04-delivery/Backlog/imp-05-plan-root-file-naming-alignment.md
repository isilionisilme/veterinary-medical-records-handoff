# IMP-05 — Plan Root File Naming Alignment

**Status:** Implemented

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (naming policy + discovery/compat + active-plan migration)

**Technical Outcome**
Replace the generic `PLAN_MASTER.md` root-file convention with a deterministic file name equal to the plan folder name, so each plan root file is uniquely identifiable by filename without opening it.

**Problem Statement**
Using `PLAN_MASTER.md` in every plan folder creates poor discoverability and high operator friction because all root files share the same name across the repository.

**Scope**
- Update canonical plan creation/execution policy so the root plan file name must match the plan folder name.
- Update active-plan discovery rules and helper scripts to resolve the new naming convention.
- Preserve temporary backward-read compatibility for legacy plans that still use `PLAN_MASTER.md` during migration.
- Migrate active plans to the new naming convention.
- Update implementation-plan and operational references that currently assume `PLAN_MASTER.md`.

**Out of Scope**
- No rewrite of completed plan body content.
- No backend/frontend product behavior changes.
- No unrelated refactors to plan schema/sections.

**Naming Rule**
- For a folder `PLAN_<YYYY-MM-DD>_<SLUG>/`, the root file must be:
  - `PLAN_<YYYY-MM-DD>_<SLUG>.md`
- `PLAN_MASTER.md` is disallowed for newly created plans.
- During migration, legacy read support remains allowed until all active plans are migrated.

**Acceptance Criteria**
- Canonical docs define the new root-file naming rule explicitly.
- Active-plan resolution logic supports the new file name and can still read legacy roots during transition.
- All active plans use folder-matching root file names.
- No newly created plan uses `PLAN_MASTER.md`.
- Global/index references and examples use the new naming convention.

**Validation Checklist**
- Search confirms active plan roots no longer use `PLAN_MASTER.md`.
- Search confirms canonical examples/templates reference folder-matching root file names.
- Plan discovery behavior is verified for:
  - new-named active plans,
  - legacy `PLAN_MASTER.md` plans (read compatibility),
  - ambiguous/missing root cases.
- Link/reference integrity remains valid after rename updates.

**Risks and Mitigations**
- Risk: tooling/scripts fail to find plans after rename.
  - Mitigation: add dual-read compatibility during transition and test both patterns.
- Risk: partial migration leaves mixed naming and confusion.
  - Mitigation: migrate all active plans in one controlled pass.
- Risk: accidental edits to completed plans.
  - Mitigation: keep migration scope limited to active plan roots and reference/index docs.

**Dependencies**
- Depends on IMP-01 policy baseline.
- Should be coordinated with IMP-02/IMP-04 to keep mappings and active-plan docs consistent.
