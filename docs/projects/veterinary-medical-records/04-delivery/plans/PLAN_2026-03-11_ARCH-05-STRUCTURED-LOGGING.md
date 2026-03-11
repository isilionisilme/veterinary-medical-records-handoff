# Plan: ARCH-05 Add Structured Logging to Critical Paths

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** improvement/arch-05-structured-logging
**Worktree:** D:/Git/worktrees/codex-permanent-1
**Execution Mode:** Autonomous
**Model Assignment:** Uniform
**PR:** Pending (PR created on explicit user request)
**Backlog item:** [arch-05-add-structured-logging-critical-paths.md](../Backlog/arch-05-add-structured-logging-critical-paths.md)
**Prerequisite:** None (ARCH-01/ARCH-02 decomposition recommended but not blocking)

---

## Agent Instructions

1. Mark each checkbox in `Execution Status` immediately after completing the step.
2. Do not commit or push without explicit user approval (`Automation Mode` defaults to `Supervisado`).
3. Keep changes strictly within ARCH-05 scope (structured logging in hotspot files).

---

## Context

The architecture review (2026-03-09) found only 22 log statements across 317 functions (7% coverage). Two critical-path files have **zero logging**:

| File | Public functions | Logger | Log statements | Exception handlers (silent) |
|------|-----------------|--------|----------------|-----------------------------|
| `review_service.py` | 3 (`get_document_review`, `mark_document_reviewed`, `reopen_document_review`) | ❌ | 0 | 1 (OSError swallowed) |
| `candidate_mining.py` | 4 (`_mine_interpretation_candidates`, `_map_candidates_to_global_schema`, `_candidate_sort_key`, `_collect_external_candidates`) | ❌ | 0 | 0 |

The codebase already has a consistent logging convention:
```python
import logging
logger = logging.getLogger(__name__)
```
With structured key=value pairs in messages (e.g., `"PDF extraction finished run_id=%s document_id=%s"`) and `logger.exception()` for error handlers with contextual extras.

---

## Objective

1. Add `logging.getLogger(__name__)` to `review_service.py` and `candidate_mining.py`.
2. Add entry-level logging to every public function in both hotspot files.
3. Add error logging with contextual information to all exception handlers.
4. Follow existing codebase patterns exactly.

---

## Scope Boundary

- **In scope:** Adding logger setup and log statements to `review_service.py` and `candidate_mining.py`.
- **Out of scope:** Refactoring files, changing business logic, adding logging to already-covered files, modifying log configuration or formatting infrastructure.

---

## Design Decisions

### DD-1: key=value structured format in log messages
**Rationale:** Matches the established pattern in `orchestrator.py` (line 207). Enables grep/filter on `document_id=`, `run_id=` without JSON parsing overhead.

### DD-2: `logger.exception()` for exception handlers
**Rationale:** Matches `orchestrator.py` (line 84) and `routes_calibration.py` (line 49). Automatically includes traceback.

### DD-3: Entry-level logging at DEBUG for high-frequency functions, INFO for workflow entry points
**Rationale:** `_mine_interpretation_candidates` and `_collect_external_candidates` are called per-document during processing — DEBUG avoids log noise in production. `get_document_review`, `mark_document_reviewed`, `reopen_document_review` are user-triggered workflow actions — INFO is appropriate.

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~50-60 | 400 | ✅ |
| Code files changed | 2 | 15 | ✅ |
| Scope classification | code only | — | ✅ |
| Semantic risk | LOW (additive, no behavior change) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — This change adds log statements to existing files. No user-facing documentation, API docs, or architecture docs require updates.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — user review/decision required

### Phase 0 — Plan-start preflight

- [x] P0-A 🔄 — Resolve branch and worktree metadata. Verify clean working tree on the dedicated branch.

### Phase 1 — Add logging to review_service.py

- [x] P1-A 🔄 — Add `import logging` and `logger = logging.getLogger(__name__)` at module level.
- [x] P1-B 🔄 — Add entry-level `logger.info()` to `get_document_review()` with `document_id` context.
- [x] P1-C 🔄 — Add entry-level `logger.info()` to `mark_document_reviewed()` with `document_id` context.
- [x] P1-D 🔄 — Add entry-level `logger.info()` to `reopen_document_review()` with `document_id` context.
- [x] P1-E 🔄 — Add `logger.warning()` to the silent `except OSError` handler (line ~306) with file path context.
- [x] P1-F 🚧 — 📌 Checkpoint: present diff for `review_service.py` for user review.

### Phase 2 — Add logging to candidate_mining.py

- [x] P2-A 🔄 — Add `import logging` and `logger = logging.getLogger(__name__)` at module level.
- [x] P2-B 🔄 — Add `logger.debug()` entry log to `_mine_interpretation_candidates()` with text-length context.
- [x] P2-C 🔄 — Add `logger.debug()` entry log to `_map_candidates_to_global_schema()`.
- [x] P2-D 🔄 — Add `logger.debug()` entry log to `_collect_external_candidates()` with field-count context.
- [x] P2-E 🚧 — 📌 Checkpoint: present diff for `candidate_mining.py` for user review.

### Phase 3 — Validation

- [x] P3-A 🔄 — Run existing test suite to verify no regressions.
- [x] P3-B 🔄 — Verify acceptance criteria: every public function in hotspots has at least entry-level logging; error handlers include contextual info; log format matches codebase convention.
- [x] P3-C 🚧 — Hard-gate: present final summary and commit proposal to user.

---

## Prompt Queue

### Prompt 1 — Phase 1: review_service.py logging

**Steps:** P1-A through P1-E
**Files:** `backend/app/application/documents/review_service.py`

**Instructions:**

1. Add `import logging` after existing imports and `logger = logging.getLogger(__name__)` at module level, following the pattern in `orchestrator.py` line 31.
2. Add `logger.info("get_document_review called document_id=%s", document_id)` at the start of `get_document_review()` (line 265).
3. Add `logger.info("mark_document_reviewed called document_id=%s", document_id)` at the start of `mark_document_reviewed()` (line 1312).
4. Add `logger.info("reopen_document_review called document_id=%s", document_id)` at the start of `reopen_document_review()` (line 1360).
5. Replace the silent `except OSError` (line ~306) with `logger.warning("Failed to read raw_text file path=%s", raw_text_path)` before `raw_text = None`.
6. Present the diff at P1-F checkpoint.

---

### Prompt 2 — Phase 2: candidate_mining.py logging

**Steps:** P2-A through P2-D
**Files:** `backend/app/application/processing/candidate_mining.py`

**Instructions:**

1. Add `import logging` after existing imports and `logger = logging.getLogger(__name__)` at module level.
2. Add `logger.debug("_mine_interpretation_candidates start chars=%d", len(raw_text))` at the start of `_mine_interpretation_candidates()` (line 27).
3. Add `logger.debug("_map_candidates_to_global_schema start")` at the start of `_map_candidates_to_global_schema()` (line 39).
4. Add `logger.debug("_collect_external_candidates start fields=%d", len(context.fields))` at the start of `_collect_external_candidates()` (line 49). Adjust the context attribute name if needed based on actual parameter inspection.
5. Present the diff at P2-E checkpoint.

---

### Prompt 3 — Phase 3: Validation

**Steps:** P3-A through P3-C
**Files:** All test files under `backend/tests/`

**Instructions:**

1. Run the full backend test suite: `python -m pytest backend/tests/ -x -q`.
2. Verify each acceptance criterion from the backlog item.
3. Present a summary table of logging additions and the commit proposal.

---

## Active Prompt

_(empty — execution has not started)_

---

## Acceptance Criteria

- [x] Every public function in `review_service.py` and `candidate_mining.py` has at least entry-level logging.
- [x] The silent `except OSError` in `review_service.py` now logs a warning with file path context.
- [x] Log format uses `key=value` structured messages consistent with `orchestrator.py`.
- [x] `logging.getLogger(__name__)` pattern used in both files.
- [x] All existing tests pass without modification.

---

## How to Test

1. Run `python -m pytest backend/tests/ -x -q` — all tests must pass.
2. Grep for logger usage: `grep -n "logger\." backend/app/application/documents/review_service.py backend/app/application/processing/candidate_mining.py` — confirm log statements exist.
3. Manually invoke `get_document_review` via API and verify log output includes `document_id=`.
