# Plan: Iteration 11 — E2E expansion + Error UX + testing depth + DX hardening

> **Operational rules:** See [execution-rules.md](execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `improvement/iteration-11`
**PR:** #167 (single PR → `main`)
**Prerequisito:** Iteration 10 (#165) merged to `main`.

## Context

Post-Iter 10: 377 backend tests (90.41%), 266 frontend tests (85%), 5 E2E specs, 10 CI jobs green, 0 lint. The most impactful remaining gaps are:

1. **E2E coverage at 8%** of the full plan (5/61 specs) — every past iteration broke something visible (PdfViewer 3×, toolbar, blob URLs) that unit tests missed.
2. **Raw error messages** in toasts — backend errors shown verbatim to users.
3. **Zero performance baselines** — no P50/P95 latency evidence.
4. **Shallow failure-path coverage** — backend orchestrator, DB lock/retry untested.
5. **PdfViewer mock duplication** across 9 test files and scattered `os.getenv` reads.
6. **Monolithic repository** at 751 LOC spanning 4 aggregates.
7. **OpenAPI polish** — `/docs` works but lacks tags, error schemas, and health response model.

**Entry metrics:** 377 backend tests (90.41%), 266 frontend tests (85%), 5 E2E specs, 10 CI jobs, 0 lint.
**Exit metrics target:** ~20 E2E specs, error UX mapping live, P50/P95 benchmark suite, backend ~93% cov, frontend ~88% cov, repository split into 3 modules, OpenAPI tags + error schemas.

---

## Estado de ejecución — update on completion of each step

> **Protocolo "Continúa":** open a new chat, select the correct agent, attach this file and write `Continúa`. The agent reads the state, executes the next step, and stops on completion.

**Automation legend:**
- 🔄 **auto-chain** — Codex executes alone; you review the result *afterwards*.
- 🚧 **hard-gate** — Requires your decision before continuing. Do not skip.

### Fase 18 — Iteration 11

#### Phase A — Quick wins (warmup)

- [x] F18-A 🔄 — Centralize 2 debug `os.getenv` reads into `settings.py` (Codex)
- [x] F18-B 🔄 — Extract shared PdfViewer mock helper, deduplicate 9 test files (Codex)
- [x] F18-C 🔄 — OpenAPI polish: add route tags, error response schemas, health response model (Codex)

#### Phase B — E2E expansion (Phases 0 + 1 + 2 from E2E coverage plan)

> E2E prompts originally from the standalone E2E coverage expansion plan (now merged inline). Completed steps (F18-D→J) retain their original short prompts; pending steps (F18-K→N) have full prompts inlined below.

- [x] F18-D 🔄 — Add 17 missing `data-testid` attributes to UI components (Codex) → source: F17-A
- [x] F18-E 🔄 — Update `playwright.config.ts` with smoke/core/extended projects (Codex) → source: F17-B
- [x] F18-F 🔄 — Add npm scripts: `test:e2e:smoke`, `test:e2e:all` (Codex) → source: F17-C
- [x] F18-G 🔄 — Create reusable E2E helpers (`e2e/helpers.ts`) + fixture files (Codex) → source: F17-D
- [x] F18-H 🔄 — Verify green baseline: existing 5 tests pass (Codex) → source: F17-E
- [x] F18-I 🔄 — Refine `app-loads.spec.ts`: add `viewer-empty-state` assertion [A4] (Codex) → source: F17-F
- [x] F18-J 🔄 — Implement `pdf-viewer.spec.ts`: Tests 3–8 [D1,D3,D4,D6,D7,D9,D10–D13] (Codex) → source: F17-G
- [x] F18-K 🔄 — Implement `document-sidebar.spec.ts`: Tests 9–11 [B1,B2,B3,B6] (Codex) → source: F17-H
- [x] F18-L 🔄 — Implement `extracted-data.spec.ts`: Tests 12–14 [H1–H5,H7] (Codex) → source: F17-I
- [x] F18-M 🔄 — Refactor `edit-flow.spec.ts` → `field-editing.spec.ts`: Tests 15–17 [J1,J2,J9,J10,J15] (Codex) → source: F17-J
- [x] F18-N 🔄 — Refactor `mark-reviewed.spec.ts` → `review-workflow.spec.ts`: Tests 18–19 [K1–K5] (Codex) → source: F17-K

#### Phase C — Error UX + performance evidence

- [x] F18-O 🔄 — Error UX mapping: `errorCodeMap` + user-friendly toast messages (Codex)
- [x] F18-P 🔄 — Latency benchmarks: P50/P95 for upload, list, extract endpoints (Codex)

#### Phase D — Testing depth + architecture

- [x] F18-Q 🔄 — Backend failure-path tests: orchestrator partial failures + DB lock/retry (Codex)
- [x] F18-R 🔄 — SourcePanel + UploadDropzone test depth: branch coverage + interaction edge cases (Codex)
- [x] F18-S 🔄 — Split `sqlite_document_repository.py` by aggregate: documents, runs, calibration (Codex)

#### Phase E — Documentation refresh

- [x] F18-T 🚧 — DELIVERY_SUMMARY + TECHNICAL_DESIGN refresh for Iter 11 metrics (Claude)
- [x] F18-U 🚧 — FUTURE_IMPROVEMENTS refresh: mark completed items + update roadmap (Claude)

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.

---

### F18-A — Centralize debug `os.getenv` reads into `settings.py`

**Paso objetivo:** Move 2 remaining direct `os.getenv` calls from processing modules into the typed `Settings` dataclass, completing 12-Factor Factor III compliance.

**Prompt:**

**SCOPE BOUNDARY — F18-A**

**Branch:** `improvement/iteration-11` (create from `main` if it doesn't exist).

**Objective:** Eliminate all direct `os.getenv` calls outside `settings.py` and `config.py` by centralizing them in the `Settings` dataclass.

**Pre-flight context (do not re-discover — trust these facts):**
- `backend/app/settings.py` has a frozen `@dataclass` `Settings` with `@lru_cache` singleton via `get_settings()`. All env vars use `_getenv()` helper.
- `backend/app/application/processing/pdf_extraction.py` line ~48: reads `os.getenv("PDF_EXTRACTOR_FORCE")` at runtime using constant `PDF_EXTRACTOR_FORCE_ENV` from `constants.py`.
- `backend/app/application/processing/interpretation.py` line ~180: reads `os.getenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES")` using constant `INTERPRETATION_DEBUG_INCLUDE_CANDIDATES_ENV` from `constants.py`.

**Changes required:**

1. **`backend/app/settings.py`** — Add 2 new fields to the `Settings` dataclass:
   ```python
   pdf_extractor_force: str = _getenv("PDF_EXTRACTOR_FORCE", "")
   include_interpretation_candidates: bool = _getenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES", "") != ""
   ```

2. **`backend/app/application/processing/pdf_extraction.py`** — Replace the `os.getenv(PDF_EXTRACTOR_FORCE_ENV)` call with `get_settings().pdf_extractor_force`. Import `get_settings` from `backend.app.settings`. Remove `import os` if no longer needed.

3. **`backend/app/application/processing/interpretation.py`** — Replace the `os.getenv(INTERPRETATION_DEBUG_INCLUDE_CANDIDATES_ENV)` call with `get_settings().include_interpretation_candidates`. Import `get_settings`.

4. **`backend/app/application/processing/constants.py`** — Remove or comment out `PDF_EXTRACTOR_FORCE_ENV` and `INTERPRETATION_DEBUG_INCLUDE_CANDIDATES_ENV` if they are no longer referenced anywhere else.

**Validation:**
- `cd backend && python -m pytest tests/ -x -q --tb=short` → all pass.
- `grep -rn "os\.getenv" backend/app/ --include="*.py" | grep -v settings.py | grep -v config.py | grep -v __pycache__` → 0 results.

**Commit:** `refactor(plan-f18a): centralize debug env reads in Settings`

⚠️ AUTO-CHAIN → F18-B

---

### F18-B — Extract shared PdfViewer mock helper

**Paso objetivo:** Replace 9 duplicated `vi.mock("...PdfViewer", ...)` blocks with a single shared auto-mock, reducing maintenance overhead.

**Prompt:**

**SCOPE BOUNDARY — F18-B**

**Branch:** `improvement/iteration-11`

**Objective:** Create a Vitest auto-mock for PdfViewer and remove duplicated mock blocks from 9 test files.

**Pre-flight context:**
- 9 test files duplicate a `vi.mock("...PdfViewer", ...)` factory:
  - `frontend/src/App.test.tsx` (~L11)
  - `frontend/src/AppShellFlowsA.test.tsx` (~L11)
  - `frontend/src/AppShellFlowsB.test.tsx` (~L11)
  - `frontend/src/components/UploadPanel.test.tsx` (~L13)
  - `frontend/src/components/StructuredDataView.test.tsx` (~L17)
  - `frontend/src/components/StructuredDataViewConfidence.test.tsx` (~L17)
  - `frontend/src/components/ReviewWorkspace.test.tsx` (~L23)
  - `frontend/src/components/DocumentSidebar.test.tsx` (~L12)
  - `frontend/src/components/review/SourcePanelContent.test.tsx` (~L6)
- All use the same pattern: mock PdfViewer to return a simple `<div data-testid="pdf-viewer-mock" />`.

**Changes required:**

1. **Create `frontend/src/components/__mocks__/PdfViewer.tsx`** — Vitest auto-mock:
   ```tsx
   import { vi } from "vitest";

   const PdfViewer = vi.fn(() => <div data-testid="pdf-viewer-mock">PdfViewer Mock</div>);
   export default PdfViewer;
   ```

2. **Update all 9 test files:** Replace the `vi.mock("...PdfViewer", () => ({ ... }))` block with a simple `vi.mock("...PdfViewer")` call (no factory — Vitest resolves to `__mocks__/PdfViewer.tsx` automatically). Preserve the import path (relative to each test file). If the manual mock had named exports beyond default, include them in the `__mocks__` file.

3. **Verify the mock path resolution** works for each test. The `__mocks__` convention in Vitest resolves to sibling `__mocks__/<module>.tsx` relative to the mocked module, not the test.

**Validation:**
- `cd frontend && npx vitest run --reporter=verbose` → all pass, no regressions.
- Verify the `__mocks__/PdfViewer.tsx` file is picked up correctly.

**Commit:** `refactor(plan-f18b): extract shared PdfViewer auto-mock, deduplicate 9 test files`

⚠️ AUTO-CHAIN → F18-C

---

### F18-C — OpenAPI polish: tags, error schemas, health response model

**Paso objetivo:** Improve the auto-generated OpenAPI spec quality by adding route tags, error response models, and a health response schema. The `/docs` Swagger UI is already enabled.

**Prompt:**

**SCOPE BOUNDARY — F18-C**

**Branch:** `improvement/iteration-11`

**Objective:** Polish the existing OpenAPI spec so `/docs` is evaluator-ready with grouped endpoints, documented error responses, and complete response types.

**Pre-flight context:**
- FastAPI app in `backend/app/main.py` (~L136) has `title`, `description`, `version`.
- Route modules: `routes_documents.py`, `routes_review.py`, `routes_processing.py`, `routes_calibration.py`, `routes_health.py`.
- Most routes already have `response_model=...` set.
- Routes are registered via APIRouter in each module — tags can be set on the router itself.
- `routes_health.py` has no response model (returns `JSONResponse` directly).

**Changes required:**

1. **Add tags to each APIRouter** — In each `routes_*.py`, add `tags=["..."]` to the `APIRouter()` constructor:
   - `routes_documents.py`: `tags=["Documents"]`
   - `routes_review.py`: `tags=["Review"]`
   - `routes_processing.py`: `tags=["Processing"]`
   - `routes_calibration.py`: `tags=["Calibration"]`
   - `routes_health.py`: `tags=["Health"]`

2. **Add `HealthResponse` model** in `schemas.py`:
   ```python
   class HealthResponse(BaseModel):
       status: str = Field(description="Health status: 'healthy' or 'degraded'")
       database: str = Field(description="Database connectivity status")
       storage: str = Field(description="File storage status")
   ```
   Wire as `response_model=HealthResponse` on the health endpoint.

3. **Add `ErrorResponse` model** in `schemas.py`:
   ```python
   class ErrorResponse(BaseModel):
       detail: str = Field(description="Human-readable error message")
   ```
   Add `responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}` to upload and edit endpoints where validation errors are most common.

4. **Add endpoint descriptions** — Add `summary=` and `description=` to each route decorator where missing. Keep descriptions to one line.

**Validation:**
- `cd backend && python -m pytest tests/ -x -q --tb=short` → all pass.
- Start the backend locally and verify `http://localhost:8000/docs` renders with tags, error schemas, and health model.

**Commit:** `docs(plan-f18c): OpenAPI polish — tags, error schemas, health response model`

⚠️ AUTO-CHAIN → F18-D

---

### F18-D — Add missing `data-testid` attributes

**Paso objetivo:** Add 17 `data-testid` attributes to 4 component files so E2E tests have stable selectors.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-A, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-E

---

### F18-E — Update Playwright config with projects

**Paso objetivo:** Configure `playwright.config.ts` with smoke/core/extended project groups.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-B, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-F

---

### F18-F — Add npm scripts for E2E

**Paso objetivo:** Add npm scripts `test:e2e:smoke`, `test:e2e:all`.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-C, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-G

---

### F18-G — Create reusable E2E helpers + fixtures

**Paso objetivo:** Create `e2e/helpers.ts` with reusable E2E utilities and fixture files.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-D, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-H

---

### F18-H — Verify green baseline

**Paso objetivo:** Verify all existing 5 E2E tests pass on the current branch.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-E, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-I

---

### F18-I — Refine P0 smoke: `app-loads.spec.ts`

**Paso objetivo:** Add `viewer-empty-state` assertion to complete A4 coverage.

**Prompt:** _(Originally from E2E coverage expansion plan § F17-F, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-J

---

### F18-J — Implement `pdf-viewer.spec.ts`

**Paso objetivo:** Implement Tests 3–8 covering PDF viewer interactions [D1,D3,D4,D6,D7,D9,D10–D13].

**Prompt:** _(Originally from E2E coverage expansion plan § F17-G, now merged inline. Step completed.)_

⚠️ AUTO-CHAIN → F18-K

---

### F18-K — Implement `document-sidebar.spec.ts`

**Paso objetivo:** Implement Tests 9–11 covering sidebar document list [B1,B2,B3,B6].

**Prompt:**

**SCOPE BOUNDARY — F18-K**

**Branch:** `improvement/iteration-11`

**Objective:** Create `frontend/e2e/document-sidebar.spec.ts` with 3 tests.

**Tests to implement:**
- Test 9: Document list shows groups "Para revisar" / "Revisados"
- Test 10: Selecting a document marks it active (`aria-pressed`, `aria-current`, PDF loads)
- Test 11: Each document shows its status chip

**Validation:**
- `cd frontend && npm run test:e2e` → includes these new tests (core project)

**Commit:** `feat(plan-f18k): add document-sidebar E2E tests (3 tests)`

⚠️ AUTO-CHAIN → F18-L

---

### F18-L — Implement `extracted-data.spec.ts`

**Paso objetivo:** Implement Tests 12–14 covering structured data extraction view [H1–H5,H7].

**Prompt:**

**SCOPE BOUNDARY — F18-L**

**Branch:** `improvement/iteration-11`

**Objective:** Create `frontend/e2e/extracted-data.spec.ts` with 3 tests. Uses real backend — upload PDF, wait for processing to complete.

**Tests to implement:**
- Test 12: Panel shows sections with headers ("Datos extraídos", section titles)
- Test 13: Fields show formatted values; missing fields show "—"
- Test 14: Confidence indicators visible; field count summary in toolbar

**Validation:**
- `cd frontend && npx playwright test extracted-data.spec.ts --project=core` → 3 tests pass

**Commit:** `feat(plan-f18l): add extracted-data E2E tests (3 tests)`

⚠️ AUTO-CHAIN → F18-M

---

### F18-M — Refactor `edit-flow.spec.ts` → `field-editing.spec.ts`

**Paso objetivo:** Refactor and expand edit flow spec into field-editing with Tests 15–17 [J1,J2,J9,J10,J15].

**Prompt:**

**SCOPE BOUNDARY — F18-M**

**Branch:** `improvement/iteration-11`

**Objective:** Rename `frontend/e2e/edit-flow.spec.ts` to `frontend/e2e/field-editing.spec.ts`. Split the single test into 3 focused tests using shared setup. Import `buildMockReviewPayload` and `buildMockDocumentPayload` from helpers.

**Tests to implement:**
- Test 15: Click on field opens edit dialog (verify dialog title, input pre-populated)
- Test 16: Edit value + save → dialog closes, value updated, toast shown
- Test 17: Cancel edit → dialog closes, value unchanged

**Validation:**
- `cd frontend && npx playwright test field-editing.spec.ts --project=core` → 3 tests pass

**Commit:** `feat(plan-f18m): refactor edit-flow into field-editing spec (3 tests)`

⚠️ AUTO-CHAIN → F18-N

---

### F18-N — Refactor `mark-reviewed.spec.ts` → `review-workflow.spec.ts`

**Paso objetivo:** Refactor and expand review spec into review-workflow with Tests 18–19 [K1–K5].

**Prompt:**

**SCOPE BOUNDARY — F18-N**

**Branch:** `improvement/iteration-11`

**Objective:** Rename `frontend/e2e/mark-reviewed.spec.ts` to `frontend/e2e/review-workflow.spec.ts`. Split into 2 tests.

**Tests to implement:**
- Test 18: Mark as reviewed → button changes to "Reabrir", document moves to "Revisados" group
- Test 19: Reopen → button changes to "Marcar revisado", document moves to "Para revisar" group

**Validation:**
- `cd frontend && npx playwright test review-workflow.spec.ts --project=core` → 2 tests pass

**Commit:** `feat(plan-f18n): refactor mark-reviewed into review-workflow spec (2 tests)`

⚠️ AUTO-CHAIN → F18-O

---

### F18-O — Error UX mapping: `errorCodeMap` + user-friendly toasts

**Paso objetivo:** Replace raw HTTP error messages in toasts with user-friendly, localized copy via a centralized error code mapping.

**Prompt:**

**SCOPE BOUNDARY — F18-O**

**Branch:** `improvement/iteration-11`

**Objective:** Create a frontend error-code-to-user-message mapping system and wire it into the existing toast infrastructure so users never see raw error text.

**Pre-flight context:**
- Toast system: `frontend/src/components/toast/ToastHost.tsx` + `toast-types.ts` with `UploadFeedback` (success/error) and `ActionFeedback` (success/error/info).
- API error handling centralized in `frontend/src/api/documentApi.ts` — 11 `catch` blocks, each extracting `error.message` and passing it to callbacks.
- Hooks consume toasts: `useUploadState.ts`, `useFieldEditing.ts`, `useReviewedEditBlocker.ts`, `useRawTextActions.ts`.
- Backend returns standard HTTP errors (`400`, `404`, `422`, `429`, `500`) with `{"detail": "..."}` format.

**Changes required:**

1. **Create `frontend/src/lib/errorMessages.ts`**:
   ```typescript
   /** Maps known backend error patterns to user-friendly messages. */
   const errorPatterns: Array<{ pattern: RegExp; message: string }> = [
     { pattern: /rate.?limit|too many/i, message: "Demasiadas solicitudes. Intenta de nuevo en unos segundos." },
     { pattern: /file.*too large|size.*exceed/i, message: "El archivo es demasiado grande. El límite es 50 MB." },
     { pattern: /invalid.*uuid|not.*valid.*id/i, message: "Identificador de documento inválido." },
     { pattern: /not found|404/i, message: "Documento no encontrado." },
     { pattern: /unsupported.*type|invalid.*file/i, message: "Tipo de archivo no soportado. Solo se aceptan PDFs." },
     { pattern: /processing.*failed|extraction.*error/i, message: "Error durante el procesamiento. Intenta reprocesar el documento." },
     { pattern: /network|fetch|aborted|timeout/i, message: "Error de conexión. Verifica tu conexión a internet." },
     { pattern: /server.*error|500|internal/i, message: "Error del servidor. Intenta de nuevo más tarde." },
   ];

   export function getUserFriendlyError(rawError: string): string {
     for (const { pattern, message } of errorPatterns) {
       if (pattern.test(rawError)) return message;
     }
     return "Ocurrió un error inesperado. Intenta de nuevo.";
   }
   ```

2. **Create `frontend/src/lib/__tests__/errorMessages.test.ts`** — Test each pattern match + fallback case. At least 10 test cases.

3. **Wire into `documentApi.ts`** — Import `getUserFriendlyError` and wrap error messages in each `catch` block before passing to callbacks:
   ```typescript
   } catch (err) {
     const raw = err instanceof Error ? err.message : String(err);
     onError?.(getUserFriendlyError(raw));
   }
   ```
   Apply to all 11 catch blocks.

4. **Verify toast rendering** — Existing toast components receive the already-mapped friendly string. No changes needed in ToastHost or toast-types.

**Validation:**
- `cd frontend && npx vitest run src/lib/__tests__/errorMessages.test.ts` → all pattern tests pass.
- `cd frontend && npm run lint` → 0 errors.
- Manual: start app, trigger a 429 (rapid uploads) → verify friendly toast text.

**Commit:** `feat(plan-f18o): error UX mapping — user-friendly toast messages`

⚠️ AUTO-CHAIN → F18-P

---

### F18-P — Latency benchmarks: P50/P95 for key endpoints

**Paso objetivo:** Create a reproducible benchmark suite measuring P50/P95 latencies for the three most-used API endpoints, providing quantitative performance evidence.

**Prompt:**

**SCOPE BOUNDARY — F18-P**

**Branch:** `improvement/iteration-11`

**Objective:** Add a `pytest-benchmark` suite that measures latency for upload, list, and document-detail endpoints. Results must be reproducible and documented.

**Pre-flight context:**
- Backend test infrastructure: `pytest` with `httpx.AsyncClient` or `TestClient`.
- Key endpoints: `POST /api/documents/upload`, `GET /api/documents`, `GET /api/documents/{id}`.
- No benchmark suite exists. `metrics/llm_benchmarks/` exists for LLM evaluation.
- `requirements-dev.txt` has dev dependencies.

**Changes required:**

1. **Add `pytest-benchmark` to `requirements-dev.txt`** (if not already present).

2. **Create `backend/tests/benchmarks/` directory** with `__init__.py`.

3. **Create `backend/tests/benchmarks/test_endpoint_latency.py`**:
   - Use `pytest-benchmark` fixtures for warm measurements.
   - Test functions:
     - `test_list_documents_latency` — `GET /api/documents` (empty DB + with 5 seeded docs).
     - `test_get_document_latency` — `GET /api/documents/{id}` with a seeded document.
     - `test_upload_latency` — `POST /api/documents/upload` with a small fixture PDF.
     - `test_health_latency` — `GET /api/health` (baseline).
   - Each benchmark runs 10 rounds minimum.
   - Assert P95 < 500ms for reads, P95 < 2000ms for upload (conservative targets for CI).

4. **Create `backend/tests/benchmarks/conftest.py`** — Fixture that provides a test client with a seeded SQLite in-memory DB and a small PDF file.

5. **Add benchmark run script** — Add to `pytest.ini` a marker: `markers = benchmark: latency benchmarks`. Add npm/pip script or document the run command: `cd backend && python -m pytest tests/benchmarks/ -v --benchmark-only`.

6. **Document in `docs/projects/veterinary-medical-records/testing/`** — Create or update a brief section noting benchmark existence and how to run them.

**Validation:**
- `cd backend && python -m pytest tests/benchmarks/ -v --benchmark-enable` → all pass with P50/P95 output.

**Commit:** `perf(plan-f18p): add endpoint latency benchmarks P50/P95`

⚠️ AUTO-CHAIN → F18-Q

---

### F18-Q — Backend failure-path tests: orchestrator + DB lock/retry

**Paso objetivo:** Add tests for critical failure paths in the processing orchestrator and database layer that are currently untested, improving reliability coverage.

**Prompt:**

**SCOPE BOUNDARY — F18-Q**

**Branch:** `improvement/iteration-11`

**Objective:** Cover failure paths in orchestrator and DB layer to push backend coverage from ~90.4% toward ~93%.

**Pre-flight context:**
- `backend/app/application/processing/orchestrator.py` — orchestrates multi-step document processing. Failure paths (partial extraction failure, timeout, corrupt PDF) have low or zero coverage.
- `backend/app/infra/sqlite_document_repository.py` — uses `PRAGMA busy_timeout=5000` and WAL mode. Lock contention and retry behavior untested.
- `backend/app/application/processing/processing_runner.py` — runs processing steps. Error propagation paths untested.
- Current backend coverage: 90.41%.

**Changes required:**

1. **Create `backend/tests/test_orchestrator_failures.py`**:
   - Test: extraction raises `Exception` → run marked as `failed`, document status updated.
   - Test: PDF parsing returns empty/None → graceful degradation, step artifacts still created.
   - Test: timeout simulation (mock long-running step) → appropriate cleanup.
   - Test: partial success (step 1 OK, step 2 fails) → prior artifacts preserved, run status reflects failure.
   - Use `unittest.mock.patch` to inject failures at specific processing stages.

2. **Create `backend/tests/test_db_resilience.py`**:
   - Test: concurrent writes to same document → WAL handles without crash, data consistent.
   - Test: busy timeout exceeded (mock `sqlite3.OperationalError: database is locked`) → appropriate error raised/retry.
   - Test: corrupt/missing DB file → clear error, not silent failure.
   - Test: schema migration on existing DB → `ensure_schema()` is idempotent.

3. **Extend `backend/tests/test_processing_runner.py`** (if exists) or create:
   - Test: runner handles `KeyError` in field mapping → logs error, doesn't crash run.
   - Test: runner with empty PDF content → produces meaningful error artifact.

**Validation:**
- `cd backend && python -m pytest tests/test_orchestrator_failures.py tests/test_db_resilience.py -x -q --tb=short` → all pass.

**Commit:** `test(plan-f18q): backend failure-path tests — orchestrator + DB resilience`

⚠️ AUTO-CHAIN → F18-R

---

### F18-R — SourcePanel + UploadDropzone test depth

**Paso objetivo:** Deepen test coverage for SourcePanel and UploadDropzone components, focusing on branch coverage and interaction edge cases.

**Prompt:**

**SCOPE BOUNDARY — F18-R**

**Branch:** `improvement/iteration-11`

**Objective:** Increase branch/line coverage for SourcePanel and UploadDropzone components by testing interaction edge cases and state transitions.

**Pre-flight context:**
- `frontend/src/components/SourcePanel.tsx` — test file exists at `SourcePanel.test.tsx`.
- `frontend/src/components/UploadDropzone.tsx` — test file exists at `UploadDropzone.test.tsx`.
- `frontend/src/hooks/useSourcePanelState.ts` — test file exists.
- `frontend/src/hooks/useUploadState.ts` — test file exists.
- Current frontend coverage: 85%. Target: ≥87%.

**Changes required:**

1. **Extend `frontend/src/components/SourcePanel.test.tsx`** — Add tests for:
   - Tab switching between document view and raw text.
   - Empty state rendering (no document selected).
   - Loading state rendering.
   - Error state when PDF fails to load.
   - Panel resize interactions (if applicable).

2. **Extend `frontend/src/components/UploadDropzone.test.tsx`** — Add tests for:
   - Drag-and-drop file event handling (dragenter, dragleave, drop).
   - Multiple file upload attempt → only PDFs accepted.
   - File size validation (reject files > limit).
   - Upload in-progress state (button disabled, spinner visible).
   - Upload error state → error message displayed.
   - Upload success → callback invoked with document data.

3. **Extend hook tests** (`useSourcePanelState.test.ts`, `useUploadState.test.ts`) — Cover edge cases:
   - Rapid state toggles.
   - Error recovery paths.
   - Unmount during async operations.

**Validation:**
- `cd frontend && npx vitest run src/components/SourcePanel.test.tsx src/components/UploadDropzone.test.tsx --reporter=verbose` → all pass.
- `cd frontend && npm run lint` → 0 errors.

**Commit:** `test(plan-f18r): deepen SourcePanel + UploadDropzone coverage`

⚠️ AUTO-CHAIN → F18-S

---

### F18-S — Split `sqlite_document_repository.py` by aggregate

**Paso objetivo:** Decompose the monolithic 751 LOC repository into 3 focused modules aligned with domain aggregates, improving cohesion and testability.

**Prompt:**

**SCOPE BOUNDARY — F18-S**

**Branch:** `improvement/iteration-11`

**Objective:** Split `sqlite_document_repository.py` into 3 aggregate-focused repositories while maintaining the existing public API via a re-exporting facade.

**Pre-flight context:**
- `backend/app/infra/sqlite_document_repository.py`: 751 LOC, single class `SqliteDocumentRepository`.
- `backend/app/ports/document_repository.py`: single `DocumentRepository` Protocol with ~20 methods.
- Methods group into 4 aggregates:
  - **Documents:** `create`, `get`, `list_documents`, `count_documents`, `update_review_status`
  - **Runs + Artifacts:** `create_processing_run`, `list_queued_runs`, `try_start_run`, `complete_run`, `recover_orphaned_runs`, `get_latest_run`, `get_run`, `get_latest_completed_run`, `list_processing_runs`, `list_step_artifacts`, `append_artifact`, `get_latest_artifact_payload`
  - **Calibration:** `increment_calibration_signal`, `apply_calibration_deltas`, `get_calibration_counts`, `get_latest_applied_calibration_snapshot`
- Composition root in `main.py` wires `SqliteDocumentRepository`.

**Changes required:**

1. **Split protocol** — Create 3 protocol files under `backend/app/ports/`:
   - `document_repository.py` → keep only Document CRUD methods.
   - `run_repository.py` → Run + Artifact methods.
   - `calibration_repository.py` → Calibration methods.
   - Keep existing `document_repository.py` as backward-compatible re-export (imports from the 3 sub-protocols for any code still importing the unified protocol).

2. **Split implementation** — Create 3 implementation files under `backend/app/infra/`:
   - `sqlite_document_repo.py` → Document CRUD (~200 LOC).
   - `sqlite_run_repo.py` → Runs + Artifacts (~350 LOC).
   - `sqlite_calibration_repo.py` → Calibration (~150 LOC).
   - All share the same DB connection (passed via constructor `db_path`). Each handles its own table operations.
   - Keep existing `sqlite_document_repository.py` as a thin facade that composes the 3 sub-repos and delegates, implementing the unified protocol for backward compatibility.

3. **Update composition root** — In `main.py`, wire the 3 sub-repos if consumers accept them directly, or wire the facade. Prefer minimal disruption — use facade initially.

4. **Update imports in consumers** — If any service or route imports `SqliteDocumentRepository` directly (beyond main.py), update to use protocol types.

5. **Add/update tests** — Ensure existing repo tests cover each sub-repo independently. Add at least one test per sub-repo verifying isolated construction.

**Validation:**
- `cd backend && python -m pytest tests/test_document_repo.py tests/test_run_repo.py tests/test_calibration_repo.py -x -q --tb=short` → all pass (adjust file names to actual test files).
- `(Get-Content backend/app/infra/sqlite_document_repo.py).Count` + similar → each < 400 LOC.

**Commit:** `refactor(plan-f18s): split sqlite_document_repository by aggregate`

⚠️ AUTO-CHAIN → F18-T (different agent — HANDOFF to Claude)

---

### F18-T — DELIVERY_SUMMARY + TECHNICAL_DESIGN refresh (Claude)

**Paso objetivo:** Update delivery and technical design documentation to reflect Iteration 11 outcomes.

**Prompt:**

**SCOPE BOUNDARY — F18-T**

**Branch:** `improvement/iteration-11`

**Objective:** Refresh delivery-summary.md and technical-design.md with Iter 11 metrics, new capabilities (error UX, benchmarks, repo split), and updated known limitations.

**Changes required:**

1. **delivery-summary.md** — Update metrics table:
   - Backend tests, frontend tests, E2E specs, coverage numbers.
   - Add new capabilities: error UX mapping, latency benchmarks, OpenAPI tags, repository split.
   - Add Iter 11 PR reference.

2. **technical-design.md §14** — Update known limitations:
   - Mark "SQLite repository monolith" as resolved (split into 3 aggregates).
   - Update AppWorkspace LOC if changed.
   - Add benchmark results summary.
   - Note error UX mapping system in frontend architecture section.

**Validation:**
- Read both files and verify accuracy against actual metrics.
- No broken internal links.

**Commit:** `docs(plan-f18t): DELIVERY_SUMMARY + TECHNICAL_DESIGN refresh for Iter 11`

⚠️ AUTO-CHAIN → F18-U

---

### F18-U — FUTURE_IMPROVEMENTS refresh (Claude)

**Paso objetivo:** Update future-improvements.md to mark completed items and refresh the roadmap.

**Prompt:**

**SCOPE BOUNDARY — F18-U**

**Branch:** `improvement/iteration-11`

**Objective:** Mark Iter 11 completed items in future-improvements.md and update effort/priority for remaining items.

**Changes required:**

1. **Mark as done:**
   - #3 (centralize env reads) — ✅ Done (Iteration 11, F18-A)
   - #5 (AddFieldDialog + source panel tests) — ✅ Done (Iteration 11, F18-R) if covered
   - #10 (backend failure-path tests) — ✅ Done (Iteration 11, F18-Q)
   - #11 (SourcePanel + UploadDropzone suites) — ✅ Done (Iteration 11, F18-R)
   - #12 (centralize PdfViewer mock) — ✅ Done (Iteration 11, F18-B)
   - #13 (repository split) — ✅ Done (Iteration 11, F18-S)
   - #19 (latency benchmarks) — ✅ Done (Iteration 11, F18-P)
   - #20 (error UX mapping) — ✅ Done (Iteration 11, F18-O)
   - #22 (OpenAPI polish) — ✅ Done (Iteration 11, F18-C)

2. **Update remaining items** — Adjust priorities/effort based on what Iter 11 unblocked or changed.

3. **Add E2E progress note** — Note E2E expansion from 5→~20 specs (Iter 11). Remaining: Phase 3 extended (46 tests) deferred.

**Validation:**
- Verify no broken links.
- Cross-check completed items match actual plan execution.

**Commit:** `docs(plan-f18u): FUTURE_IMPROVEMENTS refresh — mark 9 items complete`

✅ **Todos los pasos completados.**
