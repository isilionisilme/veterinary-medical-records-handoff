# ARCH-18 — Extract Frontend State Management Layer

**Status:** Planned

**Type:** Architecture Improvement (frontend architecture)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 3 (§3.4)

**Severity:** MEDIUM  
**Effort:** M (4-8h)

**Problem Statement**
`AppWorkspace.tsx` concentrates 15 `useState` hooks, acting as a frontend state hub.

**Action**
Extract state into React Context + `useReducer` pattern to reduce state hub concentration.

**Acceptance Criteria**
- `AppWorkspace.tsx` reduced in state management complexity
- State is organized into domain-specific contexts
- All existing tests and E2E specs pass
- No user-visible behavior change

**Dependencies**
- None, but carries significant test risk due to state management refactor.
