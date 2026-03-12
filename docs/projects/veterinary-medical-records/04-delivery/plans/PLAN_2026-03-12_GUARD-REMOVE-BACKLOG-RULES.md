# Plan: Remove Backlog/ from doc_test_sync_guard

**Backlog item:** [arch-28-remove-backlog-guard-rules.md](../Backlog/arch-28-remove-backlog-guard-rules.md)  
**Branch:** `docs/update-plans`  
**Worktree:** `codex-permanent-1`  
**Execution Mode:** `Semi-supervised`  
**Model Assignment:** `Default`

## Execution Status

- Plan drafted; execution pending.

## TL;DR

The `doc_test_sync_guard` CI check fires on every Backlog file change, demanding updates to guard infrastructure files — but Backlog docs are already in `exclude_doc_globs` and never propagate to router modules. The two explicit Backlog rules in `test_impact_map.json` contradict the exclusion and create false-positive CI failures (e.g., PR #292). Remove them and update the contract tests that assert their existence.

## Context

The guard config is self-contradictory:
- `exclude_doc_globs` (lines 12–15) correctly excludes `Backlog/*.md` and `Backlog/**/*.md`
- But two explicit rules (lines 410–431) re-include them with `required_any` pointing to guard files
- Additionally, both rules reference stale paths (`backend/tests/unit/test_doc_updates_contract.py`, `backend/tests/unit/test_doc_updates_e2e_contract.py`) — those files live in `backend/tests/doc_governance/`

Backlog items will migrate to Linear, making in-repo Backlog docs legacy. Cleaning up now prevents future friction.

## Prerequisites

- Branch `docs/update-plans` checked out
- All existing tests pass before changes (baseline)

## Steps

### Step 1 — Remove Backlog rules from test_impact_map.json

- [ ] S1-1 — In `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json`, delete the two rule objects whose `doc_glob` values are:
  - `"docs/projects/veterinary-medical-records/04-delivery/Backlog/*.md"` (lines 410–420)
  - `"docs/projects/veterinary-medical-records/04-delivery/Backlog/**/*.md"` (lines 421–431)
- **Keep** the `exclude_doc_globs` entries for Backlog (lines 12–15) — they correctly suppress matching.

### Step 2 — Remove Backlog assertions from e2e contract test

- [ ] S2-1 — In `backend/tests/doc_governance/test_doc_updates_e2e_contract.py`, function `test_doc_updates_test_impact_map_covers_router_and_brand_docs()`:
  - Delete the two assertions (around lines 145–146):
    ```python
    assert "docs/projects/veterinary-medical-records/04-delivery/Backlog/*.md" in text
    assert "docs/projects/veterinary-medical-records/04-delivery/Backlog/**/*.md" in text
    ```
- **Keep** lines 159–160 (router_parity_map exclusion assertions) — they verify that `router_parity_map.json` correctly excludes Backlog from parity checks.

### Step 3 — Verify no other tests break

- [ ] S3-1 — Run the doc governance test suite:
  ```powershell
  python -m pytest backend/tests/doc_governance/ -x --tb=short -q
  ```
  All tests must pass. If any fail, investigate — every other Backlog reference in contract tests (e.g., `BACKLOG_DIR` constant, implementation-plan link assertions) is unrelated to the removed rules and should be unaffected.

- [ ] S3-2 — Run the guard script directly to confirm no false positives:
  ```powershell
  python scripts/docs/check_doc_test_sync.py --changed-files "docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-26-architecture-hygiene-pass.md"
  ```
  Expected: exit 0, no sync violations.

### 📌 Checkpoint — Commit & push

- [ ] S4-1 — Stage, commit, push:
  ```powershell
  git add docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json backend/tests/doc_governance/test_doc_updates_e2e_contract.py
  git commit -m "fix(guard): remove contradictory Backlog rules from doc_test_sync_guard"
  git push
  ```
- [ ] S4-2 — Verify PR #292 CI goes green.

## Relevant files

| File | Action | What changes |
|------|--------|-------------|
| `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json` | MODIFY | Delete 2 Backlog rule objects (lines 410–431) |
| `backend/tests/doc_governance/test_doc_updates_e2e_contract.py` | MODIFY | Delete 2 Backlog assertions (lines 145–146) |
| `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json` | NO CHANGE | Backlog exclusions (lines 8–9) remain correct |
| `backend/tests/doc_governance/test_doc_updates_contract.py` | NO CHANGE | `BACKLOG_DIR` constant and link assertions are unrelated |
| `scripts/docs/check_doc_test_sync.py` | NO CHANGE | Script logic is fine; only the data was wrong |

## Files NOT to touch

The following references to "Backlog" are **not** part of this change — they test that `implementation-plan.md` links to Backlog items, not guard rules:
- `test_doc_updates_contract.py` lines 602–617 (US-08, US-09, US-32, US-39 link assertions)
- `test_doc_updates_contract.py` line 640 (US-46 link assertion) 
- `test_doc_updates_contract.py` line 646 (`test_implementation_plan_backlog_split_propagates_to_owner_entry`)
- `test_doc_router_contract.py` line 237 (`BACKLOG_DIR` path construction)
- `test_doc_router_parity_contract.py` lines 150–170 (parity exclusion test — validates correct behavior)

## How to test

1. After Step 2, run `python -m pytest backend/tests/doc_governance/ -x --tb=short -q` — all pass
2. Run `python scripts/docs/check_doc_test_sync.py --changed-files "docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-26-architecture-hygiene-pass.md"` — exit 0
3. Push and confirm PR #292 CI is green
