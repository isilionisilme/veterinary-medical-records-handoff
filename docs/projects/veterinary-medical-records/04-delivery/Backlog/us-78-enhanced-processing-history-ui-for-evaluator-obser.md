# US-78 — Enhanced processing history UI for evaluator observability

**Status:** Planned

**Plan:** [PLAN_2026-03-07_PROCESSING-HISTORY-UI.md](../plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md)

**User Story**
As an evaluator, I want to see a clear, informative processing history with state badges, durations, and per-run raw text access so that I can verify the system preserves all processing runs and artifacts end-to-end.

**Acceptance Criteria**

- Each processing run displays a visual state badge (success / failure / timeout / running / queued).
- The most recent run is visually distinguished with a "latest" label.
- Each run card shows total run duration (from `started_at` to `completed_at`).
- I can view the raw text artifact for any historical run, not just the latest.
- Runs are displayed in reverse-chronological order (newest first).
- Existing E2E tests pass without regression.

**Scope Clarification**

- This story is **frontend-only**; no backend or API changes required.
- All data is already served by existing endpoints (`GET /documents/{id}/processing-history`, `GET /runs/{run_id}/artifacts/raw-text`).
- This story extends the existing processing history rendering (US-11) with evaluator-oriented observability enhancements.
- The component is extracted from the current inline rendering in `PdfViewerPanel.tsx` "Technical" tab into a dedicated `ProcessingHistorySection` component.
- Out of scope: interpretation diff/comparison between runs; new tabs or panels; changes to the raw text main tab behavior; performance metrics/trends dashboard; changes to processing logic.

**Dependencies**

- US-11 — View document processing history (✅ Implemented).
- US-42 — Evaluator-friendly installation & execution (✅ Implemented).

**Authoritative References**

- Tech: Processing history endpoint contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3.1.
- Tech: Run artifacts endpoint: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3.2.
- Execution plan: [`docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md`](../plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md).

**Test Expectations**

- State badges render correctly for each run state.
- Per-run raw text retrieval works for historical runs.
- No regressions in existing E2E tests.

**Definition of Done (DoD)**

- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---

# Improvement Details
