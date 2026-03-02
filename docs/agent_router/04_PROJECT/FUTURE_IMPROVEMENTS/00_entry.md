# FUTURE_IMPROVEMENTS — Modules

Owner entry for `docs/projects/veterinary-medical-records/04-delivery/future-improvements.md` propagation in DOC_UPDATES workflow.
Canonical source remains `docs/projects/veterinary-medical-records/04-delivery/future-improvements.md`.
Current source links point to `docs/projects/veterinary-medical-records/02-tech/adr/*` after ADR relocation under project docs.

## Propagated updates
- Item 7 renumbered to 7a (routes) and 7b (AppWorkspace decomposition) added from CTO verdict iteration 2 (F8-D). Cross-referenced from TECHNICAL_DESIGN §14 limitations table.
- Iteration 3 closure (F9-E): marked completed items in roadmap — 7b (AppWorkspace decomposition), 9 (upload streaming guard), and 15 (minimal auth/token boundary).
- Iteration 7 closure (F13): marked completed items 8 (extraction observability modularization), 8a (interpretation decomposition), 8b (pdf extraction decomposition), and 8c (DRY constants consolidation).
- Iteration 7 extension of 7b: AppWorkspace decomposition now reflects both iterations 3 and 7, including hook extraction and updated LOC reduction.
- Iteration 8 closure (F14-M): marked completed item 4 (frontend utils error-path coverage via F14-H/I/J). Extended 7b with Iteration 8 render-section extraction (PdfViewerPanel, StructuredDataPanel, UploadPanel — 2,221 LOC, −62% from original). Extended 8a with F14-K candidate_mining further split into candidate_mining.py + date_parsing.py (399 LOC each). Added PdfViewer worker fix and regression guard notes.
- Plan restructure: updated internal link references from monolithic `AI_ITERATIVE_EXECUTION_PLAN.md` to `docs/projects/veterinary-medical-records/04-delivery/implementation-history.md` (clarification only, no content change).
- Iteration 9/10 planning refresh (F15-K): marked roadmap items #1, #6, and #7a as completed; appended deferred candidates #19-#24 from Iteration 10 draft triage; normalized broken links (`production/*` -> `implementation/*`) and removed dead draft-plan references.
- Iteration 10 closure (F16-L): marked roadmap item #2 (CI coverage thresholds) as completed via F16-E, and item #24 as partially completed via F16-CI (cache + path filtering + conditional E2E + concurrency). Added post-iteration provenance note dated 2026-02-27.
- Iteration 11 closure (F18-U): marked items #3, #10, #11, #12, #13, #19, #20, and #22 as completed; updated E2E progress note (5 -> ~20 specs) and refreshed remaining roadmap priorities/effort.
- Iteration 12 reframing (F19-N): source document switched from active backlog framing to "Known Limitations & Future Directions" and removed timeline language for closed-project posture.
