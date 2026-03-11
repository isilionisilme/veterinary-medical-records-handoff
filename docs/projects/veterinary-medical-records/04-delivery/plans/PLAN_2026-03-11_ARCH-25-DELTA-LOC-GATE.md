# Plan: ARCH-25 Delta-based LOC Complexity Gate

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** PENDING PLAN-START RESOLUTION
**Worktree:** PENDING PLAN-START RESOLUTION
**Execution Mode:** PENDING USER SELECTION
**Model Assignment:** PENDING USER SELECTION
**PR:** Pending (PR created on explicit user request)
**Backlog item:** [arch-25-delta-loc-complexity-gate.md](../Backlog/arch-25-delta-loc-complexity-gate.md)
**Prerequisite:** None

---

## Agent Instructions

1. Mark each checkbox in `Execution Status` immediately after completing the step.
2. Do not commit or push without explicit user approval (`Automation Mode` defaults to `Supervisado`).
3. Keep changes strictly within ARCH-25 scope (LOC gate logic in `architecture_metrics.py` + tests).

---

## Context

The CI complexity gate (`scripts/quality/architecture_metrics.py --check --max-loc 500`) evaluates **absolute LOC** for every changed backend Python file. When a file already exceeds the threshold (e.g., `review_service.py` at 1405 LOC), any touch — even +5 lines of logging — triggers a hard FAIL. This blocks legitimate maintenance work like ARCH-05.

### Current gate logic (LOC section of `check_thresholds`, line 620-625):

```python
for fp, count in loc_data.get("files", {}).items():
    if not _is_backend_app_path(fp):
        continue
    if changed_backend_paths is not None and fp not in changed_backend_paths:
        continue
    if count > max_loc:
        failures.append(f"FAIL: LOC {count} > {max_loc}: {fp}")
```

### Problem: No delta awareness. A file at 1405 LOC fails identically whether you added 2 lines or 200.

### Existing infrastructure available:
- `_changed_backend_python_paths(base_ref)` already computes which files changed.
- `base_ref` is passed through CLI (`--base-ref main`).
- `git show {base_ref}:{path}` can retrieve file content at base to count baseline LOC.

---

## Objective

1. Add a helper `_base_ref_loc(base_ref, path)` to count LOC of a file at the base ref.
2. Modify the LOC section of `check_thresholds` to use delta-aware logic.
3. Add CLI argument `--max-loc-growth` (default: 50) for the growth cap on pre-existing violations.
4. Add unit tests for the three scenarios.

---

## Scope Boundary

- **In scope:** `scripts/quality/architecture_metrics.py` (LOC gate logic only), new test file `scripts/quality/tests/test_architecture_metrics.py`.
- **Out of scope:** CC gate logic, report generation, hotspot scoring, `preflight-ci-local.ps1`, any other CI scripts.

---

## Design Decisions

### DD-1: Delta logic with three outcomes

| Scenario | base LOC | current LOC | delta | Result |
|----------|----------|-------------|-------|--------|
| Pre-existing, small change | > max_loc | > max_loc | <= growth cap | WARNING |
| Threshold crossing | <= max_loc | > max_loc | any | FAIL |
| Pre-existing, large growth | > max_loc | > max_loc | > growth cap | FAIL |

**Rationale:** Catches real regressions while allowing maintenance of legacy files. The growth cap (default 50) prevents gradual uncontrolled inflation.

### DD-2: `git show` for baseline LOC

**Rationale:** Reuses existing `base_ref` parameter. No new dependencies. If `git show` fails (new file), baseline is 0 — the file is treated as introduced in this PR.

### DD-3: Default growth cap of 50 LOC

**Rationale:** 50 lines is generous for maintenance work (logging, error handling) but prevents adding entire features to already-bloated files without triggering the gate.

### DD-4: WARNING output for pre-existing violations

**Rationale:** Maintains CI visibility. Teams can grep for `WARNING: LOC` to track deferred decomposition work. Never silent.

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~60-80 | 400 | ✅ |
| Code files changed | 2 (script + test) | 15 | ✅ |
| Scope classification | CI tooling only | — | ✅ |
| Semantic risk | LOW (gate logic, not business logic) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — Internal CI tooling change. The new `--max-loc-growth` flag follows the existing CLI pattern and the script's docstring will be updated in-code.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — user review/decision required

### Phase 0 — Plan-start preflight

- [ ] P0-A 🔄 — Resolve branch and worktree metadata. Verify clean working tree on the dedicated branch.

### Phase 1 — Implement delta-aware LOC gate

- [ ] P1-A 🔄 — Add `_base_ref_loc(base_ref: str, rel_path: str) -> int` helper that runs `git show {base_ref}:{rel_path}` and counts lines. Returns 0 on failure (new file).
- [ ] P1-B 🔄 — Add `--max-loc-growth` CLI argument (default: 50) to argparse.
- [ ] P1-C 🔄 — Modify `check_thresholds` signature to accept `base_ref: str | None` and `max_loc_growth: int`.
- [ ] P1-D 🔄 — Replace absolute LOC check with delta-aware logic implementing the three-outcome table from DD-1.
- [ ] P1-E 🔄 — Update the script docstring to document the new `--max-loc-growth` flag.
- [ ] P1-F 🚧 — 📌 Checkpoint: present diff of `architecture_metrics.py` for user review.

### Phase 2 — Add unit tests

- [ ] P2-A 🔄 — Create `scripts/quality/tests/test_architecture_metrics.py` with tests for:
  - Scenario 1: pre-existing violation + small delta → WARNING, no FAIL.
  - Scenario 2: file crosses threshold in this PR → FAIL.
  - Scenario 3: pre-existing violation + large delta (> growth cap) → FAIL.
  - Scenario 4: file at/below threshold, stays at/below → no WARNING, no FAIL.
  - Scenario 5: no `base_ref` provided (fallback to absolute check) → existing behavior.
- [ ] P2-B 🚧 — 📌 Checkpoint: present test file for user review.

### Phase 3 — Validation

- [ ] P3-A 🔄 — Run `python -m pytest scripts/quality/tests/ -x -q` — all new tests pass.
- [ ] P3-B 🔄 — Run `python scripts/quality/architecture_metrics.py --check --base-ref main --max-loc 500` on current branch to verify review_service.py produces WARNING instead of FAIL.
- [ ] P3-C 🚧 — Hard-gate: present final summary and commit proposal to user.

---

## Prompt Queue

### Prompt 1 — Phase 1: Delta-aware LOC gate implementation

**Steps:** P1-A through P1-E
**Files:** `scripts/quality/architecture_metrics.py`

**Instructions:**

1. After existing helpers (around line 95), add:
   ```python
   def _base_ref_loc(base_ref: str, rel_path: str) -> int:
       """Count LOC of a file at the given git ref. Returns 0 if not found (new file)."""
       result = _run(["git", "show", f"{base_ref}:{rel_path}"])
       if result.returncode != 0:
           return 0
       return sum(1 for line in result.stdout.splitlines())
   ```

2. In `main()` argparse section (after `--max-loc`), add:
   ```python
   parser.add_argument(
       "--max-loc-growth", type=int, default=50,
       help="Max LOC growth allowed in files already above --max-loc (default: 50)"
   )
   ```

3. Add `base_ref` and `max_loc_growth` parameters to `check_thresholds`:
   ```python
   def check_thresholds(
       data: dict,
       max_cc: int,
       max_loc: int,
       warn_cc: int,
       changed_backend_paths: set[str] | None = None,
       base_ref: str | None = None,
       max_loc_growth: int = 50,
   ) -> tuple[list[str], list[str]]:
   ```

4. Replace the LOC for-loop (lines 620-625) with delta-aware logic:
   ```python
   for fp, count in loc_data.get("files", {}).items():
       if not _is_backend_app_path(fp):
           continue
       if changed_backend_paths is not None and fp not in changed_backend_paths:
           continue
       if count > max_loc:
           base_loc = _base_ref_loc(base_ref, fp) if base_ref else 0
           delta = count - base_loc
           if base_loc > max_loc:
               # Pre-existing violation
               if delta > max_loc_growth:
                   failures.append(
                       f"FAIL: LOC {count} (delta +{delta}) > growth cap {max_loc_growth}: {fp}"
                   )
               else:
                   warnings.append(
                       f"WARNING: LOC {count} > {max_loc} (pre-existing, delta +{delta}): {fp}"
                   )
           else:
               # This PR crossed the threshold
               failures.append(f"FAIL: LOC {count} > {max_loc}: {fp}")
   ```

5. In `main()`, update the `check_thresholds` call to pass the new parameters:
   ```python
   warnings, failures = check_thresholds(
       data, args.max_cc, args.max_loc, args.warn_cc, changed_backend_paths,
       base_ref=args.base_ref, max_loc_growth=args.max_loc_growth,
   )
   ```

6. Update the module docstring to include `--max-loc-growth`:
   ```
   python scripts/quality/architecture_metrics.py --check --base-ref main --warn-cc 11 --max-cc 30 --max-loc 500 --max-loc-growth 50
   ```

---

### Prompt 2 — Phase 2: Unit tests

**Steps:** P2-A, P2-B
**Files:** `scripts/quality/tests/test_architecture_metrics.py`

**Instructions:**

1. Create test file importing `check_thresholds` and `_base_ref_loc` from `scripts.quality.architecture_metrics` (or using sys.path manipulation).
2. Mock `_base_ref_loc` via `unittest.mock.patch` to avoid git dependency.
3. Build synthetic `data` dicts with controlled `loc.files` and `radon_cc.functions` values.
4. Test the five scenarios:
   - **test_preexisting_small_delta**: file at 600 LOC base, 605 current, max_loc=500, growth_cap=50 → 0 failures, 1 warning.
   - **test_threshold_crossing**: file at 490 LOC base, 510 current, max_loc=500 → 1 failure, 0 warnings.
   - **test_preexisting_large_growth**: file at 600 LOC base, 680 current, max_loc=500, growth_cap=50 → 1 failure.
   - **test_below_threshold**: file at 200 LOC, max_loc=500 → 0 failures, 0 warnings.
   - **test_no_base_ref_absolute_fallback**: no base_ref, file at 600 LOC, max_loc=500 → 1 failure (existing behavior).

---

### Prompt 3 — Phase 3: Validation

**Steps:** P3-A through P3-C
**Files:** `scripts/quality/tests/test_architecture_metrics.py`, `scripts/quality/architecture_metrics.py`

**Instructions:**

1. Run `python -m pytest scripts/quality/tests/ -x -q`.
2. Run `python scripts/quality/architecture_metrics.py --check --base-ref main --max-loc 500 --max-loc-growth 50` and verify `review_service.py` produces WARNING, not FAIL.
3. Present summary table of changes and commit proposal.

---

## Active Prompt

_(empty — execution has not started)_

---

## Acceptance Criteria

- [ ] Files already above `--max-loc` at base-ref do not FAIL for small additive changes (delta <= growth cap).
- [ ] Files that cross the threshold in the current PR still FAIL.
- [ ] Large growth (delta > growth cap) in already-over files still FAIL.
- [ ] Pre-existing violations emit WARNING (never silenced).
- [ ] Existing CC gate logic unchanged.
- [ ] Unit tests cover all five scenarios and pass.
- [ ] `--max-loc-growth` flag documented in script docstring.

---

## How to Test

1. Run `python -m pytest scripts/quality/tests/ -x -q` — all tests pass.
2. Run `python scripts/quality/architecture_metrics.py --check --base-ref main --max-loc 500 --max-loc-growth 50` — `review_service.py` shows WARNING instead of FAIL.
3. Verify: `python scripts/quality/architecture_metrics.py --check --max-loc 500` (no base-ref) — existing absolute behavior preserved, `review_service.py` FAIL as before.
