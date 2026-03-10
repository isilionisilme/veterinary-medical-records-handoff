# IMP-08 — Documentation Contract Enforcement for Docs-Only PRs

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (CI workflow + doc guards + contract sources)

**Technical Outcome**
Prevent documentation-only pull requests from merging when canonical policy text, compatibility stubs, and documentation contract tests drift out of sync.

**Problem Statement**
The current validation model lets docs-only PRs pass CI when they update canonical operational docs and router outputs but forget to update or execute the focused documentation contract suite. The result is a false-green PR: guards pass, while targeted contract tests still fail locally. This is especially risky for policy renames and compatibility-stub updates because multiple files encode the same contract manually.

**Scope**

### S1 — Docs-only contract test job in CI

Add a dedicated CI job that runs on pull requests with documentation changes and executes the focused documentation contract suite without backend coverage gating. Minimum scope:

1. Run `backend/tests/unit/test_doc_updates_contract.py`.
2. Run `backend/tests/unit/test_doc_router_contract.py`.
3. Run `backend/tests/unit/test_doc_updates_e2e_contract.py`.
4. Keep this job independent from the backend `quality` job so docs-only PRs still validate contracts.

### S2 — Tighten DOC_UPDATES sync semantics

Refactor the DOC_UPDATES sync model so mapping rules distinguish between:

1. **Owner propagation** — files that must be updated when a source doc changes.
2. **Guard wiring** — scripts/maps that define the validation system.
3. **Required tests** — focused tests that must be updated or executed for rule changes.

The current `required_any` model is too permissive because a PR can satisfy the guard by touching map/wiring files without fixing the broken contract test.

### S3 — Rule-classified docs must trigger focused contracts

Use the existing documentation classifier to escalate validation:

1. If overall classification is `Rule`, require the focused contract job to run.
2. If classification is `Clarification` or `Navigation`, the lighter guard path may remain valid.
3. If classification is stale or unavailable, fail closed to the stricter path.

### S4 — Centralize doc contract expectations

Reduce manual duplication for high-risk policy names and compatibility sections by introducing a single structured source of expectations. Candidate approaches:

1. A machine-readable manifest consumed by contract tests.
2. Generated compatibility stubs from canonical sources.
3. Shared expected-term fixtures imported by multiple test modules.

The objective is to make policy renames a single-source update instead of a coordinated manual edit across canonical docs, stubs, and tests.

### S5 — Documentation and operational guidance

Update the relevant operational docs so contributors understand:

1. Why docs-only PRs now run focused contract tests.
2. Which files define owner propagation versus test enforcement.
3. How to update a policy rename safely.

**Out of Scope**
- No product/API/UI behavior changes.
- No redesign of the full backend `quality` job.
- No unrelated documentation cleanup outside the validation path.
- No migration of historical completed plans.

**Acceptance Criteria**
- Docs-only PRs run a focused documentation contract test job in CI.
- A docs-only PR that renames a canonical policy term but leaves `test_doc_updates_contract.py` stale fails in CI.
- DOC_UPDATES sync rules distinguish owner propagation from required tests.
- Rule-classified doc changes fail closed to the stricter validation path.
- At least one shared contract source or generated artifact removes manual duplication for high-risk policy names.
- Contributor-facing docs explain the new validation path.

**Validation Checklist**
- Create a temporary branch with a docs-only policy rename and no contract-test update → CI fails.
- Add the required contract test update → CI passes.
- Create a clarification-only doc PR → focused contract job is skipped or passes via the lighter path as designed.
- Confirm stale classification artifacts still fail closed.
- Confirm local L1/L2/L3 guidance remains coherent with CI behavior.

**Risks and Mitigations**
- Risk: docs-only PR latency increases.
  - Mitigation: run only the focused contract suite, not the full backend coverage job.
- Risk: mapping semantics become harder to maintain.
  - Mitigation: separate owner propagation from required-tests explicitly in schema and docs.
- Risk: generated stubs or manifests become another drift source.
  - Mitigation: derive them from canonical docs and validate generation in CI.

**Dependencies**
- Builds on the canonical policy changes from IMP-05.
- Should remain aligned with IMP-02 (DOC_UPDATES contract synchronization) and IMP-07 (CI parity guard local vs remote).

---