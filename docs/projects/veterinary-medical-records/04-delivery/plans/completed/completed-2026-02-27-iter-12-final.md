# Plan: Iteration 12 (Final) — E2E Phase 3-4 + WCAG + final polish

> **Operational rules:** See [execution-rules.md](execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Rama:** `improvement/iteration-12-final`
**PR:** #169
**Prerequisito:** Iteration 11 merged to `main`.

## Context

Post-Iter 11 (estimated): ~390 backend tests (≥92%), ~280 frontend tests (≥87%), ~20 E2E specs, error UX mapping live, P50/P95 benchmarks, repository split, OpenAPI polished, 10+ CI jobs green.

**This is the final iteration.** The project has reached a point of diminishing returns after 11 iterations. The remaining high-value items are:

1. **E2E coverage at ~33%** — 20 of 61 planned specs. Phase 3-4 brings it to full coverage (61/61).
2. **No WCAG audit** — moderate aria coverage exists but no systematic audit or automated checks.
3. **No badges/GIF/one-pager** in README — low effort, high evaluator impact for first impression.
4. **No `architecture.md`** — technical-design.md is 2K lines; evaluators need a scannable one-pager.
5. **Documentation final sweep** — close out FUTURE_IMPROVEMENTS, refresh DELIVERY_SUMMARY with final metrics.

**Entry metrics (expected post-Iter 11):** ~390 backend tests (≥92%), ~280 frontend tests (≥87%), ~20 E2E specs, 10+ CI jobs, 0 lint.
**Exit metrics target:** 61 E2E specs (100% plan coverage), WCAG quick fixes applied, axe-core in CI, badges + demo GIF in README, architecture.md one-pager, all documentation finalized.

---

## Estado de ejecución — update on completion of each step

> **Protocolo "Continúa":** open a new chat, select the correct agent, attach this file and write `Continúa`. The agent reads the state, executes the next step, and stops on completion.

**Automation legend:**
- 🔄 **auto-chain** — Codex executes alone; you review the result *afterwards*.
- 🚧 **hard-gate** — Requires your decision before continuing. Do not skip.

### Fase 19 — Iteration 12 (Final)

#### Phase A — E2E expansion Phase 3-4 (from E2E coverage plan)

> E2E prompts originally from the standalone E2E coverage expansion plan (Phase 3–4), now merged inline.

- [x] F19-A 🔄 — Bloque Viewer: `viewer-tabs`, `raw-text`, `zoom-advanced` — 10 tests (Codex) → source: F17-L ✅ 7c5cdfa8 + fix 0d775e4f
- [x] F19-B 🔄 — Bloque Data: `structured-filters`, `field-validation`, `add-field` — 13 tests (Codex) → source: F17-M ✅ 7fa52122
- [x] F19-C 🔄 — Bloque Workflow: `reprocess`, `toasts` — 5 tests (Codex) → source: F17-N ✅ eb6128f8
- [x] F19-D 🔄 — Bloque Layout: `source-panel`, `split-panel`, `sidebar-interactions` — 8 tests (Codex) → source: F17-O ✅ 11d23e1d + fix 43acb9b8 + fix 15fbca79
- [x] F19-E 🔄 — Bloque Avanzado: `visit-grouping`, `upload-validation` — 5 tests (Codex) → source: F17-P ✅ 025d2358
- [x] F19-F 🔄 — Run full suite in Docker, verify 61 tests green (Codex) → source: F17-Q ✅ 56e5808d + fix 7696bf0f
- [x] F19-G 🔄 — Remove legacy spec files absorbed by new specs (Codex) → source: F17-R ✅ d5f66e92
- [x] F19-H 🚧 — Update `plan-e2e-test-coverage.md` §7 checkboxes + metrics (Claude) → source: F17-S ✅

#### Phase B — WCAG quick wins + automated a11y

- [x] F19-I 🔄 — Add `@axe-core/playwright` E2E accessibility audit + fix critical violations (Codex) ✅ df33d3fb
- [x] F19-J 🔄 — Add missing aria-labels, focus management, and color contrast fixes (Codex) ✅ done

#### Phase C — README + Architecture one-pager

- [x] F19-K 🚧 — Create `architecture.md` one-pager with Mermaid diagram (Claude) ✅ 402a2ff0
- [x] F19-L 🚧 — README final polish: badges, tech stack table, demo GIF placeholder, streamlined structure (Claude) ✅ 093fb6eb

#### Phase D — Final documentation close-out

- [x] F19-M 🚧 — DELIVERY_SUMMARY final refresh with Iter 11+12 metrics (Claude) ✅
- [x] F19-N 🚧 — FUTURE_IMPROVEMENTS → reframe as "Known Limitations & Future Directions" (Claude) ✅ 096efbbf
- [x] F19-O 🚧 — TECHNICAL_DESIGN §14 final update: mark resolved limitations, add Iter 12 outcomes (Claude) ✅

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.
> Prompts that depend on Iter 11 results are marked "just-in-time" — Claude writes them after Iter 11 closes.

---

### F19-A — Bloque Viewer: `viewer-tabs`, `raw-text`, `zoom-advanced` (10 tests)

**Paso objetivo:** Implement 3 spec files for viewer tab switching, raw text features, and advanced zoom.

**Prompt:**

**SCOPE BOUNDARY — F19-A**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create three spec files:

1. **`frontend/e2e/viewer-tabs.spec.ts`** — Tests 22–25:
   - Test 22: Tab "Documento" shows PDF (default active)
   - Test 23: Tab "Texto extraído" shows raw text
   - Test 24: Tab "Detalles técnicos" shows processing history
   - Test 25: "Descargar" button opens PDF in new tab

2. **`frontend/e2e/raw-text.spec.ts`** — Tests 26–30:
   - Test 26: Extracted text is visible
   - Test 27: Search existing text → "Coincidencia encontrada"
   - Test 28: Search nonexistent → "No se encontraron coincidencias"
   - Test 29: Copy to clipboard
   - Test 30: Download text file

3. **`frontend/e2e/zoom-advanced.spec.ts`** — Tests 50–51:
   - Test 50: Ctrl + scroll wheel zooms in/out
   - Test 51: Zoom persists in localStorage across reload

**Validation:**
- `cd frontend && npx playwright test viewer-tabs.spec.ts raw-text.spec.ts zoom-advanced.spec.ts --project=extended` → 10 tests pass

**Commit:** `feat(plan-f19a): add viewer-tabs, raw-text, zoom-advanced E2E tests (10 tests)`

⚠️ AUTO-CHAIN → F19-B

---

### F19-B — Bloque Data: `structured-filters`, `field-validation`, `add-field` (13 tests)

**Paso objetivo:** Implement 3 spec files for structured data filtering, field validation, and adding fields.

**Prompt:**

**SCOPE BOUNDARY — F19-B**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create three spec files using mock routes for deterministic data:

1. **`frontend/e2e/structured-filters.spec.ts`** — Tests 31–36:
   - Test 31: Search by text filters results
   - Test 32: Clear search restores all fields
   - Test 33: Filter by low confidence
   - Test 34: Filter critical only
   - Test 35: Filter "with value" / "empty only"
   - Test 36: Reset filters restores full view

2. **`frontend/e2e/field-validation.spec.ts`** — Tests 37–41:
   - Test 37: Microchip invalid format → validation error
   - Test 38: Sex dropdown with canonical options
   - Test 39: Species dropdown with canonical options
   - Test 40: Weight rejects non-numeric
   - Test 41: Date rejects invalid format

3. **`frontend/e2e/add-field.spec.ts`** — Tests 60–61:
   - Test 60: Add new field with key + value
   - Test 61: Editing blocked on reviewed document → shows toast

**Validation:**
- `cd frontend && npx playwright test structured-filters.spec.ts field-validation.spec.ts add-field.spec.ts --project=extended` → 13 tests pass

**Commit:** `feat(plan-f19b): add structured-filters, field-validation, add-field E2E tests (13 tests)`

⚠️ AUTO-CHAIN → F19-C

---

### F19-C — Bloque Workflow: `reprocess`, `toasts` (5 tests)

**Paso objetivo:** Implement 2 spec files for reprocessing and toast behavior.

**Prompt:**

**SCOPE BOUNDARY — F19-C**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create two spec files:

1. **`frontend/e2e/reprocess.spec.ts`** — Tests 52–53:
   - Test 52: Reprocess button shows confirmation modal
   - Test 53: Confirm reprocess → toast, status changes to PROCESSING

2. **`frontend/e2e/toasts.spec.ts`** — Tests 57–59:
   - Test 57: Success toast auto-closes (~3.5s)
   - Test 58: Error toast auto-closes slower (~5s)
   - Test 59: Manual close toast via X button

**Validation:**
- `cd frontend && npx playwright test reprocess.spec.ts toasts.spec.ts --project=extended` → 5 tests pass

**Commit:** `feat(plan-f19c): add reprocess and toasts E2E tests (5 tests)`

⚠️ AUTO-CHAIN → F19-D

---

### F19-D — Bloque Layout: `source-panel`, `split-panel`, `sidebar-interactions` (8 tests)

**Paso objetivo:** Implement 3 spec files for source panel, split layout, and sidebar interactions.

**Prompt:**

**SCOPE BOUNDARY — F19-D**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create three spec files:

1. **`frontend/e2e/source-panel.spec.ts`** — Tests 42–44:
   - Test 42: Selecting field navigates PDF to evidence page
   - Test 43: Source panel shows page number + snippet
   - Test 44: Pin and close source panel

2. **`frontend/e2e/split-panel.spec.ts`** — Tests 48–49:
   - Test 48: Split grid visible with handle
   - Test 49: Double-click handle resets ratio

3. **`frontend/e2e/sidebar-interactions.spec.ts`** — Tests 45–47:
   - Test 45: Pin/unpin sidebar
   - Test 46: Refresh document list
   - Test 47: Hover expands collapsed sidebar

**Validation:**
- `cd frontend && npx playwright test source-panel.spec.ts split-panel.spec.ts sidebar-interactions.spec.ts --project=extended` → 8 tests pass

**Commit:** `feat(plan-f19d): add source-panel, split-panel, sidebar-interactions E2E tests (8 tests)`

⚠️ AUTO-CHAIN → F19-E

---

### F19-E — Bloque Avanzado: `visit-grouping`, `upload-validation` (5 tests)

**Paso objetivo:** Implement 2 spec files for visit grouping and upload validation.

**Prompt:**

**SCOPE BOUNDARY — F19-E**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create two spec files:

1. **`frontend/e2e/visit-grouping.spec.ts`** — Tests 54–56 (mock routes with multi-visit payload):
   - Test 54: Visit episodes grouped and numbered
   - Test 55: Each visit shows metadata (date, reason)
   - Test 56: Unassigned group visible for orphan fields

2. **`frontend/e2e/upload-validation.spec.ts`** — Tests 20–21:
   - Test 20: Non-PDF file rejected → error toast
   - Test 21: Drag & drop on viewer triggers upload overlay

**Validation:**
- `cd frontend && npx playwright test visit-grouping.spec.ts upload-validation.spec.ts --project=extended` → 5 tests pass

**Commit:** `feat(plan-f19e): add visit-grouping and upload-validation E2E tests (5 tests)`

⚠️ AUTO-CHAIN → F19-F

---

### F19-F — Full validation in Docker

**Paso objetivo:** Run the complete 61-test suite and verify within time budgets.

**Prompt:**

**SCOPE BOUNDARY — F19-F**

**Branch:** `improvement/iteration-12-final`

**Objective:** End-to-end validation of the full test suite.

**Steps:**
1. `docker compose up -d --build --wait`
2. `cd frontend && npm run test:e2e:all` → 61 tests pass
3. Measure total time: target < 10 minutes
4. Run again to check for flakiness
5. If any test fails, fix it. If flaky, add appropriate waits or retry logic.

**Commit:** `fix(plan-f19f): stabilize E2E suite` (only if fixes needed)

⚠️ AUTO-CHAIN → F19-G

---

### F19-G — Legacy spec cleanup

**Paso objetivo:** Remove legacy spec files superseded by new structured tests.

**Prompt:**

**SCOPE BOUNDARY — F19-G**

**Branch:** `improvement/iteration-12-final`

**Objective:** Delete legacy spec files that have been superseded:

- `frontend/e2e/review-flow.spec.ts` → absorbed by `pdf-viewer.spec.ts` + `document-sidebar.spec.ts`
- `frontend/e2e/edit-flow.spec.ts` → replaced by `field-editing.spec.ts` (if renamed in Iter 11)
- `frontend/e2e/mark-reviewed.spec.ts` → replaced by `review-workflow.spec.ts` (if renamed in Iter 11)

**Validation:**
- `cd frontend && npm run test:e2e:all` → still 61 tests (no fewer, no duplicates)

**Commit:** `chore(plan-f19g): remove legacy E2E specs superseded by coverage expansion`

⚠️ STOP → F19-H requires Claude

---

### F19-H — Update E2E test coverage plan metrics (Claude)

**Paso objetivo:** Update documentation with final E2E metrics and mark all checkboxes.

**Prompt:**

**Steps:**
1. Update `plan-e2e-test-coverage.md` §7 checkboxes
2. Update this plan's Estado de ejecución
3. Record in `implementation-history.md`

**Commit:** `docs(plan-f19h): update E2E coverage plan with final metrics`

⚠️ AUTO-CHAIN → F19-I

---

### F19-I — Add `@axe-core/playwright` E2E accessibility audit + fix critical violations

**Paso objetivo:** Add automated accessibility testing to the E2E suite and fix any critical WCAG 2.1 AA violations found.

**Prompt:**

**SCOPE BOUNDARY — F19-I**

**Branch:** `improvement/iteration-12-final` (create from `main` if it doesn't exist).

**Objective:** Integrate `@axe-core/playwright` into the E2E test suite to catch WCAG 2.1 AA violations automatically, then fix any critical/serious findings.

**Pre-flight context:**
- Playwright E2E tests exist under `frontend/e2e/`.
- Playwright config at `frontend/playwright.config.ts` with smoke/core/extended projects (set up in Iter 11).
- ~14 of ~30 component files already have aria attributes; key gaps include `ui/` primitives, `AddFieldDialog`, `FieldEditDialog`, `WorkspaceDialogs`, and several `app/` components.
- No accessibility testing setup exists currently.

**Changes required:**

1. **Install dependency:**
   ```bash
   cd frontend && npm install --save-dev @axe-core/playwright
   ```

2. **Create `frontend/e2e/accessibility.spec.ts`** — Axe audit on 3 key views:
   ```typescript
   import { test, expect } from "@playwright/test";
   import AxeBuilder from "@axe-core/playwright";

   test.describe("Accessibility — WCAG 2.1 AA", () => {
     test("upload view has no critical violations", async ({ page }) => {
       await page.goto("/");
       const results = await new AxeBuilder({ page })
         .withTags(["wcag2a", "wcag2aa"])
         .analyze();
       expect(results.violations.filter(v => v.impact === "critical")).toEqual([]);
     });

     test("review view has no critical violations", async ({ page }) => {
       // Navigate to review view (upload a doc or mock route)
       await page.goto("/");
       // ... select a document to enter review view
       const results = await new AxeBuilder({ page })
         .withTags(["wcag2a", "wcag2aa"])
         .analyze();
       expect(results.violations.filter(v => v.impact === "critical")).toEqual([]);
     });

     test("full app audit — serious violations < 5", async ({ page }) => {
       await page.goto("/");
       const results = await new AxeBuilder({ page })
         .withTags(["wcag2a", "wcag2aa"])
         .analyze();
       const serious = results.violations.filter(
         v => v.impact === "critical" || v.impact === "serious"
       );
       // Log for visibility
       if (serious.length > 0) {
         console.log("Serious a11y violations:", JSON.stringify(serious, null, 2));
       }
       expect(serious.length).toBeLessThan(5);
     });
   });
   ```

3. **Run the audit** and fix any **critical** violations found. Common fixes:
   - Missing `<html lang="es">` in `index.html`.
   - Missing `alt` on any `<img>` tags.
   - Color contrast ratios below 4.5:1 on text.
   - Missing form labels on inputs.
   - Missing `role` on interactive elements.

4. **Add to Playwright extended project** — The accessibility spec should run as part of the extended E2E suite (not smoke).

**Validation:**
- `cd frontend && npx playwright test e2e/accessibility.spec.ts` → all pass.
- `cd frontend && npx vitest run` → existing unit tests unaffected.
- `cd frontend && npm run lint` → 0 errors.

**Commit:** `test(plan-f19i): add axe-core accessibility audit + fix critical WCAG violations`

⚠️ AUTO-CHAIN → F19-J

---

### F19-J — Add missing aria-labels, focus management, and color contrast fixes

**Paso objetivo:** Systematic pass through components missing accessibility attributes — focusing on interactive elements, dialogs, and UI primitives.

**Prompt:**

**SCOPE BOUNDARY — F19-J**

**Branch:** `improvement/iteration-12-final`

**Objective:** Add `aria-label`, `role`, `tabIndex`, focus trapping, and color contrast fixes to the ~16 component files identified as missing accessibility attributes.

**Pre-flight context:**
Components currently **without** adequate aria/role/tabIndex coverage:
- `frontend/src/components/ui/badge.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/card.tsx`
- `frontend/src/components/ui/dialog.tsx`
- `frontend/src/components/ui/input.tsx`
- `frontend/src/components/ui/scroll-area.tsx`
- `frontend/src/components/ui/separator.tsx`
- `frontend/src/components/ui/tabs.tsx`
- `frontend/src/components/ui/toggle-group.tsx`
- `frontend/src/components/app/CriticalBadge.tsx`
- `frontend/src/components/app/Field.tsx`
- `frontend/src/components/app/IconButton.tsx`
- `frontend/src/components/app/Section.tsx`
- `frontend/src/components/app/DocumentStatusCluster.tsx`
- `frontend/src/components/review/WorkspaceDialogs.tsx`
- `frontend/src/components/structured/AddFieldDialog.tsx`
- `frontend/src/components/structured/FieldEditDialog.tsx`

**Changes required:**

1. **`ui/` primitives** — Most are likely Radix-based (shadcn/ui) and may already have built-in accessibility. Verify each:
   - `dialog.tsx`: ensure `Dialog.Content` has `aria-describedby` and focus is trapped (Radix does this, but verify the props are passed).
   - `button.tsx`: ensure disabled state uses `aria-disabled` if visual-only.
   - `input.tsx`: ensure associated `<label>` or `aria-label` on all instances.
   - `tabs.tsx`: verify Radix `Tabs` provides keyboard nav (arrow keys between tabs).
   - `separator.tsx`: ensure `role="separator"` or `<hr>`.
   - `scroll-area.tsx`: ensure `aria-label` on scroll container.

2. **`app/` components:**
   - `IconButton.tsx`: already accepts `label` prop — verify it renders as `aria-label`.
   - `Field.tsx`: add `aria-label` describing the field name/value for screen readers.
   - `CriticalBadge.tsx`: add `aria-label="Campo crítico"` or equivalent.
   - `Section.tsx`: add `role="region"` + `aria-labelledby` pointing to heading.
   - `DocumentStatusCluster.tsx`: add `aria-label` describing current status.

3. **Dialogs:**
   - `WorkspaceDialogs.tsx`: ensure each dialog variant has `aria-labelledby` (title) and `aria-describedby` (description).
   - `AddFieldDialog.tsx`: add `aria-label` to form inputs, focus first input on open.
   - `FieldEditDialog.tsx`: same — form labels + auto-focus.

4. **`index.html`** — Verify `<html lang="es">` is set (if not already).

5. **Color contrast** — Check Tailwind classes. If any text uses `text-gray-400` or similar on white bg, bump to `text-gray-500` minimum (4.5:1 ratio for AA).

**Validation:**
- `cd frontend && npx playwright test e2e/accessibility.spec.ts` → all pass (critical + serious < 5).
- `cd frontend && npx vitest run` → existing unit tests pass.
- `cd frontend && npm run lint` → 0 errors.
- Manual: tab through the upload and review views — all interactive elements reachable via keyboard.

**Commit:** `fix(plan-f19j): add missing aria-labels, focus management, contrast fixes`

⚠️ STOP → F19-K requires Claude

---

### F19-K — Create `architecture.md` one-pager with Mermaid diagram (Claude)

**Paso objetivo:** Create a scannable one-page architecture overview for evaluators who won't read the 2K-line technical-design.md.

**Prompt:**

**SCOPE BOUNDARY — F19-K**

**Branch:** `improvement/iteration-12-final`

**Objective:** Create `docs/projects/veterinary-medical-records/02-tech/architecture.md` — a ~100-line document with a Mermaid C4-style diagram, tech stack table, data flow summary, and links to detailed docs.

**Structure:**

```markdown
# Architecture Overview

> One-page summary for evaluators. For full detail, see [technical-design.md](technical-design.md).

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + TypeScript + Tailwind CSS | Type-safe SPA with utility-first styling |
| Backend | Python 3.11 + FastAPI | Async-first, auto-generated OpenAPI |
| Database | SQLite (WAL mode) | Zero-config, ACID, portable |
| PDF parsing | pdfplumber + PyMuPDF | Dual-engine extraction with fallback |
| Testing | Vitest + Pytest + Playwright | Unit → integration → E2E pyramid |
| CI/CD | GitHub Actions (10 jobs) | Path-filtered, cached, parallel |
| Containers | Docker Compose | One-command `docker compose up` |

## System diagram

​```mermaid
graph TB
    subgraph "Frontend (React SPA)"
        UI[AppWorkspace] --> API[documentApi.ts]
    end
    subgraph "Backend (FastAPI)"
        Routes[API Routes] --> Services[Application Services]
        Services --> Ports[Repository Protocol]
        Ports --> SQLite[(SQLite DB)]
        Ports --> Storage[File Storage]
        Services --> Processing[Processing Pipeline]
    end
    API -->|REST /api/*| Routes
    Processing --> Extraction[PDF Extraction]
    Processing --> Interpretation[Field Interpretation]
    Processing --> Confidence[Confidence Scoring]
​```

## Key architectural decisions

| Decision | Record |
|----------|--------|
| Hexagonal architecture | [ADR-ARCH-0001](adr/ADR-ARCH-0001-modular-monolith.md) |
| SQLite as primary DB | [ADR-ARCH-0002](adr/ADR-ARCH-0002-sqlite-database.md) |
| Raw SQL over ORM | [ADR-ARCH-0003](adr/ADR-ARCH-0003-raw-sql-repository-pattern.md) |
| In-process async processing | [ADR-ARCH-0004](adr/ADR-ARCH-0004-in-process-async-processing.md) |

## Data flow

1. **Upload** → PDF stored on disk, metadata in SQLite, processing queued
2. **Extract** → PDF text extraction (pdfplumber → PyMuPDF fallback)
3. **Interpret** → Field identification via regex + candidate mining + confidence scoring
4. **Review** → Evaluator sees structured fields, can edit, approve, reprocess
```

**Adjust:** Read current technical-design.md headings and ADR references to ensure accuracy. Verify tech versions from `pyproject.toml` and `package.json`.

**Validation:** Links are valid, Mermaid renders, file < 150 lines.

**Commit:** `docs(plan-f19k): add architecture.md one-pager with Mermaid diagram`

⚠️ AUTO-CHAIN → F19-L

---

### F19-L — README final polish: badges, tech stack table, streamlined structure (Claude)

**Paso objetivo:** Add CI/coverage badges, a tech stack summary at the top, a demo screenshot placeholder, and streamline the structure for evaluator first impressions.

**Prompt:**

**SCOPE BOUNDARY — F19-L**

**Branch:** `improvement/iteration-12-final`

**Objective:** Polish README.md as the project's front door. Currently 316 lines with no badges, no visual, and a dense structure.

**Changes required:**

1. **Add badges** after the title (line 1):
   ```markdown
   ![CI](https://github.com/isilionisilme/veterinary-medical-records/actions/workflows/ci.yml/badge.svg?branch=main)
   ![License](https://img.shields.io/badge/license-MIT-blue)
   ![Python](https://img.shields.io/badge/python-3.11-blue)
   ![React](https://img.shields.io/badge/react-18-61dafb)
   ```
   Verify the CI badge URL matches the actual workflow file name.

2. **Add tech stack summary** right after badges (before TL;DR):
   ```markdown
   > **Stack:** Python 3.11 · FastAPI · React 18 · TypeScript · SQLite · Docker · Playwright · GitHub Actions
   ```

3. **Add demo screenshot placeholder** section after TL;DR:
   ```markdown
   ## Demo

   <!-- Replace with actual screenshot or GIF -->
   > 📸 _Screenshot placeholder — run `docker compose up --build` and visit `http://localhost:5173` to see the app._
   ```

4. **Add link to `architecture.md`** in the "Architecture at a glance" section:
   ```markdown
   For a visual overview, see [architecture.md](docs/projects/veterinary-medical-records/02-tech/architecture.md).
   ```

5. **Verify existing links** — All relative links in README must still resolve.

**Validation:**
- All badge URLs resolve (test in browser).
- No dead links.
- README renders properly on GitHub's Markdown viewer.

**Commit:** `docs(plan-f19l): README final polish — badges, tech stack, demo placeholder`

⚠️ AUTO-CHAIN → F19-M

---

### F19-M — DELIVERY_SUMMARY final refresh (Claude)

**Paso objetivo:** Update delivery-summary.md with final metrics from Iterations 11 and 12.

**Prompt:**

_Just-in-time — depends on Iter 11+12 actual results. Claude writes this after F19-L._

**Changes required:**
1. Update "At a glance" metrics table with final numbers (backend/frontend tests, E2E count, coverage %).
2. Add Iter 11 and Iter 12 sections with key outcomes.
3. Add final PR references.

**Commit:** `docs(plan-f19m): DELIVERY_SUMMARY final refresh`

⚠️ AUTO-CHAIN → F19-N

---

### F19-N — FUTURE_IMPROVEMENTS → "Known Limitations & Future Directions" (Claude)

**Paso objetivo:** Reframe future-improvements.md from an active backlog to a permanent "known limitations and ideas" document appropriate for a completed project.

**Prompt:**

**SCOPE BOUNDARY — F19-N**

**Branch:** `improvement/iteration-12-final`

**Objective:** Restructure future-improvements.md to reflect project completion. The document should communicate "we know about these and chose not to pursue them" rather than "these are upcoming tasks."

**Changes required:**

1. **Rename title** → `# Known Limitations & Future Directions`

2. **Add preamble:**
   ```markdown
   > After 12 iterations, this project has reached its target quality bar. The items
   > below represent conscious scope decisions — not gaps. Each was evaluated and
   > deferred because the ROI did not justify the effort for a portfolio/demo project.
   ```

3. **Reorganize into 3 sections:**
   - **Completed improvements** — Collapsed summary of all ✅ items (just a count + link to IMPLEMENTATION_HISTORY).
   - **Known limitations** — Items 14, 16, 17, 18, 21, 23, 24 reframed as "We chose not to..." with brief rationale.
   - **If this were production** — 3-4 bullet points of what you'd do first (PostgreSQL, auth, monitoring).

4. **Remove week-based timeline framing** — No longer relevant for a completed project.

**Validation:** Links valid, tone is "completed project" not "active backlog."

**Commit:** `docs(plan-f19n): reframe FUTURE_IMPROVEMENTS as known limitations`

⚠️ AUTO-CHAIN → F19-O

---

### F19-O — TECHNICAL_DESIGN §14 final update (Claude)

**Paso objetivo:** Final update to known limitations section reflecting all resolved items through Iter 12.

**Prompt:**

_Just-in-time — depends on Iter 11+12 actual results. Claude writes specifics after all code steps complete._

**Changes required:**
1. Mark resolved limitations (repo split, E2E coverage, accessibility).
2. Update metrics to final numbers.
3. Cross-reference architecture.md and KNOWN_LIMITATIONS.md.
4. Ensure §14 reflects the "completed project" framing.

**Commit:** `docs(plan-f19o): TECHNICAL_DESIGN §14 final update`

✅ **Todos los pasos completados. Proyecto cerrado.**

---

## Risks & mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Iter 11 not merged when starting Iter 12 | Blocker | Wait for Iter 11 merge; plan is branch-independent |
| E2E Phase 3 tests flaky in CI | High | Retry logic + worker=1 already configured; `test.setTimeout(90_000)` |
| axe-core finds >50 violations | Medium | Filter to critical/serious only; `ui/` Radix components likely pass |
| Demo GIF not captured | Low | Placeholder is acceptable; screenshot can be added post-merge |
| Mermaid diagram doesn't render on GitHub | Low | Use simple `graph TB` syntax; verified compatible |

---

## How to test

```bash
# Full E2E suite (61 tests):
$env:FRONTEND_PORT='80'; docker compose up -d --build --wait
cd frontend && npm run test:e2e:all

# Accessibility audit:
cd frontend && npx playwright test e2e/accessibility.spec.ts

# All unit + integration:
cd backend && python -m pytest tests/ -x -q --tb=short
cd frontend && npx vitest run

# Verify docs:
# Open README.md in GitHub preview — badges render, links work
# Open architecture.md — Mermaid diagram renders
```
