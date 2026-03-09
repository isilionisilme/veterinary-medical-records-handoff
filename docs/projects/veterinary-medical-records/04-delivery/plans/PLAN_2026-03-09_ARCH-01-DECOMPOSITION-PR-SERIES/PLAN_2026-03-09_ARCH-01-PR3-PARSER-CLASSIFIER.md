# Plan: ARCH-01 PR-3 — Extract SegmentParser + ClauseClassifier + Final Cleanup

> **ARCH origin:** `ARCH-01` — [arch-01-decompose-review-service.md](../../Backlog/arch-01-decompose-review-service.md)
> **Related plans (series):**
> - [PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md](PLAN_2026-03-09_ARCH-01-PR1-PROJECTOR-AGE.md)
> - [PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md](PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md)
> - **Current:** `PLAN_2026-03-09_ARCH-01-PR3-PARSER-CLASSIFIER.md`

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for execution protocol, hard-gates, and handoff behavior.

**Backlog item:** [arch-01-decompose-review-service.md](../../Backlog/arch-01-decompose-review-service.md)
**Branch:** `refactor/arch-01-pr3-parser-classifier`
**PR:** Pending (PR created on explicit user request)
**User Story:** N/A (Architecture improvement ARCH-01, PR 3 of 3)
**Prerequisite:** PR-2 merged ([PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE](PLAN_2026-03-09_ARCH-01-PR2-VISIT-ENGINE.md))
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

After PR-1 (projector + age) and PR-2 (visit engine), `review_service.py` still contains the highest-complexity code: `_split_segment_into_observations_actions` (CC ~99, ~150 LOC) with deeply nested classification heuristics. This PR-3 tackles the highest-risk extraction and performs final cleanup.

### Extraction targets for this PR

**SegmentParser** — clause normalization and splitting:
- `_normalize_segment_clause` (line ~887)
- `_extract_reason_for_visit_from_segment` (line ~850)
- Segment-splitting portion of `_split_segment_into_observations_actions` (line ~910): text splitting, regex matching, candidate fragment extraction.

**ClauseClassifier** — classification heuristics (the CC-99 core):
- Classification portion of `_split_segment_into_observations_actions` (line ~910): the if/elif chains that determine whether a clause is therapeutic/action, diagnostic, recommendation/plan, or pure observation.

### Final cleanup scope

- Remove dead private helpers from `review_service.py` that were migrated in PR-1, PR-2, and PR-3.
- Full API compatibility verification across all 3 PRs.
- Complete ARCH-01 documentation task.

### Public API functions (must remain unchanged)

- `get_document_review` (line ~269)
- `mark_document_reviewed` (line ~1675)
- `reopen_document_review` (line ~1723)

---

## Objective

1. Decompose the CC-99 function `_split_segment_into_observations_actions` into `SegmentParser` + `ClauseClassifier`, each below CC 20.
2. Remove dead code from `review_service.py` left by all 3 extraction PRs.
3. Verify full API compatibility and meet all ARCH-01 acceptance criteria.
4. Complete the mandatory documentation task for the full ARCH-01 decomposition.

---

## Scope Boundary

- **In scope:** extraction of segment parsing/classification into new modules, dead code removal from `review_service.py`, full validation suite, documentation task, final ARCH-01 evidence.
- **Out of scope:** API contract changes, DTO/schema redesign, frontend changes, repository interface changes.

---

## PR Roadmap

This plan is **PR-3 of 3** (Option C — maximum caution):

| PR | Plan | Scope | Risk |
|---|---|---|---|
| PR-1 (done) | ARCH-01-PR1-PROJECTOR-AGE | `ReviewPayloadProjector` + `AgeNormalizer` | Low |
| PR-2 (done) | ARCH-01-PR2-VISIT-ENGINE | `VisitAssignmentEngine` | Medium |
| **PR-3 (this)** | ARCH-01-PR3-PARSER-CLASSIFIER | `SegmentParser` + `ClauseClassifier` + final cleanup | Medium-high |

---

## Commit Recommendations (inline, non-blocking)

| After steps | Scope | Suggested message | Expected validation |
|---|---|---|---|
| S1-A..S1-C | Safety net + skeletons | `refactor(plan-arch-01): add parser/classifier skeletons and safety-net tests` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| S2-A..S2-D | Parser + classifier extraction | `refactor(plan-arch-01): extract segment parser and clause classifier` | `scripts/ci/test-L2.ps1 -BaseRef main` |
| S3-A..S3-C | Cleanup + full validation | `refactor(plan-arch-01): remove dead helpers and validate full API` | `scripts/ci/test-L2.ps1 -BaseRef main` |
| S4-A..S4-B | Evidence and docs | `docs(plan-arch-01): ARCH-01 final decomposition evidence` | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |

---

## Execution Status

**Legend**
- 🔄 auto-chain
- 🚧 hard-gate

### Phase 1 — Preconditions and scaffolding

- [ ] S1-A 🔄 `[GPT-4.1]` — Verify PR-2 is merged and branch is based on latest `main`. Confirm all prior extracted modules exist and are wired.
- [ ] S1-B 🔄 `[Codex]` — Add/refine focused regression tests around observation/action split behavior and clause classification output.
- [ ] S1-C 🔄 `[Codex]` — Create module skeletons: `segment_parser.py`, `clause_classifier.py`.
- [ ] S1-D 🚧 — Hard-gate: user gives explicit go/no-go to start extraction.

### Phase 2 — Extract SegmentParser + ClauseClassifier

- [ ] S2-A 🔄 `[Claude]` — Move `_normalize_segment_clause`, `_extract_reason_for_visit_from_segment`, and segment-splitting logic into `segment_parser.py`.
- [ ] S2-B 🔄 `[Claude]` — Move classification heuristics (the CC-99 if/elif chains) into `clause_classifier.py` as a strategy-style classifier.
- [ ] S2-C 🔄 `[Claude]` — Replace `_split_segment_into_observations_actions` in `review_service.py` with a thin orchestrator (<30 LOC, CC <10) that calls `SegmentParser` + `ClauseClassifier`.
- [ ] S2-D 🔄 `[Codex]` — Run targeted backend tests and fix regressions. Verify CC of all touched functions is below 20. Record evidence.

### Phase 3 — Final cleanup and stabilization

- [ ] S3-A 🔄 `[Codex]` — Verify all three public API functions remain unchanged: signatures, return structures, side effects. Verify dataclass definitions are unchanged.
- [ ] S3-B 🔄 `[Codex]` — Remove dead private helpers from `review_service.py` that were migrated across PR-1, PR-2, and PR-3.
- [ ] S3-C 🔄 `[Codex]` — Run full backend suite plus L2 gate. Verify all complexity/LOC thresholds across ALL extracted modules.

### Phase 4 — Documentation, evidence, and final handoff

- [ ] S4-A 🔄 `[GPT-4.1]` — Complete mandatory documentation task for the full ARCH-01 decomposition. Update architecture notes if the decomposition introduces lasting patterns; otherwise `no-doc-needed`.
- [ ] S4-B 🔄 `[GPT-4.1]` — Record final ARCH-01 completion evidence (all 3 PRs aggregate: modules, LOC/CC, test outcomes, architecture impact).
- [ ] S4-C 🚧 — Hard-gate: user validates results and authorizes PR creation. Mark ARCH-01 backlog item as done.

---

## Prompt Queue

### S1-A — Verify PR-2 merge and baseline

```text
Verify preconditions for PR-3:
1) Confirm current branch is based on latest main (after PR-2 merge):
   git log --oneline -5 main
2) Confirm all extracted modules from PR-1 and PR-2 exist:
   - backend/app/application/documents/review_payload_projector.py
   - backend/app/application/documents/age_normalizer.py
   - backend/app/application/documents/visit_assignment_engine.py
3) Confirm review_service.py imports from all three.
4) Baseline LOC/CC snapshot of review_service.py post-PR-2:
   radon cc -s -n C backend/app/application/documents/review_service.py
   (Get-Content backend/app/application/documents/review_service.py).Count
5) Baseline CC of _split_segment_into_observations_actions:
   radon cc -s backend/app/application/documents/review_service.py | Select-String "split_segment"

Record in ## Evidence.
```

### S1-B — Add safety-net tests for parser/classifier

```text
Strengthen regression safety for PR-3 extraction scope:
1) Locate existing tests covering:
   - observation/action split output shape
   - clause classification behavior (therapeutic, diagnostic, recommendation, observation)
   - segment clause normalization
   - reason-for-visit extraction from segments
2) Add focused assertions for:
   - deterministic classification output for known input patterns
   - edge cases: empty clauses, single-word clauses, mixed-language clauses
   - observation/action tuple stability
3) Keep tests deterministic. Avoid broad rewrites.

Run: pytest backend/tests -k "review or segment or observation or action or clause" -q
Record evidence: test count, pass/fail, file references.
```

### S1-C — Create parser/classifier skeletons

```text
Create module skeleton files under backend/app/application/documents/:

1) segment_parser.py:
   - Module docstring: "Segment clause normalization, splitting, and reason-for-visit extraction."
   - Function signatures:
     - normalize_segment_clause(*, raw_clause: str) -> str
     - extract_reason_for_visit_from_segment(*, segment_text: str) -> str | None
     - split_segment_into_fragments(*, segment_text: str) -> tuple[list[str], list[str]]
       (or matching current return contract)
   - Bodies: pass

2) clause_classifier.py:
   - Module docstring: "Clause classification for observation/action/diagnostic/plan categorization."
   - Class or function signature:
     - classify_clause(clause: str) -> str  (returns category label)
     - Or a ClauseClassifier class with a classify method
   - Bodies: pass

Keep imports minimal (stdlib + typing).
```

### S1-D — Execution go/no-go hard-gate

```text
Summarize: PR-2 merge status (S1-A), safety-net tests (S1-B), skeletons created (S1-C).
Present the risk profile: this PR decomposes the CC-99 function, highest risk in the series.
Ask the user for explicit go/no-go to start extraction.
Stop until user confirms go.
```

### S2-A — Extract SegmentParser

```text
Move clause normalization and splitting logic into segment_parser.py.

Target functions to move:
- _normalize_segment_clause (line ~887)
- _extract_reason_for_visit_from_segment (line ~850)
- Segment-splitting portion of _split_segment_into_observations_actions (line ~910):
  the text splitting, regex matching, and candidate fragment extraction.

Responsibilities:
- normalize raw clauses (whitespace, punctuation, casing rules),
- split segment text into candidate observation/action fragments,
- preserve language-specific regex behavior.

Drop leading underscores for public module API.
No behavior redesign in this step — pure mechanical extraction.
```

### S2-B — Extract ClauseClassifier

```text
Move classification heuristics into clause_classifier.py.

Target: the classification portion of _split_segment_into_observations_actions
(line ~910, CC ~99) — the if/elif chains that determine whether a clause
is therapeutic/action, diagnostic, recommendation/plan, or pure observation.

Strategy:
- Create a classify_clause function (or ClauseClassifier class with classify method).
- Break the monolithic if/elif chain into focused rule groups:
  - is_therapeutic_action(clause) -> bool
  - is_diagnostic(clause) -> bool
  - is_recommendation_plan(clause) -> bool
  - Default: observation
- Each rule group should be <CC 10.
- The top-level classifier dispatches to rule groups in priority order.

Preserve current priority ordering so outputs remain stable.
Goal: no function in this module above CC 20.
```

### S2-C — Orchestrate parser/classifier from review_service

```text
Replace _split_segment_into_observations_actions in review_service.py
with a thin orchestrator that calls:
- SegmentParser for text splitting and clause normalization
- ClauseClassifier for observation/action/diagnostic/plan classification

The orchestrator should be:
- <30 LOC
- CC <10
- Same return contract as the original function

Ensure _normalize_canonical_review_scoping still produces identical output.
Ensure no public API changes.
```

### S2-D — Validate extraction and CC targets

```text
Run targeted backend tests:
  pytest backend/tests -k "review or segment or observation or action or clause" -q

Run complexity/size checks on ALL new modules:
  radon cc -s -n C backend/app/application/documents/segment_parser.py
  radon cc -s -n C backend/app/application/documents/clause_classifier.py
  radon cc -s -n C backend/app/application/documents/review_service.py
  Get-ChildItem backend/app/application/documents/*.py | ForEach-Object { "$($_.Name): $((Get-Content $_).Count) LOC" }

Verify:
- No function above CC 20 in any touched module.
- No extracted module above 400 LOC.
- _split_segment_into_observations_actions orchestrator is CC <10.

If a function exceeds threshold, perform one additional extraction split.

Record in ## Evidence:
- pytest output summary
- radon cc output for segment_parser.py and clause_classifier.py
- LOC per file table
- any additional splits performed
```

### S3-A — Full API and contract freeze check

```text
Verify all three public API functions remain unchanged across the full
ARCH-01 decomposition (PR-1 + PR-2 + PR-3):
- get_document_review: signature, return structure, side effects
- mark_document_reviewed: signature, return structure, side effects
- reopen_document_review: signature, return structure, side effects

Verify dataclass definitions are unchanged:
- DocumentReview, DocumentReviewLookupResult, ReviewToggleResult

Run full test suite to confirm no behavioral changes:
  pytest backend/tests -k "review or canonical or visit or age or segment" -q
```

### S3-B — Remove dead private helpers

```text
Remove migrated private helpers from review_service.py that were extracted
across PR-1, PR-2, and PR-3. Checklist of functions to verify removal:

PR-1 migrations (should already be removed):
- _project_review_payload_to_canonical → review_payload_projector.py
- _normalize_review_interpretation_data → review_payload_projector.py
- _has_non_empty_string → review_payload_projector.py
- _normalize_age_from_review_projection → age_normalizer.py
- _resolve_existing_age_field_state → age_normalizer.py
- _upsert_age_field_from_global_schema → age_normalizer.py
- _resolve_age_display_from_global_schema → age_normalizer.py
- _format_age_display_from_years → age_normalizer.py

PR-2 migrations (should already be removed):
- _resolve_snippet_anchor_offset → visit_assignment_engine.py
- _resolve_visit_from_anchor → visit_assignment_engine.py
- _find_nearest_target → visit_assignment_engine.py
- _find_line_start_offset → visit_assignment_engine.py
- _resolve_visit_segment_bounds → visit_assignment_engine.py
- _populate_visit_scoped_fields_from_segment_candidates → visit_assignment_engine.py
- _build_visit_segment_text_by_visit_id → visit_assignment_engine.py
- _populate_missing_reason_for_visit_from_segments → visit_assignment_engine.py
- _populate_visit_observations_actions_from_segments → visit_assignment_engine.py
- _append_visit_segment_summary_field → visit_assignment_engine.py

PR-3 migrations (remove in this step):
- _normalize_segment_clause → segment_parser.py
- _extract_reason_for_visit_from_segment → segment_parser.py
- _split_segment_into_observations_actions (original) → replaced by thin orchestrator

Do NOT delete helpers still used by public API paths.
Keep diff focused on migrated code only.
```

### S3-C — Full backend validation

```text
Run full backend validation:
  scripts/ci/test-L2.ps1 -BaseRef main

Also run comprehensive targeted tests:
  pytest backend/tests -k "review or canonical or visit or age or segment" -q

Run final complexity/size checks across ALL modules:
  radon cc -s -n C backend/app/application/documents/
  Get-ChildItem backend/app/application/documents/*.py | ForEach-Object { "$($_.Name): $((Get-Content $_).Count) LOC" }

Verify ARCH-01 acceptance criteria:
- No file > 400 LOC (extracted modules)
- No function CC > 20 in touched paths
- All tests pass
- review_service.py significantly reduced from 1,765 LOC

Record in ## Evidence:
- L2 gate output (pass/fail)
- pytest summary
- final radon cc snapshot for ALL modules under documents/
- final LOC per file table
- review_service.py LOC: before (1,765) → after PR-3
```

### S4-A — Mandatory documentation task (ARCH-01 final)

```text
Decide and execute documentation task for the full ARCH-01 decomposition:

Assessment:
- The decomposition is an internal refactor with no API changes.
- However, the new module structure (5 modules extracted from 1) is a lasting
  architectural pattern that future contributors should understand.

Options:
a) `no-doc-needed`: if the module docstrings and function signatures are
   self-documenting enough.
b) Update architecture notes: add a brief note in the architecture review
   or ADR documenting the decomposition rationale and module boundaries.

Record decision and rationale in ## Evidence.
```

### S4-B — Record final ARCH-01 completion evidence

```text
Update ## Evidence with final ARCH-01 aggregate summary:

1) Module inventory (all 5 extracted modules):
   | Module | Functions | LOC | Max CC |
   |---|---|---|---|
   | review_payload_projector.py | ... | ... | ... |
   | age_normalizer.py | ... | ... | ... |
   | visit_assignment_engine.py | ... | ... | ... |
   | segment_parser.py | ... | ... | ... |
   | clause_classifier.py | ... | ... | ... |
   | review_service.py (residual) | ... | ... | ... |

2) review_service.py LOC: 1,765 → <final>
3) _split_segment_into_observations_actions CC: 99 → <final orchestrator CC>
4) _normalize_canonical_review_scoping LOC: ~400 → <final>
5) Full test suite: pass/fail
6) L2 gate: pass/fail
7) ARCH-01 backlog item status: Ready to close
```

### S4-C — User validation hard-gate (ARCH-01 final)

```text
Present final ARCH-01 decomposition summary to user:

- **PR-1**: ReviewPayloadProjector + AgeNormalizer (merged)
- **PR-2**: VisitAssignmentEngine (merged)
- **PR-3**: SegmentParser + ClauseClassifier + cleanup (this PR)
- review_service.py LOC: 1,765 → <final>
- CC-99 function eliminated
- All ARCH-01 acceptance criteria met
- Full test suite passes

Ask user for explicit authorization to:
1. Create PR-3
2. Mark ARCH-01 backlog item as Done after PR-3 merge

Stop until user confirms.
```

---

## Active Prompt

Pending user activation.

---

## Evidence

_Section for recording step completion evidence per protocol §8 EVIDENCE BLOCK. Each step records: Step ID, Code commit SHA, CI run ID + conclusion, Plan commit SHA._

---

## Acceptance criteria

1. `segment_parser.py` and `clause_classifier.py` are created with extracted logic.
2. `_split_segment_into_observations_actions` is replaced by a thin orchestrator (CC <10, <30 LOC).
3. No function in any touched module exceeds CC 20.
4. No extracted file exceeds 400 LOC.
5. Dead private helpers removed from `review_service.py`.
6. Public API remains unchanged for `get_document_review`, `mark_document_reviewed`, and `reopen_document_review`.
7. Existing tests pass without broad rewrites.
8. Full ARCH-01 acceptance criteria met (aggregate across all 3 PRs).
9. Mandatory documentation task completed.
10. ARCH-01 backlog item ready to close.

---

## How to test

```powershell
# Focused backend checks for PR-3 scope
pytest backend/tests -k "review or canonical or visit or age or segment or clause" -q

# Complexity checks for all extracted modules
radon cc -s -n C backend/app/application/documents/

# LOC checks for all modules
Get-ChildItem backend/app/application/documents/*.py | ForEach-Object { Write-Output "$($_.Name): $((Get-Content $_).Count) LOC" }

# Project L2 gate
scripts/ci/test-L2.ps1 -BaseRef main
```
