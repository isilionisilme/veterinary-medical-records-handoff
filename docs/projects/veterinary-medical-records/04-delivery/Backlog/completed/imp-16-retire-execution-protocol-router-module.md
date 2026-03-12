# IMP-16 — Retire Execution Protocol Router Module

**Status:** Implemented

**Type:** Technical Improvement (documentation cleanup)

**Target release:** N/A — standalone cleanup

**Parent:** [IMP-15 — Remove Plan/Backlog Governance Layer](imp-15-remove-plan-backlog-governance-layer.md)

**Origin:** Code review feedback on [PR #297](https://github.com/isilionisilme/veterinary-medical-records/pull/297) — S1 finding: `plan-execution-protocol.md` remains as canonical source in the router without guardrails after IMP-15 removed the governance layer.

## Problem Statement

After IMP-15 removed the plan/backlog governance layer (CI scripts, agent prompts, instructions, ceremony tests), the `EXECUTION_PROTOCOL` router module still declares `plan-execution-protocol.md` as its canonical source. This creates orphaned routing infrastructure:

- 12 auto-generated files in `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/` citing `plan-execution-protocol.md`
- 13 entries in `MANIFEST.yaml` linking source → router fragments
- 1 `required_terms` validation rule in `router_parity_map.json`
- 7 cross-references to `plan-creation.md` from EXECUTION_PROTOCOL modules
- 1 reference in `40_commit-discipline.md` to execution protocol §7

With plans migrating to Linear, this infrastructure has no active consumers and increases maintenance surface without value.

## Scope

### Delete

- `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/` — entire directory (12 files: `00_entry.md`, `10_purpose.md`, `20_execution-mode.md`, `30_iterations-state.md`, `40_step-eligibility.md`, `50_rollback-governance.md`, `60_step-completion.md`, `70_format-preflight.md`, `80_next-step-prompt.md`, `90_hard-gates-scope.md`, `100_iteration-lifecycle.md`, `110_conventions.md`)

### Modify

- `docs/agent_router/MANIFEST.yaml` — remove the `03_SHARED/EXECUTION_PROTOCOL` section (lines ~175–224)
- `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json` — remove the `execution-rules.md` → `EXECUTION_PROTOCOL/00_entry.md` parity rule (or update `required_terms` to drop `plan-execution-protocol.md`)
- `docs/agent_router/03_SHARED/WAY_OF_WORKING/40_commit-discipline.md` — replace reference to `plan-execution-protocol.md §7` with inline rule or remove
- Regenerate router files: `python scripts/docs/generate-router-files.py`

### Do NOT delete

- `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` — remains as historical archive
- `docs/projects/veterinary-medical-records/03-ops/plan-creation.md` — remains as historical archive

## Acceptance Criteria

- [ ] No files remain in `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/`
- [ ] `MANIFEST.yaml` has no entries referencing `plan-execution-protocol.md`
- [ ] `router_parity_map.json` has no `required_terms` referencing `plan-execution-protocol.md`
- [ ] `40_commit-discipline.md` has no dangling reference to retired source
- [ ] `python scripts/docs/generate-router-files.py --check` passes
- [ ] All doc governance tests pass: `python -m pytest backend/tests/doc_governance/ -v`
- [ ] `scripts/ci/test-L3.ps1 -SkipDocker -SkipE2E` passes
- [ ] Source docs remain intact as historical archive

## Dependencies

- Requires IMP-15 merged first (PR #297)
