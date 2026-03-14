# Track Plan T4 (AUDIT-01-T4): Frontend API Layer DRY Extraction

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.
>
> **Master plan:** [AUDIT-01 Master](PLAN_2026-03-12_AUDIT-01-CODEBASE-QUALITY-MASTER.md)

**Branch:** improvement/audit-01-t4-frontend-dry
**Worktree:** D:/Git/worktrees/4
**Execution Mode:** Autonomous
**Model Assignment:** Claude Opus 4.6
**PR:** [#307](https://github.com/isilionisilme/veterinary-medical-records/pull/307)
**Related item ID:** `AUDIT-01-T4`
**Prerequisite:** None (independent track)

**Implementation Report:** [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T4-FRONTEND-DRY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T4-FRONTEND-DRY.md)

---

## TL;DR

Extract the duplicated try/catch/error-handling pattern across 14 async functions in `documentApi.ts` into a single typed fetch wrapper. Reduces ~450 lines of repetitive boilerplate to ~50 lines of wrapper + 14 slim callers.

---

## Context

### Problem: DRY-1.1 Violation

**File:** `frontend/src/api/documentApi.ts` — 14 exported async functions.

All 14 functions implement an identical error-handling pattern:

```typescript
try {
    response = await fetch(API_BASE_URL + endpoint);
} catch (error) {
    if (isNetworkFetchError(error)) {
        throw new UiError(friendlyMsg, debugMsg);
    }
    throw error;
}
if (!response.ok) {
    try {
        const payload = await response.json();
        errorMessage = resolveFriendlyPayloadMessage(payload?.message, fallback);
    } catch { /* ignore */ }
    throw new UiError(errorMessage, debugMsg);
}
return response.json();
```

This is ~30 lines duplicated 14 times. Any change to error handling (e.g., adding correlation ID headers, retry logic, logging) requires modifying all 14 functions.

**Functions affected:**
1. `fetchOriginalPdf` (line 28)
2. `fetchDocuments` (line 59)
3. `fetchDocumentDetails` (line 93)
4. `fetchDocumentReview` (line 122)
5. `fetchProcessingHistory` (line 163)
6. `fetchVisitScopingMetrics` (line 194)
7. `triggerReprocess` (line 225)
8. `markDocumentReviewed` (line 242)
9. `reopenDocumentReview` (line 275)
10. `editRunInterpretation` (line 308)
11. `fetchRawText` (line 361)
12. `uploadDocument` (line 402)
13. `copyTextToClipboard` (line 445)
14. `lookupClinicAddress` (line 491)

---

## Scope Boundary

- **In scope:** B1 (extract fetch wrapper, refactor all 14 functions)
- **Out of scope:** Adding new API functions, changing error types, modifying `UiError` class, adding retry logic, adding request interceptors (those would build on this wrapper later)

---

## Design Decisions

### DD-1: Generic typed wrapper function
**Approach:** Create `apiFetch<T>(endpoint, options, errorContext)` that encapsulates the try/catch/response-check pattern and returns `Promise<T>`.
**Rationale:** TypeScript generics preserve type safety at call sites. The wrapper lives in the same file to avoid import churn.

### DD-2: Keep wrapper in `documentApi.ts` (not a separate file)
**Rationale:** The wrapper is specific to this API layer's error conventions (`UiError`, `isNetworkFetchError`, `resolveFriendlyPayloadMessage`). Extracting to a separate file would create an artificial abstraction boundary. If a second API module is added later, the wrapper can be moved then.

### DD-3: Preserve all existing error messages exactly
**Rationale:** Tests and UI components may assert on specific error messages. Zero behavioral change.

### DD-4: Special handling for blob/text responses
**Rationale:** `fetchOriginalPdf` returns a `Blob`, `fetchRawText` returns text, `copyTextToClipboard` has clipboard logic. The wrapper should support response type variants: `json` (default), `blob`, `text`, `none` (for fire-and-forget).

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~350 (mostly deletions) | 400 | ✅ |
| Code files changed | 1 | 15 | ✅ |
| Scope classification | code only | — | ✅ |
| Semantic risk | MEDIUM (single file, all callers change, 345 vitest tests validate) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — Internal refactoring. No API contract or user-facing changes.

---

## Steps

### Phase 1 — Create the Fetch Wrapper

**AGENTE: Claude Opus 4.6**

#### Step 1: Define types and wrapper function

At the top of `documentApi.ts` (below existing imports and constants), add:

```typescript
type ResponseType = "json" | "blob" | "text" | "none";

interface ApiFetchOptions extends RequestInit {
  responseType?: ResponseType;
}

interface ErrorContext {
  friendlyMessage: string;
  debugPrefix: string;
}

async function apiFetch<T>(
  endpoint: string,
  options: ApiFetchOptions = {},
  errorContext: ErrorContext,
): Promise<T> {
  const { responseType = "json", ...fetchOptions } = options;
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      throw new UiError(
        errorContext.friendlyMessage,
        `${errorContext.debugPrefix}: network error`,
      );
    }
    throw error;
  }

  if (!response.ok) {
    let errorMessage = errorContext.friendlyMessage;
    try {
      const payload = await response.json();
      errorMessage = resolveFriendlyPayloadMessage(
        payload?.message,
        errorContext.friendlyMessage,
      );
    } catch {
      // Ignore JSON parse errors on error responses
    }
    throw new UiError(
      errorMessage,
      `${errorContext.debugPrefix}: ${response.status}`,
    );
  }

  switch (responseType) {
    case "blob":
      return (await response.blob()) as T;
    case "text":
      return (await response.text()) as T;
    case "none":
      return undefined as T;
    default:
      return (await response.json()) as T;
  }
}
```

### Phase 2 — Refactor Each Function

**AGENTE: Claude Opus 4.6**

#### Step 2: Refactor all 14 functions to use the wrapper

Each function should be reduced to its unique logic (building the endpoint URL, preparing the request body) + a call to `apiFetch`. Example transformation:

**Before:**
```typescript
export async function fetchDocuments(): Promise<DocumentListResponse> {
  const endpoint = "/documents";
  let response: Response;
  try {
    response = await fetch(API_BASE_URL + endpoint);
  } catch (error) {
    if (isNetworkFetchError(error)) { throw new UiError(...); }
    throw error;
  }
  if (!response.ok) { ... }
  return response.json();
}
```

**After:**
```typescript
export async function fetchDocuments(): Promise<DocumentListResponse> {
  return apiFetch<DocumentListResponse>("/documents", {}, {
    friendlyMessage: "Could not load documents.",
    debugPrefix: "fetchDocuments",
  });
}
```

Apply this pattern to all 14 functions, preserving:
- Exact endpoint paths
- HTTP methods and headers
- Request bodies
- Response types (`blob` for PDF, `text` for raw text)
- All existing error messages (character-for-character)

**AGENTE: Claude Opus 4.6**

#### Step 3: Handle special cases

- `fetchOriginalPdf`: uses `responseType: "blob"`
- `fetchRawText`: uses `responseType: "text"`
- `uploadDocument`: uses `method: "POST"` with `FormData` body
- `editRunInterpretation`: uses `method: "PATCH"` with JSON body
- `copyTextToClipboard`: has clipboard API call after fetch — keep post-fetch logic in the function, use wrapper for the fetch part only
- `triggerReprocess`, `markDocumentReviewed`, `reopenDocumentReview`: use `method: "POST"`

### Phase 3 — Validation

**AGENTE: Claude Opus 4.6**

#### Step 4: Run full vitest suite

```bash
cd frontend && npm run test -- --run
```

All 345 tests must pass. Pay special attention to:
- API mock tests that assert on specific call patterns
- Error handling tests that verify `UiError` messages

#### Step 5: Run lint

```bash
cd frontend && npm run lint
```

Zero errors.

#### Step 6: Type check

```bash
cd frontend && npx tsc --noEmit
```

Zero errors.

---

## Execution Status

### Phase 0 — Preflight

- [x] P0-A — Create branch `improvement/audit-01-t4-frontend-dry` from latest `main`. Verify clean worktree.
- [x] P0-B — Read `documentApi.ts` fully. Catalog each function's unique parameters, error messages, response types.

### Phase 1 — Wrapper

- [x] P1-A — Define `apiFetch<T>` wrapper with types + `throwApiResponseError` helper.
- [x] P1-B — Wrapper code reviewed (autonomous mode).

### Phase 2 — Refactoring

- [x] P2-A — Refactor functions 1–7 (fetch* and triggerReprocess).
- [x] P2-B — Refactor functions 8–11 (mark/reopen/edit/fetchRawText).
- [x] P2-C — Refactor functions 12–14 (upload/clipboard/lookup). `copyTextToClipboard` unchanged — no fetch call.
- [x] P2-D — Verify zero behavioral change: 345/345 vitest tests pass, all error messages preserved.
- [x] P2-E — Full diff reviewed (autonomous mode).

### Phase 3 — Final

- [x] P3-A — Run vitest (345 tests). All pass.
- [x] P3-B — Run eslint + tsc + prettier. Zero errors.
- [x] P3-C — Commit proposal (autonomous mode).

---

## Relevant Files

| File | Action |
|------|--------|
| `frontend/src/api/documentApi.ts` | REFACTOR (add wrapper, simplify 14 functions) |
| `frontend/src/api/*.test.*` | VERIFY (no changes, all must pass) |

---

## Acceptance Criteria

- [x] Single `apiFetch` wrapper function handles all fetch + error logic
- [x] 13 of 14 API functions use the wrapper (no duplicate try/catch blocks). `copyTextToClipboard` excluded — no fetch call.
- [x] All existing user-facing error messages preserved character-for-character
- [x] 345 vitest tests pass
- [x] `eslint` + `tsc` — zero errors
- [x] Net LOC reduction: 184 lines (367 deleted, 183 inserted)
