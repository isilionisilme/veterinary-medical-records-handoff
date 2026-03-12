# Plan B: Regression Tests — Visit Scoping & Projection Pipeline

**Backlog item:** [arch-27-regression-tests-visit-scoping.md](../Backlog/arch-27-regression-tests-visit-scoping.md)

## TL;DR
Añadir tests que cubren los edge cases de mayor riesgo en el pipeline visit scoping/projection extraído en ARCH-01: fecha duplicada, campo sin visit (unassigned fallback), y derivación de peso desde raw text.

## Prerequisitos
- Branch: crear `test/arch-01-regression-coverage` desde `main` actualizado
- Verificar que ARCH-01 merge está en main

## Steps

### Phase 1: Test file setup
1. **Create `backend/tests/unit/test_visit_scoping_regression.py`**
   - Import `normalize_canonical_review_scoping` from `backend.app.application.documents.visit_scoping`
   - Import `_project_review_payload_to_canonical` from `backend.app.application.documents.review_payload_projector`
   - Follow existing test naming conventions (see `test_visit_date_detection_from_raw_text.py`, `test_visit_segment_observations_actions.py`)

### Phase 2: Core regression test cases
2. **Test: repeated same-day visits** — `test_duplicate_date_creates_separate_visits`
   - Input: `data` with `fields` that have 2+ visit-scoped fields with same normalized date in evidence
   - Raw text containing the same date appearing twice (e.g., "01/15/2025 ... 01/15/2025")
   - Assert: two separate visit objects are created, each with correctly assigned fields
   - Entry point: `normalize_canonical_review_scoping(data, raw_text=raw_text)`

3. **Test: unassigned visit-scoped fields** — `test_ambiguous_field_falls_back_to_unassigned`
   - Input: `data` with visit-scoped field that has ambiguous date token (can't be resolved)
   - Multiple visits present (len(visit_by_date) > 1) so single-visit default doesn't apply
   - Assert: field lands in `unassigned` visit (visit_id="unassigned", visit_date=None)
   - Entry point: `normalize_canonical_review_scoping(data, raw_text=raw_text)`

4. **Test: latest-weight derivation from raw text** — `test_weight_derived_from_raw_text_recovery`
   - Input: `data` with no weight in structured fields
   - Raw text containing weight pattern (e.g., "Peso: 4.5 kg" near a date)
   - Assert: `fields` output contains `derived-weight-current` with correct value
   - Assert: `key == "weight"`, `scope == "document"`, `origin == "derived"`
   - Entry point: `normalize_canonical_review_scoping(data, raw_text=raw_text)`
   - Reference: `_extract_latest_visit_weight_from_raw_text()` in visit_helpers.py

5. **Test: single visit default assignment** — `test_single_visit_absorbs_all_fields`
   - Input: `data` with 1 visit date and multiple visit-scoped fields (no ambiguous date token)
   - Assert: all fields assigned to the single visit, no unassigned visit created
   - Entry point: `normalize_canonical_review_scoping(data, raw_text=raw_text)`

6. **Test: document-level weight from visit weights** — `test_latest_visit_weight_becomes_document_weight`
   - Input: `data` with 2 visits, each having a weight field with different dates
   - Assert: document-level `derived-weight-current` takes value from most recent visit's weight
   - Entry point: `normalize_canonical_review_scoping(data, raw_text=raw_text)`

### Phase 3: Shim compatibility test (nice-to-have from review)
7. **Test: backward-compat shim in test alias** — `test_segment_parser_public_api_matches_legacy_name`
   - Import `split_segment_into_observations_actions` from `segment_parser`
   - Assert it's callable and returns expected structure for a simple input
   - Lightweight — just proves the new public name works

### Phase 4: Fixture design
8. Build **minimal fixture dicts** — don't use full document payloads. Each fixture needs:
   - `fields`: list of dicts with `key`, `value`, `scope`, `section`, `evidence` (with `snippet`)
   - `visits`: list of dicts with `visit_id`, `visit_date`, `fields: []`
   - `raw_text`: string (optional, for weight/date detection tests)
   - Reference field structure: see `_assign_fields_to_visits` in visit_scoping.py — fields need `scope: "visit"` and evidence with `snippet` containing date tokens

### Phase 5: Validate
9. Run `ruff check --fix` + `ruff format` on new test file
10. Run `python -m pytest backend/tests/unit/test_visit_scoping_regression.py -x -v` — all new tests pass
11. Run `python -m pytest backend/tests/ -x --tb=short -q` — 706+ tests still pass (no regressions)
12. Run `scripts/ci/test-L3.ps1 -SkipDocker -SkipE2E` — green

## Relevant files
- `backend/app/application/documents/visit_scoping.py` — `normalize_canonical_review_scoping()` (line 345, orchestrator entry point)
- `backend/app/application/documents/visit_helpers.py` — `postprocess_weights()` (line 295+, weight derivation)
- `backend/app/application/documents/visit_helpers.py` — `_extract_latest_visit_weight_from_raw_text()` (weight from raw text)
- `backend/app/application/documents/visit_scoping.py` — `_build_visit_roster()` (line 130+, duplicate date handling)
- `backend/app/application/documents/visit_scoping.py` — `_assign_fields_to_visits()` (line 215+, unassigned fallback)
- `backend/app/application/documents/review_payload_projector.py` — `_project_review_payload_to_canonical()` (line 82, higher-level entry)
- `backend/app/application/documents/_shared.py` — constants: `_VISIT_SCOPED_KEY_SET`, `_VISIT_GROUP_METADATA_KEYS`
- `backend/tests/unit/test_visit_segment_observations_actions.py` — reference for test style/conventions

## Verification
1. `python -m pytest backend/tests/unit/test_visit_scoping_regression.py -v` — all 6-7 tests pass
2. Coverage: `python -m pytest backend/tests/unit/test_visit_scoping_regression.py --cov=backend.app.application.documents.visit_scoping --cov-report=term-missing` — key branches hit
3. `scripts/ci/test-L3.ps1 -SkipDocker -SkipE2E` — green

## Decisions
- Tests go through `normalize_canonical_review_scoping` (not internal functions) — protects against refactoring
- Minimal fixtures, not full document payloads — tests are focused and fast
- No mocking of internal functions — these are integration-style regression tests at the module boundary
- Scope excludes segment_parser tests (already covered by existing test_visit_segment_observations_actions.py)

## Parallel notes
- No conflict with Plan A (hygiene pass) — this plan only imports public entry points that won't be renamed by Plan A
- If Plan A renames `_project_review_payload_to_canonical` → `project_review_payload_to_canonical`, update imports in this test file after merge
