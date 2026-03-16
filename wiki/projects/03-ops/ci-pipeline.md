# CI Pipeline

This document describes every automated check that runs in the CI pipeline (`.github/workflows/ci.yml`) and how to reproduce them locally.

---

## Pipeline Overview

CI triggers on **push to `main`** and on **every pull request**. In-progress runs for the same branch are cancelled automatically.

A path-filter job (`changes`) detects which areas changed and conditionally activates downstream jobs. This keeps CI fast: unchanged areas are skipped.

```
changes ──┬── frontend_test_build
           ├── brand_guard
           ├── frontend_design_system_guard
           ├── quality
           ├── complexity_gate
           ├── docker_packaging_guard ── e2e
           └── e2e
```

---

## Jobs

### 1. `changes` — Path Filter

Detects which paths changed and sets output flags consumed by all other jobs.

| Flag | Paths |
|---|---|
| `backend` | `backend/**`, `requirements*.txt`, `pyproject.toml`, `pytest.ini` |
| `frontend` | `frontend/**` |

### 2. `frontend_test_build` — Frontend Quality & Build

**Runs when:** frontend or backend paths changed.

| Step | Tool | What it checks |
|---|---|---|
| ESLint | `npm run lint` | Linting rules and code quality |
| Prettier | `npm run format:check` | Formatting consistency |
| Unit tests | `npm run test:coverage` (Vitest) | Component and hook tests; **≥ 80 %** line/function/statement, **≥ 70 %** branch coverage |
| Build | `npm run build` | TypeScript compilation and Vite production build |
| Security audit | `npm audit --audit-level=high` | Known vulnerabilities in npm dependencies |

### 3. `brand_guard` — Brand Compliance

**Runs when:** PR with frontend changes.

Runs `scripts/quality/check_brand_compliance.py` against only the **added lines** in the PR diff. Verifies brand colors and typography tokens conform to design-system standards.

### 4. `frontend_design_system_guard` — Design System Violations

**Runs when:** PR with frontend changes.

Runs `scripts/quality/check_design_system.mjs`. Detects raw design tokens, inline style escapes, and unlabeled icon usage that bypass the design system.

### 5. `quality` — Backend Lint & Tests

**Runs when:** backend paths changed.

| Step | Tool | What it checks |
|---|---|---|
| Ruff lint | `ruff check .` | Python linting (import order, unused vars, style) |
| Ruff format | `ruff format --check .` | Python formatting consistency |
| Pytest | `pytest -x --tb=short --cov=backend/app --cov-report=term-missing` | Unit + integration tests; **≥ 85 %** coverage (enforced by `pytest.ini`) |
| Security audit | `pip-audit --requirement backend/requirements.txt --strict` | Known vulnerabilities in Python dependencies |

### 6. `complexity_gate` — Architecture Enforcement

**Runs when:** backend paths changed (PR events).

Runs `scripts/quality/architecture_metrics.py --check` against changed files:

| Metric | Threshold |
|---|---|
| Max cyclomatic complexity per function | **≤ 30** |
| Max lines of code per file | **≤ 500** |
| Warning threshold (CC) | 11 |

### 7. `docker_packaging_guard` — Docker Image Validation

**Runs when:** Docker-related files, shared contracts, backend, or frontend paths changed.

Builds both Docker images (`Dockerfile.backend`, `Dockerfile.frontend`) and verifies that `shared/global_schema_contract.json` exists inside each image. This ensures the frontend–backend schema contract ships correctly.

### 8. `e2e` — End-to-End Tests

**Runs when:** PR or push to main, with frontend or backend changes. Depends on `docker_packaging_guard`.

| Step | Detail |
|---|---|
| Docker stack | `docker compose up -d --wait` — starts full application stack |
| Playwright suite | Runs smoke + core projects (12 workers, retry × 2 on CI) |
| Failure artifacts | Uploads Playwright report and test-results on failure |

The E2E suite is organized in three Playwright projects:

| Project | Tests | Scope |
|---|---|---|
| **smoke** | 2 | App loads, upload smoke |
| **core** | 5 | PDF viewer, extracted data, field editing, review workflow, sidebar |
| **extended** | 23 | Full test suite including accessibility, validation, split-panel, toasts, visits |

CI runs the `test:e2e` script, which executes smoke + core. The full extended suite can be triggered locally.

---

## Enforced Thresholds Summary

| Metric | Threshold | Job |
|---|---|---|
| Backend test coverage | ≥ 85 % | `quality` |
| Frontend test coverage (line/function/statement) | ≥ 80 % | `frontend_test_build` |
| Frontend test coverage (branch) | ≥ 70 % | `frontend_test_build` |
| Cyclomatic complexity per function | ≤ 30 | `complexity_gate` |
| Lines of code per file | ≤ 500 | `complexity_gate` |
| npm vulnerability level | high | `frontend_test_build` |
| pip-audit | strict | `quality` |

---

## Local Reproduction — Preflight Tiers

The local preflight script (`scripts/ci/preflight-ci-local.ps1`) mirrors the CI pipeline with three tiers plus a CI-parity mode.

| Tier | Script | When to use | What it runs |
|---|---|---|---|
| **L1 — Quick** | `scripts/ci/test-L1.ps1` | Pre-commit | Ruff lint + format on changed files only |
| **L2 — Push** | `scripts/ci/test-L2.ps1` | Pre-push | Full Ruff, Pytest + coverage, ESLint, Prettier, Vitest + coverage, build, brand + design-system guards, Docker guard |
| **L3 — Full** | `scripts/ci/test-L3.ps1` | Pre-PR | Everything in L2 + Playwright E2E + Docker image validation |
| **CI parity** | `preflight-ci-local.ps1 -Mode CI -ParityMode` | Validate exact CI behavior | Same as L3 but file detection restricted to commit range (excludes staged/unstaged) |

### Useful flags

| Flag | Effect |
|---|---|
| `-ForceFrontend` | Run frontend checks even if no frontend paths changed |
| `-ForceFull` | Force all checks regardless of changed paths |
| `-SkipDocker` | Skip Docker image build/validation |
| `-SkipE2E` | Skip Playwright E2E tests |
| `-ParityMode` | Restrict changed-file detection to commit range only (mirrors GitHub Actions) |

### Git hooks

Pre-configured hooks automate L1/L2:

```
.githooks/pre-commit  → scripts/ci/test-L1.ps1  (quick lint)
.githooks/pre-push    → scripts/ci/test-remote-mirror.ps1  (remote sync guard)
```

Install with:
```powershell
./scripts/ci/install-pre-commit-hook.ps1
./scripts/ci/install-pre-push-hook.ps1
```

---

## Test Inventory

### Backend (~84 test files)

| Category | Location | Count | Examples |
|---|---|---|---|
| Unit | `backend/tests/unit/` | 53 | Visit helpers, weight normalization, PDF extraction, scheduler, pet name normalization |
| Integration | `backend/tests/integration/` | 25 | Upload, document review, visit assignment, extraction observability, rate limiting, auth boundary |
| Root-level | `backend/tests/` | 6 | Health, calibration repo, document repo, run repo, DB resilience, orchestrator failures |

### Frontend — Unit (~56 test files)

| Category | Location | Count | Examples |
|---|---|---|---|
| App-level | `frontend/src/` | 3 | App, AppShellFlowsA, AppShellFlowsB |
| Components | `frontend/src/components/` | 8 | ErrorBoundary, DocumentSidebar, SourcePanel, ReviewWorkspace, PdfViewer |
| Hooks | `frontend/src/hooks/` | 35+ | useUploadState, useReview*, usePdf*, useField*, useDocument*, useConnectivityToasts |
| API / Lib | `frontend/src/api/`, `frontend/src/lib/` | 5 | documentApi, fieldValidators, candidateSuggestions, structuredDataFilters |

### Frontend — E2E (21 spec files)

Full inventory in [E2E Test Coverage](plan-e2e-test-coverage).
