# IMP-09 — Rationalize Documentation Governance Tests

**Status:** Done

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 22 — Documentation governance follow-up

**PR strategy:** Single dedicated PR (docs test suite + CI wiring + guard semantics)

**Technical Outcome**
Keep the highest-signal documentation governance tests, reduce duplicated and prose-fragile assertions, and ensure documentation-focused pull requests execute the tests that are supposed to protect them.

**Problem Statement**
The current documentation governance suite provides useful coverage, but it mixes three different concerns in a way that is becoming expensive to maintain:

1. High-value behavior tests for guards and plan execution.
2. Broad contract tests that assert many exact documentation strings.
3. Partial overlap between tests that inspect the same guard behavior from slightly different angles.

There is also a CI gap: documentation-focused pull requests can execute the dedicated documentation guards while skipping part of the focused pytest suite that validates the same documentation contracts. This reduces the real protection value of the tests.

**Scope**

### S1 — Preserve high-signal guard behavior tests

Keep and maintain the tests that validate executable behavior with low maintenance cost:

1. `test_doc_router_parity_contract.py`
2. `test_router_directionality_guard.py`
3. `test_no_canonical_router_refs_guard.py`
4. `test_plan_execution_guard.py`
5. `test_classify_doc_change.py`
6. `test_doc_test_sync_guard.py`

These tests should remain behavior-oriented and should prefer rule semantics over exact prose checks.

### S2 — Reduce duplication and fragmentation

Refactor or merge tests that overlap too heavily:

1. Merge `test_check_no_canonical_router_refs.py` into `test_no_canonical_router_refs_guard.py`, or otherwise remove the duplication between categorization-only tests and broader guard behavior tests.
2. Review `test_doc_updates_contract.py`, `test_doc_updates_e2e_contract.py`, and `test_doc_router_contract.py` to remove duplicated assertions that only restate the same documentation text in multiple files.
3. Keep only the minimum contract checks needed to protect routing, mappings, required outputs, and critical propagation rules.

### S3 — Shift contract tests toward semantic invariants

Replace brittle exact-string expectations where possible with more stable assertions:

1. Prefer checking required sections, required terms, required files, and decision invariants.
2. Avoid large numbers of exact prose assertions unless the wording itself is the contract.
3. Keep exact-string checks only for high-risk normative phrases and compatibility terms.

### S4 — Fix documented but currently under-enforced guard semantics

Align the doc/test synchronization system with the intended policy:

1. Make `check_doc_test_sync.py` honor `rule_change_only` rules from `test_impact_map.json`.
2. Revisit the current global PR-level classification model and evaluate file-level classification when mixed doc changes are present.
3. Preserve fail-closed behavior for real rule changes.
4. Avoid forcing unrelated guard/map churn for closeout or clarification-only documentation updates.

### S5 — Ensure docs-focused PRs run the relevant pytest suite

Close the current CI gap so documentation-focused pull requests execute the focused documentation-governance pytest modules, not only the standalone guards.

Minimum expected coverage:

1. `backend/tests/unit/test_doc_updates_contract.py`
2. `backend/tests/unit/test_doc_updates_e2e_contract.py`
3. `backend/tests/unit/test_doc_router_contract.py`
4. Any additional focused guard tests required to validate the changed contract area.

### S6 — Clarify governance expectations for future contributors

Update the corresponding documentation so contributors can tell the difference between:

1. Behavior tests that should almost never be removed.
2. Contract tests that may need consolidation.
3. Guards that run unconditionally in CI.
4. Tests that must also run for docs-only PRs.

**Out of Scope**
- No product/backend/frontend feature changes.
- No redesign of the full test strategy outside documentation governance.
- No rewrite of the router generation architecture.
- No migration of historical backlog items unless required for broken links.

**Acceptance Criteria**
- A documented keep/modify/merge decision exists for every documentation-governance test module.
- Duplicated low-signal coverage around canonical-router reference categorization is merged or removed.
- At least one of the large contract suites is simplified to rely less on exact prose assertions.
- `check_doc_test_sync.py` honors `rule_change_only` semantics or an explicitly approved replacement design.
- Docs-focused PRs execute the focused documentation-governance pytest suite in CI.
- Contributor-facing guidance explains which documentation tests are high-value behavioral guards versus broader contract checks.

**Validation Checklist**
- Confirm the resulting suite still catches router parity regressions.
- Confirm the resulting suite still catches canonical→router reference violations.
- Confirm the resulting suite still catches invalid active plan state.
- Create a docs-focused PR touching contract text only and verify the focused pytest suite runs in CI.
- Create a clarification-only documentation change and verify the guard path remains proportionate.
- Create a rule-level documentation change using a `rule_change_only` mapping and verify the strict path triggers as intended.

**Risks and Mitigations**
- Risk: reducing prose assertions may remove some intended policy coverage.
  - Mitigation: keep exact-string checks only where wording is itself normative.
- Risk: merging tests may hide useful behavioral distinctions.
  - Mitigation: merge only overlapping cases and preserve distinct behavior scenarios.
- Risk: adding docs-focused pytest jobs increases CI time.
  - Mitigation: run only the focused documentation-governance test subset.

**Dependencies**
- Closely related to [IMP-02 — Router and DOC_UPDATES Contract Synchronization](imp-02-router-and-doc-updates-contract-synchronization.md).
- Closely related to [IMP-08 — Documentation Contract Enforcement for Docs-Only PRs](../imp-08-documentation-contract-enforcement-for-docs-only-prs.md).
- Depends on keeping the plan execution protocol and DOC_UPDATES workflow as the current policy source of truth.

---
