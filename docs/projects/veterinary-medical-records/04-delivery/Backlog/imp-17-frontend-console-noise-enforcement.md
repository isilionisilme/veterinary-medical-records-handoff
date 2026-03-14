# IMP-17 — Frontend Console Noise Enforcement

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 23 — Frontend test infrastructure hardening

**Origin:** Manual audit of frontend test suite output (2026-03-12). Confirmed zero visible noise today, but identified 5 unguarded console spy patterns across 3 test files and 1 missing `restoreAllMocks` teardown.

**Plan:** [PLAN_2026-03-12_IMP-17-FRONTEND-CONSOLE-ENFORCEMENT.md](../plans/PLAN_2026-03-12_IMP-17-FRONTEND-CONSOLE-ENFORCEMENT.md)

**Severity:** LOW

**Effort:** XS (< 1h)

## Problem Statement

The frontend test suite (53 files, Vitest + jsdom) currently passes with zero visible `console.error`/`console.warn` noise. However, this cleanliness depends entirely on per-test discipline: each test that exercises an error path must independently `vi.spyOn(console, ...)` and restore afterward. There is:

- No global enforcement that fails a test on unexpected console output.
- No shared helper — the same 3-line spy pattern is duplicated across 3 files (5 call sites).
- One confirmed spy leak: `StructuredDataViewConfidence.test.tsx` mocks `console.warn` without an `afterEach` restore.
- One unconditionally-emitting `console.warn` in production code (`emitConfidencePolicyDiagnosticEvent`) that any new test touching the degraded-confidence path would surface as noise without warning.

The risk: new tests silently introduce console noise, and the team doesn't notice until someone audits CI logs manually.

## Action / Acceptance Criteria

1. **Global enforcement hook in `setupTests.ts`**: Any test that triggers `console.error` or `console.warn` without explicitly opting in MUST fail with a descriptive message.
2. **Shared helpers in `test/helpers.tsx`**: `suppressConsoleError()`, `suppressConsoleWarn()`, and `suppressExpectedWindowError()` available for tests that produce expected output.
3. **Migrate 3 existing test files** to use the shared helpers instead of inline spies.
4. **Fix spy leak** in `StructuredDataViewConfidence.test.tsx` (add missing `afterEach` with `restoreAllMocks`).
5. **Zero test regressions**: `npm run test:coverage` passes green, coverage thresholds (80/80/70/80) maintained.

## Scope Clarification

**In scope:**
- Global `beforeEach`/`afterEach` enforcement hook for `console.error` and `console.warn`
- Shared test helpers for expected console output
- Migration of 3 test files: `ErrorBoundary.test.tsx`, `PdfViewer.test.tsx`, `StructuredDataViewConfidence.test.tsx`
- Bug fix for missing `restoreAllMocks` in `StructuredDataViewConfidence.test.tsx`

**Out of scope:**
- Refactoring the diagnostic logging system (`pdfDebug.ts`, `extractionDebug.ts`, etc.)
- Changing env gates on existing gated logs
- E2E test noise (Playwright suite)
- Adding new test coverage beyond the enforcement infrastructure

## Affected Files

| File | Change |
|------|--------|
| `frontend/src/setupTests.ts` | Add global `beforeEach`/`afterEach` enforcement hooks |
| `frontend/src/test/helpers.tsx` | Add `suppressConsoleError`, `suppressConsoleWarn`, `suppressExpectedWindowError` |
| `frontend/src/components/ErrorBoundary.test.tsx` | Migrate to shared helpers, remove local `suppressExpectedWindowError` |
| `frontend/src/components/PdfViewer.test.tsx` | Migrate 2 inline `console.error` spies to shared helpers |
| `frontend/src/components/StructuredDataViewConfidence.test.tsx` | Migrate 1 inline `console.warn` spy, add missing `afterEach` restore |

## Test Expectations

- `npm run test:coverage` passes with 53 test files, zero failures
- Coverage thresholds maintained: 80% lines, 80% functions, 70% branches, 80% statements
- TypeScript: `npx tsc --noEmit` passes
- Enforcement validation: a bare `console.error("leak")` in any test body triggers a descriptive failure

## Definition of Done

- [x] Global enforcement hook active in `setupTests.ts`
- [x] Shared helpers exported from `test/helpers.tsx`
- [x] 3 test files migrated to shared helpers
- [x] Spy leak in `StructuredDataViewConfidence.test.tsx` fixed
- [x] `npm run test:coverage` green
- [x] `npx tsc --noEmit` green
- [x] Enforcement manually validated (temporary leak → failure → removal)

## Dependencies

None. This is a self-contained test infrastructure improvement with no external dependencies.
