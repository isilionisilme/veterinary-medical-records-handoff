# IMP-14 — Runbook Contract Completeness

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** TBD

**Parent:** [IMP-13 — Operational Runbook Architecture](imp-13-operational-runbook-architecture.md)

**Origin:** Code review feedback on [PR #274](https://github.com/isilionisilme/veterinary-medical-records/pull/274)

## Problem Statement

After IMP-13 PR3 migrated operational rules into self-contained runbooks, two gaps remain:

1. **Incomplete runbook surface for DOC_UPDATES**: The `doc-updates.prompt.md` runbook covers triggers A, B, C but does not port Use case D (no repo/git access) or Use case E (change rule by RULE_ID) from the legacy router entry (`docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`).
2. **No semantic contract tests for runbooks**: Existing contract tests validate the router modules and file presence but do not assert operational content within `.github/prompts/*.prompt.md` runbooks.

## Acceptance Criteria

- [ ] `doc-updates.prompt.md` includes Use case D (snippet-based fallback when git is unavailable) and Use case E (change rule by RULE_ID lookup).
- [ ] Contract tests in `backend/tests/unit/` validate semantic content of at least `doc-updates.prompt.md`, `code-review.prompt.md`, `start-work.prompt.md`, and `pr-workflow.prompt.md` runbooks (triggers, fallback branches, required output formats).
- [ ] All existing tests pass without regression.
