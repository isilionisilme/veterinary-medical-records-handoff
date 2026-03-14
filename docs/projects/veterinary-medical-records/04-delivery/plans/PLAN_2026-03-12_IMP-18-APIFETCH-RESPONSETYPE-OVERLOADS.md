# Plan: IMP-18 — Strengthen `apiFetch` responseType / return-type contract

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.

**Branch:** improvement/imp-18-apifetch-responsetype-overloads
**Worktree:** TBD
**Execution Mode:** Supervisado
**Model Assignment:** Uniform
**PR:** Pending
**Backlog item:** [imp-18-apifetch-responsetype-overloads.md](../Backlog/imp-18-apifetch-responsetype-overloads.md)
**Related item ID:** `IMP-18`
**CI Mode:** 1) Simple validation

---

## Agent Instructions

1. Mark checkbox `[x]` immediately after completing each step (no batching).
2. Run `cd frontend && npx tsc --noEmit` and `npm run test` after each phase to validate.
3. No commit/push without explicit user approval.
4. If any test or type check fails after a change, fix it before moving to the next step.

---

## Context

PR #307 introduced `apiFetch<T>`, a generic fetch wrapper for the frontend API layer. The wrapper's `responseType` parameter selects the parser (`json`, `blob`, `text`, `raw`), but the generic `T` is independent — the compiler cannot enforce that `T` matches the parser output. All current call sites are correct, but future callers have no compile-time guard.

## Objective

Replace the free-form generic with overloads (or a discriminated-union config) so the compiler enforces `responseType` ↔ return-type alignment without changing any existing caller.

## Scope Boundary

**In scope:** `apiFetch` signature in `frontend/src/api/documentApi.ts`, TypeScript overloads, compile-time verification.
**Out of scope:** New API functions, runtime behavior changes, test logic changes, caller refactoring.

---

## Steps

### Phase 1 — Design overload signatures

- [ ] **Step 1:** Define TypeScript overload signatures for `apiFetch`:

  ```typescript
  // Overload: blob
  async function apiFetch(endpoint: string, config: ApiFetchConfig<Blob> & { responseType: "blob" }): Promise<Blob>;
  // Overload: text
  async function apiFetch(endpoint: string, config: ApiFetchConfig<string> & { responseType: "text" }): Promise<string>;
  // Overload: raw (returns Response)
  async function apiFetch(endpoint: string, config: ApiFetchConfig<Response> & { responseType: "raw" }): Promise<Response>;
  // Overload: json (default) — caller provides T
  async function apiFetch<T>(endpoint: string, config: ApiFetchConfig<T> & { responseType?: "json" }): Promise<T>;
  // Implementation signature (not public)
  async function apiFetch<T>(endpoint: string, config: ApiFetchConfig<T>): Promise<T> { ... }
  ```

  Adjust the `ApiFetchConfig<T>` interface so `onResponseError` return type aligns with each overload.

- [ ] **Step 2:** Run `npx tsc --noEmit` — all existing call sites must compile with zero changes.

### Phase 2 — Negative compile-time test

- [ ] **Step 3:** Add a `// @ts-expect-error` block in the test file (or a dedicated type-test file) that proves a mismatched call is rejected:

  ```typescript
  // @ts-expect-error — blob responseType must resolve to Blob, not string
  apiFetch<string>("/x", { responseType: "blob", friendlyMessage: "" });
  ```

- [ ] **Step 4:** Run `npx tsc --noEmit` — the `@ts-expect-error` must be consumed (no "unused" warning).

### Phase 3 — Validation

- [ ] **Step 5:** Run `cd frontend && npm run test` — all tests pass (345+).
- [ ] **Step 6:** Run `cd frontend && npm run build` — build succeeds.
- [ ] **Step 7:** Run `cd frontend && npm run lint` — no new warnings or errors.

---

## Rollback

Revert the overload signatures and restore the single generic signature. No runtime behavior is affected.
