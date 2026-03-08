# Plan: Processing History UI — Visibility for Evaluators

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for execution protocol and hard-gates.

**Branch:** `veterinary-medical-records/feat/processing-history-ui`
**PR:** Pending (branch PR not created yet)
**User Story:** [US-78](../Backlog/us-78-enhanced-processing-history-ui-for-evaluator-obser.md)
**Prerequisite:** `main` stable with green tests.
**Worktree:** `D:/Git/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** `Codex 5.3`
**Automation Mode:** `Supervisado`
**Iteration:** 20
**Mode:** lightweight feature — no API changes required.

---

## Context

### What exists today

The backend already persists **all processing runs** append-only with per-run artifacts:

| Layer | What exists | Status |
|-------|-------------|--------|
| **DB schema** | `processing_runs` table with `run_id`, `state`, `failure_type`, timestamps | ✅ Complete |
| **Filesystem** | `{doc_id}/runs/{run_id}/raw-text.txt` — per-run raw text | ✅ Complete |
| **API** | `GET /documents/{id}/processing-history` → all runs + steps | ✅ Complete |
| **API** | `GET /runs/{run_id}/artifacts/raw-text` → raw text for any run | ✅ Complete |
| **Frontend fetch** | `fetchProcessingHistory()` + React Query (`["documents", "history", id]`) | ✅ Complete |
| **Frontend types** | `ProcessingHistoryRun`, `ProcessingStep`, `StepGroup` | ✅ Complete |
| **Frontend rendering** | Inline in `PdfViewerPanel.tsx` "Technical" tab — flat list of runs + steps | ✅ Basic |

### The gap

The "Technical" tab shows processing history as a flat chronological list. For evaluators, several observability features are missing:

1. **No run comparison view** — cannot see how interpretations differ between runs.
2. **No per-run raw text access** — the raw text tab always shows the latest run; the API supports any `run_id` but the UI doesn't expose it.
3. **No duration/performance summary** — step durations are shown per-step but there's no run-level total or trend.
4. **Run cards lack visual hierarchy** — all runs look identical; no quick distinction between latest vs. historical, success vs. failure.

### Why this matters for evaluators

This feature showcases:

- **Append-only architecture** working end-to-end.
- **Full pipeline traceability** — every processing attempt is preserved and inspectable.
- **Observable system behavior** — step timings, retries, failure types visible without logs.

---

## Objective

1. Evaluators can visually distinguish runs by state (success/failure/timeout) and identify the latest run at a glance.
2. Evaluators can view raw text from any historical run (not just the latest).
3. Run-level total duration is visible.
4. No backend changes required — all data is already served by existing endpoints.
5. No regressions in existing E2E tests.

## Scope Boundary (strict)

- **In scope:** Frontend-only changes to enhance the "Technical" tab in `PdfViewerPanel.tsx`; new or extracted component for run cards; wiring existing `GET /runs/{run_id}/artifacts/raw-text` to a "view raw text" action per run; run-level duration display; visual state badges.
- **Out of scope:** Backend API changes; interpretation diff/comparison between runs; new tabs or panels; changes to the raw text main tab behavior; performance metrics/trends dashboard; changes to processing logic.

---

## Commit recommendations (inline, non-blocking)

- After `P0-B + P0-C`: recommend `refactor(plan-p0): extract ProcessingHistorySection component`.
- After `P1-A..P1-D`: recommend `feat(plan-p1): enhanced run cards with state badges and duration`.
- After `P2-A..P2-C`: recommend `feat(plan-p2): per-run raw text viewer`.
- After `P3-A..P3-C`: recommend `test(plan-p3): processing history UI tests`.
- In `Supervisado`, each commit requires explicit user confirmation.
- Push remains manual in all modes.
- PR creation/update is user-triggered only and requires pre-PR commit-history review.

---

## Steps

### P0 — Preparation & baseline

| Step | Task | Agent | Gate |
|------|------|-------|------|
| P0-A | Snapshot current E2E test results (baseline green) | 🔄 auto | — |
| P0-B | Extract `ProcessingHistorySection` from `PdfViewerPanel.tsx` inline rendering (~L385–L510) into a dedicated component `frontend/src/components/workspace/ProcessingHistorySection.tsx` — pure refactor, no behavior change | 🔄 auto | — |
| P0-C | Verify no visual regression: existing E2E tests pass, UI renders identically | 🔄 auto | — |

---

### P1 — Enhanced run cards with state badges and duration

| Step | Task | Agent | Gate |
|------|------|-------|------|
| P1-A | Add visual state badge to each run card: green dot for COMPLETED, red for FAILED, orange for TIMED_OUT, blue for RUNNING, gray for QUEUED | 🔄 auto | — |
| P1-B | Add "latest" label/badge to the most recent run | 🔄 auto | — |
| P1-C | Calculate and display total run duration (`started_at` → `completed_at`) alongside the run header | 🔄 auto | — |
| P1-D | Reverse run order: show latest run first (currently chronological ASC) | 🔄 auto | — |

---

### P2 — Per-run raw text access

| Step | Task | Agent | Gate |
|------|------|-------|------|
| P2-A | Add a "Ver texto extraído" button to each COMPLETED run card | 🔄 auto | — |
| P2-B | On click, fetch `GET /runs/{run_id}/artifacts/raw-text` and display in an expandable section or modal within the run card | 🔄 auto | — |
| P2-C | Handle loading/error states (run still processing, artifact missing → 410) | 🔄 auto | — |

---

### P3 — Tests & validation

| Step | Task | Agent | Gate |
|------|------|-------|------|
| P3-A | Unit tests for `ProcessingHistorySection`: rendering with 0, 1, N runs; state badge mapping; duration calculation | 🔄 auto | — |
| P3-B | E2E test: reprocess a document → verify two runs appear with correct state badges | 🔄 auto | — |
| P3-C | Full E2E suite pass — no regressions | 🔄 auto | — |
| P3-D | 🚧 User review: demo the feature with a reprocessed document | 🚧 hard-gate | User approval |
| P3-E | 🚧 Documentación wiki: actualizar documentación de observabilidad UI o cerrar con `no-doc-needed` | 🚧 hard-gate | User decision |

---

---

## Estado de ejecución

**Legend**

- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — requires user review/decision

| Step | Description | Status |
|------|-------------|--------|
| P0-A | Snapshot baseline E2E | [ ] |
| P0-B | Extract ProcessingHistorySection | [ ] |
| P0-C | Verify no visual regression | [ ] |
| P1-A | State badges per run | [ ] |
| P1-B | "Latest" label on newest run | [ ] |
| P1-C | Run-level total duration | [ ] |
| P1-D | Reverse run order (latest first) | [ ] |
| P2-A | "Ver texto extraído" button | [ ] |
| P2-B | Fetch + display per-run raw text | [ ] |
| P2-C | Loading/error states | [ ] |
| P3-A | Unit tests for ProcessingHistorySection | [ ] |
| P3-B | E2E test: multi-run visibility | [ ] |
| P3-C | Full E2E suite green | [ ] |
| P3-D | 🚧 User review / demo | [ ] |
| P3-E | 🚧 Documentación wiki / no-doc-needed | [ ] |

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Raw text fetch latency for large documents | Low | Show loading spinner; text already on local filesystem |
| Run card layout breaks on many runs (>5) | Low | Scrollable container; cards already in overflow-y-auto |
| E2E flakiness with polling-based reprocess | Medium | Use existing `waitForProcessing` helper from E2E fixtures |

---

## Key Files

| File | Role |
|------|------|
| `frontend/src/components/workspace/PdfViewerPanel.tsx` L385–L510 | Current inline rendering (to extract) |
| `frontend/src/lib/processingHistory.ts` | Step grouping logic |
| `frontend/src/lib/processingHistoryView.ts` | Formatting utilities (statusIcon, formatDuration, formatTime) |
| `frontend/src/api/documentApi.ts` L162–L189 | `fetchProcessingHistory()` + raw text fetch |
| `frontend/src/types/appWorkspace.ts` L50–L70 | Types: ProcessingHistoryRun, ProcessingStep |
| `backend/app/api/routes_processing.py` L68–L145 | `GET /runs/{run_id}/artifacts/raw-text` (existing, no changes) |
