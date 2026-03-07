# Plan: Iteration 14 — Decompose PdfViewer.tsx & extract debug/rendering modules

> **Operational rules:** See [execution-rules.md](../execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Iteración:** 14
**Rama:** `refactor/decompose-pdf-viewer`
**PR:** [#174](https://github.com/isilionisilme/veterinary-medical-records/pull/174)
**Prerequisito:** Iteration 13 merged to `main`.

## Context

`frontend/src/components/PdfViewer.tsx` tiene **944 líneas** en un solo componente. Contiene ~7 `useState`, ~13 `useRef`, ~13 `useEffect`, 1 `useMemo`, y ~200 líneas de utilidades de debug diagnóstico embebidas (transform analysis, snapshot capture). Es el segundo archivo más grande del frontend.

El componente mezcla cuatro responsabilidades distintas:
1. **Debug diagnostics** (~200 LOC): `analyzeTransform`, `captureDebugSnapshot`, `getNodeId`, debug flags — funciones puras que no necesitan ser hooks.
2. **PDF document loading** (~80 LOC): fetch/load PDF, manage `PDFDocumentProxy` lifecycle.
3. **Page rendering** (~200 LOC): canvas rendering, render task management, text extraction, retry logic.
4. **Zoom & navigation** (~100 LOC): zoom persistence, wheel handler, page tracking, intersection observer, scroll-to-page.
5. **Toolbar + viewer JSX** (~150 LOC): UI composition.

### Otros archivos analizados (no incluidos en este plan)

| Archivo | Líneas | Decisión |
|---|---|---|
| `PdfViewerPanel.tsx` | 559 | Aceptable — mostly JSX props wiring |
| `ReviewFieldRenderers.tsx` | 546 | Aceptable — factory pattern justified |
| `ReviewSectionLayout.tsx` | 491 | Aceptable |
| `appWorkspaceUtils.ts` | 470 | Evaluar en Iter 15 si sigue creciendo |
| `FieldEditDialog.tsx` | 452 | Aceptable — complex dialog |
| `DocumentsSidebar.tsx` | 442 | Aceptable |
| `pdf_extraction_nodeps.py` (backend) | 1014 | **Candidato Iter 15** — fuera de scope frontend |

**Entry state:** PdfViewer.tsx = 944 líneas, 1 componente monolítico.

**Exit target:** PdfViewer.tsx ≤ 200 líneas (composición de hooks + JSX), 4 nuevos módulos (1 lib + 3 hooks), tests unitarios, todos los tests existentes verdes.

## Scope Boundary (strict)

- **In scope:** `frontend/src/components/PdfViewer.tsx`, nuevos hooks en `frontend/src/hooks/`, nuevo módulo en `frontend/src/lib/`, tests.
- **Out of scope:** Backend, AppWorkspace (Iter 13), otros componentes que no se modifiquen.
- **Principio:** Cada extracción es mecánica (move, no rewrite). Zero cambios de comportamiento.

## Arquitectura de destino

```
PdfViewer.tsx (~200 LOC)
├── usePdfZoom (hook)           — zoom state, localStorage, wheel handler
├── usePdfDocument (hook)       — PDF load, PDFDocumentProxy lifecycle
├── usePdfRenderer (hook)       — canvas rendering, render tasks, text extraction, retry
├── usePdfNavigation (hook)     — page tracking, intersection observer, scrollToPage
└── lib/pdfDebug.ts (module)    — debugFlags, analyzeTransform, captureDebugSnapshot, getNodeId
```

### Dependencias

```
lib/pdfDebug.ts (standalone — pure functions)
usePdfZoom (standalone)
usePdfDocument (standalone, depende de fileUrl)
usePdfRenderer (depende de usePdfDocument.pdfDoc, usePdfZoom.zoomLevel, pdfDebug)
usePdfNavigation (depende de usePdfRenderer.pageRefs, pdfDoc)
```

---

## Estado de ejecución — update on completion of each step

**Leyenda:**
- 🔄 **auto-chain** — Codex ejecuta; usuario revisa después.
- 🚧 **hard-gate** — Claude; requiere decisión del usuario.

### Phase 0 — Bootstrap

- [x] P0-A 🔄 — Create branch `refactor/decompose-pdf-viewer` from `main`, create PR (Codex)

### Phase 1 — Pure utility extraction

- [x] P1-A 🔄 — Extract `lib/pdfDebug.ts` — move `analyzeTransform()`, `captureDebugSnapshot()`, `getNodeId()`, debug flags computation, related types and constants (`PDF_ZOOM_STORAGE_KEY`, etc.). Write test for `analyzeTransform` (pure function). (Codex)

### Phase 2 — Hook extractions (leaf → dependent)

- [x] P2-A 🔄 — Extract `usePdfZoom` — state: `zoomLevel`; effects: localStorage persistence, ctrl+wheel handler; exports: `zoomLevel`, `setZoomLevel`, `canZoomIn`, `canZoomOut`, `zoomPercent`, zoom control functions. Write test. (Codex)
- [x] P2-B 🔄 — Extract `usePdfDocument` — state: `pdfDoc`, `totalPages`, `loading`, `error`; effect: PDF fetch/load lifecycle with cleanup. Write test. (Codex)
- [x] P2-C 🔄 — Extract `usePdfRenderer` — refs: `canvasRefs`, `pageRefs`, `renderedPages`, `renderingPages`, `renderSessionRef`, `renderTasksByPageRef`, `renderTaskStatusRef`; state: `pageTextByIndex`; effects: render-all-pages with retry, session/document identity guards; fn: `cancelAllRenderTasks`. Write test. (Codex)
- [x] P2-D 🔄 — Extract `usePdfNavigation` — state: `pageNumber`; refs: `scrollRef`, `contentRef`; effects: intersection observer page tracking, focus-page scroll; fn: `scrollToPage`; derived: `canGoBack`, `canGoForward`, `showPageNavigation`, snippet highlight detection. Write test. (Codex)

### Phase 3 — Component cleanup

- [x] P3-A 🔄 — Optionally extract `PdfViewerToolbar` sub-component (toolbar JSX ~80 lines) if PdfViewer still exceeds 200 lines. Clean up dead imports, verify lint. (Codex)

### Phase 4 — Integration & closure

- [x] P4-A 🚧 — Review: verify hooks compose correctly, no behavior regressions, existing PdfViewer tests pass, line count target met (Claude)
- [x] P4-B 🔄 — Final cleanup: `npm run lint`, `npm run test`, E2E tests, report final line count (Codex)
- [x] P4-C 🚧 — User acceptance review (Claude)

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.

### P0-A — Create branch and PR

```
Crea la rama `refactor/decompose-pdf-viewer` desde `main` y un PR con título
"refactor: decompose PdfViewer.tsx into hooks and utility modules" y body que resuma el plan.
No hagas cambios de código aún.
```
⚠️ AUTO-CHAIN → P1-A

### P1-A — Extract lib/pdfDebug.ts

```
Extrae las utilidades de debug de `PdfViewer.tsx` a `frontend/src/lib/pdfDebug.ts`.

**Código que migra:**
- Constantes: PDF_ZOOM_STORAGE_KEY, MIN_ZOOM_LEVEL, MAX_ZOOM_LEVEL, ZOOM_STEP, clampZoomLevel()
- Función pura: analyzeTransform(rawTransform) → { determinant, negativeDeterminant, hasMirrorScale }
- Función: createDebugFlags() — el useMemo actual que lee import.meta.env y URLSearchParams
- Tipo: DebugFlags (el shape { enabled, noTransformSubtree, noMotion, hardRemountCanvas })
- Funciones de snapshot: getNodeId (needs ref maps as params), captureDebugSnapshot (needs state as params)
- Exports necesarios para que PdfViewer los importe

**Reglas:**
1. Las funciones `getNodeId` y `captureDebugSnapshot` reciben sus refs/state como parámetros (no dependen de closure del componente).
2. `analyzeTransform` es pura — test unitario directo.
3. En PdfViewer.tsx, reemplaza el código inline con imports de pdfDebug.ts.
4. `npm run test` verde.
```
⚠️ AUTO-CHAIN → P2-A

### P2-A — Extract usePdfZoom

```
Extrae `usePdfZoom` de `PdfViewer.tsx` a `frontend/src/hooks/usePdfZoom.ts`.

**Estado que migra:**
- useState: zoomLevel (con initializer que lee localStorage)
- Effects: localStorage persistence (write on change), ctrl+wheel zoom handler
- Funciones: zoom in/out/fit handlers

**Interfaz del hook:**
- Params: { scrollRef: RefObject<HTMLDivElement | null> }
- Returns: { zoomLevel, setZoomLevel, canZoomIn, canZoomOut, zoomPercent, handleZoomIn, handleZoomOut, handleZoomFit }

**Reglas:** Extracción mecánica. Test con renderHook + vi. Verde.
```
⚠️ AUTO-CHAIN → P2-B

### P2-B — Extract usePdfDocument

```
Extrae `usePdfDocument` de `PdfViewer.tsx` a `frontend/src/hooks/usePdfDocument.ts`.

**Estado que migra:**
- useState: pdfDoc, totalPages, loading, error
- Effect: PDF fetch + pdfjsLib.getDocument lifecycle (fileUrl dependency)
- Effect: scroll-to-top on new fileUrl
- Effect: pdfDoc cleanup/destroy on unmount
- Fn: cancelAllRenderTasks (pass as callback or integrate)

**Interfaz del hook:**
- Params: { fileUrl, scrollRef, onRenderSessionReset?: () => void }
- Returns: { pdfDoc, totalPages, loading, error }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → P2-C

### P2-C — Extract usePdfRenderer

```
Extrae `usePdfRenderer` de `PdfViewer.tsx` a `frontend/src/hooks/usePdfRenderer.ts`.

**Estado que migra:**
- Refs: canvasRefs, renderedPages, renderingPages, renderSessionRef, renderTasksByPageRef, renderTaskStatusRef, currentDocumentIdRef, nodeIdentityMapRef, nodeIdentityCounterRef, lastCanvasNodeByPageRef
- State: pageTextByIndex, containerWidth
- Effects: renderAllPages (the big ~200-line effect), containerWidth ResizeObserver, session reset on zoom/doc change
- Fn: cancelAllRenderTasks

**Interfaz del hook:**
- Params: { pdfDoc, totalPages, zoomLevel, documentId, contentRef, debugFlags }
- Returns: { canvasRefs, pageRefs, pageTextByIndex, containerWidth, renderSessionRef }

**Reglas:** Este es el hook más grande (~250 líneas). Extracción mecánica cuidadosa. Test. Verde.
```
⚠️ AUTO-CHAIN → P2-D

### P2-D — Extract usePdfNavigation

```
Extrae `usePdfNavigation` de `PdfViewer.tsx` a `frontend/src/hooks/usePdfNavigation.ts`.

**Estado que migra:**
- useState: pageNumber
- Effects: intersection observer for page tracking, focus-page scroll effect
- Fn: scrollToPage
- Derived: canGoBack, canGoForward, showPageNavigation, normalizedSnippet, isSnippetLocated

**Interfaz del hook:**
- Params: { pdfDoc, totalPages, loading, error, fileUrl, focusPage, highlightSnippet, focusRequestId, scrollRef, pageRefs, pageTextByIndex }
- Returns: { pageNumber, canGoBack, canGoForward, showPageNavigation, isSnippetLocated, scrollToPage }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → P3-A

### P3-A — Optional toolbar extraction + cleanup

```
1. Si PdfViewer.tsx sigue por encima de 200 líneas, extrae `PdfViewerToolbar.tsx` con el JSX del toolbar.
2. Elimina imports no usados en PdfViewer.tsx.
3. Ejecuta `npm run lint` y corrige errores.
4. `npm run test` verde.
5. Reporta line count de PdfViewer.tsx.
```
⚠️ AUTO-CHAIN → P4-A

### P4-A — Integration review (just-in-time)

_Claude writes after P3-A is complete._

### P4-B — Final cleanup

```
1. Revisa PdfViewer.tsx: elimina imports no usados, verifica que no queden useState/useRef/useEffect huérfanos.
2. Dead code cleanup: elimina el parámetro `onRenderSessionReset` de `usePdfDocument`
   (tipo, destructuring, llamada en loadPdf, dependency array) — ya no se usa desde PdfViewer.
   Actualiza `usePdfDocument.test.tsx` removiendo la aserción sobre `onRenderSessionReset`.
3. Ejecuta `npm run lint` en frontend/ y corrige errores.
4. Ejecuta `npm run test` en frontend/ y verifica todo verde.
5. Ejecuta tests e2e: `npx playwright test`.
6. Reporta line count final de PdfViewer.tsx.
```

### P4-C — User acceptance (just-in-time)

_Claude writes after P4-B._

---

## Prompt activo

### Paso objetivo: P4-B — Final cleanup

```
1. Revisa PdfViewer.tsx: elimina imports no usados, verifica que no queden useState/useRef/useEffect huérfanos.
2. Dead code cleanup: elimina el parámetro `onRenderSessionReset` de `usePdfDocument`
   (tipo, destructuring, llamada en loadPdf, dependency array) — ya no se usa desde PdfViewer.
   Actualiza `usePdfDocument.test.tsx` removiendo la aserción sobre `onRenderSessionReset`.
3. Ejecuta `npm run lint` en frontend/ y corrige errores.
4. Ejecuta `npm run test` en frontend/ y verifica todo verde.
5. Ejecuta tests e2e: `npx playwright test`.
6. Reporta line count final de PdfViewer.tsx.
```
⚠️ AUTO-CHAIN → P4-C

---

## Risk log

| Risk | Mitigation |
|---|---|
| pdf.js canvas lifecycle breaks | `usePdfRenderer` keeps exact same ref patterns; render session guards preserved |
| Debug snapshots lose component closure | `captureDebugSnapshot` refactored to accept state as params instead of closure |
| Zoom persistence race condition | Same localStorage write pattern; single source of truth in `usePdfZoom` |
| IntersectionObserver timing | `usePdfNavigation` preserves exact same observer setup and threshold config |
| Large P2-C (renderer) | ~250 lines is acceptable for a rendering hook; can split render loop from task management if needed |
| E2E tests brittle with PdfViewer | Existing data-testid attributes preserved; no DOM structure changes |
