# IMP-15 — Remove Plan/Backlog Governance Layer

**Status:** Implemented

**Type:** CI / Process Improvement (governance removal)

**Target release:** N/A — standalone cleanup

**Origin:** PR #296 CI failure — `plan_execution_guard` rejects plans missing `## Execution Status`. Recurring friction from ceremony-only CI checks on plan and backlog documents.

**Severity:** HIGH (blocks PRs, creates recurring CI friction)
**Effort:** M (2-4h)

**Problem Statement**
The plan execution guard, plan-start checker, plan-close-step helper, plan agent prompts, plan/backlog agent instructions, and associated ceremony tests create significant friction without protecting product functionality. Every plan document change risks CI failure for format violations. Plans and backlog items will migrate to Linear, making in-repo governance infrastructure obsolete.

**Action**
1. Remove the `plan_execution_guard` CI job from `.github/workflows/doc-governance.yml`.
2. Delete CI/dev scripts: `check_plan_execution_guard.py`, `plan-close-step.ps1`, `plan-start-check.py`.
3. Remove plan guard invocation from `preflight-ci-local.ps1`.
4. Delete agent prompts: `plan-create`, `plan-start`, `plan-resume`, `plan-closeout`.
5. Delete agent instructions: `plan-files.instructions.md`, `backlog-files.instructions.md`.
6. Remove plan/backlog runbook lines and plan-specific global rules from `AGENTS.md`.
7. Delete test files: `test_plan_execution_guard.py`, `test_plan_start_check.py`.
8. Remove ceremony tests from `test_doc_updates_contract.py`, `test_doc_router_contract.py`, `test_doc_router_parity_contract.py`.
9. Update expected sets in remaining tests that enumerate prompts/instructions.
10. Clean up governance maps (`test_impact_map.json`, `router_parity_map.json`).

**Acceptance Criteria**
- `plan_execution_guard` job no longer exists in CI workflow
- No script references to `check_plan_execution_guard.py`, `plan-close-step.ps1`, or `plan-start-check.py` remain in CI/preflight
- Agent prompts and instructions for plans/backlog are deleted
- All remaining tests pass (`python -m pytest backend/tests/unit/ -v`)
- `scripts/ci/test-L3.ps1 -SkipDocker -SkipE2E` passes
- Plan/backlog docs remain as historical archive (not deleted)

**Dependencies**
- Subsumes ARCH-28 scope (ARCH-28 is a subset of this work).

**Plan:** [PLAN_2026-03-12_GUARD-REMOVE-BACKLOG-RULES](../../plans/PLAN_2026-03-12_GUARD-REMOVE-BACKLOG-RULES.md)
