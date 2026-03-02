# Codebase Maintainability Audit

> **⚠️ Historical snapshot (2026-02-23).** All 15 findings were resolved in Iterations 1–12. Compliance scores below reflect the state at audit time and are no longer current. See [DELIVERY_SUMMARY](delivery-summary.md) for up-to-date metrics.

Date: 2026-02-23

## Scope and methodology
- Repository-only audit over workspace content at d:/Git/veterinary-medical-records.
- No external web research used.
- Read-only assessment (no code changes).
- Evidence sources: core backend/frontend modules, infra/config, CI workflows, tests, and project docs.
- Scoring approach: worker-based maintainability/compliance review aligned with ln-620-codebase-auditor intent (9 categories), weighted by evaluator impact.

## Stack/context constraints
- Stack: FastAPI (Python 3.11), React 18 + TypeScript, SQLite, Docker Compose.
- Architecture baseline is intentional modular monolith with hexagonal/ports-and-adapters (must be preserved).
- Evaluation context prioritizes maintainability, architecture clarity, and incremental delivery.
- Recommendations explicitly avoid:
  - changing hexagonal architecture,
  - replacing SQLite with PostgreSQL,
  - introducing microservices/distributed systems,
  - removing the documentation system.

## Executive summary
The codebase is strong on architecture intent, documentation governance, and CI discipline, but maintainability risk is concentrated in a few monolithic hotspots that are evaluator-visible immediately. The three pre-identified targets are confirmed as critical debt: frontend/src/App.tsx, backend/app/application/processing_runner.py, and backend/app/application/document_service.py.

The primary gap is not missing architecture, but responsibility overload inside key modules, causing test fragility, high regression risk, and slower iteration. Secondary gaps are tooling consistency (frontend linting/format enforcement), duplicated tests, and single-process SQLite concurrency sensitivity.

Overall: architecture direction is correct; maintainability execution is currently below evaluator expectations for a cleanly evolvable codebase unless F2 refactor decomposition is completed.

## Compliance score table (9 workers/categories)

| Worker / Category | Score | Status | Evidence (repo) | Notes |
|---|---:|---|---|---|
| Security | 72/100 | Partial | backend/app/api/routes.py, backend/app/cli.py | Upload type checks and masked config output exist; no auth/rate-limiting layer and upload size is checked after full in-memory read. |
| Build & CI | 84/100 | Good | .github/workflows/ci.yml, docker-compose.yml | Good multi-job CI and packaging guard; frontend lint is type-check only. |
| Architecture | 78/100 | Good-Partial | backend/app/main.py, backend/app/ports/document_repository.py, backend/app/domain/models.py | Hexagonal layering is solid, but very large application modules weaken boundary clarity. |
| Code Quality | 58/100 | At risk | frontend/src/App.tsx, backend/app/application/processing_runner.py, backend/app/application/document_service.py | High complexity concentration in few files. |
| Dependencies | 67/100 | Partial | frontend/package.json, backend/requirements.txt, requirements-dev.txt | Versions pinned/declared, but frontend quality tooling enforcement is incomplete. |
| Dead Code / Redundancy | 62/100 | Partial | frontend/src/lib/processingHistory.test.ts, frontend/src/lib/__tests__/processingHistory.test.ts | Test duplication introduces maintenance drag and divergence risk. |
| Observability | 74/100 | Good-Partial | backend/app/application/extraction_observability.py, backend/app/api/routes.py | Useful extraction observability path exists, but observability module itself is large and mixed in responsibilities. |
| Concurrency | 64/100 | Partial | backend/app/infra/database.py, backend/app/infra/scheduler_lifecycle.py, backend/app/application/processing_runner.py | In-process scheduler and run guards exist; SQLite lock sensitivity remains. |
| Lifecycle / Operability | 81/100 | Good | backend/app/main.py, backend/app/settings.py, backend/app/cli.py, README.md | Startup/shutdown, version endpoint, env settings, and one-off admin commands are in place. |

## Severity summary totals

| Severity | Total |
|---|---:|
| Critical | 2 |
| High | 4 |
| Medium | 6 |
| Low | 3 |
| **Total findings** | **15** |

## Detailed findings

| # | Worker | File | Finding | Impact on Evaluation | Effort (S/M/L) | Acceptance Criterion |
|---:|---|---|---|---|---|---|
| 1 | Code Quality / Architecture | frontend/src/App.tsx | Monolithic UI orchestration (~6k lines) mixing view composition, API calls, query wiring, validation, diagnostics, and panel state. | Immediate single-file app anti-pattern perception; high regression risk and slow onboarding. | L | App decomposed into feature modules/pages/hooks/services; no single feature file exceeds agreed cap (e.g., 500 lines). |
| 2 | Code Quality | frontend/src/App.test.tsx | Large integration-like monolithic test suite (~3k+ lines) tightly coupled to App internals. | Refactor friction; evaluator sees low test maintainability and brittle coupling. | M | Tests redistributed by feature/component, preserving behavior coverage with smaller focused specs. |
| 3 | Architecture / Code Quality | backend/app/application/processing_runner.py | Mixed responsibilities (~2.9k lines): scheduler execution, extraction strategy, PDF parsing fallback, candidate mining, confidence composition, artifact building. | Violates single reason to change; high blast radius for any processing change. | L | Pipeline split into cohesive modules (scheduler/orchestrator/extractors/interpretation assembly) with stable public entrypoints. |
| 4 | Architecture / Quality | backend/app/application/document_service.py | Too many responsibilities (~1.8k lines): upload use cases, review projection, edit application, calibration updates, list/history mapping. | Difficult to reason about correctness; evaluator flags service-layer overload. | L | Service split into narrower use-case modules with unchanged API-facing behavior. |
| 5 | Security / Quality | backend/app/api/routes.py | Upload size limit enforced after fully reading request body into memory. | Potential memory pressure/DoS vector perception under concurrent uploads. | M | Streaming/chunked size guard or bounded parser prevents full memory load before rejecting oversized payload. |
| 6 | Security | backend/app/api/routes.py | No authentication/authorization layer on document endpoints. | For regulated-domain impression, may be flagged as security incompleteness (even for exercise MVP). | M | Explicit security boundary documented and minimally enforced (token gate for non-local mode) without changing core architecture. |
| 7 | Concurrency | backend/app/infra/database.py | ✅ Resuelto en Iteration 2: `get_connection()` aplica `PRAGMA journal_mode=WAL` y `PRAGMA busy_timeout=5000` en cada conexión. | Mitiga lock contention bajo escenarios de reproceso con lecturas concurrentes. | M | ✅ Cubierto con `backend/tests/integration/test_database_concurrency.py` (WAL/timeout + lectura concurrente durante escritura). |
| 8 | Build / Quality | frontend/package.json | lint script maps to TypeScript check only; no ESLint/format policy enforcement in CI. | Evaluator may interpret missing frontend static quality gate. | S | Frontend lint pipeline enforces ESLint + formatter consistency in CI and local hooks. |
| 9 | Dependencies / Tooling | .pre-commit-config.yaml | Pre-commit currently backend-centric (Ruff only), no frontend checks. | Inconsistent quality controls across stack. | S | Pre-commit covers Python + frontend lint/format checks with clear opt-in performance profile. |
| 10 | Dead Code / Redundancy | frontend/src/lib/processingHistory.test.ts and frontend/src/lib/__tests__/processingHistory.test.ts | Overlap in tests creates duplicated intent. | Redundant tests inflate maintenance cost and can diverge semantically. | S | Consolidate duplicate scenarios into one canonical test location; remove overlaps. |
| 11 | Observability / Quality | backend/app/application/extraction_observability.py | Observability module itself is very large (~1k+ lines), combining persistence, normalization, scoring, and summarization. | Observability changes become high-risk; maintainability concern shifts from feature to plumbing. | M | Split module into storage, transformation, and aggregation units with unchanged endpoint contracts. |
| 12 | Architecture / API | backend/app/api/routes.py | Route layer (~900+ lines) accumulates broad endpoint orchestration and response mapping complexity. | Evaluator may see adapter bloat reducing adapter clarity. | M | Route file decomposed by bounded endpoint groups (documents/runs/review/observability) while preserving thin-adapter pattern. |
| 13 | Lifecycle / Config | backend/app/config.py | Frequent settings cache clears in config helpers can cause inconsistent runtime config reads across hot paths. | Subtle operability/performance smell; complicates deterministic config behavior. | S | Configuration reads are deterministic per process lifecycle with explicit refresh points only where needed. |
| 14 | Build / Test Quality | .github/workflows/ci.yml, pytest.ini, frontend/vite.config.ts | CI runs tests but no coverage thresholds/quality budget enforcement. | Harder to prove safe refactor progression during large decomposition. | M | CI publishes coverage and enforces minimum threshold gates for frontend/backend. |
| 15 | Code Quality / UX layer | frontend/src/App.tsx | Console debug paths and diagnostics are mixed with production flow state management. | Signals non-modular debug strategy; increases cognitive load in core UI path. | S | Debug/diagnostics extracted to dedicated utility/hooks with controlled environment toggles. |

## Pre-identified critical targets

### 1) frontend/src/App.tsx monolithic risk
- Confirmed critical hotspot: single-file concentration of application shell, API client logic, query orchestration, validation, and rendering composition.
- Evaluator impact: very high, immediately visible in repository navigation.

### 2) backend/app/application/processing_runner.py mixed responsibilities
- Confirmed critical hotspot: scheduler lifecycle execution plus extraction/parsing and interpretation assembly in one module.
- Evaluator impact: very high for backend maintainability and separation-of-concerns scoring.

### 3) backend/app/application/document_service.py too many responsibilities
- Confirmed high hotspot: upload handling, review normalization, interpretation edit pipeline, calibration side effects, and list/history adapters in one service.
- Evaluator impact: high; appears as service-layer overreach despite correct overall architecture.

## Prioritized remediation backlog (Top 10)

| # | Worker | File | Finding | Impact on Evaluation | Effort (S/M/L) | Acceptance Criterion |
|---:|---|---|---|---|---|---|
| 1 | Code Quality / Architecture | frontend/src/App.tsx | Decompose monolithic App into feature slices (shell, data access, review workspace, upload/list sidebar, dialogs). | Highest visible maintainability gain. | L | App responsibilities split into modules with unchanged UX/API behavior; tests pass. |
| 2 | Architecture / Quality | backend/app/application/processing_runner.py | Extract orchestrator, extraction adapters, interpretation builder, and confidence logic into dedicated modules. | Major reduction of backend complexity risk. | L | Public run behavior unchanged; existing tests pass; module boundaries explicit. |
| 3 | Architecture / Quality | backend/app/application/document_service.py | Split into upload/review/edit/calibration/read-model services. | High evaluator impact on service maintainability. | L | Existing API contract behavior preserved with smaller cohesive modules. |
| 4 | Quality / Testing | frontend/src/App.test.tsx | Refactor monolithic test into feature-focused test suites aligned to new decomposition. | Improves confidence and refactor safety signal. | M | Coverage parity maintained; test files mapped to features/components. |
| 5 | Security / API | backend/app/api/routes.py | Implement bounded upload body handling before full payload allocation. | Addresses practical security/reliability concern. | M | Oversized uploads are rejected early without allocating full file in memory. |
| 6 | Concurrency | backend/app/infra/database.py | Add explicit SQLite lock-handling policy (timeout/busy handling) and document expected behavior. | Improves reliability perception under queue pressure. | M | Lock contention path is deterministic and covered by tests/documentation. |
| 7 | Build / Tooling | frontend/package.json and .github/workflows/ci.yml | Add frontend static lint/format enforcement. | Strengthens quality gate maturity for evaluators. | S | CI fails on lint/format violations and passes on clean branch. |
| 8 | Dead Code / Test hygiene | frontend/src/lib/processingHistory.test.ts and frontend/src/lib/__tests__/processingHistory.test.ts | Consolidate overlapping tests. | Low effort, quick maintainability win. | S | Single canonical test set remains with equivalent assertions. |
| 9 | Observability | backend/app/application/extraction_observability.py | Modularize observability internals (storage, transforms, aggregates). | Prevents new monolith while preserving useful telemetry. | M | Observability endpoints unchanged; internal modules focused and testable. |
| 10 | Lifecycle / Quality | .github/workflows/ci.yml, pytest.ini, frontend/vite.config.ts | Add coverage thresholds for backend/frontend during refactor phase. | Improves change safety and evaluator confidence in incremental delivery. | M | CI reports/enforces defined minimum coverage thresholds across stacks. |

## How to test
- Open this report and verify each finding references real repository files.
- Validate the three critical hotspots in frontend/src/App.tsx, backend/app/application/processing_runner.py, and backend/app/application/document_service.py.
- Cross-check tooling/CI findings in frontend/package.json, .pre-commit-config.yaml, and .github/workflows/ci.yml.
