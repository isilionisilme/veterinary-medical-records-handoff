# Plan: ARCH-01 PR-2 — Extract VisitAssignmentEngine

> **ARCH origin:** `ARCH-01` — [arch-01-decompose-review-service.md](../../Backlog/arch-01-decompose-review-service.md)
> **Related plans (series):**
> - [PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md](PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md)
> - **Current:** `PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md`
> - [PLAN_2026-03-09_ARCH-01-PR3-PARSER-CLASSIFIER.md](PLAN_2026-03-09_ARCH-01-PR3-PARSER-CLASSIFIER.md)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for execution protocol, hard-gates, and handoff behavior.

**Backlog item:** [arch-01-decompose-review-service.md](../../Backlog/arch-01-decompose-review-service.md)
**Branch:** `refactor/arch-01-pr2-visit-engine`
**PR:** Pending (PR created on explicit user request)
**User Story:** N/A (Architecture improvement ARCH-01, PR 2 of 3)
**Prerequisite:** PR-1 merged ([PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE](PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md))
**Worktree:** `C:/Users/ferna/.codex/worktrees/c691/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Automation Mode:** `Supervisado`

---

## Agent Instructions

1. Follow Extended Execution State lifecycle (§3): mark `⏳ IN PROGRESS` before starting a step; mark `🔒 STEP LOCKED` after code commit but before CI green; mark `[x]` only after CI green and plan-update commit.
2. At each commit recommendation point, run the validation level indicated in the commit recommendations table; if it fails, repair and re-run (max 2 attempts), then escalate.
3. Do not commit or push without explicit user approval (`Supervisado` mode).
4. Every step completion message MUST include the EVIDENCE BLOCK (§8): Step, Code commit, CI run, Plan commit.
5. Before auto-chain or handoff, verify the AUTO-HANDOFF GUARD (§8): CI green + plan committed.
6. **Model routing (hard rule).** Each step has a `[Model]` tag. On step completion, check the `[Model]` tag of the next pending step. If it differs from the current model, **STOP immediately** and tell the user: *"Next step recommends [Model X]. Switch to that model and say 'continue'."* Do NOT auto-chain across model boundaries.

---

## Context

After PR-1 extracted `ReviewPayloadProjector` and `AgeNormalizer`, `review_service.py` still contains the visit-scoping logic concentrated in `_normalize_canonical_review_scoping` (~400 LOC, high CC). This PR-2 extracts the visit assignment and population helpers into a dedicated `VisitAssignmentEngine`.

### Extraction targets for this PR

**VisitAssignmentEngine** — visit anchor resolution + segment boundaries:
- `_resolve_snippet_anchor_offset` (line ~708)
- `_resolve_visit_from_anchor` (line ~734)
- `_find_nearest_target` (line ~750)
- `_find_line_start_offset` (line ~810)
- `_resolve_visit_segment_bounds` (line ~816)

**VisitAssignmentEngine** — visit-scoped field population:
- `_populate_visit_scoped_fields_from_segment_candidates` (line ~1194)
- `_build_visit_segment_text_by_visit_id` (line ~1125)
- `_populate_missing_reason_for_visit_from_segments` (line ~1169)
- `_populate_visit_observations_actions_from_segments` (line ~1080)
- `_append_visit_segment_summary_field` (line ~1058)

### Public API functions (must remain unchanged across all 3 PRs)

- `get_document_review` (line ~269)
- `mark_document_reviewed` (line ~1675)
- `reopen_document_review` (line ~1723)

### Key orchestrator (remains in review_service.py, gets hollowed out)

- `_normalize_canonical_review_scoping` (line ~1267) — will delegate visit assignment/population to the new engine but retain orchestration ownership.

---

## Objective

1. Extract visit assignment and population logic into `VisitAssignmentEngine`.
2. Hollow out `_normalize_canonical_review_scoping` by delegating visit-related blocks to the new engine.
3. Keep behavior, public API, and evidence/metadata semantics unchanged.
4. Meet maintainability thresholds: no extracted file above 400 LOC, no function above CC 20 in touched paths.

---

## Scope Boundary

- **In scope:** extraction of visit anchor, segment boundary, and visit-scoped population helpers into `visit_assignment_engine.py`; rewiring `_normalize_canonical_review_scoping` to delegate; regression validation.
- **Out of scope:** segment parser/classifier extraction (PR-3), dead code cleanup in review_service.py (PR-3), API contract changes, frontend changes.

---

## PR Roadmap

This plan is **PR-2 of 3** (Option C — maximum caution):

| PR | Plan | Scope | Risk |
|---|---|---|---|
| PR-1 (done) | ARCH-01-PR1-PROJECTOR-AGE | `ReviewPayloadProjector` + `AgeNormalizer` | Low |
| **PR-2 (this)** | ARCH-01-PR2-VISIT-ENGINE | `VisitAssignmentEngine` | Medium |
| PR-3 | ARCH-01-PR3-PARSER-CLASSIFIER | `SegmentParser` + `ClauseClassifier` + final cleanup | Medium-high |

---

## Commit Recommendations (inline, non-blocking)

| After steps | Scope | Suggested message | Expected validation |
|---|---|---|---|
| S1-A..S1-B | Safety net + skeleton | `refactor(plan-arch-01): add visit engine skeleton and safety-net tests` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| S2-A..S2-D | Visit engine extraction | `refactor(plan-arch-01): extract visit assignment engine` | `scripts/ci/test-L2.ps1 -BaseRef main` |
| S3-A..S3-B | Evidence and docs | `docs(plan-arch-01): PR-2 visit engine evidence` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |

---

## Execution Status

**Legend**
- 🔄 auto-chain
- 🚧 hard-gate

### Phase 1 — Preconditions and scaffolding

- [ ] S1-A 🔄 `[GPT-4.1]` — Verify PR-1 is merged and branch is based on latest `main`. Confirm `review_payload_projector.py` and `age_normalizer.py` exist and are wired.
- [ ] S1-B 🔄 `[Codex]` — Add/refine focused regression tests around visit scoping, evidence offsets, and segment population behavior.
- [ ] S1-C 🔄 `[Codex]` — Create module skeleton: `visit_assignment_engine.py` with function signatures matching current private functions.
- [ ] S1-D 🚧 — Hard-gate: user gives explicit go/no-go to start extraction.

### Phase 2 — Extract VisitAssignmentEngine

- [ ] S2-A 🔄 `[Codex]` — Move visit anchor resolution helpers (`_resolve_snippet_anchor_offset`, `_resolve_visit_from_anchor`, `_find_nearest_target`, `_find_line_start_offset`, `_resolve_visit_segment_bounds`) into `visit_assignment_engine.py`.
- [ ] S2-B 🔄 `[Codex]` — Move visit-scoped population helpers (`_populate_visit_scoped_fields_from_segment_candidates`, `_build_visit_segment_text_by_visit_id`, `_populate_missing_reason_for_visit_from_segments`, `_populate_visit_observations_actions_from_segments`, `_append_visit_segment_summary_field`) into `visit_assignment_engine.py`.
- [ ] S2-C 🔄 `[Codex]` — Rewire `_normalize_canonical_review_scoping` to delegate visit-related blocks to the engine. Verify evidence offsets, snippets, visit identifiers, and grouped field associations remain identical.
- [ ] S2-D 🔄 `[Codex]` — Run targeted backend tests and fix regressions. Record evidence with CC/LOC snapshots.

### Phase 3 — Documentation and handoff

- [ ] S3-A 🔄 `[GPT-4.1]` — Complete mandatory documentation task: `no-doc-needed` or update architecture notes if needed.
- [ ] S3-B 🔄 `[GPT-4.1]` — Record completion evidence in this plan.
- [ ] S3-C 🚧 — Hard-gate: user validates results and authorizes PR creation.

---

## Prompt Queue

### S1-A — Verify PR-1 merge and baseline

```text
Verify preconditions for PR-2:
1) Confirm current branch is based on latest main (after PR-1 merge):
   git log --oneline -5 main
2) Confirm extracted modules from PR-1 exist:
   - backend/app/application/documents/review_payload_projector.py
   - backend/app/application/documents/age_normalizer.py
3) Confirm review_service.py imports from these modules.
4) Take baseline LOC/CC snapshot of review_service.py post-PR-1:
   radon cc -s -n C backend/app/application/documents/review_service.py
   (Get-Content backend/app/application/documents/review_service.py).Count

Record in ## Evidence.
```

### S1-B — Add safety-net tests for visit scoping

```text
Strengthen regression safety for PR-2 extraction scope:
1) Locate existing tests covering:
   - visit scoping / segment boundary resolution
   - evidence offset handling
   - visit-scoped field population (observations, actions, reason-for-visit)
2) Add focused assertions for:
   - visit ordering and identifier stability
   - evidence snippet offsets after scoping
   - observation/action population per visit
   - reason-for-visit backfill behavior
3) Keep tests deterministic. Avoid broad rewrites.

Run: pytest backend/tests -k "review or visit or segment" -q
Record evidence: test count, pass/fail, file references.
```

### S1-C — Create visit engine skeleton

```text
Create backend/app/application/documents/visit_assignment_engine.py:
- Module docstring: "Visit assignment, segment boundary resolution, and visit-scoped field population."
- Function signatures matching current private functions:
  - resolve_snippet_anchor_offset(...)
  - resolve_visit_from_anchor(...)
  - find_nearest_target(...)
  - find_line_start_offset(...)
  - resolve_visit_segment_bounds(...)
  - populate_visit_scoped_fields_from_segment_candidates(...)
  - build_visit_segment_text_by_visit_id(...)
  - populate_missing_reason_for_visit_from_segments(...)
  - populate_visit_observations_actions_from_segments(...)
  - append_visit_segment_summary_field(...)
- Bodies: pass (scaffold only)
- Keep imports minimal (stdlib + typing).
```

### S1-D — Execution go/no-go hard-gate

```text
Summarize: PR-1 merge status (S1-A), safety-net tests (S1-B), skeleton created (S1-C).
Ask the user for explicit go/no-go to start extraction.
Stop until user confirms go.
```

### S2-A — Extract visit anchor resolution helpers

```text
Move visit anchor resolution and segment bounds logic to visit_assignment_engine.py.

Target functions to move (replacing scaffolded stubs):
- _resolve_snippet_anchor_offset (line ~708)
- _resolve_visit_from_anchor (line ~734)
- _find_nearest_target (line ~750)
- _find_line_start_offset (line ~810)
- _resolve_visit_segment_bounds (line ~816)

Drop leading underscore for public module API.
Keep algorithmic behavior unchanged.
```

### S2-B — Extract visit-scoped population helpers

```text
Move visit-scoped field population logic into visit_assignment_engine.py.

Target functions to move:
- _populate_visit_scoped_fields_from_segment_candidates (line ~1194)
- _build_visit_segment_text_by_visit_id (line ~1125)
- _populate_missing_reason_for_visit_from_segments (line ~1169)
- _populate_visit_observations_actions_from_segments (line ~1080)
- _append_visit_segment_summary_field (line ~1058)

Provide a single orchestration entrypoint (e.g., `assign_visit_scoped_fields(...)`)
that _normalize_canonical_review_scoping can call to replace the inline population block.

Preserve: visit ordering, metadata keys, evidence snippet handling.
```

### S2-C — Rewire _normalize_canonical_review_scoping

```text
Refactor _normalize_canonical_review_scoping in review_service.py to delegate
visit-related blocks to visit_assignment_engine:
- Replace inline anchor resolution with engine calls.
- Replace inline population block with engine orchestration entrypoint.
- Keep overall orchestration flow in review_service.py.

Verify identical behavior for:
- evidence offsets and snippets,
- visit identifiers and ordering,
- grouped field associations.

The function should shrink significantly but still own the top-level loop.
```

### S2-D — Validate and record evidence

```text
Run targeted backend tests:
  pytest backend/tests -k "review or visit or segment" -q

Run complexity/size checks:
  radon cc -s -n C backend/app/application/documents/visit_assignment_engine.py
  (Get-Content backend/app/application/documents/visit_assignment_engine.py).Count
  radon cc -s -n C backend/app/application/documents/review_service.py

If regressions: fix in extracted module first.

Record in ## Evidence:
- pytest command and output summary
- radon cc snapshot for visit_assignment_engine.py
- LOC for visit_assignment_engine.py (must be < 400)
- review_service.py LOC after extraction
- residual risks
```

### S3-A — Mandatory documentation task

```text
Decide and execute documentation task:
- This is an internal refactor with no new long-lived architectural rules.
- Close as `no-doc-needed` with rationale: "PR-2 extracts visit assignment
  helpers into focused engine module; no new rules, no API changes."
Record decision in ## Evidence.
```

### S3-B — Record completion evidence

```text
Update ## Evidence with:
- visit_assignment_engine.py function list
- LOC/CC verification table: module | LOC | max CC
- review_service.py LOC after PR-2
- _normalize_canonical_review_scoping LOC after delegation
- pytest + L2 gate results
- confirmation that public API is unchanged
```

### S3-C — User validation hard-gate

```text
Present PR-2 summary to user:
- what was extracted (1 module, ~10 functions)
- review_service.py LOC before/after (delta from PR-1 baseline)
- _normalize_canonical_review_scoping LOC reduction
- compatibility guarantees verified
- validation evidence

Ask user for explicit authorization to create PR.
Stop until user confirms.

Remind user: after PR-2 merge, PR-3 (SegmentParser + ClauseClassifier + cleanup) is next.
```

---

## Active Prompt

Pending user activation.

---

## Evidence

_Section for recording step completion evidence per protocol §8 EVIDENCE BLOCK. Each step records: Step ID, Code commit SHA, CI run ID + conclusion, Plan commit SHA._

---

## Acceptance criteria

1. `visit_assignment_engine.py` is created with extracted visit assignment and population logic.
2. `_normalize_canonical_review_scoping` delegates visit blocks to the engine.
3. Public API remains unchanged for `get_document_review`, `mark_document_reviewed`, and `reopen_document_review`.
4. Evidence offsets, snippets, visit identifiers, and field associations are unchanged.
5. No extracted file exceeds 400 LOC.
6. No function in touched refactor scope exceeds CC 20.
7. Existing tests pass without broad rewrites.
8. Mandatory documentation task is completed.

---

## How to test

```powershell
# Focused backend checks for PR-2 scope
pytest backend/tests -k "review or visit or segment" -q

# Complexity/size checks
radon cc -s -n C backend/app/application/documents/visit_assignment_engine.py
radon cc -s -n C backend/app/application/documents/review_service.py

# LOC checks
Get-ChildItem backend/app/application/documents/visit_assignment_engine.py, backend/app/application/documents/review_service.py | ForEach-Object { Write-Output "$($_.Name): $((Get-Content $_).Count) LOC" }

# Project L2 gate
scripts/ci/test-L2.ps1 -BaseRef main
```
