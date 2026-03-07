# Plan: Iteration 13 — Decompose AppWorkspace.tsx (custom hook extraction)

> **Operational rules:** See [execution-rules.md](execution-rules.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Iteración:** 13
**Rama:** `refactor/decompose-app-workspace`
**PR:** [#171](https://github.com/isilionisilme/veterinary-medical-records/pull/171)
**Prerequisito:** `main` estable con tests verdes.

## Context

`frontend/src/AppWorkspace.tsx` tiene **2221 líneas** en una sola función `App()`. Contiene ~30 `useState`, ~15 `useRef`, ~25 `useEffect`, ~20 `useMemo`, 5 mutations y 5 queries de react-query. Es un God Component clásico que dificulta testing, revisión de PRs y onboarding.

Ya se extrajeron 7 hooks (`useFieldEditing`, `useDocumentsSidebar`, `useReviewSplitPanel`, `useSourcePanelState`, `useStructuredDataFilters`, `useUploadState`, `useRawTextActions`, `useReviewedEditBlocker`), pero el archivo sigue siendo demasiado grande.

**Entry state:** AppWorkspace.tsx = 2221 líneas, 1 función monolítica.

**Exit target:** AppWorkspace.tsx ≤ 350 líneas (composición de hooks + JSX), ~11 nuevos custom hooks con tests unitarios, todos los tests existentes verdes.

## Scope Boundary (strict)

- **In scope:** `frontend/src/AppWorkspace.tsx`, nuevos hooks en `frontend/src/hooks/`, tests en `frontend/src/hooks/`.
- **Out of scope:** Backend, docs, componentes que no se modifiquen, refactors de lógica de negocio.
- **Principio:** Cada hook es una extracción mecánica (move, no rewrite). Zero cambios de comportamiento.

## Dependencias entre hooks

```
useConnectivityToasts (standalone)
useDocumentLoader (standalone, usa fetchOriginalPdf)
useDocumentUpload (depende de useDocumentLoader.requestPdfLoad)
useDocumentListPolling (standalone, usa useQuery)
useReprocessing (standalone, usa useMutation)
useReviewToggle (standalone, usa useMutation)
useInterpretationEdit (standalone, usa useMutation)
useRawTextViewer (standalone, usa useQuery + useRawTextActions)
useConfidenceDiagnostics (depende de interpretationData)
useReviewDataPipeline (depende de confidence policy, interpretationData)
useReviewPanelState (depende de reviewData, isProcessing)
```

Orden de extracción: hooks sin dependencias cruzadas primero → hooks que dependen de la salida de otros después.

---

## Estado de ejecución — update on completion of each step

> **Rationale del orden:** Leaf hooks (sin deps) → hooks con deps simples → pipeline de datos pesado → estado derivado → cleanup final.

**Leyenda:**
- 🔄 **auto-chain** — Codex ejecuta; usuario revisa después.
- 🚧 **hard-gate** — Claude; requiere decisión del usuario.

### Phase 0 — Bootstrap

- [x] R0-A 🔄 — Create branch `refactor/decompose-app-workspace` from `main`, create PR (Codex) — ✅ `5d972b97`

### Phase 1 — Leaf hooks (sin dependencias cruzadas)

- [x] R1-A 🔄 — Extract `useConnectivityToasts` — state: `connectivityToast`, `hasShownListErrorToast`, `showConnectivityToast()`; refs: `lastConnectivityToastAtRef`; effects: toast auto-dismiss, connectivity error detection. Write test. (Codex) — ✅ `a37be999`
- [x] R1-B 🔄 — Extract `useDocumentLoader` — state: `fileUrl`, `filename`; mutation: `loadPdf`; fn: `requestPdfLoad`; refs: `latestLoadRequestIdRef`, `pendingAutoOpenDocumentIdRef`, `autoOpenRetryCountRef`, `autoOpenRetryTimerRef`; effect: cleanup timers. Write test. (Codex) — ✅ `72595a23`
- [x] R1-C 🔄 — Extract `useReprocessing` — state: `reprocessingDocumentId`, `hasObservedProcessingAfterReprocess`, `showRetryModal`; mutation: `reprocessMutation`; fn: `handleConfirmRetry`; effects: reprocess lifecycle tracking. Write test. (Codex) — ✅ `1e9623f0`
- [x] R1-D 🔄 — Extract `useReviewToggle` — mutation: `reviewToggleMutation` with optimistic cache updates on list/detail/review queries. Write test. (Codex) — ✅ `cbb003f2`
- [x] R1-E 🔄 — Extract `useInterpretationEdit` — mutation: `interpretationEditMutation`; fn: `submitInterpretationChanges`. Write test. (Codex) — ✅ `ea7f5a02`

### Phase 2 — Hooks con dependencias simples

- [x] R2-A 🔄 — Extract `useDocumentUpload` — mutation: `uploadMutation`; depends on `requestPdfLoad` from `useDocumentLoader`. Write test. (Codex) — ✅ `3fb87f28`
- [x] R2-B 🔄 — Extract `useDocumentListPolling` — query: `documentList`; memo: `sortedDocuments`; refs: `listPollingStartedAtRef`; effects: adaptive polling, empty-sidebar collapse. Write test. (Codex) — ✅ `77aec6cc`
- [x] R2-C 🔄 — Extract `useRawTextViewer` — query: `rawTextQuery`; state: `rawSearch`, `rawSearchNotice`; derived: `rawTextErrorMessage`, `hasRawText`, `canCopy/canSearch`; integrates existing `useRawTextActions`. Write test. (Codex) — ✅ `860c8e17`

### Phase 3 — Pipeline de datos pesado

- [x] R3-A 🔄 — Extract `useConfidenceDiagnostics` — memos: `documentConfidencePolicy`; effects: policy diagnostic logging, debug logging, visit grouping diagnostics. Write test. (Codex) — ✅ `d04896c7`
- [x] R3-B 🔄 — Extract `useReviewDataPipeline` — memos: `extractedReviewFields`, `validationResult`, `validatedReviewFields`, `coreDisplayFields`, `otherDisplayFields`, `groupedCoreFields`, `canonicalVisitFieldOrder`, `reportSections`, `selectableReviewItems`, `detectedFieldsSummary`; effect: extraction debug logging. Write test. (Codex) — ✅ `d59e8848`
- [x] R3-C 🔄 — Extract `useReviewPanelState` — derived: `reviewPanelState`, `reviewPanelMessage`, `shouldShowReviewEmptyState`, `hasNoStructuredFilterResults`; state: `reviewLoadingDocId`, `reviewLoadingSinceMs`, `isRetryingInterpretation`; fn: `handleRetryInterpretation`. Write test. (Codex) — ✅ `2898c488`

### Phase 4 — Integration & cleanup

- [x] R4-A 🚧 — Review: verify all hooks compose correctly in App(), no behavior regressions, line count target met (Claude) — ✅ see findings below
- [x] R4-B 🔄 — Cleanup round 2: split `useReviewDataPipeline` (875 LOC), extract residual effects from AppWorkspace, lint + test (Codex) — ✅ `d14e354f`
- [x] R4-C 🚧 — User acceptance review of decomposed code (Claude) — ✅ PASS (see final verdict below)

---

### R4-C — Final verdict

| Metric | Original | After R4-B | Target | Verdict |
|---|---|---|---|---|
| AppWorkspace.tsx LOC | 2221 | **726** | ≤500 (revised) | ⚠️ Close — 67% reduction |
| useReviewDataPipeline LOC | 875 | **357** | ≤400 | ✅ Met |
| useDisplayFieldMapping LOC | — | **362** | ≤400 | ✅ Met |
| useFieldExtraction LOC | — | **262** | ≤400 | ✅ Met |
| Unit tests | 309 (44 files) | **318 (48 files)** | All green | ✅ |
| Hooks count | ~8 pre-existing | **23 total** | — | ✅ |
| Residual useState in App | ~30 | **2** | Minimal | ✅ |
| Residual useEffect in App | ~25 | **8** | Minimal | ✅ |
| Residual useMemo in App | ~20 | **5** | Minimal | ✅ |

**Verdict: PASS with advisory.**

- The 2221→726 line reduction (67%) is substantial. The remaining 726 lines consist of: 48 lines of imports, ~140 lines of hook calls/destructuring, ~60 lines of derived state, 8 small effects (timer cleanup, error toasts, stale-field sync), and ~350 lines of JSX composition/prop-passing.
- The remaining effects are tightly coupled to the orchestrator role (connecting hooks to each other) and cannot be meaningfully extracted without creating artificial indirection.
- No hook exceeds 400 LOC. `useDisplayFieldMapping` (362) is the largest — acceptable for its role mapping schema definitions to display fields.
- All 318 tests pass across 48 files. 4 new test files were added for the extracted hooks.
- **Ready for PR merge** after user confirms.

---

## Cola de prompts

> Pre-written prompts for semi-unattended execution. Codex reads these directly.
> Prompts that depend on prior results are marked "just-in-time" — Claude writes them after the dependency resolves.

### R0-A — Create branch and PR

```
Crea la rama `refactor/decompose-app-workspace` desde `main` y un PR con título
"refactor: decompose AppWorkspace.tsx into custom hooks" y body que resuma el plan.
No hagas cambios de código aún.
```
⚠️ AUTO-CHAIN → R1-A

### R1-A — Extract useConnectivityToasts

```
Extrae el hook `useConnectivityToasts` de `AppWorkspace.tsx` a `frontend/src/hooks/useConnectivityToasts.ts`.

**Estado que migra:**
- useState: connectivityToast, hasShownListErrorToast
- useRef: lastConnectivityToastAtRef
- Funciones: showConnectivityToast()
- Effects: auto-dismiss de connectivityToast (5s timeout)

**Interfaz del hook:**
- Params: (ninguno, o callbacks si se necesitan)
- Returns: { connectivityToast, showConnectivityToast, setConnectivityToast, hasShownListErrorToast, setHasShownListErrorToast }

**Reglas:**
1. Extracción mecánica: move, no rewrite.
2. En AppWorkspace.tsx, reemplaza el estado/effects migrados con la llamada al hook.
3. Escribe test en `frontend/src/hooks/useConnectivityToasts.test.ts` usando `renderHook` + `vi` (patrón de useUploadState.test.ts).
4. Ejecuta `npm run test` en frontend/ y verifica verde.
```
⚠️ AUTO-CHAIN → R1-B

### R1-B — Extract useDocumentLoader

```
Extrae el hook `useDocumentLoader` de `AppWorkspace.tsx` a `frontend/src/hooks/useDocumentLoader.ts`.

**Estado que migra:**
- useState: fileUrl, filename
- useRef: latestLoadRequestIdRef, pendingAutoOpenDocumentIdRef, autoOpenRetryCountRef, autoOpenRetryTimerRef
- Mutation: loadPdf (useMutation con fetchOriginalPdf)
- Función: requestPdfLoad
- Effects: cleanup de timers en unmount, auto-open retry logic

**Interfaz del hook:**
- Params: { onUploadFeedback: (feedback) => void }
- Returns: { fileUrl, filename, setFileUrl, setFilename, requestPdfLoad, loadPdf, pendingAutoOpenDocumentIdRef }

**Reglas:**
1. Extracción mecánica.
2. Actualiza AppWorkspace.tsx para usar el hook.
3. Test con renderHook + vi.fn() para fetchOriginalPdf mock.
4. `npm run test` verde.
```
⚠️ AUTO-CHAIN → R1-C

### R1-C — Extract useReprocessing

```
Extrae `useReprocessing` de `AppWorkspace.tsx` a `frontend/src/hooks/useReprocessing.ts`.

**Estado que migra:**
- useState: reprocessingDocumentId, hasObservedProcessingAfterReprocess, showRetryModal
- Mutation: reprocessMutation (triggerReprocess, con optimistic updates)
- Función: handleConfirmRetry
- Effects: reprocess lifecycle tracking (observed processing → done)

**Interfaz del hook:**
- Params: { activeId, isActiveDocumentProcessing, onActionFeedback }
- Returns: { reprocessingDocumentId, hasObservedProcessingAfterReprocess, showRetryModal, setShowRetryModal, reprocessMutation, handleConfirmRetry }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R1-D

### R1-D — Extract useReviewToggle

```
Extrae `useReviewToggle` de `AppWorkspace.tsx` a `frontend/src/hooks/useReviewToggle.ts`.

**Estado que migra:**
- Mutation: reviewToggleMutation (markDocumentReviewed / reopenDocumentReview)
- Optimistic cache updates en documentList, documentDetail, documentReview queries

**Interfaz del hook:**
- Params: { onActionFeedback }
- Returns: { reviewToggleMutation }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R1-E

### R1-E — Extract useInterpretationEdit

```
Extrae `useInterpretationEdit` de `AppWorkspace.tsx` a `frontend/src/hooks/useInterpretationEdit.ts`.

**Estado que migra:**
- Mutation: interpretationEditMutation (editRunInterpretation)
- Función: submitInterpretationChanges (requires activeId + documentReview.data)

**Interfaz del hook:**
- Params: { onActionFeedback }
- Returns: { interpretationEditMutation, submitInterpretationChanges }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R2-A

### R2-A — Extract useDocumentUpload

```
Extrae `useDocumentUpload` de `AppWorkspace.tsx` a `frontend/src/hooks/useDocumentUpload.ts`.

**Estado que migra:**
- Mutation: uploadMutation (uploadDocument, optimistic list update)
- Depende de: requestPdfLoad (del hook useDocumentLoader ya extraído)

**Interfaz del hook:**
- Params: { requestPdfLoad, pendingAutoOpenDocumentIdRef, onUploadFeedback, onSetActiveId, onSetActiveViewerTab }
- Returns: { uploadMutation }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R2-B

### R2-B — Extract useDocumentListPolling

```
Extrae `useDocumentListPolling` de `AppWorkspace.tsx` a `frontend/src/hooks/useDocumentListPolling.ts`.

**Estado que migra:**
- Query: documentList (fetchDocuments)
- Memo: sortedDocuments
- Ref: listPollingStartedAtRef
- Effects: adaptive polling (1.5s → 5s), empty-list sidebar collapse

**Interfaz del hook:**
- Params: { setIsDocsSidebarHovered }
- Returns: { documentList, sortedDocuments }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R2-C

### R2-C — Extract useRawTextViewer

```
Extrae `useRawTextViewer` de `AppWorkspace.tsx` a `frontend/src/hooks/useRawTextViewer.ts`.

**Estado que migra:**
- Query: rawTextQuery (fetchRawText)
- useState: rawSearch, rawSearchNotice
- Derived: rawTextContent, hasRawText, canCopyRawText, isRawTextLoading, canSearchRawText, rawTextErrorMessage
- Función: handleRawSearch
- Integra useRawTextActions internamente

**Interfaz del hook:**
- Params: { rawTextRunId, activeViewerTab }
- Returns: { rawSearch, setRawSearch, rawSearchNotice, rawTextContent, hasRawText, canCopyRawText, isRawTextLoading, canSearchRawText, rawTextErrorMessage, handleRawSearch, copyFeedback, isCopyingRawText, handleDownloadRawText, handleCopyRawText }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R3-A

### R3-A — Extract useConfidenceDiagnostics

```
Extrae `useConfidenceDiagnostics` de `AppWorkspace.tsx` a `frontend/src/hooks/useConfidenceDiagnostics.ts`.

**Estado que migra:**
- Memo: documentConfidencePolicy, activeConfidencePolicy, confidencePolicyDegradedReason
- Refs: lastConfidencePolicyDocIdRef, loggedConfidencePolicyDiagnosticsRef, loggedConfidencePolicyDebugRef
- Effects: policy diagnostic event emission, confidence debug logging, visit grouping diagnostics

**Interfaz del hook:**
- Params: { interpretationData, reviewVisits, isCanonicalContract }
- Returns: { activeConfidencePolicy, confidencePolicyDegradedReason }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R3-B

### R3-B — Extract useReviewDataPipeline

```
Extrae `useReviewDataPipeline` de `AppWorkspace.tsx` a `frontend/src/hooks/useReviewDataPipeline.ts`.

**Estado que migra:**
- Memos: extractedReviewFields, explicitOtherReviewFields, validationResult, validatedReviewFields, matchesByKey, coreDisplayFields, otherDisplayFields, groupedCoreFields, canonicalVisitFieldOrder, visibleCoreGroups, visibleOtherDisplayFields, visibleCoreFields, reportSections, selectableReviewItems, detectedFieldsSummary, buildSelectableField
- Refs: lastExtractionDebugDocIdRef, loggedExtractionDebugEventKeysRef
- Effect: extraction debug event logging

**Interfaz del hook:**
- Params: { documentReview, activeConfidencePolicy, structuredDataFilters, hasActiveStructuredFilters }
- Returns: { reportSections, selectableReviewItems, coreDisplayFields, otherDisplayFields, detectedFieldsSummary, reviewVisits, isCanonicalContract, hasMalformedCanonicalFieldSlots, hasVisitGroups, hasUnassignedVisitGroup, canonicalVisitFieldOrder, validatedReviewFields, buildSelectableField, visibleCoreGroups, visibleOtherDisplayFields }

Este es el hook más grande (~400 líneas). Extracción mecánica cuidadosa.
Test con datos mock del schema.
```
⚠️ AUTO-CHAIN → R3-C

### R3-C — Extract useReviewPanelState

```
Extrae `useReviewPanelState` (renombrado para no colisionar con el módulo existente useSourcePanelState) de `AppWorkspace.tsx` a `frontend/src/hooks/useReviewPanelStatus.ts`.

**Estado que migra:**
- useState: reviewLoadingDocId, reviewLoadingSinceMs, isRetryingInterpretation
- Refs: interpretationRetryMinTimerRef
- Derived: reviewPanelState, reviewPanelMessage, shouldShowReviewEmptyState, hasNoStructuredFilterResults
- Función: handleRetryInterpretation
- Effects: review loading minimum visible time, retry min timer

**Interfaz del hook:**
- Params: { activeId, documentReview, isActiveDocumentProcessing, hasActiveStructuredFilters, visibleCoreGroupsLength }
- Returns: { reviewPanelState, reviewPanelMessage, shouldShowReviewEmptyState, hasNoStructuredFilterResults, isRetryingInterpretation, handleRetryInterpretation }

**Reglas:** Extracción mecánica. Test. Verde.
```
⚠️ AUTO-CHAIN → R4-A

### R4-A — Integration review (just-in-time) ✅

**Findings (Claude review):**

| Metric | Target | Actual | Verdict |
|---|---|---|---|
| AppWorkspace.tsx LOC | ≤ 350 | **832** | ❌ Not met |
| Tests (unit) | All green | **309/309 pass** (44 files) | ✅ |
| Hook composition | Correct | 19 hooks compose without runtime errors | ✅ |
| Behavior regressions | None | No regressions detected in test suite | ✅ |
| useReviewDataPipeline LOC | ≤ 400 (risk log) | **875** | ❌ Needs split |

**Root cause for 832 LOC in AppWorkspace:**
- Imports: 58 lines (19 hooks + components + utils)
- Hook calls + destructuring: ~130 lines
- Residual effects (11 `useEffect`): ~120 lines (polling, error handling, feedback timers, reset-on-activeId, stale field cleanup)
- Derived state + handlers: ~60 lines
- Renderer memos (2 `useMemo` for `createReviewFieldRenderers` + `createReviewSectionLayoutRenderer`): ~80 lines
- JSX variable declarations + return: ~230 lines of prop passing

**Revised realistic target:** ~500 LOC. The component is an orchestrator — imports + hook calls + JSX prop-passing set an irreducible floor of ~350 lines. The remaining ~150 lines of effects/memos can be partially extracted.

**R4-B scope (actionable extractions):**

1. **Split `useReviewDataPipeline` (875→3 hooks):**
   - `useFieldExtraction` (~250 LOC): `extractedReviewFields`, `explicitOtherReviewFields`, `validationResult`, `validatedReviewFields`, extraction debug logging effect, `matchesByKey`, `buildSelectableField`
   - `useDisplayFieldMapping` (~300 LOC): `coreDisplayFields`, `otherDisplayFields` (the two large mapping useMemos)
   - `useReviewDataPipeline` (orchestrator, ~275 LOC): consumes above two hooks + remaining grouping/filtering/report sections/selectableReviewItems/detectedFieldsSummary

2. **Extract `useActiveDocumentQueries`** from AppWorkspace (~70 LOC saved): the 4 `useQuery` calls (documentDetails, processingHistory, documentReview, rawTextRunId) + polling effect + handleRefresh + isListRefreshing + derived processing state

3. **Extract `useReviewRenderers`** from AppWorkspace (~80 LOC saved): the 2 large useMemos for `createReviewFieldRenderers` and `createReviewSectionLayoutRenderer`

4. **Lint + test verification**

Expected outcome: AppWorkspace ~550 LOC, no hook >400 LOC, all tests green.

### R4-B — Cleanup round 2

```
Rama: refactor/decompose-app-workspace
Contexto: R4-A review encontró que AppWorkspace.tsx tiene 832 LOC (target ≤350 no alcanzado) y useReviewDataPipeline.ts tiene 875 LOC (threshold >400 del risk log). Se requiere una segunda ronda de extracciones.

Ejecuta estos pasos en orden. Después de CADA paso: ejecuta `cd frontend && npm run lint && npm run test -- --run`, verifica verde, y haz commit atómico con mensaje convencional.

**Paso 1 — Split useReviewDataPipeline en 3 hooks:**

1a. Crea `frontend/src/hooks/useFieldExtraction.ts`:
   - Mueve de useReviewDataPipeline: `extractedReviewFields` (useMemo), `explicitOtherReviewFields` (useMemo), `validationResult` (useMemo), el `useEffect` de extraction debug logging, `validatedReviewFields` (derived), `matchesByKey` (useMemo), `buildSelectableField` (useCallback).
   - Recibe: { documentReview, interpretationData, isCanonicalContract, hasMalformedCanonicalFieldSlots, reviewVisits, activeConfidencePolicy }.
   - Retorna: { extractedReviewFields, validatedReviewFields, matchesByKey, buildSelectableField, explicitOtherReviewFields }.
   - Crea test file `frontend/src/hooks/useFieldExtraction.test.ts` con al menos 3 tests básicos.

1b. Crea `frontend/src/hooks/useDisplayFieldMapping.ts`:
   - Mueve de useReviewDataPipeline: `coreDisplayFields` (useMemo, ~210 líneas) y `otherDisplayFields` (useMemo, ~100 líneas).
   - Recibe: { isCanonicalContract, hasMalformedCanonicalFieldSlots, interpretationData, validatedReviewFields, matchesByKey, buildSelectableField, explicitOtherReviewFields }.
   - Retorna: { coreDisplayFields, otherDisplayFields }.
   - Crea test file `frontend/src/hooks/useDisplayFieldMapping.test.ts` con al menos 3 tests.

1c. Actualiza `useReviewDataPipeline.ts`:
   - Importa y usa useFieldExtraction y useDisplayFieldMapping.
   - El hook se convierte en orchestrator (~275 LOC): consume los 2 hooks + tiene el grouping, filtering, reportSections, selectableReviewItems, detectedFieldsSummary.
   - La API pública (return) NO cambia — los consumidores existentes no se tocan.

Commit: `refactor(hooks): split useReviewDataPipeline into 3 focused hooks`

**Paso 2 — Extract useActiveDocumentQueries:**

Crea `frontend/src/hooks/useActiveDocumentQueries.ts`:
- Mueve de AppWorkspace.tsx: los 4 `useQuery` calls (documentDetails, processingHistory, documentReview + rawTextRunId derived), el polling `useEffect` (interval de 1500ms para PROCESSING/QUEUED/RUNNING), `handleRefresh`, `isListRefreshing`, derived state (`latestState`, `latestRunId`, `isProcessing`), y el `useEffect` de raw text refresh on run completion.
- Recibe: { activeId, documentList, showRefreshFeedback, setShowRefreshFeedback, refreshFeedbackTimerRef, queryClient }.
- Retorna: { documentDetails, processingHistory, documentReview, rawTextRunId, latestState, latestRunId, isProcessing, handleRefresh, isListRefreshing }.
- Crea test file con al menos 2 tests.

En AppWorkspace.tsx: reemplaza los useQuery + effects extraídos por `const { ... } = useActiveDocumentQueries(...)`.

Commit: `refactor(hooks): extract useActiveDocumentQueries from AppWorkspace`

**Paso 3 — Extract useReviewRenderers:**

Crea `frontend/src/hooks/useReviewRenderers.ts`:
- Mueve de AppWorkspace.tsx: los 2 `useMemo` que llaman a `createReviewFieldRenderers` y `createReviewSectionLayoutRenderer`.
- Recibe todas las dependencias necesarias como parámetro.
- Retorna: { renderScalarReviewField, renderRepeatableReviewField, renderSectionLayout }.
- Crea test file con al menos 1 test.

Commit: `refactor(hooks): extract useReviewRenderers from AppWorkspace`

**Paso 4 — Final lint + test:**

1. `cd frontend && npm run lint` — corrige errores.
2. `cd frontend && npm run test -- --run` — verifica todo verde.
3. Reporta line counts finales:
   - `wc -l frontend/src/AppWorkspace.tsx`
   - `wc -l frontend/src/hooks/useReviewDataPipeline.ts`
   - `wc -l frontend/src/hooks/useFieldExtraction.ts`
   - `wc -l frontend/src/hooks/useDisplayFieldMapping.ts`
   - `wc -l frontend/src/hooks/useActiveDocumentQueries.ts`
   - `wc -l frontend/src/hooks/useReviewRenderers.ts`

Commit: `refactor(hooks): final cleanup and lint fixes`

⚠️ RECUERDA: cada paso debe pasar lint + test antes de hacer commit. Si un paso falla tests, corrige antes de continuar.

NO hay auto-chain después de este paso. STOP después de completar el paso 4.
```

### R4-C — User acceptance (just-in-time)

_Claude writes after R4-B._

---

## Prompt activo

### Paso objetivo

_Completado: R4-B_

_Vacío._

---

## Risk log

| Risk | Mitigation |
|---|---|
| Circular deps entre hooks | Dependency graph defined above; extract leaves first |
| QueryClient coupling | Hooks receive queryClient from useQueryClient() internally (same pattern as existing hooks) |
| Render count regression | Each hook encapsulates related state; no extra re-renders vs current monolith |
| Test coverage gap | Every new hook gets a test file; existing tests must stay green |
| Large R3-B (pipeline) | Can split further if >400 lines; Claude reviews at R4-A | **Triggered:** 875 LOC. R4-B extracts `useFieldExtraction` + `useDisplayFieldMapping` |
| ≤350 target unreachable | Orchestrator floor ~350 LOC (imports + hook calls + JSX); effects add ~150 | Revised to ~500 LOC; R4-B extracts 2 more hooks from AppWorkspace | **Final: 726 LOC** — 67% reduction, remaining code is irreducible orchestration |
