# Plan: Iteration 9 — E2E testing + evaluator experience polish

> **Operational rules:** See [execution-rules.md](execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `improvement/iteration-9-e2e`
**PR:** #163 (single PR → `main`)
**Prerequisito:** Playwright installed by Codex (setup on `improvement/playwright` branch, merged before this iteration starts).

## Context

Post-merge Iteration 8: all files >500 LOC are modularized, backend coverage 90%, frontend 85%. The most impactful gap is the total absence of E2E tests — every iteration has broken something visible (PdfViewer 3 times, toolbar, blob URLs) that unit tests don't detect. An evaluator seeing E2E in CI gains immediate confidence.

**Entry metrics:** 372 backend tests (90%), 263 frontend tests (85%), 0 lint, 8 CI jobs green.

---

## Estado de ejecución — update on completion of each step

> **Protocolo "Continúa":** open a new chat, select the correct agent, attach this file and write `Continúa`. The agent reads the state, executes the next step, and stops on completion.

**Automation legend:**
- 🔄 **auto-chain** — Codex executes alone; you review the result *afterwards*.
- 🚧 **hard-gate** — Requires your decision before continuing. Do not skip.

### Fase 15 — Iteration 9 (E2E testing + evaluator experience polish)

- [x] F15-A 🔄 — Playwright config tuning: verify config, add CI job, add `data-testid` attributes to key components (Codex)
- [x] F15-B 🔄 — E2E: upload flow — navigate → upload PDF → verify processing starts → wait for completion (Codex)
- [x] F15-C 🔄 — E2E: review flow — select document → verify PDF renders with toolbar → verify structured data panel loads (Codex)
- [x] F15-D 🔄 — E2E: edit flow — edit a field → confirm edit → verify persistence (reload page) (Codex)
- [x] F15-E 🔄 — E2E: mark reviewed — toggle reviewed status → verify banner/state change (Codex)
- [x] F15-F 🚧 — delivery-summary.md refresh: update metrics for Iter 7-8, add E2E evidence (Claude) ✅ (Claude, 2026-02-27)
- [x] F15-G 🚧 — technical-design.md §14 refresh: verify/update Known Limitations post-Iter 8 (Claude) ✅ (Claude, 2026-02-27)
- [x] F15-H 🚧 — README E2E section: add instructions to run E2E tests + CI badge (Claude) ✅ (Claude, 2026-02-27)
- [ ] F15-I 🔄 — cli.py tests: coverage 0% → 80%+ (Codex) ⏭️ DEFERRED to Iter 10 (F16-H)
- [ ] F15-J 🔄 — Docker healthcheck: nginx serves `/index.html` (not just TCP) (Codex) ⏭️ DEFERRED to Iter 10 (F16-I)
- [x] F15-K 🚧 — FUTURE_IMPROVEMENTS refresh + smoke test (Claude) ✅ (Claude, 2026-02-27)

**Iteration closed:** 2026-02-27. PR #163 merged (squash). Archived to [completed-iter-9-e2e.md](completed/completed-2026-02-26-iter-9-e2e.md).

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.

---

### F15-A — Playwright config tuning + data-testid attributes

**Paso objetivo:** Verify Playwright config and CI job, then add missing `data-testid` attributes to components needed by subsequent E2E tests (F15-C/D/E).

**Prompt:**

**SCOPE BOUNDARY — F15-A**

**Branch:** `improvement/iteration-9-e2e` (create from `main` if it doesn't exist).

**Objective:** Prepare the E2E infrastructure — verify config/CI, then add `data-testid` attributes to UI elements that E2E tests will target.

**Pre-flight context (do not re-discover — trust these facts):**
- `frontend/playwright.config.ts` exists: Chromium-only, headless, `baseURL: http://localhost:80`, HTML reporter. **No changes needed.**
- `.github/workflows/ci.yml` has an `e2e` job depending on `docker_packaging_guard`. Starts Docker stack, runs `npm run test:e2e`, uploads artifacts on failure. **No changes needed.**
- Existing E2E specs: `e2e/app-loads.spec.ts`, `e2e/upload-smoke.spec.ts`. **Leave them untouched.**
- Many components already have `data-testid`. The following are **missing** and required by F15-C/D/E:

**Changes required:**

1. **`frontend/src/components/workspace/StructuredDataPanel.tsx`** — The "Marcar revisado" / "Reabrir" `<Button>` (around lines 99-122) has **no** `data-testid`. Add `data-testid="review-toggle-btn"` to that `<Button>`.

2. **`frontend/src/components/structured/FieldEditDialog.tsx`** — The edit dialog has no testids. Add:
   - `data-testid="field-edit-dialog"` on the `<DialogContent>` wrapper.
   - `data-testid="field-edit-input"` on the main `<Input>`, `<textarea>`, or `<select>` element (whichever renders for the field type — add it to each variant).
   - `data-testid="field-edit-save"` on the "Guardar" `<Button>`.
   - `data-testid="field-edit-cancel"` on the "Cancelar" `<Button>`.

3. **`frontend/src/components/review/ReviewFieldRenderers.tsx`** — The pencil/edit `<IconButton label="Editar">` (around lines 212-222 inside the value area) has no testid. Add `data-testid={`field-edit-btn-${item.id}`}` to it.

**Validation:**
- `cd frontend && npm test` → all existing unit tests pass (no regressions from adding attributes).
- `cd frontend && npx tsc --noEmit` → no type errors.

**Commit:** `feat(plan-f15a): add data-testid attributes for E2E test targets`

**Post-push (STEP C rule):** This is the first push of the iteration — create a **draft PR**:
```bash
gh pr create --draft --base main \
  --title "feat: iteration 9 — E2E testing + evaluator polish" \
  --body "Tracking: PLAN_2026-02-26_ITER-9-E2E.md

## Progress
- [x] F15-A — data-testid attributes
- [x] F15-B — E2E: upload flow
- [x] F15-C — E2E: review flow
- [x] F15-D — E2E: edit flow
- [x] F15-E — E2E: mark reviewed
- [x] F15-F — DELIVERY_SUMMARY refresh
- [x] F15-G — TECHNICAL_DESIGN refresh
- [x] F15-H — README E2E section
- [ ] F15-I — cli.py tests
- [ ] F15-J — Docker healthcheck
- [x] F15-K — FUTURE_IMPROVEMENTS + smoke"
```
Record the PR number: update `**PR:** TBD` in the plan header to `**PR:** #<number>` (plan-update commit).

⚠️ AUTO-CHAIN → F15-B

---

### F15-B — E2E: upload flow

**Paso objetivo:** Enhance the existing upload E2E test to verify the full upload-to-processing flow.

**Prompt:**

**SCOPE BOUNDARY — F15-B**

**Branch:** `improvement/iteration-9-e2e` (already created in F15-A).

**Objective:** Review and enhance `frontend/e2e/upload-smoke.spec.ts` to cover: navigate → upload PDF → verify document appears → verify processing status is visible.

**Pre-flight context:**
- `upload-smoke.spec.ts` already tests: navigate → upload → intercept upload API (201) → wait for `doc-row-${documentId}` in sidebar. Timeout is 90 s.
- API: `POST /documents/upload` returns `{ document_id }`.
- Sidebar doc rows show a status text and/or icon. After upload, documents start in a non-reviewed processing state.
- In CI, the backend may not have an LLM key, so extraction may not complete. Do NOT rely on full processing completion.

**Changes required:**

1. Read the existing `upload-smoke.spec.ts`. If it already covers navigate + upload + doc-row verification, the core test is done.
2. **Enhance:** After the `doc-row-${id}` assertion, add a check that verifies the document row exists in the sidebar and is interactive:
   - Assert `doc-row-${id}` is clickable (use `page.getByTestId(\`doc-row-${id}\`).click()` and verify the center panel reacts — e.g., `document-layout-grid` or `review-split-grid` becomes visible).
3. If the document status text is visible in the sidebar row (e.g., "Procesando", "Completado"), add a comment explaining what states are expected but do NOT assert a specific final status (processing may not complete in CI).
4. Add a brief description comment at the top of the test: `// E2E: full upload flow — upload PDF → verify sidebar → verify document is selectable`.

**Guardrails:**
- Do NOT break the existing passing test flow.
- Keep the 90 s timeout.
- Use `data-testid` selectors and Playwright best practices.

**Validation:**
- `cd frontend && npx tsc --noEmit` → no type errors in E2E files.
- Test code is structurally correct and follows existing patterns.

**Commit:** `test(plan-f15b): enhance upload E2E with document selection verification`

⚠️ AUTO-CHAIN → F15-C

---

### F15-C — E2E: review flow

**Paso objetivo:** Create E2E test: select document → verify PDF renders with toolbar → verify structured data panel loads.

**Prompt:**

**SCOPE BOUNDARY — F15-C**

**Branch:** `improvement/iteration-9-e2e`

**Objective:** Create `frontend/e2e/review-flow.spec.ts` testing the document review workspace layout.

**Pre-flight context:**
- The app is a single-page workspace (no routing). Clicking `doc-row-${id}` in sidebar sets `activeId` state, which triggers PDF download and data queries.
- Key `data-testid` values already present:
  - Sidebar: `documents-sidebar`, `doc-row-${id}`
  - Layout: `document-layout-grid` or `review-split-grid`
  - PDF viewer: `pdf-toolbar-shell`, `pdf-scroll-container`, `pdf-page`
  - Structured panel: `structured-column-stack`, `right-panel-scroll`
- Fixture: `e2e/fixtures/sample.pdf` exists.
- Upload pattern: see `upload-smoke.spec.ts` for the exact upload + route-interception technique.
- In CI, the Docker stack is already running.

**Test to create (`frontend/e2e/review-flow.spec.ts`):**

```typescript
// E2E: review flow — select document → verify PDF + toolbar + structured panel
import fs from "node:fs";
import { expect, test } from "@playwright/test";

test("selecting a document shows PDF viewer and structured panel", async ({ page }) => {
  test.setTimeout(90_000);
  const pdfBuffer = fs.readFileSync("e2e/fixtures/sample.pdf");
  let docId: string | null = null;

  // Pin sidebar open
  await page.addInitScript(() => {
    window.localStorage.setItem("docsSidebarPinned", "1");
  });

  // Capture document_id from upload response
  await page.route("**/documents/upload", async (route) => {
    const response = await route.fetch();
    const json = await response.json() as { document_id?: string };
    docId = json.document_id ?? null;
    await route.fulfill({ response });
  });

  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();

  // Upload PDF
  await page.getByLabel("Archivo PDF").setInputFiles({
    name: "sample.pdf",
    mimeType: "application/pdf",
    buffer: pdfBuffer,
  });

  await expect.poll(() => docId, { timeout: 90_000 }).not.toBeNull();
  const row = page.getByTestId(`doc-row-${docId}`);
  await expect(row).toBeVisible({ timeout: 90_000 });

  // Select document
  await row.click();

  // Verify PDF viewer renders
  await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByTestId("pdf-scroll-container")).toBeVisible();
  await expect(page.getByTestId("pdf-page").first()).toBeVisible({ timeout: 30_000 });

  // Verify structured panel area is visible
  await expect(page.getByTestId("structured-column-stack")).toBeVisible();
});
```

Adapt if needed after reading the upload-smoke pattern and verifying testid names. If any testid doesn't match, fix the test to use the correct attribute.

**Validation:**
- `cd frontend && npx tsc --noEmit` → no type errors.
- Review the test: it should work against the Docker stack started by CI.

**Commit:** `test(plan-f15c): add review flow E2E test`

⚠️ AUTO-CHAIN → F15-D

---

### F15-D — E2E: edit flow

**Paso objetivo:** Create E2E test: edit a field → confirm edit → verify UI updates.

**Prompt:**

**SCOPE BOUNDARY — F15-D**

**Branch:** `improvement/iteration-9-e2e`

**Objective:** Create `frontend/e2e/edit-flow.spec.ts` testing the field editing round-trip.

**Pre-flight context:**
- Field editing flow in the UI:
  1. With a processed document selected, the structured panel shows fields with `data-testid="field-trigger-${id}"`.
  2. Hovering/focusing a field reveals a pencil `<IconButton>` with `data-testid="field-edit-btn-${id}"` (added in F15-A).
  3. Clicking pencil opens `FieldEditDialog` (`data-testid="field-edit-dialog"`).
  4. Dialog contains: input (`field-edit-input`), "Guardar" (`field-edit-save`), "Cancelar" (`field-edit-cancel`).
  5. Saving calls `POST /runs/{runId}/interpretations` with `{ base_version_number, changes }`.
- **Problem:** Processing may not complete in CI (no LLM). We need structured data to test editing.
- **Solution:** Use `page.route()` to mock the review/interpretation API response so the structured panel renders fields regardless of processing.

**Strategy:**
1. Upload PDF and capture `document_id` (reuse upload pattern).
2. After clicking the doc row, intercept `GET **/documents/${docId}/review` and fulfill with a **minimal valid mock** that includes at least one editable field. Read the real response shape from `frontend/src/api/documentApi.ts` (the `fetchDocumentReview` function) and `frontend/src/types/` to construct a valid mock. The mock should include a run with at least one interpretation containing a scalar field (e.g., `species` with value `"Canino"`).
3. Also intercept `GET **/documents/${docId}` to return a document with `status: "PROCESSED"` and `review_status: "IN_REVIEW"`.
4. Click a field trigger, click the pencil button, verify the dialog opens.
5. Clear the input and type a new value.
6. Intercept `POST **/runs/*/interpretations` to capture the request body and return a success response.
7. Click "Guardar". Verify the dialog closes.
8. Verify the API call was made with the correct payload shape.

**Guardrails:**
- `test.setTimeout(90_000)`.
- Pin sidebar: `localStorage.setItem("docsSidebarPinned", "1")`.
- If constructing a valid mock is too complex (deeply nested types), **simplify:** just verify that the field edit dialog opens and closes correctly when triggered. A partial test is better than no test.
- Do NOT hardcode run IDs — extract them from the mock you create.

**Validation:**
- `cd frontend && npx tsc --noEmit` → no type errors.
- Test code is structurally sound.

**Commit:** `test(plan-f15d): add edit flow E2E test`

⚠️ AUTO-CHAIN → F15-E

---

### F15-E — E2E: mark reviewed

**Paso objetivo:** Create E2E test: toggle reviewed status → verify banner/state change.

**Prompt:**

**SCOPE BOUNDARY — F15-E**

**Branch:** `improvement/iteration-9-e2e`

**Objective:** Create `frontend/e2e/mark-reviewed.spec.ts` testing the "mark as reviewed" flow.

**Pre-flight context:**
- Review toggle button: `data-testid="review-toggle-btn"` (added in F15-A).
  - Not reviewed → text "Marcar revisado".
  - Reviewed → text "Reabrir" with RefreshCw icon.
- API: `POST /documents/{id}/reviewed` (mark reviewed), `DELETE /documents/{id}/reviewed` (reopen).
- When reviewed, UI shows: read-only banner with text containing "solo lectura", edit buttons hidden, toast "Documento marcado como revisado."
- **Same mock strategy as F15-D** — mock the review and document detail APIs so the structured panel renders.

**Test to create (`frontend/e2e/mark-reviewed.spec.ts`):**

1. Upload PDF, capture `document_id`.
2. Mock `GET **/documents/${docId}/review` and `GET **/documents/${docId}` with processed-document responses (same pattern as F15-D, or import a shared helper if F15-D created one).
3. Click document row.
4. Wait for structured panel (`structured-column-stack`) to be visible.
5. Verify "Marcar revisado" button is visible: `page.getByTestId("review-toggle-btn")` should contain text "Marcar revisado".
6. Mock `POST **/documents/${docId}/reviewed` to return `{ "status": "ok" }` with status 200.
7. Click the button.
8. Verify button text changes to "Reabrir" (use `expect(page.getByTestId("review-toggle-btn")).toContainText("Reabrir")`).
9. Verify read-only indicator appears — look for text "solo lectura" in the page or structured panel area.
10. **(Bonus)** Click "Reabrir", mock `DELETE **/documents/${docId}/reviewed`, verify text reverts to "Marcar revisado".

**Guardrails:**
- `test.setTimeout(90_000)`.
- Pin sidebar.
- The optimistic cache update should handle the UI transition; the mock just needs to return a non-error response.

**Validation:**
- `cd frontend && npx tsc --noEmit` → no type errors.
- Test code is structurally sound.

**Commit:** `test(plan-f15e): add mark-reviewed E2E test`

⚠️ AUTO-CHAIN: **STOP.** Next step F15-F is a 🚧 hard-gate for Claude. Tell the user: "✅ F15-E completado. Siguiente: abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** → adjunta el `PLAN` activo → escribe `Continúa`."

---

### F15-I — cli.py tests: coverage 0% → 80%+

**Paso objetivo:** Add unit tests for `backend/app/cli.py` targeting ≥80% coverage.

**Prompt:**

**SCOPE BOUNDARY — F15-I**

**Branch:** `improvement/iteration-9-e2e`

**Objective:** Create `backend/tests/test_cli.py` with comprehensive tests for `backend/app/cli.py` (currently 0% → target ≥80%).

**Pre-flight context:**
- `cli.py` (80 lines) contains:
  - `_mask_config(key, value)` — masks sensitive config values (tokens with "secret"/"token"/"password"/"key" in key name). Short values → "****", longer → "ab***ef".
  - `command_db_schema()` → calls `database.ensure_schema()`, prints success, returns 0.
  - `command_db_check()` → reads DB path, checks existence, counts tables, prints info, returns 0.
  - `command_config_check()` → dumps masked settings as JSON, returns 0.
  - `build_parser()` → argparse with 3 subcommands: `db-schema`, `db-check`, `config-check`.
  - `main()` → parses args, dispatches to command functions. Returns 0 on success.
- Dependencies to mock: `backend.app.infra.database`, `backend.app.settings.get_settings`.
- See existing test files in `backend/tests/` for import conventions and mock patterns used in this project.

**Tests to write (at minimum):**

1. `_mask_config`: sensitive key with long value → partial mask. Sensitive key with short value (≤4 chars) → "****". Non-sensitive key → value unchanged. Non-string value with sensitive key → value unchanged.
2. `command_db_schema`: mock `database.ensure_schema()`, verify it's called, verify return 0, verify stdout contains "Schema ensured".
3. `command_db_check`: mock `database.get_database_path()` and `database.get_connection()` (context manager returning a mock connection with `.execute().fetchone()` returning `(5,)`). Verify output contains path, existence, table count.
4. `command_config_check`: mock `get_settings()` returning a simple object with attributes (include one sensitive key). Verify JSON output is valid and values are masked.
5. `build_parser`: parse each valid subcommand, verify `args.command`. Parse empty args → `SystemExit`.
6. `main`: mock `sys.argv` and the corresponding command function for each subcommand. Verify dispatch and return value.

**Validation:**
- `cd backend && python -m pytest tests/test_cli.py -v` → all pass.
- `cd backend && python -m pytest tests/test_cli.py --cov=backend.app.cli --cov-report=term-missing` → coverage ≥80%.

**Commit:** `test(plan-f15i): add cli.py unit tests for 80%+ coverage`

⚠️ AUTO-CHAIN → F15-J

---

### F15-J — Docker healthcheck: nginx serves `/index.html`

**Paso objetivo:** Ensure the frontend Docker image includes a `HEALTHCHECK` that verifies nginx serves actual content.

**Prompt:**

**SCOPE BOUNDARY — F15-J**

**Branch:** `improvement/iteration-9-e2e`

**Objective:** Add `HEALTHCHECK` instruction to `Dockerfile.frontend` runtime stage so the image is self-sufficient for health monitoring.

**Pre-flight context:**
- `Dockerfile.frontend` has 3 stages: `dev` (Node 20 Alpine, port 5173), `build` (Vite build), `runtime` (nginx:alpine, port 8080).
- The runtime stage serves the Vite build output at port 8080.
- `docker-compose.yml` has a healthcheck (`wget -q -O /dev/null http://127.0.0.1:8080/`), but the Dockerfile itself has **no** `HEALTHCHECK`.
- Adding a `HEALTHCHECK` to the Dockerfile makes standalone `docker run` work with health monitoring.

**Changes required:**

1. In `Dockerfile.frontend`, in the `runtime` stage (after `COPY` and `EXPOSE`, before or after `CMD`), add:
   ```dockerfile
   HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=5s \
     CMD wget -q -O /dev/null http://127.0.0.1:8080/index.html || exit 1
   ```
   nginx:alpine includes `wget` by default. Use `/index.html` explicitly to verify the app is served.

2. Verify Docker build: `docker build -f Dockerfile.frontend --target runtime -t vmr-frontend-hc-test .` (from repo root, next to Dockerfile.frontend).

3. Quick sanity (optional if Docker Desktop is available): run the image briefly and check health status.

**Validation:**
- Docker build succeeds without errors.
- Existing `docker-compose.yml` healthcheck still works (compose healthcheck overrides Dockerfile healthcheck when present, so no conflict).

**Commit:** `feat(plan-f15j): add HEALTHCHECK to Dockerfile.frontend runtime stage`

⚠️ AUTO-CHAIN: **STOP.** Next step F15-K is a 🚧 hard-gate for Claude. Tell the user: "✅ F15-J completado. Siguiente: abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** → adjunta el `PLAN` activo → escribe `Continúa`."

---

## Prompt activo

### Paso objetivo
_Vacío._

### Prompt
_Vacío._
