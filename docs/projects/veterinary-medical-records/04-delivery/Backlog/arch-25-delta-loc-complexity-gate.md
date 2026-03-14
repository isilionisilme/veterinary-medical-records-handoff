# ARCH-25 — Delta-based LOC Complexity Gate

**Status:** Planned

**Type:** CI / Architecture Improvement (tooling)

**Target release:** Release 20 — Architecture hardening

**Origin:** ARCH-05 execution blocker — `review_service.py` (1405 LOC) fails absolute LOC gate on any touch

**Severity:** HIGH (blocks unrelated work on pre-existing large files)
**Effort:** S (2-4h)

**Plan:** [PLAN_2026-03-11_ARCH-25-DELTA-LOC-GATE](../plans/PLAN_2026-03-11_ARCH-25-DELTA-LOC-GATE.md)

**Problem Statement**
The CI complexity gate in `scripts/quality/architecture_metrics.py` uses absolute LOC thresholds (`--max-loc 500`). When a PR touches a file that already exceeds the threshold (e.g., `review_service.py` at 1405 LOC), the gate fails even if the change is minimal and additive (e.g., +5 lines of logging). This creates false-positive CI blocks on legitimate maintenance work.

**Action**
1. Compute LOC of changed files at `base-ref` to obtain a baseline.
2. Change the LOC gate logic from "absolute total" to "delta-aware":
   - If the file was already above the threshold at base-ref, only FAIL if delta exceeds a configurable growth cap (default: 50 LOC).
   - If the file was at or below the threshold at base-ref and now exceeds it, FAIL (the PR introduced the violation).
3. Emit structured WARNING for pre-existing violations to maintain visibility.
4. Add unit tests for the new threshold logic.

**Acceptance Criteria**
- Files already above `--max-loc` at base-ref do not FAIL for small additive changes (delta <= growth cap).
- Files that cross the threshold in the current PR still FAIL.
- Large growth (delta > growth cap) in already-over files still FAIL.
- Pre-existing violations emit WARNING (never silenced).
- Existing CC gate logic is unchanged.
- Unit tests cover all three scenarios (pre-existing small delta, threshold crossing, large growth).

**Dependencies**
- None. This unblocks ARCH-05.
