# Frontend Implementation Notes

## Purpose

This document describes **how the frontend should be implemented** to satisfy the UX and backend contracts
defined elsewhere in the repository documentation.
Reading order, document authority, and cross-document precedence are defined in [`docs/README.md`](../README.md).
If anything here appears to conflict with other documentation, **STOP and ask**.
 
It must remain **implementation-only**:
- UI stack and technical choices
- frontend architecture and patterns
- PDF rendering + scrolling strategy
- UI implementation strategies for complex interaction requirements
- frontend testing strategy

It does **not** redefine:
- product meaning / governance
- UX semantics or workflow guarantees
- backend contracts (endpoints, payloads, error semantics)
- user story scope, order, or acceptance criteria

---

## Frontend Stack

The frontend is implemented using:

- **React + TypeScript (Vite)**  
  Chosen to explicitly satisfy the React frontend requirement while keeping setup fast and standard.

- **Tailwind CSS**  
  Used for styling, layout, responsiveness, and dark mode support with minimal custom CSS.

- **Local UI primitives**  
  Prefer lightweight, local components under `/frontend/src/components/ui/*`.
  Do not add a UI component library unless required to satisfy accessibility or interaction requirements,
  and justify any new dependency.

- **Lean design system contract**
  Follow [`docs/projects/veterinary-medical-records/01-product/design-system.md`](design-system.md) for tokens, primitives, wrappers, and guard rules.

- **TanStack Query**  
  Used for server state management (loading, error, invalidation) without introducing global client state complexity.

- **Lucide React**  
  Lightweight and consistent iconography.

- **Framer Motion (minimal usage)**  
  Used only for subtle transitions (e.g., skeleton → content), never for core logic.

- **PDF.js (`pdfjs-dist`)**  
  Used to render PDFs and support evidence-based review and highlighting.

---

## Project Structure

The repository uses a single repo with explicit separation:

- `/frontend` contains all React code.
- `/backend` remains the FastAPI application.
- `/docs` contains repository documentation (see [`docs/README.md`](../README.md) for structure and reading order).

The frontend is built and served independently but lives in the same repository.

---

## Frontend Architecture

The frontend is implemented as a small set of explicit, testable modules.

Suggested structure:

- `/frontend/src/lib/`
  - API client (one fetch wrapper that normalizes errors).
  - Query keys and TanStack Query helpers.
- `/frontend/src/components/`
  - View components (document list, review layout).
  - PDF viewer + evidence navigation helpers.
- `/frontend/src/components/ui/`
  - Small, reusable UI primitives (buttons, badges, panels).

State rules:
- **Server state** (documents, status, review payloads, raw text) lives in TanStack Query only.
- **Local UI state** (selected field, raw text panel open, current active page) lives in the view component(s).
- Avoid introducing a global client-state store.

---

## PDF Review and Evidence Rendering

Document review is implemented using **evidence-based navigation**, not precise spatial annotation.

The frontend must consume the "evidence" fields exactly as defined by backend contracts
in the authoritative documentation (see [`docs/README.md`](../README.md)) (do not invent fields or semantics here).

Frontend behavior:
- when a field is selected, the PDF viewer navigates to the referenced page,
- the snippet is displayed as explicit evidence,
- the review flow remains usable even if highlighting fails.

This ensures:
- traceability,
- explainability,
- and zero blocking of the review experience.

---

## Review Rendering Backbone (Global Schema)

Rendering authority for the full key universe, ordering, section grouping, repeatability, and fallback rules is
[`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) (Global Schema).

Frontend implementation guidance:
- Use Global Schema as the review rendering backbone.
- Render all keys in stable order, grouped by the same sections (A-G), even when values are missing.
- Show explicit empty states/placeholders for missing values; do not hide keys only because the model omitted them.
- If `document_date` is missing, display the Product Design fallback to `visit_date`.

Repeatable keys: `medication`, `diagnosis`, `procedure`, `lab_result`, `line_item`, `symptoms`, `vaccinations`, `imaging`.
- Always render the repeatable field container.
- Render an explicit empty-list state when there are no items.
- Scope note: payloads may include billing repeatables (for example `line_item`) even when Medical Record MVP UI scope excludes non-clinical concepts.

Value typing:
- Respect the existing contract value types: `string | date | number | boolean | unknown`.
- For ambiguous or unit-bearing values, default to `string`.
- Do not introduce new parsing obligations beyond existing backend/frontend contracts.

---

## Continuous Scroll Preview

The document preview renders PDF pages in a single vertical scroll so users can read continuously
without manual page switching.

Implementation uses `pdfjs-dist` for PDF rendering. Rendering must be incremental (lazy) to avoid blocking the UI
on large PDFs.

### PDF.js wiring (Vite)
PDF.js must be configured with an explicit worker (required for production builds).
In Vite, use a worker URL import and assign it to `GlobalWorkerOptions.workerSrc`.

### Paging and navigation rules
- Evidence `page` values are **1-based** (as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md)). Keep viewer navigation 1-based.
- "Next" / "Previous" scroll within the viewer's scroll container only (no global page scroll hijacking).
- Track active page based on scroll position (IntersectionObserver), keeping the page index in sync with what is visible.
- Show placeholders while a page is loading/rendering; empty/blank content must be treated as a normal transient state.

Navigation buttons remain available:
- **Next** scrolls to the top of the next page in the continuous stack.
- **Previous** scrolls to the top of the previous page.

Tests should validate the scroll + navigation behavior at the component level, without relying on pixel-perfect rendering.

---

## File-Type Support

End-to-end review is implemented for PDFs.

Frontend implications:
- Preview behavior is implemented for PDFs via PDF.js (continuous scroll).
- Download behavior must work for PDFs via `GET /documents/{id}/download`.

## Additional File Types

Format expansion is handled by dedicated user stories in [`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](implementation-plan.md) (US-19 and US-20).

---

## Highlight Strategy (Progressive Enhancement)

Text highlighting inside the PDF is implemented as **progressive enhancement**, never as a dependency for usability.

Implementation approach:
- render the PDF using PDF.js,
- use the text layer to search for the provided snippet on the target page,
- highlight the closest or first matching occurrence.

If matching fails:
- no highlight is shown,
- page navigation and snippet evidence remain visible,
- the UI does not attempt to fake precision.

---

## Confidence Rendering

Confidence values are rendered as **visual attention signals**, not as control mechanisms.
Confidence semantics are owned by [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md), and interaction behavior is owned by [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md).

Frontend representation:
- qualitative signal first (e.g. color or emphasis),
- numeric confidence value visible inline or via tooltip.

The frontend must treat confidence as:
- non-blocking,
- non-authoritative,
- and purely assistive.

No frontend logic may interpret confidence as correctness or validation.

### Confidence rendering rules (UX contract)

- Show `field_mapping_confidence` by default in veterinarian UI; `candidate_confidence` is diagnostic-only and must never be rendered in veterinarian UI unless explicit debug mode is enabled.
- Derive low/mid/high confidence bands from `field_mapping_confidence` using cutoffs from the active policy version (temporary hardcoded cutoffs are acceptable only until policy config wiring is complete).
- When backend provides `policy_version` + cutoffs, frontend must consume those values instead of hardcoding band thresholds.
- Avoid visual churn on confidence updates: do not animate rapid oscillations; treat updates as stable presentation changes.
- Smoothing/calibration mechanics are backend responsibilities and must not be reimplemented in frontend.
- Do not expose governance terms such as `pending_review`, `reviewer`, or `governance` in veterinarian-facing UI.

### Confidence tooltip breakdown rendering (MVP)

- Tooltip may show numeric `field_mapping_confidence` and breakdown components, but `field_mapping_confidence` remains the primary visual signal.
- Frontend must render only values provided by backend.
- Frontend must not implement confidence composition math; backend provides composed `field_mapping_confidence`.
- Edge cases:
  - no history: show `Ajuste por histórico de revisiones: 0%`.
  - missing candidate confidence: show `Fiabilidad del candidato: No disponible`.
- Positive/negative/neutral adjustment styling must use existing semantic tokens/classes; do not introduce new colors.
- Keep veterinarian copy free of governance terminology.

### Reviewed toggle UI behavior

- Provide a single action toggle: `Mark as reviewed` / `Reopen`.
- After toggle, refetch both document-list status and current document review payload to avoid stale UI state.
- Toggling reviewed state must not reset or discard edited field values.

---

## API Integration

Server state is managed exclusively via **TanStack Query**.

### Contract authority (backend)
- Endpoint paths, payload shapes, and error semantics are owned by [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) (Appendix B3/B3.2).
- This document references contracts for implementation convenience only; if any conflict exists, [`technical-design.md`](technical-design.md) wins.

### Error handling (authoritative rule)
The frontend MUST branch on `error_code` (and optional `details.reason`) only.
It must not branch on HTTP status alone, message strings, or backend stack traces.

Implement a single API wrapper that:
- Parses the normative error response shape `{ error_code, message, details? }` (Appendix B2.6).
- Throws/returns a typed error that downstream UI code can switch on via `error_code` and `details.reason`.

Patterns:
- `useQuery` for fetching:
  - document lists,
  - document status,
  - document interpretations.
- `useMutation` for:
  - persisting field edits,
  - marking documents as reviewed.
- query invalidation is used to keep UI state consistent after mutations.

No custom caching or duplication of server state logic is introduced.

---

## Sequencing (Authority)

Implementation sequencing and scope are owned by [`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](implementation-plan.md).
This document must not introduce or reorder stories; it only provides implementation notes within each story.

---

## Testing Strategy

Use Vitest + React Testing Library (already used by the repository frontend).

Minimum coverage:
- Continuous scroll: Next/Previous navigation scrolls to the correct page container.
- Active page tracking: scrolling updates the active page label deterministically.
- Progressive enhancement: highlight failures do not block review (no crashes; snippet still visible).
- Error states: UI branches on `error_code` and `details.reason` only (e.g., `CONFLICT` with `NO_COMPLETED_RUN`).

---

## Implementation note

Keep the review experience explainable and non-blocking; introduce additional tooling only when required by a user story.

For deterministic CI and local builds, keep test/setup files out of the production TypeScript compilation scope and validate them through Vitest in the test job.

Repository operations recommendation: protect `main` and require both `quality` and `frontend_test_build` checks before merge.

