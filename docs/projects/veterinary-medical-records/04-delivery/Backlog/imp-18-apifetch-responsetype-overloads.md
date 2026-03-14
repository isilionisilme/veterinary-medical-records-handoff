# IMP-18 — Strengthen `apiFetch` responseType / return-type contract

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Next frontend quality pass

**Origin:** Code review finding (nice-to-have) on PR #307 — `[AUDIT-01-T4] Frontend API layer DRY extraction`.

**Plan:** [PLAN_2026-03-12_IMP-18-APIFETCH-RESPONSETYPE-OVERLOADS.md](../plans/PLAN_2026-03-12_IMP-18-APIFETCH-RESPONSETYPE-OVERLOADS.md)

**Severity:** LOW

**Effort:** XS (< 1h)

## Problem Statement

The `apiFetch<T>` wrapper introduced in PR #307 accepts an independent generic `T` and a `responseType` field (`"json" | "blob" | "text" | "raw"`). The compiler cannot verify that `T` matches the parser selected by `responseType`. For example, `apiFetch<string>("/x", { responseType: "blob" })` compiles without error but returns a `Blob` cast to `string` at runtime.

Today all 14 call sites are correct and covered by tests, so the risk is limited to future additions.

## Action / Acceptance Criteria

1. Replace the single generic signature with TypeScript overloads or a discriminated-union config so the compiler enforces `responseType` ↔ return-type alignment.
2. All existing call sites must compile without changes (no caller-side refactoring).
3. A mismatched call like `apiFetch<string>("/x", { responseType: "blob" })` must produce a compile-time error.
4. All 345+ vitest tests and the build must continue to pass.
