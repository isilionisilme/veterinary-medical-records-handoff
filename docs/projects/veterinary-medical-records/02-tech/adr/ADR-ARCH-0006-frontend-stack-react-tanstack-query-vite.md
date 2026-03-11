---
title: "ADR-ARCH-0006: Frontend Stack (React + TanStack Query + Vite)"
type: adr
status: active
audience: contributor
last-updated: 2026-03-11
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [ADR-ARCH-0006: Frontend Stack (React + TanStack Query + Vite)](#adr-arch-0006-frontend-stack-react--tanstack-query--vite)
  - [Status](#status)
  - [Context](#context)
  - [Decision Drivers](#decision-drivers)
  - [Considered Options](#considered-options)
    - [Option A — React + TanStack Query + Vite](#option-a--react--tanstack-query--vite)
    - [Option B — Next.js App Router (full framework)](#option-b--nextjs-app-router-full-framework)
    - [Option C — React with ad-hoc `fetch` + local component state](#option-c--react-with-ad-hoc-fetch--local-component-state)
  - [Decision](#decision)
  - [Rationale](#rationale)
  - [Consequences](#consequences)
    - [Positive](#positive)
    - [Negative](#negative)
    - [Risks](#risks)
  - [Code Evidence](#code-evidence)
  - [Related Decisions](#related-decisions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# ADR-ARCH-0006: Frontend Stack (React + TanStack Query + Vite)

## Status

- Accepted
- Date: 2026-03-11

## Context

The evaluator-facing UI requires a responsive review workflow with frequent data refreshes (document list, detail,
review payloads, processing history, and reprocessing actions). The project keeps a Docker-first local setup and
prioritizes low-friction onboarding.

The selected frontend stack must support:

- Fast local startup and build feedback.
- Predictable server-state synchronization.
- Type-safe component development.
- Incremental evolution without framework-level lock-in.

## Decision Drivers

- Fast dev server and production builds for evaluator iteration loops.
- Clear split between server state and local UI state.
- Strong TypeScript ergonomics and broad ecosystem support.
- Minimal configuration overhead in a single-repo workflow.

## Considered Options

### Option A — React + TanStack Query + Vite

#### Pros

- Fast startup and HMR via Vite.
- Declarative server-state caching, invalidation, and optimistic updates.
- Mature React ecosystem aligned with current component architecture.
- Simple TypeScript integration with low tooling overhead.

#### Cons

- Requires explicit cache-key conventions and query invalidation discipline.
- Additional conceptual layer (QueryClient/query lifecycle) for contributors.

### Option B — Next.js App Router (full framework)

#### Pros

- Integrated routing/data/tooling conventions in one framework.
- Strong production deployment ecosystem.

#### Cons

- Adds framework complexity not required for current SPA scope.
- More opinionated runtime model than needed for current evaluator workflow.

### Option C — React with ad-hoc `fetch` + local component state

#### Pros

- Fewer dependencies.
- Lowest initial conceptual overhead.

#### Cons

- Higher risk of duplicated request logic and inconsistent loading/error handling.
- No shared caching/invalidation model for multi-panel review screens.

## Decision

Adopt **Option A: React + TanStack Query + Vite** as the frontend runtime stack.

## Rationale

1. `frontend/src/main.tsx` initializes a shared `QueryClient` and app-wide `QueryClientProvider`.
2. `frontend/src/hooks/useReprocessing.ts` uses TanStack Query mutations with optimistic updates and targeted cache
   invalidation for review flows.
3. `frontend/vite.config.ts` and `frontend/package.json` define Vite as dev/build toolchain with React plugin.
4. `frontend/package.json` pins React and TanStack Query dependencies used across hooks and workspace components.

## Consequences

### Positive

- Consistent server-state lifecycle across review and processing screens.
- Faster local feedback loop for contributors and evaluators.
- Clear test strategy with Vitest/Playwright around a stable React + Vite baseline.

### Negative

- Query key hygiene becomes an explicit architecture concern.
- Contributors must understand mutation side effects and invalidation boundaries.

### Risks

- Poor query invalidation patterns can create stale UI behavior.
- Mitigation: maintain explicit query-key conventions and integration tests for critical review workflows.

## Code Evidence

- `frontend/src/main.tsx`
- `frontend/src/hooks/useReprocessing.ts`
- `frontend/vite.config.ts`
- `frontend/package.json`

## Related Decisions

- [ADR-ARCH-0001: Modular Monolith over Microservices](ADR-ARCH-0001-modular-monolith.md)
- [ADR-ARCH-0004: In-Process Async Processing](ADR-ARCH-0004-in-process-async-processing.md)
- [ADR-ARCH-0005: Complexity Gate Thresholds for CI Enforcement](ADR-ARCH-0005-complexity-gate-thresholds.md)
