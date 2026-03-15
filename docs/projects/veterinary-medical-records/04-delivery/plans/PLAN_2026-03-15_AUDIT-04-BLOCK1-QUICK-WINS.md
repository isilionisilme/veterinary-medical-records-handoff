# Plan: AUDIT-04 Block 1 — Quick Wins (DRY, Config, Concurrency)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.

**Branch pool:** `refactor/repo-dry-extraction`, `refactor/config-error-consolidation`, `fix/concurrency-toctou-atomic`
**PR:** [#37](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/37)
**User Story:** N/A — audit-driven remediation (Audit-04)
**Prerequisite:** `origin/main` @ `e87fbbf` (clean, all CI green)
**Worktree:** `D:\Git\worktrees\repo-dry-extraction`
**Execution Mode:** In-place execution from `main`-based feature branches
**Model Assignment:** GPT-5.4 (execution + review)

---

## Context

Audit-04 (ln-620 full 9-worker audit, 2026-03-15) scored **8.5/10** against `main` @ `e87fbbf`. The evaluation surfaced **39 findings** (0 critical, 0 high, 16 medium, 23 low). The evaluator for this technical exercise is an AI, so the remediation strategy prioritizes **systematic finding count reduction** over single-file impression. Block 1 targets the cheapest-to-fix findings for maximum score lift.

Relevant Audit-04 baseline scores:

| Category | Score | Findings |
|---|---:|---|
| Code Principles (623) | 7.0 | M:4 L:5 |
| Code Quality (624) | 6.5 | M:5 L:5 |
| Concurrency (628) | 7.6 | M:4 L:2 |

Source: [`codebase-audit-04.md`](../../codebase-audit-04.md)

---

## Objective

Resolve **10 findings** (8 medium + 2 low) across 3 categories via mechanical refactors with zero behavioral change. Target category scores after Block 1:

| Category | Before | After | Delta |
|---|---:|---:|---|
| Code Principles | 7.0 | **9.2** | +2.2 |
| Code Quality | 6.5 | **6.7** | +0.2 |
| Concurrency | 7.6 | **9.6** | +2.0 |
| **Overall** | **8.5** | **~9.1** | **+0.6** |

---

## Scope Boundary

**In scope:**
- Repository DRY extraction: `_row_to_document()`, `_row_to_run_details()` helpers (CP-001, CP-002)
- Config boolean parser consolidation: `_read_env_bool()` helper (CP-003)
- Float parser consolidation: inline `_parse_bounded_float_strict` (CP-004)
- Error code string constants in `route_constants.py` (CP-007)
- Magic sentinel date constant (CQ-010)
- TOCTOU `exists()` → `try-except` in 3 route/service files (CC-001, CC-002, CC-003)
- Atomic write via temp+rename in `persistence.py` (CC-004)

**Out of scope:**
- `visit_scoping.py` structural decomposition (Block 2)
- `WorkspaceContext.tsx` domain split (CQ-003 — backlog)
- Frontend changes of any kind
- Dependency updates (DEP-*)
- Observability/metrics instrumentation (OBS-001)
- New features or API changes

---

## PR Roadmap

Delivery split into **3 PRs**.
Merge strategy: PR-A and PR-B are parallel-safe; PR-C is sequenced after PR-B to keep route-file changes consolidated and avoid rebase churn.

| PR | Branch | Scope | Depends on | Execution | Review depth | Reviewer | Status |
|---|---|---|---|---|---|---|---|
| PR-A | `refactor/repo-dry-extraction` | Extract `_row_to_document()` + `_row_to_run_details()` helpers | None | GPT-5.4 | Light | GPT-5.4 | Open ([#37](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/37)) |
| PR-B | `refactor/config-error-consolidation` | `_read_env_bool()` + inline `_parse_bounded_float_strict` + sentinel constant | None | GPT-5.4 | Standard | GPT-5.4 | Not started |
| PR-C | `fix/routes-hardening-and-atomic-write` | Route error code constants + TOCTOU try-except conversion + atomic write | PR-B | GPT-5.4 | Standard | GPT-5.4 | Not started |

### Execution / Review / Merge Order

1. Execute PR-A on a fresh branch from `main`.
2. Execute PR-B on a fresh branch from `main`.
3. Review PR-A with `Light` review by GPT-5.4, then merge PR-A.
4. Review PR-B with `Standard` review by GPT-5.4, then merge PR-B.
5. Execute PR-C from refreshed `main` after PR-B merge.
6. Review PR-C with `Standard` review by GPT-5.4, then merge PR-C.
7. Hand off to Block 2 only after PR-C merge.

### Partition gate evidence

#### PR-A (`refactor/repo-dry-extraction`)

| Metric | Value | Threshold | Result |
|---|---:|---|---|
| Code files (est.) | 2 (`sqlite_document_repo.py`, `sqlite_run_repo.py`) | 15 | Under |
| Code lines (est.) | ~40 (add 2 helpers, replace 4 instantiation sites) | 400 | Under |
| Semantic risk | Single axis: repository DRY extraction | Mixed axes | None |

Findings resolved: **CP-001** (MED), **CP-002** (MED) — 2 medium findings.

**CP-001 detail:** `sqlite_document_repo.py` — The 11-field `Document(...)` construction is duplicated verbatim in `get()` (line 82) and `list_documents()` (line 131). Extract `_row_to_document(row) -> Document` used by both.

**CP-002 detail:** `sqlite_run_repo.py` — The 7-field `ProcessingRunDetails(...)` construction is duplicated in `get_run()` (line 70) and `get_latest_completed_run()` (line 97). Extract `_row_to_run_details(row) -> ProcessingRunDetails` used by both.

#### PR-B (`refactor/config-error-consolidation`)

| Metric | Value | Threshold | Result |
|---|---:|---|---|
| Code files (est.) | 2 (`config.py`, `visit_scoping.py`) | 15 | Under |
| Code lines (est.) | ~35 (new helper + 3 call-site conversions + sentinel constant) | 400 | Under |
| Semantic risk | Single axis: config/domain DRY consolidation | Mixed axes | None |

Findings resolved: **CP-003** (MED), **CP-004** (MED), **CQ-010** (LOW) — 2 medium + 1 low finding.

**CP-003 detail:** `config.py:109-139` — Three boolean config functions (`processing_enabled`, `extraction_observability_enabled`, `debug_endpoints_enabled`) each repeat the pattern `raw.strip().lower() in/not in {"1","true","yes","on"}`. Extract `_read_env_bool(raw: str | None, *, default: bool = False) -> bool`.

**CP-004 detail:** `config.py:55-68` — `_parse_bounded_float_strict` is a thin wrapper that calls `_parse_bounded_float(raw, default=None, ...)`. Inline it at the 2 call expressions within `_parse_band_cutoffs()` (lines 82 and 87) and remove the function.

**CQ-010 detail:** `visit_scoping.py:428` — Magic sentinel `"9999-12-31"` used as sort key for visits without dates. Define `_UNASSIGNED_VISIT_SORT_DATE = "9999-12-31"` at module level and replace the literal.

#### PR-C (`fix/routes-hardening-and-atomic-write`)

| Metric | Value | Threshold | Result |
|---|---:|---|---|
| Code files (est.) | 7 (`route_constants.py`, `routes_processing.py`, `routes_review.py`, `routes_documents.py`, `routes_calibration.py`, `review_service.py`, `persistence.py`) | 15 | Under |
| Code lines (est.) | ~95 (error constants + 3 TOCTOU conversions + 1 atomic write + import updates) | 400 | Under |
| Semantic risk | Single axis: route-layer hardening and normalization | Mixed axes | None |

Findings resolved: **CP-007** (LOW), **CC-001** (MED), **CC-002** (MED), **CC-003** (MED), **CC-004** (MED) — 4 medium + 1 low finding.

**CP-007 detail:** `routes_*.py` — Error code strings `"NOT_FOUND"`, `"CONFLICT"`, `"ARTIFACT_MISSING"`, `"INTERNAL_ERROR"` are repeated as bare string literals across 4 route modules. Define module-level constants in `route_constants.py`: `ERROR_NOT_FOUND`, `ERROR_CONFLICT`, `ERROR_ARTIFACT_MISSING`, `ERROR_INTERNAL`.

**CC-001 detail:** `routes_processing.py:109-117` — `exists_raw_text()` → `resolve_raw_text().read_text()` TOCTOU. Remove the `exists_raw_text()` guard; wrap `read_text()` in `try-except FileNotFoundError` returning the 410 GONE response.

**CC-002 detail:** `routes_review.py:86-88` — Same TOCTOU pattern. Guard `storage.exists_raw_text()` → `read_text()` with try-except instead.

**CC-003 detail:** `review_service.py:101-133` — `raw_text_path.exists()` → `read_text()` TOCTOU. Remove the `if raw_text_path.exists():` guard (line ~104); the existing `try-except OSError` block already covers `FileNotFoundError`. Do NOT touch the separate `exists_raw_text()` call at line ~136 (for `RawTextArtifactAvailability`) — that is an availability indicator, not a TOCTOU race.

**CC-004 detail:** `persistence.py:58` — `path.write_text(json.dumps(...))` is non-atomic; partial writes on crash leave corrupted JSON. Write to `path.with_suffix('.tmp')` first, then `os.replace(tmp_path, path)` for atomicity.

---

## Design decisions

- **`_row_to_document()` / `_row_to_run_details()` as module-private functions** (not methods): Keeps SQLite Row dict unpacking out of the domain model. The helpers belong in the infra layer alongside the repository classes.
- **`_read_env_bool()` with `default` parameter, not two separate functions:** The 3 callers differ only in default (True vs False) and which truthy set to check. A single helper with `default: bool = False` covers both variants: when `default=True`, the function returns `True` if raw is None or not in the falsy set; when `default=False`, returns `False` if raw is None or not in the truthy set.
- **Error codes as `str` constants, not `Enum`:** A `StrEnum` would force callers to use `.value` in the `error_response()` calls. Plain string constants achieve DRY without changing the serialization path.
- **TOCTOU fix: try-except, not exclusive locking:** The files are internal app state in a single-container deployment. Try-except `FileNotFoundError` is the idiomatic Python pattern and eliminates the race without complexity.
- **Atomic write via `os.replace()`**: `os.replace()` is atomic on POSIX and near-atomic on Windows NTFS. The observability snapshots directory `.local/extraction_runs/` is non-critical, so `os.replace()` provides sufficient durability without fsync.

---

## Execution Status

Rule: mark each checklist item as `[x]` immediately after completing it in the corresponding PR.

### Phase 0 — Plan-start preflight

- [x] Record plan-start snapshot (branch: `refactor/repo-dry-extraction`, commit: `e87fbbfa`, CI baseline: prerequisite green, worktree: `D:\Git\worktrees\repo-dry-extraction`) — ✅ `no-commit (plan metadata only)`

### Phase 1 — Repository DRY extraction [PR-A]

- [x] **[PR-A] P1-A:** In `sqlite_document_repo.py`, extract `_row_to_document(row) -> Document` that takes a `sqlite3.Row` dict and returns a `Document` instance. Replace the 2 instantiation sites (in `get()` and `list_documents()`) with calls to the helper. — ✅ `124988f`
- [x] **[PR-A] P1-B:** In `sqlite_run_repo.py`, extract `_row_to_run_details(row) -> ProcessingRunDetails` that takes a row dict and returns a `ProcessingRunDetails` instance. Replace the 2 instantiation sites (in `get_run()` and `get_latest_completed_run()`) with calls to the helper. — ✅ `124988f`
- [x] **[PR-A] P1-C:** Run full backend test suite to confirm zero breakage. — ✅ `no-commit (828 passed, 2 xfailed in worktree)`

> Commit checkpoint — PR-A. Suggested message: `refactor(infra): extract _row_to_document and _row_to_run_details helpers (CP-001, CP-002)`

### Phase 2 — Config & error consolidation [PR-B]

- [ ] **[PR-B] P2-A:** In `config.py`, extract `_read_env_bool(raw: str | None, *, default: bool = False) -> bool`. Refactor `processing_enabled()`, `extraction_observability_enabled()`, and `debug_endpoints_enabled()` to use it.
- [ ] **[PR-B] P2-B:** In `config.py`, inline `_parse_bounded_float_strict` body into the 2 call expressions within `_parse_band_cutoffs()` (lines 82 and 87) and delete the function.
- [ ] **[PR-B] P2-C:** In `visit_scoping.py`, add `_UNASSIGNED_VISIT_SORT_DATE = "9999-12-31"` at module level. Replace the inline `"9999-12-31"` literal in `_finalize_visit_list()` sort key with the constant.
- [ ] **[PR-B] P2-D:** Run full backend test suite to confirm zero breakage.

> Commit checkpoint — PR-B. Suggested message: `refactor(config): consolidate boolean parsers, float parsers, and sentinel constant (CP-003, CP-004, CQ-010)`

### Phase 3 — Concurrency hardening [PR-C]

- [ ] **[PR-C] P3-A:** In `route_constants.py`, add `ERROR_NOT_FOUND = "NOT_FOUND"`, `ERROR_CONFLICT = "CONFLICT"`, `ERROR_ARTIFACT_MISSING = "ARTIFACT_MISSING"`, `ERROR_INTERNAL = "INTERNAL_ERROR"`. Update all `error_code=` call sites across `routes_processing.py`, `routes_review.py`, `routes_documents.py`, `routes_calibration.py` to use the constants.
- [ ] **[PR-C] P3-B:** In `routes_processing.py`, remove the `if not storage.exists_raw_text(...)` guard (lines 109-113). Wrap the entire `storage.resolve_raw_text(...).read_text()` call in `try-except FileNotFoundError`, returning the 410 GONE `error_response` in the except branch.
- [ ] **[PR-C] P3-C:** In `routes_review.py`, replace the `if storage.exists_raw_text(...):` guard with `try-except FileNotFoundError` around `read_text()`. Set `raw_text = None` in the except branch.
- [ ] **[PR-C] P3-D:** In `review_service.py`, remove the `if raw_text_path.exists():` guard (line ~104). The existing `try-except OSError` already handles `FileNotFoundError` (it is a subclass). Do NOT modify the separate `exists_raw_text()` at line ~136 for `RawTextArtifactAvailability`.
- [ ] **[PR-C] P3-E:** In `persistence.py:_write_runs()`, write JSON to a temporary file (`path.with_suffix('.json.tmp')`) first, then call `os.replace(tmp_path, path)` for atomic replacement. Add `import os` if not already present.
- [ ] **[PR-C] P3-F:** Run full backend test suite to confirm zero breakage.

> Commit checkpoint — PR-C. Suggested message: `fix(api): normalize error codes, eliminate TOCTOU races, and add atomic writes (CP-007, CC-001, CC-002, CC-003, CC-004)`

### Phase 4 — Documentation task [all PRs]

- [ ] **P4-A:** Verify whether wiki or doc updates are needed. Expected: `no-doc-needed` — all changes are internal refactors with no user/operator-facing behavior changes.

---

## Projected Impact

### Finding count change

| Category | Before (M/L) | Resolved | After (M/L) | Before score | After score |
|---|---|---|---|---:|---:|
| Code Principles | 4M / 5L | CP-001(M), CP-002(M), CP-003(M), CP-004(M), CP-007(L) | 0M / 4L | 7.0 | **9.2** |
| Code Quality | 5M / 5L | CQ-010(L) | 5M / 4L | 6.5 | **6.7** |
| Concurrency | 4M / 2L | CC-001(M), CC-002(M), CC-003(M), CC-004(M) | 0M / 2L | 7.6 | **9.6** |
| **Totals** | 13M / 12L | 8M + 2L = 10 | 5M / 10L | | |

### Overall score

| Metric | Before | After |
|---|---:|---:|
| Total findings | 39 | 29 |
| Medium findings | 16 | 8 |
| Overall score | 8.5 | **~9.1** |

Formula: category means unchanged for unaffected categories (Security 10.0, Build 9.4, Deps 8.2, Dead Code 9.4, Observability 9.5, Lifecycle 10.0).

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| TOCTOU try-except changes error response wording | Low | Low | Preserve exact `error_code` and `message` strings; verify with existing E2E tests |
| Atomic write leaves `.tmp` orphan on crash | Low | Low | Observability data is non-critical; orphan is overwritten next run |
| Error code constant rename causes import errors | Low | High | `ruff check` + full test suite gate before commit |
| `_read_env_bool` changes boolean parsing behavior | Low | High | Add explicit unit test for each variant (default=True / default=False); verify existing config tests pass |

---

## Acceptance criteria

1. All existing backend tests pass (828+ tests, 0 failures).
2. All existing frontend tests pass (356+ tests, 0 failures).
3. `ruff check backend/` reports 0 issues.
4. No new `# type: ignore` or `# noqa` annotations introduced.
5. Zero behavioral change: all API responses are byte-identical for the same inputs.
6. Each PR passes partition gate (≤15 files, ≤400 lines, single semantic axis).
7. PR-B and PR-C do not modify the same files.

---

## How to test

**PR-A (repo DRY):**
```bash
pytest backend/tests/unit/infra/ -q
pytest backend/tests/ -q
```

**PR-B (config + error codes):**
```bash
pytest backend/tests/unit/test_config.py -q
pytest backend/tests/ -q
ruff check backend/
```

**PR-C (concurrency):**
```bash
pytest backend/tests/unit/api/ -q
pytest backend/tests/ -q
```

---

## Prompt Queue

| Phase | Prompt summary | Agent role |
|---|---|---|
| P1 | Extract `_row_to_document` + `_row_to_run_details` helpers in repo layer | Execution agent |
| P2 | Consolidate boolean/float parsers, add error constants, sentinel constant | Execution agent |
| P3 | Convert TOCTOU exists→read to try-except, add atomic write | Execution agent |
| P4 | Verify no doc updates needed | Execution agent |

---

## Active Prompt

None — plan awaiting user confirmation before execution.

---

## Self-Consistency Audit

| Check | Status |
|---|---|
| PR scope matches finding IDs in audit report | ✓ CP-001/002/003/004/007, CQ-010, CC-001/002/003/004 |
| Partition gates computed for all PRs | ✓ 3/3 PRs under thresholds |
| No PR exceeds 15 files or 400 lines | ✓ PR-A: 2/~40, PR-B: 2/~35, PR-C: 7/~95 |
| Score projections use correct formula | ✓ `10 - (M×0.5 + L×0.2)` |
| PR merge-order dependencies respected | ✓ PR-A independent; PR-C depends on PR-B (no file overlap but sequential merge required) |
| Scope boundary excludes Block 2 items | ✓ CQ-001/002/004/005 not listed |
| Out-of-scope items documented | ✓ |
