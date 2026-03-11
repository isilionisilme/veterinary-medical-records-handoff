# IMP-03 — Plan Execution Guard Enforcement (Local + CI)

**Status:** Done

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (scripts + CI workflow changes only)

**Technical Outcome**
Enforce plan-execution protocol invariants through deterministic local and CI guardrails so progress cannot continue to push/merge when plan state is out of sync.

**Problem Statement**
Operational rules exist in docs, but enforcement is incomplete. Agents can still forget plan-state transitions (for example leaving steps unclosed), and the system currently relies on manual discipline instead of hard technical blocking.

**Scope**
- Add a new plan execution guard script under `scripts/ci` to validate active-plan integrity.
- Integrate the guard into local preflight execution (`preflight-ci-local.ps1`) for push/full modes when an active plan exists.
- Add a CI job in `.github/workflows/ci.yml` (for PRs) to run the same guard.
- Define clear blocking error messages for invalid states.
- Add a deterministic helper command (`plan-close-step.ps1`) to standardize step closure with required evidence checks.

**Out of Scope**
- No canonical policy wording changes (owned by IMP-01).
- No router/maps synchronization (owned by IMP-02).
- No migration of active plan content (owned by IMP-04/IMP-05).
- No backend/frontend product behavior changes.

**Guard Invariants (minimum required)**
- If an active plan exists for the current branch, `Execution Status` must be present.
- At most one step may be labeled `IN PROGRESS` or `STEP LOCKED` at any time.
- A new step cannot start while a `STEP LOCKED` line exists.
- A step is considered closed only when represented as clean `[x]` (no active-progress lock labels).
- Required evidence for step closure must be present before accepting closure.
- Active plan resolution must be deterministic:
  - search active plans under current plan roots excluding `completed/`,
  - branch match based on `**Branch:**`,
  - 0 matches => no-plan mode (pass),
  - >1 matches => hard fail with ambiguity message.

**Acceptance Criteria**
- Local preflight blocks invalid plan states with actionable errors.
- CI PR guard blocks invalid plan states with actionable errors.
- Valid happy-path plan progression passes both local and CI guard checks.
- No-plan branches are not blocked.
- Ambiguous active-plan detection fails explicitly.

**Validation Checklist**
- Happy path: in-progress step -> close via helper -> guard passes local + CI.
- Locked path: `STEP LOCKED` present and next step attempted -> guard fails.
- Ambiguity path: two active plans for same branch -> guard fails.
- No-plan path: branch without active plan -> guard passes.
- Error output includes next-step remediation guidance.

**Risks and Mitigations**
- Risk: false positives block unrelated branches.
  - Mitigation: strict active-plan detection by branch metadata and no-plan pass mode.
- Risk: guard bypass through manual markdown edits.
  - Mitigation: helper command + invariant checks in both local and CI.
- Risk: CI adoption friction.
  - Mitigation: clear messages and deterministic failure criteria; no warn-only final mode.

**Dependencies**
- Depends on IMP-01 policy semantics being finalized.
- Should land after or with IMP-02 if guard terms rely on updated mapped terminology.

---
