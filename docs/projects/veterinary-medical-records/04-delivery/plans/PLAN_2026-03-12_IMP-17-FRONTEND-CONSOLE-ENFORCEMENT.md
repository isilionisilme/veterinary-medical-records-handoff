# Plan: IMP-17 — Frontend Console Noise Enforcement

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.

**Branch:** improvement/imp-17-frontend-console-enforcement
**Worktree:** D:\Git\worktrees\cuarto
**Execution Mode:** Supervisado
**Model Assignment:** Uniform
**PR:** Pending
**Backlog item:** [imp-17-frontend-console-noise-enforcement.md](../Backlog/imp-17-frontend-console-noise-enforcement.md)
**Related item ID:** `IMP-17`
**CI Mode:** 1) Simple validation

---

## Agent Instructions

1. Mark checkbox `[x]` immediately after completing each step (no batching).
2. Run `cd frontend && npm run test:coverage` after each phase to validate.
3. No commit/push without explicit user approval.
4. If any test fails after a change, fix it before moving to the next step.

---

## Context

The frontend test suite passes clean today with zero console noise. However, cleanliness depends on per-test `vi.spyOn(console, ...)` discipline with no enforcement layer. This plan adds a global enforcement hook and shared helpers, then migrates existing inline spies.

## Objective

Add fail-on-unexpected-console-output enforcement to the frontend test suite and consolidate duplicated spy patterns into shared helpers.

## Scope Boundary

**In scope:** Global enforcement hook, shared helpers, 3-file migration, 1 spy-leak fix.
**Out of scope:** Diagnostic logging refactor, env gate changes, E2E noise, new test coverage.

---

## Steps

### Phase 1 — Shared helpers (`frontend/src/test/helpers.tsx`)

- [x] **Step 1:** Add shared console suppression helpers to `frontend/src/test/helpers.tsx`.

  Add these exports at the end of the file:

  - `suppressConsoleError(pattern?: string | RegExp)`: Returns a restore function. Calls `vi.spyOn(console, "error").mockImplementation(...)`. If `pattern` is provided, only suppresses calls matching it; others still throw. The returned function restores the original and returns the spy for assertions.
  - `suppressConsoleWarn(pattern?: string | RegExp)`: Same pattern for `console.warn`.
  - `suppressExpectedWindowError(message: string)`: Move from `ErrorBoundary.test.tsx`. Adds a `window.addEventListener("error", ...)` handler that calls `event.preventDefault()` for errors matching `message`. Returns cleanup function.

  Design constraint: these helpers must NOT call `mockRestore` automatically. The caller (or `afterEach`) is responsible for restoration. This ensures compatibility with the global enforcement hook.

- [x] **Step 2:** Verify TypeScript compiles: `cd frontend && npx tsc --noEmit`.

### Phase 2 — Global enforcement hook (`frontend/src/setupTests.ts`)

- [x] **Step 3:** Add global console enforcement to `frontend/src/setupTests.ts`.

  After the existing `afterEach(() => { cleanup(); })` block, add:

  ```typescript
  let consoleErrorSpy: ReturnType<typeof vi.spyOn> | undefined;
  let consoleWarnSpy: ReturnType<typeof vi.spyOn> | undefined;

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, "error");
    consoleWarnSpy = vi.spyOn(console, "warn");
  });

  afterEach(() => {
    // Only enforce if the test didn't replace the spy's implementation.
    // When a test does vi.spyOn(console, "error").mockImplementation(() => {}),
    // it takes ownership — we skip enforcement for that method.
    if (consoleErrorSpy && consoleErrorSpy.mock.calls.length > 0) {
      const impl = consoleErrorSpy.getMockImplementation();
      if (!impl) {
        const calls = consoleErrorSpy.mock.calls;
        consoleErrorSpy.mockRestore();
        throw new Error(
          `Unexpected console.error (${calls.length} call(s)). ` +
          `First call: ${JSON.stringify(calls[0])}. ` +
          `Use suppressConsoleError() from test/helpers to allow expected errors.`
        );
      }
    }
    consoleErrorSpy?.mockRestore();

    if (consoleWarnSpy && consoleWarnSpy.mock.calls.length > 0) {
      const impl = consoleWarnSpy.getMockImplementation();
      if (!impl) {
        const calls = consoleWarnSpy.mock.calls;
        consoleWarnSpy.mockRestore();
        throw new Error(
          `Unexpected console.warn (${calls.length} call(s)). ` +
          `First call: ${JSON.stringify(calls[0])}. ` +
          `Use suppressConsoleWarn() from test/helpers to allow expected warnings.`
        );
      }
    }
    consoleWarnSpy?.mockRestore();
  });

Key design: the spy is created without mockImplementation, so console output still prints to terminal for debugging. Tests that explicitly mock (via the shared helpers or direct mockImplementation) are detected by getMockImplementation() returning truthy → enforcement skipped.

 Step 4: Run cd frontend && npm run test:coverage. All 53 test files must pass. If any fail, it means they were silently producing console output — fix them before proceeding. ✅
Phase 3 — Migrate existing tests
 Step 5: Migrate frontend/src/components/ErrorBoundary.test.tsx. ✅

Remove the local suppressExpectedWindowError function (lines 10-19).
Import suppressConsoleError and suppressExpectedWindowError from ../test/helpers.
In each test that uses vi.spyOn(console, "error").mockImplementation(...), replace with const restoreConsole = suppressConsoleError().
In the cleanup section of each test, replace consoleErrorSpy.mockRestore() with restoreConsole().
Keep the existing afterEach(() => vi.restoreAllMocks()).
 Step 6: Migrate frontend/src/components/PdfViewer.test.tsx. ✅

Import suppressConsoleError from ../test/helpers.
In the two tests at lines ~372 and ~383, replace vi.spyOn(console, "error").mockImplementation(...) with const restoreConsole = suppressConsoleError().
The file already has afterEach(() => vi.restoreAllMocks()).
 Step 7: Migrate frontend/src/components/StructuredDataViewConfidence.test.tsx. ✅

Import suppressConsoleWarn from ../test/helpers.
In the test at line ~281, replace vi.spyOn(console, "warn").mockImplementation(...) with const restoreWarn = suppressConsoleWarn().
Add afterEach(() => { vi.restoreAllMocks(); }) to the describe block — this file currently lacks it, causing a spy leak.
 Step 8: Run cd frontend && npm run test:coverage. All 53 files must pass. ✅

Phase 4 — Verification
 Step 9: Validate enforcement catches leaks. ✅

Temporarily add console.error("deliberate-leak") inside any passing test body (e.g., first test in ErrorBoundary.test.tsx).
Run the test — it must fail with the enforcement message.
Remove the temporary leak.
 Step 10: Final validation. ✅

cd frontend && npm run test:coverage — green.
cd frontend && npx tsc --noEmit — green.
Report results and wait for user commit approval.

Commit Suggestion
When all steps pass:
git add setupTests.ts helpers.tsx \
      ErrorBoundary.test.tsx \
      PdfViewer.test.tsx \
      StructuredDataViewConfidence.test.tsx
git commit -m "test(frontend): add global console.error/warn enforcement hook

- Add beforeEach/afterEach enforcement in setupTests.ts that fails on
  unexpected console.error/console.warn calls
- Add suppressConsoleError, suppressConsoleWarn, suppressExpectedWindowError
  shared helpers in test/helpers.tsx
- Migrate 3 test files from inline vi.spyOn to shared helpers
- Fix missing restoreAllMocks in StructuredDataViewConfidence.test.tsx

Closes IMP-17"

Acceptance Criteria (from backlog)
✅ Global enforcement hook active in setupTests.ts
✅ Shared helpers exported from test/helpers.tsx
✅ 3 test files migrated to shared helpers
✅ Spy leak in StructuredDataViewConfidence.test.tsx fixed
✅ npm run test:coverage green (53 files, thresholds maintained)
✅ npx tsc --noEmit green
✅ Enforcement manually validated
