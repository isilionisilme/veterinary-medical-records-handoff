# Veterinary Medical Records Processing — Technical Exercise

![CI](https://github.com/isilfrith/veterinary-medical-records/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18-61dafb)
![License](https://img.shields.io/badge/license-MIT-blue)

> **Stack:** Python 3.11 · FastAPI · React 18 · TypeScript · SQLite · Docker · Playwright · GitHub Actions

This repository contains the implementation and supporting materials for a technical exercise focused on **interpreting and processing veterinary medical records**.

The purpose of the exercise is to demonstrate **product thinking, architectural judgment, and a scalable approach to document interpretation in a regulated domain**, rather than to deliver a fully automated system.

---

## TL;DR / Evaluator Quickstart

Prerequisites:
- Docker Desktop with Docker Compose v2 (`docker compose`)

Run evaluation mode:
- `docker compose up --build`

Open:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`

Stop:
- `docker compose down`

Scope and sequencing source of truth:
- [`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md)

---

## Demo

<!-- Replace with actual screenshot or GIF -->
> 📸 _Screenshot placeholder — run `docker compose up --build` and visit `http://localhost:5173` to see the app._

---

## Problem context

Barkibu processes veterinary insurance claims based on **heterogeneous, unstructured medical documents**, typically PDFs originating from different clinics, countries, and formats.

The core operational challenge is not claim decision logic, but:

- interpreting documents consistently,
- extracting relevant medical and financial information,
- and reducing repetitive manual work for veterinarians,
while preserving safety, traceability, and trust.

This project explores an approach that assists veterinarians during document review and improves incrementally over time without disrupting existing workflows.

---

## Repository structure

- `backend/` — FastAPI API + persistence (SQLite + filesystem) + tests
- `frontend/` — React app for document upload/list/review flows
- [`docs/`](docs/) — authoritative documentation (start at [`docs/README.md`](docs/README.md))

## Architecture at a glance

For a visual overview with Mermaid diagram, see [**architecture.md**](docs/projects/veterinary-medical-records/02-tech/architecture.md).

- Architectural style: modular monolith with clear application/domain/infrastructure boundaries.
- Backend pattern: ports-and-adapters with explicit use cases and append-only review/processing artifacts.
- Frontend pattern: feature-oriented React modules centered on upload, review workspace, and structured data editing.
- Runtime model: Docker-first local environment with deterministic evaluation mode and optional dev overlay.

Key design references:
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](docs/projects/veterinary-medical-records/02-tech/technical-design.md)
- [`docs/projects/veterinary-medical-records/01-product/product-design.md`](docs/projects/veterinary-medical-records/01-product/product-design.md)
- [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](docs/projects/veterinary-medical-records/01-product/ux-design.md)

Key technical decisions (ADRs):
- [`docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0001-modular-monolith.md`](docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0001-modular-monolith.md) — modular monolith over microservices.
- [`docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0002-sqlite-database.md`](docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0002-sqlite-database.md) — SQLite trade-offs and PostgreSQL migration path.
- [`docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0003-raw-sql-repository-pattern.md`](docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0003-raw-sql-repository-pattern.md) — raw SQL + repository pattern, no ORM.
- [`docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0004-in-process-async-processing.md`](docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0004-in-process-async-processing.md) — in-process async scheduler over external queue.
- ADR index: [`docs/projects/veterinary-medical-records/02-tech/adr/index.md`](docs/projects/veterinary-medical-records/02-tech/adr/index.md)

---

## Documentation overview

The repository documentation is intentionally split by audience and purpose.

Start here:

📄 **[`docs/README.md`](docs/README.md)** — reading order + document authority.

---

### Project documentation (authoritative)

📄 **[`docs/projects/veterinary-medical-records/01-product/product-design.md`](docs/projects/veterinary-medical-records/01-product/product-design.md)**  
Product intent + semantics summary (with canonical Google Doc link).

---

📄 **[`docs/projects/veterinary-medical-records/01-product/ux-design.md`](docs/projects/veterinary-medical-records/01-product/ux-design.md)**  
UX interaction contract (roles, workflow guarantees, confidence UX rules).

📄 **[`docs/shared/01-product/brand-guidelines.md`](docs/shared/01-product/brand-guidelines.md)**  
Visual identity and tone of user-facing copy.

📄 **[`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](docs/projects/veterinary-medical-records/02-tech/technical-design.md)**  
Architecture + invariants + authoritative contracts (endpoint map, error semantics, state rules, schemas).

---

📄 **[`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md)**  
Scope + story order + acceptance criteria.

📄 **[`docs/projects/veterinary-medical-records/02-tech/backend-implementation.md`](docs/projects/veterinary-medical-records/02-tech/backend-implementation.md)**  
Backend implementation details (“how”).

📄 **[`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md)**  
Frontend implementation details (“how”).

---

### Shared engineering rules

📄 **[`AGENTS.md`](AGENTS.md)**  
Canonical AI assistant entrypoint for this repo.

📄 **[`docs/shared/03-ops/engineering-playbook.md`](docs/shared/03-ops/engineering-playbook.md)**  
Engineering standards for implementation and changes.

📄 **[`docs/shared/01-product/ux-guidelines.md`](docs/shared/01-product/ux-guidelines.md)**  
Shared UX principles referenced by project UX design.

---

### Optional / Repo internals

- Operational router (AI assistants): `docs/agent_router/00_AUTHORITY.md`
- Token optimization benchmarks: `metrics/llm_benchmarks/`

### Delivery evidence and audit trail

- **Delivery summary (start here):** [`docs/projects/veterinary-medical-records/04-delivery/delivery-summary.md`](docs/projects/veterinary-medical-records/04-delivery/delivery-summary.md)
- 12-factor architecture audit: [`docs/projects/veterinary-medical-records/99-archive/12-factor-audit.md`](docs/projects/veterinary-medical-records/99-archive/12-factor-audit.md)
- Maintainability/codebase audit: [`docs/projects/veterinary-medical-records/99-archive/codebase-audit.md`](docs/projects/veterinary-medical-records/99-archive/codebase-audit.md)
- Iterative execution log and decisions: [`docs/projects/veterinary-medical-records/04-delivery/implementation-history.md`](docs/projects/veterinary-medical-records/04-delivery/implementation-history.md)
- Future roadmap (2/4/8 weeks): [`docs/projects/veterinary-medical-records/04-delivery/future-improvements.md`](docs/projects/veterinary-medical-records/04-delivery/future-improvements.md)
- Project ADR index: [`docs/projects/veterinary-medical-records/02-tech/adr/index.md`](docs/projects/veterinary-medical-records/02-tech/adr/index.md)

---

## Evaluation & Dev details

Preferred target: Docker Compose (evaluation mode by default).

### Evaluation mode (default, stable)

Evaluation mode is production-like for local validation:
- no source-code bind mounts,
- deterministic image builds,
- local persistence for SQLite/files via mounted data/storage paths.

### Reset / persistence

By default, evaluation mode persists local state in:
- `backend/data`
- `backend/storage`

To fully reset local persisted state:
- stop services: `docker compose down`
- delete those directories (`backend/data` and `backend/storage`)

### Windows / WSL2 notes (minimal)

- On Windows, prefer running this repo from WSL2 for more reliable local filesystem behavior.
- Dev-mode file watcher polling is enabled in `docker-compose.dev.yml` (`CHOKIDAR_USEPOLLING=true`, `WATCHPACK_POLLING=true`).
- If ports are busy, change `.env` values for `FRONTEND_PORT` and `BACKEND_PORT`.

### Minimal manual smoke test

1. Open `http://localhost:5173`.
2. Upload a PDF document.
3. Verify the document appears in list/status views.
4. Open review view and preview/download the source PDF.
5. Open structured data and edit at least one field.
6. If available in your current MVP build, toggle "mark reviewed" and verify state updates.

### Dev mode (hot reload, no local toolchain install)

Dev mode is explicit and keeps evaluation mode untouched.
It mounts `backend/`, `frontend/`, and `shared/` into containers for live code reload.

Commands:
- Start dev mode:
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- Stop dev mode:
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml down`

Notes:
- Backend runs with `uvicorn --reload`.
- Frontend runs with Vite dev server and polling watchers for Windows/WSL2 friendliness.
- Code changes do not require image rebuild in dev mode (except dependency or Dockerfile changes).

### Automated tests (Compose profile)

- Backend tests:
  - `docker compose --profile test run --rm backend-tests`
- Frontend tests:
  - `docker compose --profile test run --rm frontend-tests`

### End-to-end tests (Playwright)

E2E tests run against the full Docker stack (frontend + backend + DB). They cover the 4 critical user flows: upload, review, field editing, and mark-reviewed.

```bash
# 1. Start the application stack
docker compose up -d --build

# 2. Run all E2E tests (headless Chromium)
cd frontend && npx playwright test

# 3. Run a specific spec
npx playwright test e2e/upload-smoke.spec.ts

# 4. Open interactive UI mode (useful for debugging)
npx playwright test --ui
```

**CI:** E2E tests run automatically in the `e2e` GitHub Actions job on every PR. Failure artifacts (screenshots, traces) are uploaded for debugging.

**Specs:** `app-loads`, `upload-smoke`, `review-flow`, `edit-flow`, `mark-reviewed` — see `frontend/e2e/`.

### Local quality gates (3 levels)

> **Prerequisite:** install dev tooling once per venv:
> `pip install -r requirements-dev.txt`

Use the preflight scripts by level:

- **L1 — Quick (before commit):**
  - PowerShell: `./scripts/ci/test-L1.ps1`
  - Windows launcher: `scripts\ci\test-L1.bat`
- **L2 — Push (before every push):**
  - PowerShell: `./scripts/ci/test-L2.ps1`
  - Windows launcher: `scripts\ci\test-L2.bat`
  - Frontend checks run only for frontend-impact changes by default.
- **L3 — Full (before PR creation/update):**
  - PowerShell: `./scripts/ci/test-L3.ps1`
  - Windows launcher: `scripts\ci\test-L3.bat`
  - Path-scoped by default; use `-ForceFull` to run full backend/frontend/docker scope.
  - Before merge to `main`, verify CI is green — local L3 is not required when CI has passed.

Optional arguments:
- `-BaseRef main` (default for all levels)
- `-SkipDocker` (push/full)
- `-SkipE2E` (full)
- `-ForceFrontend` (push/full)
- `-ForceFull` (full) — useful for broad local validation when CI is unavailable

### Hooks installation (recommended)

Install local hooks so the correct level runs automatically at the correct moment:

- Pre-commit quick gate: `./scripts/ci/install-pre-commit-hook.ps1`
- Pre-push gate: `./scripts/ci/install-pre-push-hook.ps1`

Files:
- Hook entrypoints: `.githooks/pre-commit`, `.githooks/pre-push`
- Core runner: `scripts/ci/preflight-ci-local.ps1`
- Level wrappers: `scripts/ci/test-L1.ps1`, `scripts/ci/test-L2.ps1`, `scripts/ci/test-L3.ps1`

### Administrative commands

- Ensure DB schema: `python -m backend.app.cli db-schema`
- Check DB readability and table count: `python -m backend.app.cli db-check`
- Print resolved runtime config: `python -m backend.app.cli config-check`
- Commands are idempotent and intended for one-off local maintenance/diagnostics.

### Rebuild guidance after changes

- If you changed code only and are in dev mode: no rebuild needed.
- If you changed code and are in evaluation mode:
  - `docker compose up --build`
- If you changed dependencies or Dockerfiles:
  - `docker compose build --no-cache`
  - `docker compose up`

### Troubleshooting

- `Global Schema contract file not found` or frontend import errors for `global_schema_contract.json`:
  - Both images now copy `shared/` to `/app/shared` during build.
  - Rebuild without cache to rule out stale images:
    - `docker compose build --no-cache backend frontend`
    - `docker compose up`

- Docker Desktop starts but containers fail unexpectedly:
  - Confirm daemon health: `docker info`
  - Validate compose config: `docker compose config`
  - Tail logs: `docker compose logs -f backend frontend`

### Global Schema migration note

- API payloads now expose canonical `active_interpretation.data.global_schema` only.
- Versioned schema keys are not supported.
- Consumers must read `global_schema` only.

## Backend implementation

The backend is implemented using:

- **Python**
- **FastAPI**
- **SQLite** (metadata and structured artifacts)
- **Filesystem storage** (original documents and large artifacts)

The system follows a **modular monolith architecture** with clear separation of concerns and explicit state transitions.

Key characteristics include:
- append-only persistence for extracted and structured data,
- explicit processing runs and failure modes,
- and full traceability from document upload to review.

### Backend configuration

Environment variables:
- `VET_RECORDS_DB_PATH`: override the SQLite database location.
- `VET_RECORDS_STORAGE_PATH`: override the filesystem root for stored documents.
- `VET_RECORDS_CORS_ORIGINS`: comma-separated list of allowed frontend origins.
Confidence policy:
- `VET_RECORDS_CONFIDENCE_POLICY_VERSION`
- `VET_RECORDS_CONFIDENCE_LOW_MAX`
- `VET_RECORDS_CONFIDENCE_MID_MAX`

For backend configuration and local runtime details, see [`docs/projects/veterinary-medical-records/02-tech/backend-implementation.md`](docs/projects/veterinary-medical-records/02-tech/backend-implementation.md).

---

## Notes for evaluators

This exercise is intentionally structured to show:

- how product and technical design inform each other,
- how scope and risk are actively controlled,
- and how a system can scale safely in a sensitive, regulated context.

The focus is on **clarity, judgment, and maintainability**, rather than feature completeness.

## How to contribute

1. Create a branch from `main` (or continue work in the designated delivery branch).
2. Keep changes scoped and update docs when behavior/contracts change.
3. Run local quality gates listed above before opening/updating PR.
4. Prefer Docker Compose commands in examples to preserve evaluator parity.
