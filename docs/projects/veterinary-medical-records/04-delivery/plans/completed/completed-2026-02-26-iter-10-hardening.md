# Plan: Iteration 10 — Security, resilience & performance hardening

> **Operational rules:** See [execution-rules.md](execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `improvement/iteration-10-hardening`
**PR:** #165 (single PR → `main`)
**Prerequisito:** Iteration 9 (E2E) merged to `main`.

## Context

Post-Iter 9: E2E tests in CI, backend 90%, frontend 85%. The most impactful remaining gaps are security (zero rate limiting, no audit scanning, no UUID validation), resilience (no React Error Boundary — a render error crashes the entire app), and performance (no DB indexes on FK columns, no cache headers, no code splitting). All items have high ROI-to-effort ratio and are directly visible to a technical evaluator.

**Entry metrics (expected post-Iter 9):** 372+ backend tests (90%), 263+ frontend tests (85%), 4+ E2E tests, 0 lint, 9 CI jobs green.

---

## Estado de ejecución — update on completion of each step

> **Protocolo "Continúa":** open a new chat, select the correct agent, attach this file and write `Continúa`. The agent reads the state, executes the next step, and stops on completion.

**Automation legend:**
- 🔄 **auto-chain** — Codex executes alone; you review the result *afterwards*.
- 🚧 **hard-gate** — Requires your decision before continuing. Do not skip.

### Fase 16 — Iteration 10 (Security, resilience & performance hardening)

- [x] F16-A 🔄 — Database indexes: add indexes on `processing_runs(document_id)`, `document_status_history(document_id)`, `artifacts(run_id)`, `artifacts(run_id, artifact_type)` (Codex)
- [x] F16-B 🔄 — UUID validation: add `document_id` path parameter validation on all routes (Codex)
- [x] F16-C 🔄 — React Error Boundary: add global error boundary wrapping the app tree (Codex)
- [x] F16-D 🔄 — Rate limiting: add `slowapi` middleware to protect upload and extraction endpoints (Codex)
- [x] F16-E 🔄 — Coverage thresholds: enforce `--cov-fail-under=85` in pytest and vitest coverage config (Codex)
- [x] F16-F 🔄 — Security audit in CI: add `pip-audit` and `npm audit` steps to CI workflow (Codex)
- [x] F16-G 🔄 — nginx cache headers: add `Cache-Control` for static assets + `Strict-Transport-Security` header (Codex)
- [x] F16-H 🔄 — PdfViewer lazy loading: `React.lazy` + `Suspense` for PdfViewer component (Codex)
- [x] F16-I 🔄 — Deep health check: verify DB connectivity + storage in `/health` endpoint (Codex)
- [x] F16-J 🔄 — Fix duplicate `@playwright/test` in package.json (Codex)
- [x] F16-K 🚧 — delivery-summary.md + technical-design.md refresh for Iter 9-10 (Claude)
- [x] F16-L 🚧 — future-improvements.md refresh + smoke test (Claude)

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.

---

### F16-A — Database indexes

**Paso objetivo:** Add missing secondary indexes to improve query performance on FK columns.

**Prompt:**

**SCOPE BOUNDARY — F16-A**

**Branch:** `improvement/iteration-10-hardening` (create from `main` if it doesn't exist).

**Objective:** Add indexes on frequently-queried FK columns that currently have no index.

**Pre-flight context (do not re-discover — trust these facts):**
- `backend/app/infra/database.py` contains schema creation functions.
- The only existing secondary index is `idx_calibration_aggregates_lookup` on `calibration_aggregates`.
- `processing_runs.document_id` is used in WHERE clauses (e.g., `sqlite_document_repository.py` L208).
- `document_status_history.document_id` is used in WHERE clauses (L295).
- `artifacts.run_id` is used in WHERE clauses (L290, L326).
- `artifacts(run_id, artifact_type)` compound is used in WHERE clauses (L460, L518).

**Changes required:**

1. In `backend/app/infra/database.py`, in the function `_ensure_processing_runs_schema(cur)`, add after the CREATE TABLE statement:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_processing_runs_document_id ON processing_runs (document_id);
   ```

2. In `_ensure_status_history_schema(cur)`, add after the CREATE TABLE:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_document_status_history_document_id ON document_status_history (document_id);
   ```

3. In `_ensure_artifacts_schema(cur)`, add after the CREATE TABLE:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON artifacts (run_id);
   CREATE INDEX IF NOT EXISTS idx_artifacts_run_id_type ON artifacts (run_id, artifact_type);
   ```

**Validation:**
- `cd backend && python -m pytest tests/ -v` → all pass.
- Verify with a quick script or test that `ensure_schema()` runs without errors on a fresh DB.

**Commit:** `perf(plan-f16a): add database indexes on FK columns`

⚠️ AUTO-CHAIN → F16-B

---

### F16-B — UUID validation on document_id

**Paso objetivo:** Add type-safe UUID validation to all route path parameters.

**Prompt:**

**SCOPE BOUNDARY — F16-B**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Replace `document_id: str` with proper UUID validation on all API routes.

**Pre-flight context:**
- Routes in `backend/app/api/routes_documents.py` accept `document_id: str` with no validation (lines ~125, ~180, ~240, and others).
- Routes in `backend/app/api/routes_review.py` also take `document_id: str`.
- FastAPI supports `from uuid import UUID` as a path type — if `document_id` is not a valid UUID, FastAPI auto-returns 422.
- The domain uses UUID strings consistently (generated via `uuid.uuid4()`).

**Changes required:**

1. In `routes_documents.py`, change all `document_id: str` path parameters to `document_id: str` but add a Pydantic `Path` constraint with regex validation:
   ```python
   from fastapi import Path
   
   document_id: str = Path(..., pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
   ```
   Apply this to every route that has `document_id` as a path parameter.

2. Do the same in `routes_review.py` for all `document_id` path params.

3. Also apply to `run_id` path parameters if any exist — they are also UUIDs.

**Guardrails:**
- Do NOT change the internal type to `UUID` — keep as `str` to avoid breaking the repository/domain layer. Only add validation at the API boundary.
- If existing tests pass `document_id` as a non-UUID string, update those tests to use valid UUIDs.

**Validation:**
- `cd backend && python -m pytest tests/ -v` → all pass.
- Manually verify: a request with `document_id=../etc/passwd` would now return 422 instead of hitting the DB.

**Commit:** `sec(plan-f16b): add UUID validation on document_id path params`

⚠️ AUTO-CHAIN → F16-C

---

### F16-C — React Error Boundary

**Paso objetivo:** Add a global React Error Boundary to prevent full app crash on render errors.

**Prompt:**

**SCOPE BOUNDARY — F16-C**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Create a React Error Boundary component and wrap the app tree with it.

**Pre-flight context:**
- Currently zero Error Boundary in the frontend. An error in any component crashes the entire app to a white screen.
- App mount: `main.tsx` → `StrictMode` → `QueryClientProvider` → `TooltipProvider` → `App` → `ReviewWorkspace`.
- The project uses shadcn/ui components with Tailwind CSS.

**Changes required:**

1. **Create `frontend/src/components/ErrorBoundary.tsx`:**
   - A class component implementing `componentDidCatch` and `getDerivedStateFromError`.
   - On error: render a centered recovery UI with:
     - Error icon or emoji
     - Heading: "Algo salió mal"
     - Description: "Se produjo un error inesperado. Intenta recargar la página."
     - A "Recargar página" button that calls `window.location.reload()`
     - A collapsible "Detalles técnicos" section showing `error.message` and `error.stack` (collapsed by default)
   - Style with existing Tailwind utility classes. Match the app's design (dark-friendly, centered, clean).
   - Export as default and named export.

2. **Create `frontend/src/components/ErrorBoundary.test.tsx`:**
   - Test: renders children when no error.
   - Test: renders fallback UI when a child throws during render.
   - Test: "Recargar" button calls `window.location.reload`.
   - Use vitest + @testing-library/react.

3. **Wrap in `frontend/src/main.tsx`:**
   - Import `ErrorBoundary`.
   - Wrap around `<App />` (inside `QueryClientProvider` but outside `TooltipProvider`):
     ```tsx
     <QueryClientProvider client={queryClient}>
       <ErrorBoundary>
         <TooltipProvider>
           <App />
         </TooltipProvider>
       </ErrorBoundary>
     </QueryClientProvider>
     ```

**Validation:**
- `cd frontend && npm test` → all existing + new tests pass.
- `cd frontend && npx tsc --noEmit` → no type errors.

**Commit:** `feat(plan-f16c): add global React Error Boundary`

⚠️ AUTO-CHAIN → F16-D

---

### F16-D — Rate limiting with slowapi

**Paso objetivo:** Add rate limiting middleware to protect critical API endpoints.

**Prompt:**

**SCOPE BOUNDARY — F16-D**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Install `slowapi` and add rate limiting to upload and extraction-heavy endpoints.

**Pre-flight context:**
- Currently zero rate limiting on any endpoint.
- `backend/requirements.txt` has `fastapi==0.115.14`, `uvicorn==0.34.0`.
- The app is created in `backend/app/main.py` via `create_app()`.
- Critical endpoints: `POST /documents/upload` (file upload, CPU-intensive), `GET /documents/{id}/review` (data-heavy query).

**Changes required:**

1. **Add `slowapi` to `backend/requirements.txt`:**
   ```
   slowapi==0.1.9
   ```

2. **Configure rate limiter in `backend/app/main.py`:**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   ```
   - Add `app.state.limiter = limiter` after `app = FastAPI(...)`.
   - Add `app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)`.

3. **Apply rate limits to critical routes:**
   - `POST /documents/upload`: `@limiter.limit("10/minute")` — max 10 uploads per minute per IP.
   - `GET /documents/{id}/download`: `@limiter.limit("30/minute")` — max 30 downloads per minute per IP.
   - All other routes: no explicit limit (reasonable default).
   - Pass `request: Request` to decorated endpoints if not already present.

4. **Add rate limit configuration to `backend/app/config.py` or settings:**
   - Make limits configurable via env var `VET_RECORDS_RATE_LIMIT_UPLOAD` (default: `"10/minute"`).
   - Make limits configurable via env var `VET_RECORDS_RATE_LIMIT_DOWNLOAD` (default: `"30/minute"`).

5. **Add basic test in `backend/tests/test_rate_limiting.py`:**
   - Test that the limiter is configured on the app.
   - Test that exceeding the limit returns 429.

**Guardrails:**
- Rate limiting should be disabled in test mode or configurable. Check if there's a test settings override — if so, set generous limits for tests.
- Do NOT add limits to `/health` or `/version` endpoints.

**Validation:**
- `cd backend && python -m pytest tests/ -v` → all pass.
- `pip install slowapi==0.1.9` succeeds.

**Commit:** `sec(plan-f16d): add rate limiting with slowapi`

⚠️ AUTO-CHAIN → F16-E

---

### F16-E — Coverage thresholds in CI

**Paso objetivo:** Enforce minimum coverage thresholds so CI fails if coverage drops.

**Prompt:**

**SCOPE BOUNDARY — F16-E**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Add `--cov-fail-under` to pytest and coverage `thresholds` to vitest so CI gates on coverage regression.

**Pre-flight context:**
- Backend: `pytest.ini` has `addopts = --cov=backend/app --cov-report=term-missing` — no fail-under.
- Frontend: `vite.config.ts` has `coverage: { provider: "v8", reporter: ["text", "lcov"] }` — no thresholds.
- Current coverage: backend ~90%, frontend ~85%.

**Changes required:**

1. **`pytest.ini`**: Change `addopts` line to add `--cov-fail-under=85`:
   ```ini
   addopts = --cov=backend/app --cov-report=term-missing --cov-fail-under=85
   ```
   (Set to 85, not 90 — leaves room for new modules that start low.)

2. **`frontend/vite.config.ts`**: Add `thresholds` to the coverage config:
   ```ts
   coverage: {
     provider: "v8",
     reporter: ["text", "lcov"],
     reportsDirectory: "./coverage",
     thresholds: {
       lines: 80,
       functions: 80,
       branches: 70,
       statements: 80,
     },
   },
   ```
   (Set to 80/80/70/80 — slightly below current to avoid flakiness while protecting against major drops.)

**Validation:**
- `cd backend && python -m pytest tests/ -v` → passes (coverage currently ~90% > 85%).
- `cd frontend && npm run test:coverage` → passes (coverage currently ~85% > 80%).
- Verify that if you temporarily set threshold to 99%, the tests fail (proving the gate works). Revert after.

**Commit:** `ci(plan-f16e): enforce coverage thresholds in pytest and vitest`

⚠️ AUTO-CHAIN → F16-F

---

### F16-F — Security audit in CI

**Paso objetivo:** Add `pip-audit` and `npm audit` to CI pipeline.

**Prompt:**

**SCOPE BOUNDARY — F16-F**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Add security dependency scanning to the CI workflow.

**Pre-flight context:**
- `.github/workflows/ci.yml` has no audit steps.
- `requirements-dev.txt` has no audit tools.
- The `quality` job runs Python linting; the `frontend_test_build` job runs frontend checks.

**Changes required:**

1. **Add `pip-audit` to `requirements-dev.txt`:**
   ```
   pip-audit==2.7.3
   ```

2. **Add audit step to `quality` job** in `.github/workflows/ci.yml`, after the pytest step:
   ```yaml
   - name: Security audit (pip-audit)
     run: pip-audit --requirement backend/requirements.txt --strict
   ```

3. **Add audit step to `frontend_test_build` job**, after the build step:
   ```yaml
   - name: Security audit (npm audit)
     run: npm --prefix frontend audit --audit-level=high
     continue-on-error: true
   ```
   Use `continue-on-error: true` for npm audit initially — npm audit is noisy and may flag transitive deps that can't be fixed immediately. The step still reports findings visibly. For pip-audit, use `--strict` to fail on known vulnerabilities.

**Guardrails:**
- If `pip-audit` fails on a known advisory with no fix available, add it to `--ignore-vuln` with a comment explaining why.
- If `npm audit` has too many false positives, keep `continue-on-error: true` but ensure the step is visible in CI output.

**Validation:**
- Run `pip-audit --requirement backend/requirements.txt --strict` locally → verify it passes or identify advisories to ignore.
- Run `npm --prefix frontend audit --audit-level=high` locally → note output.

**Commit:** `ci(plan-f16f): add pip-audit and npm audit to CI`

⚠️ AUTO-CHAIN → F16-G

---

### F16-G — nginx cache headers + HSTS

**Paso objetivo:** Add proper cache headers for static assets and HSTS.

**Prompt:**

**SCOPE BOUNDARY — F16-G**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Add `Cache-Control` for hashed static assets and `Strict-Transport-Security` header.

**Pre-flight context:**
- `frontend/nginx.conf` has 49 lines, one `location /` block, security headers but no cache directives.
- Vite produces hashed filenames for JS/CSS (`assets/index-abc123.js`) — safe for immutable caching.
- `index.html` must NOT be cached aggressively (it references the hashed files).

**Changes required:**

1. **Add a location block for hashed static assets** in `frontend/nginx.conf`, before the existing `location /`:
   ```nginx
   # Immutable hashed assets (JS, CSS, images from Vite build)
   location ~* \.(?:js|css|woff2?|svg|png|jpg|jpeg|gif|ico|webp)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
       access_log off;
   }
   ```

2. **Add `no-cache` for HTML** in the existing `location /` block:
   ```nginx
   add_header Cache-Control "no-cache";
   ```

3. **Add `Strict-Transport-Security`** to the existing security headers block:
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```

**Guardrails:**
- The `add_header` in the new location block does NOT inherit parent headers — you must repeat the security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `Referrer-Policy`, `HSTS`) in the new block too, OR use `include` for shared headers.
- Prefer the `include` approach: extract common headers into a snippet file or repeat them explicitly.

**Validation:**
- `docker build -f Dockerfile.frontend --target runtime -t vmr-frontend-cache-test .` → builds successfully.
- Inspect config: `docker run --rm vmr-frontend-cache-test cat /etc/nginx/conf.d/default.conf` → verify headers present.

**Commit:** `perf(plan-f16g): add nginx cache headers and HSTS`

⚠️ AUTO-CHAIN → F16-H

---

### F16-H — PdfViewer lazy loading

**Paso objetivo:** Code-split PdfViewer with React.lazy + Suspense.

**Prompt:**

**SCOPE BOUNDARY — F16-H**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Lazy-load the heaviest frontend component (PdfViewer, 852 LOC) so it doesn't block initial app load.

**Pre-flight context:**
- `frontend/src/components/workspace/PdfViewerPanel.tsx` line 13: `import { PdfViewer } from "../PdfViewer";` — static import.
- PdfViewer is 852 LOC with heavy canvas rendering and pdf.js dependency.
- Vite already splits `pdfjs-dist` into a separate chunk (`pdfjs-core`), but the component code itself is in the main bundle.
- No `React.lazy` or `Suspense` used anywhere in the frontend.

**Changes required:**

1. **In `frontend/src/components/workspace/PdfViewerPanel.tsx`:**
   - Replace the static import:
     ```tsx
     // Before
     import { PdfViewer } from "../PdfViewer";
     
     // After
     import { lazy, Suspense } from "react";
     const PdfViewer = lazy(() => import("../PdfViewer").then(m => ({ default: m.PdfViewer })));
     ```
   - Wrap `<PdfViewer ... />` usage in a `<Suspense>` with a loading fallback:
     ```tsx
     <Suspense fallback={<div className="flex items-center justify-center h-full"><span className="text-muted-foreground">Cargando visor PDF…</span></div>}>
       <PdfViewer ... />
     </Suspense>
     ```

2. **Ensure PdfViewer has a named export** (not just default) — if it only has a named export `PdfViewer`, the `.then(m => ({ default: m.PdfViewer }))` pattern handles it. If it has a default export, simplify to `lazy(() => import("../PdfViewer"))`.

**Guardrails:**
- Verify the `PdfViewer` component's export style before writing the lazy import.
- This may affect tests that import `PdfViewerPanel` — the lazy import will need mocking or wrapping in tests. If tests break, wrap the test render in `<Suspense>`.

**Validation:**
- `cd frontend && npm test` → all pass.
- `cd frontend && npx tsc --noEmit` → no type errors.
- `cd frontend && npm run build` → build succeeds, verify chunk splitting in output.

**Commit:** `perf(plan-f16h): lazy-load PdfViewer with React.lazy`

⚠️ AUTO-CHAIN → F16-I

---

### F16-I — Deep health check

**Paso objetivo:** Enhance `/health` to verify DB connectivity and storage access.

**Prompt:**

**SCOPE BOUNDARY — F16-I**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Make the health check endpoint verify actual system readiness, not just return a hardcoded OK.

**Pre-flight context:**
- `backend/app/api/routes_health.py` (~20 lines): `GET /health` returns `{"status": "ok"}` unconditionally.
- DB access: `backend/app/infra/database.py` has `get_connection()` and `get_database_path()`.
- Storage: `backend/app/infra/file_storage.py` manages file storage.
- The health endpoint should remain fast (<100ms) for Docker healthcheck probes.

**Changes required:**

1. **Enhance `routes_health.py`:**
   ```python
   @router.get("/health")
   def health() -> dict:
       checks = {}
       overall = "ok"
       
       # DB check
       try:
           db_path = database.get_database_path()
           with database.get_connection() as conn:
               conn.execute("SELECT 1")
           checks["database"] = {"status": "ok", "path": str(db_path)}
       except Exception as e:
           checks["database"] = {"status": "error", "detail": str(e)}
           overall = "degraded"
       
       # Storage check
       try:
           storage_path = Path(settings.STORAGE_DIR)
           checks["storage"] = {
               "status": "ok" if storage_path.exists() and os.access(storage_path, os.W_OK) else "error",
               "path": str(storage_path),
           }
           if checks["storage"]["status"] == "error":
               overall = "degraded"
       except Exception as e:
           checks["storage"] = {"status": "error", "detail": str(e)}
           overall = "degraded"
       
       status_code = 200 if overall == "ok" else 503
       return JSONResponse({"status": overall, "checks": checks}, status_code=status_code)
   ```

2. **Add tests in `backend/tests/test_health.py`:**
   - Test: healthy state returns 200 with all checks "ok".
   - Test: simulated DB failure returns 503 with "degraded" status.

3. **Update Docker healthcheck** in `docker-compose.yml` if it currently probes `/docs` instead of `/health` — ensure it uses `/api/health` or `/health` (whichever matches the mounted prefix).

**Validation:**
- `cd backend && python -m pytest tests/test_health.py -v` → all pass.
- `cd backend && python -m pytest tests/ -v` → no regressions.

**Commit:** `feat(plan-f16i): deep health check with DB and storage verification`

⚠️ AUTO-CHAIN → F16-J

---

### F16-J — Fix duplicate @playwright/test

**Paso objetivo:** Remove duplicate `@playwright/test` entry from package.json.

**Prompt:**

**SCOPE BOUNDARY — F16-J**

**Branch:** `improvement/iteration-10-hardening`

**Objective:** Clean up the duplicate `@playwright/test` entry in `frontend/package.json`.

**Pre-flight context:**
- `frontend/package.json` has two entries:
  - `"@playwright/test": "^1.56.1"` (line ~44)
  - `"@playwright/test": "^1.58.2"` (line ~46)
- In JSON, the second key wins, so `^1.58.2` is effective. The `^1.56.1` line is dead.

**Changes required:**

1. Remove the first (older) `"@playwright/test": "^1.56.1"` line from `devDependencies`, keeping only `"@playwright/test": "^1.58.2"`.

**Validation:**
- `cd frontend && npm install` → no errors.
- `cd frontend && npx tsc --noEmit` → no type errors.
- JSON is valid: `node -e "require('./frontend/package.json')"` → no parse error.

**Commit:** `fix(plan-f16j): remove duplicate @playwright/test from package.json`

⚠️ AUTO-CHAIN: **STOP.** Next step F16-K is a 🚧 hard-gate for Claude. Tell the user: "✅ F16-J completado. Siguiente: abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** → adjunta el `PLAN` activo → escribe `Continúa`."

---

## Prompt activo

### Paso objetivo
_Completado: F16-J._

### Prompt
_Vacío._
