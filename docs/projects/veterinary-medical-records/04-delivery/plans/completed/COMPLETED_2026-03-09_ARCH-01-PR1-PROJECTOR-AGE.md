# Plan: ARCH-01 PR-1 — Extract ReviewPayloadProjector + AgeNormalizer

> **ARCH origin:** `ARCH-01` — [arch-01-decompose-review-service.md](../../Backlog/completed/arch-01-decompose-review-service.md)
> **Related plans (series):**
> - **Archived as:** `COMPLETED_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md`
> - [PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md](../PLAN_2026-03-09_ARCH-01-DECOMPOSITION-PR-SERIES/PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md)
> - [PLAN_2026-03-09_ARCH-01-PR3-PARSER-CLASSIFIER.md](../PLAN_2026-03-09_ARCH-01-DECOMPOSITION-PR-SERIES/PLAN_2026-03-09_ARCH-01-PR3-PARSER-CLASSIFIER.md)

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for execution protocol, hard-gates, and handoff behavior.

**Backlog item:** [arch-01-decompose-review-service.md](../../Backlog/completed/arch-01-decompose-review-service.md)
**Branch:** `refactor/arch-01-pr1-projector-age`
**PR:** [#254](https://github.com/isilionisilme/veterinary-medical-records/pull/254) — `refactor: extract review projector and age normalizer`
**User Story:** N/A (Architecture improvement ARCH-01, PR 1 of 3)
**Prerequisite:** ARCH-03 completed, or explicit user approval to proceed with temporary local-only complexity checks
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

`backend/app/application/documents/review_service.py` is a large hotspot (1,765 LOC, max CC 99) with mixed responsibilities. This PR-1 extracts the two lowest-risk responsibility groups:

### Extraction targets for this PR

**ReviewPayloadProjector** — canonical shape projection:
- `_project_review_payload_to_canonical` (line ~672)
- `_normalize_review_interpretation_data` (line ~346)
- `_has_non_empty_string` (line ~668)

**AgeNormalizer** — 5 age-related functions:
- `_normalize_age_from_review_projection` (line ~466)
- `_resolve_existing_age_field_state` (line ~527)
- `_upsert_age_field_from_global_schema` (line ~542)
- `_resolve_age_display_from_global_schema` (line ~627)
- `_format_age_display_from_years` (line ~659)

### Public API functions (must remain unchanged across all 3 PRs)

- `get_document_review` (line ~269)
- `mark_document_reviewed` (line ~1675)
- `reopen_document_review` (line ~1723)

### Dataclass/model definitions (stay in review_service.py)

- `LatestCompletedRunReview`, `ActiveInterpretationReview`, `RawTextArtifactAvailability`, `DocumentReview`, `DocumentReviewLookupResult`, `ReviewToggleResult`

---

## Objective

1. Extract `ReviewPayloadProjector` and `AgeNormalizer` into focused modules.
2. Keep behavior and public API unchanged.
3. Meet maintainability thresholds: no extracted file above 400 LOC, no function above CC 20 in touched paths.
4. Existing tests continue passing without test rewrites.

---

## Scope Boundary

- **In scope:** extraction of projection and age logic to new modules under `backend/app/application/documents/`, safety-net tests, wiring, regression validation.
- **Out of scope:** visit assignment extraction (PR-2), segment parser/classifier extraction (PR-3), API contract changes, DTO/schema redesign, frontend changes, repository interface changes.

---

## PR Roadmap

This plan is **PR-1 of 3** (Option C — maximum caution):

| PR | Plan | Scope | Risk |
|---|---|---|---|
| **PR-1 (this)** | ARCH-01-PR1-PROJECTOR-AGE | Scaffolding + `ReviewPayloadProjector` + `AgeNormalizer` | Low |
| PR-2 | ARCH-01-PR2-VISIT-ENGINE | `VisitAssignmentEngine` | Medium |
| PR-3 | ARCH-01-PR3-PARSER-CLASSIFIER | `SegmentParser` + `ClauseClassifier` + final cleanup | Medium-high |

Decision record:
- Selected option: `C (3 PRs)`
- Rationale: User prefers maximum caution; isolates highest-risk CC-99 decomposition in its own PR.

---

## Commit Recommendations (inline, non-blocking)

| After steps | Scope | Suggested message | Expected validation |
|---|---|---|---|
| S1-A..S1-B | Baseline and ARCH-03 check | `refactor(plan-arch-01): verify baseline and ARCH-03 dependency` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| S2-A..S2-C | Safety net + scaffolding | `refactor(plan-arch-01): add safety-net tests and module skeletons for PR-1` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| S3-A..S3-D | Projector + age extraction | `refactor(plan-arch-01): extract review projector and age normalizer` | `scripts/ci/test-L2.ps1 -BaseRef main` |
| S4-A..S4-B | Evidence and docs | `docs(plan-arch-01): PR-1 decomposition evidence` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |

---

## Execution Status

**Legend**
- 🔄 auto-chain
- 🚧 hard-gate

### Phase 1 — Preconditions and baseline

- [x] S1-A 🔄 `[GPT-4.1]` — Verify dependency status for ARCH-03 (CI complexity gates): already implemented vs temporary local guard fallback. Record baseline CC/LOC snapshot.
- [x] S1-B 🔄 `[GPT-4.1]` — Produce baseline responsibility map from current `review_service.py`: confirm function groupings, identify coupling points for PR-1 scope (projector + age).
- [x] S1-C 🚧 — Hard-gate: user gives explicit go/no-go to start implementation.

### Phase 2 — Safety net and scaffolding

- [x] S2-A 🔄 `[Codex]` — Add/refine focused regression tests around `get_document_review` canonical projection and age normalization paths.
- [x] S2-B 🔄 `[Codex]` — Create module skeletons: `review_payload_projector.py`, `age_normalizer.py`.
- [x] S2-C 🔄 `[Codex]` — Introduce import/wiring scaffolding in `review_service.py` for the two new modules without behavior changes.

### Phase 3 — Extract ReviewPayloadProjector + AgeNormalizer

- [x] S3-A 🔄 `[Codex]` — Move `_project_review_payload_to_canonical`, `_normalize_review_interpretation_data`, `_has_non_empty_string` into `review_payload_projector.py`.
- [x] S3-B 🔄 `[Codex]` — Move the 5 age-related functions into `age_normalizer.py`.
- [x] S3-C 🔄 `[Codex]` — Replace in-file calls in `review_service.py` with module calls; preserve function signatures and return payloads.
- [x] S3-D 🔄 `[Codex]` — Run targeted backend tests and fix regressions without altering product behavior. Record evidence.

### Phase 4 — Documentation and handoff

- [x] S4-A 🔄 `[GPT-4.1]` — Complete mandatory documentation task: `no-doc-needed` (internal refactor, no new long-lived rules) or update architecture notes if needed.
- [x] S4-B 🔄 `[GPT-4.1]` — Record completion evidence in this plan (LOC/CC checks, test outcomes).
- [x] S4-C 🚧 — Hard-gate: user validated results and authorized PR creation; PR #254 opened.

---

## Prompt Queue

### S1-A — Verify dependency and baseline

```text
Inspect current repository status for ARCH-03 dependency:
1) Open docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-03-add-ci-complexity-gates.md.
2) Check whether complexity gates are already implemented in CI scripts/workflow
   (look for radon or CC checks in scripts/ci/ and .github/workflows/).
3) Report one of:
   - "ARCH-03 ready" (CI already enforces CC/LOC gates), or
   - "ARCH-03 not ready" with a temporary local check strategy:
     use `radon cc -s -n C backend/app/application/documents/` and
     `(Get-Content <file>).Count` as local guards during this refactor.
4) Record conclusion in ## Evidence with:
   - files inspected,
   - guard strategy chosen,
   - baseline CC/LOC snapshot of review_service.py.
```

### S1-B — Baseline responsibility map (PR-1 scope)

```text
Analyze backend/app/application/documents/review_service.py (1,765 LOC).
Focus on confirming the PR-1 extraction targets:

1) Payload projection group:
   - _project_review_payload_to_canonical (line ~672)
   - _normalize_review_interpretation_data (line ~346)
   - _has_non_empty_string (line ~668)
   → Destination: review_payload_projector.py

2) Age normalization group:
   - _normalize_age_from_review_projection (line ~466)
   - _resolve_existing_age_field_state (line ~527)
   - _upsert_age_field_from_global_schema (line ~542)
   - _resolve_age_display_from_global_schema (line ~627)
   - _format_age_display_from_years (line ~659)
   → Destination: age_normalizer.py

For each group:
- Confirm these functions have no deep coupling to visit/segment logic.
- Identify shared constants, regexes, or dataclass imports they need.
- List callers within review_service.py that will need rewiring.

Record the map in ## Evidence before any code move.
```

### S1-C — Execution go/no-go hard-gate

```text
Summarize: ARCH-03 dependency status (S1-A), confirmed extraction map (S1-B).
Ask the user for explicit go/no-go to start Phase 2.
Stop until user confirms go.
```

### S2-A — Add safety-net tests

```text
Strengthen regression safety for PR-1 extraction scope:
1) Locate existing tests covering:
   - get_document_review (review retrieval + canonical projection)
   - age normalization paths
2) Add focused assertions for:
   - canonical payload shape returned by get_document_review
   - age field presence, format, and precedence
3) Keep tests deterministic. Avoid broad rewrites.

Run: pytest backend/tests -k "review or canonical or age" -q
Record evidence: test count, pass/fail, file references.
```

### S2-B — Create module skeletons

```text
Create module skeleton files under backend/app/application/documents/:

1) review_payload_projector.py:
   - Module docstring: "Canonical review payload projection."
   - Function signatures matching: _project_review_payload_to_canonical,
     _normalize_review_interpretation_data, _has_non_empty_string
   - Bodies: pass (scaffold only, no logic yet)

2) age_normalizer.py:
   - Module docstring: "Age normalization and display formatting."
   - Function signatures matching the 5 age-related functions
   - Bodies: pass (scaffold only)

Keep imports minimal (stdlib + typing only).
```

### S2-C — Wire scaffolding from review_service

```text
Update review_service.py:
- Add imports from review_payload_projector and age_normalizer.
- Keep existing behavior identical (import but don't call yet).
- Ensure module passes lint/tests.

Run: scripts/ci/test-L1.ps1 -BaseRef HEAD
```

### S3-A — Extract ReviewPayloadProjector

```text
Move canonical projection logic from review_service.py into review_payload_projector.py.

Target functions to move:
- _project_review_payload_to_canonical (line ~672)
- _normalize_review_interpretation_data (line ~346)
- _has_non_empty_string (line ~668)

Constraints:
- Preserve output shape exactly (dict structure, key names, fallback values).
- Preserve fallback behavior and normalization ordering.
- Keep backward-compatible semantics for missing/empty data.
- Drop leading underscore on public module functions if appropriate.
- Add/adjust tests only where needed for behavioral equivalence.
```

### S3-B — Extract AgeNormalizer

```text
Move the 5 age-related functions into age_normalizer.py:
- _normalize_age_from_review_projection (line ~466)
- _resolve_existing_age_field_state (line ~527)
- _upsert_age_field_from_global_schema (line ~542)
- _resolve_age_display_from_global_schema (line ~627)
- _format_age_display_from_years (line ~659)

Constraints:
- Keep canonical keys and labels unchanged.
- Preserve existing precedence rules for age resolution.
- Preserve behavior for invalid/missing age values.
- If functions share constants/regexes with other groups,
  keep them duplicated locally (minimal coupling for now).
```

### S3-C — Replace in-file calls

```text
Refactor review_service.py to delegate payload projection and age normalization
to the new modules.
- Replace direct function calls with imports from new modules.
- Keep function signatures and return payloads unchanged at the review_service.py boundary.
- Remove only obvious duplicated wiring; keep risky cleanup for PR-3.
```

### S3-D — Validate extracted behavior

```text
Run targeted tests:
  pytest backend/tests -k "review or canonical or age" -q

If regressions appear:
- fix in extracted module first,
- avoid changing tests unless they assert incorrect legacy behavior.

Run complexity/size checks:
  radon cc -s -n C backend/app/application/documents/review_payload_projector.py
  radon cc -s -n C backend/app/application/documents/age_normalizer.py
  (Get-Content backend/app/application/documents/review_payload_projector.py).Count
  (Get-Content backend/app/application/documents/age_normalizer.py).Count

Record in ## Evidence:
- pytest command and output summary
- files changed to fix regressions (if any)
- radon cc snapshot for both new modules
- LOC for both new modules (must be < 400 each)
```

### S4-A — Mandatory documentation task

```text
Decide and execute documentation task:
- This is an internal refactor with no new long-lived architectural rules.
- Close as `no-doc-needed` with rationale: "PR-1 extracts existing private
  helpers into focused modules; no new rules, no API changes."
- If implementation revealed new lasting rules, update architecture notes instead.
Record decision in ## Evidence.
```

### S4-B — Record completion evidence

```text
Update ## Evidence with:
- extracted modules and function list
- LOC/CC verification table: module | LOC | max CC
- review_service.py LOC after PR-1 (should be reduced by ~150-200 LOC)
- pytest + L1/L2 gate results
- confirmation that public API is unchanged
```

### S4-C — User validation hard-gate

```text
Present PR-1 summary to user:
- what was extracted (2 modules, ~8 functions)
- review_service.py LOC before/after
- compatibility guarantees verified
- validation evidence (test pass rates, CC/LOC met)

Ask user for explicit authorization to create PR.
Stop until user confirms.

Remind user: after PR-1 merge, PR-2 (VisitAssignmentEngine) is next.
```

---

## Active Prompt

Completed and archived on 2026-03-09.

---

## Evidence

_Section for recording step completion evidence per protocol §8 EVIDENCE BLOCK. Each step records: Step ID, Code commit SHA, CI run ID + conclusion, Plan commit SHA._

### Session override

- User confirmed override for this session on 2026-03-09: mark plan tasks as completed when materially complete, without waiting for the repository step-completion protocol.

### Local status snapshot (2026-03-09)

- Current branch: `refactor/arch-01-pr1-projector-age`
- Materially completed in this branch:
   - `S1-A` through `S1-C`
   - `S2-A` through `S2-C`
   - `S3-A` through `S3-D`
   - `S4-A` through `S4-B`
   - `S4-C`
- Local validation evidence:
   - Baseline reviewed from original `review_service.py` hotspot scope: projector + age functions isolated as PR-1 extraction targets; user go/no-go for implementation granted before Phase 2
   - Extracted modules present: `backend/app/application/documents/review_payload_projector.py` (174 LOC), `backend/app/application/documents/age_normalizer.py` (211 LOC)
   - `review_service.py` current size after PR-1 extraction: 1402 LOC
   - Extracted function groups:
      - `review_payload_projector.py`: `_project_review_payload_to_canonical`, `_normalize_review_interpretation_data`, `_has_non_empty_string`, microchip field backfill helper
      - `age_normalizer.py`: `_normalize_age_from_review_projection`, `_resolve_existing_age_field_state`, `_upsert_age_field_from_global_schema`, `_resolve_age_display_from_global_schema`, `_format_age_display_from_years`, local string helper
   - Backend wiring updated in `backend/app/application/documents/review_service.py`, `backend/app/application/documents/edit_service.py`, and `backend/app/application/documents/__init__.py`
   - Regression coverage updated in `backend/tests/integration/test_document_review.py`
   - Public API unchanged at `review_service.py` boundary: `get_document_review`, `mark_document_reviewed`, `reopen_document_review`
   - `scripts/ci/test-L3.ps1 -BaseRef main` passed on the backend-only slice: `827 passed, 2 xfailed`, total coverage `91.23%`, `preflight-ci-local: PASS`
   - Docs/contract drift was split into a separate branch so PR-1 remains backend-focused
   - User validated the PR-1 outcome and explicitly authorized PR creation on 2026-03-09
   - PR opened: [#254](https://github.com/isilionisilme/veterinary-medical-records/pull/254) — `refactor: extract review projector and age normalizer`

---

## Acceptance criteria

1. `review_payload_projector.py` and `age_normalizer.py` are created with extracted logic.
2. Public API remains unchanged for `get_document_review`, `mark_document_reviewed`, and `reopen_document_review`.
3. No extracted file exceeds 400 LOC.
4. No function in touched refactor scope exceeds CC 20.
5. Existing tests pass without broad rewrites.
6. Mandatory documentation task is completed (`doc updated` or `no-doc-needed` rationale).

---

## How to test

```powershell
# Focused backend checks for PR-1 scope
pytest backend/tests -k "review or canonical or age" -q

# Complexity/size checks for extracted modules
radon cc -s -n C backend/app/application/documents/review_payload_projector.py
radon cc -s -n C backend/app/application/documents/age_normalizer.py

# LOC checks
Get-ChildItem backend/app/application/documents/review_payload_projector.py, backend/app/application/documents/age_normalizer.py | ForEach-Object { Write-Output "$($_.Name): $((Get-Content $_).Count) LOC" }

# Project L2 gate
scripts/ci/test-L2.ps1 -BaseRef main
```
