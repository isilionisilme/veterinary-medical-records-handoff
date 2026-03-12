# ARCH-28 — Remove Backlog Rules from doc_test_sync_guard

**Status:** Planned

**Type:** Architecture Improvement (CI hygiene)

**Target release:** N/A — standalone cleanup

**Origin:** PR #292 CI failure — `doc_test_sync_guard` false positive on new Backlog docs (arch-26, arch-27)

**Severity:** LOW  
**Effort:** XS (<30min)

**Problem Statement**
The `test_impact_map.json` guard config is self-contradictory:
- `exclude_doc_globs` (lines 12–15) correctly excludes `Backlog/*.md` and `Backlog/**/*.md`.
- Two explicit rules (lines 410–431) re-include them with `required_any` pointing to guard infrastructure files.
- Both rules reference stale paths (`backend/tests/unit/test_doc_updates_contract.py`) — the real file is at `backend/tests/doc_governance/`.

This causes every Backlog doc change to fail CI, demanding unrelated guard file updates. Backlog items are planned to migrate to Linear, making in-repo Backlog docs legacy.

**Action**
1. Delete the 2 Backlog rule objects from `test_impact_map.json`.
2. Delete the 2 corresponding assertions from `test_doc_updates_e2e_contract.py`.
3. Keep `exclude_doc_globs` entries and `router_parity_map.json` exclusions as-is.

**Acceptance Criteria**
- No rules in `test_impact_map.json` match `Backlog/*.md` or `Backlog/**/*.md`
- `exclude_doc_globs` still lists Backlog globs
- `router_parity_map.json` Backlog exclusions unchanged
- All doc governance tests pass
- Guard script exits 0 when given a Backlog file as changed input
- PR #292 CI green

**Dependencies**
- None.

**Plan**
[PLAN_2026-03-12_GUARD-REMOVE-BACKLOG-RULES.md](../plans/PLAN_2026-03-12_GUARD-REMOVE-BACKLOG-RULES.md)
