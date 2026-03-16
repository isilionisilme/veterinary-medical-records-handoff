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

Run evaluation mode with app + documentation wiki:
- `docker compose -f docker-compose.yml -f docker-compose.evaluators.yml up --build`
- PowerShell wrapper (attached): `./scripts/up-app.ps1`
- PowerShell wrapper (detached): `./scripts/up-app.ps1 -Detached`
- Windows one-click launcher (repo root, detached): `start-app.cmd`
- macOS/Linux launcher (repo root, detached): `./start-app.sh`
- View logs after one-click start: `docker compose -f docker-compose.yml -f docker-compose.evaluators.yml logs -f`

Open:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Wiki redirect: `http://localhost:8081`
- Published GitHub Wiki: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki`

The evaluator compose profile redirects `http://localhost:8081` to the published GitHub Wiki.

Stop:
- `docker compose down`
- `docker compose -f docker-compose.yml -f docker-compose.evaluators.yml down`
- PowerShell wrapper: `./scripts/down-app.ps1`
- Windows one-click launcher (repo root): `stop-app.cmd`
- macOS/Linux launcher (repo root): `./stop-app.sh`

Note for macOS/Linux first run:
- `chmod +x ./start-app.sh ./stop-app.sh`

---

## Solution approach

We approached this exercise as a document interpretation problem rather than a pure CRUD or claim-routing system. Veterinary medical records arrive in heterogeneous formats, contain partial or ambiguous signals, and require a workflow that helps a veterinarian understand, verify, and correct machine-produced interpretations safely.

That is why the backend is a hexagonal modular monolith instead of a microservice split. The problem size does not justify distributed complexity yet, but it does require clear boundaries between application logic, persistence, processing, and reviewer workflows so the system can evolve without collapsing into a single tangled service.

At the product level, the core loop is extraction, confidence scoring, human review, and calibration. The system captures the machine suggestion, exposes its evidence and confidence, lets a reviewer correct it in context, and preserves those corrections as explicit signals for later refinement rather than hiding them inside ad hoc state changes.

The delivery strategy was iterative and evidence-driven. We used ADRs, local CI gates, backend and frontend automated tests, and end-to-end scenarios to keep the codebase reviewable while progressively improving architecture, quality, and evaluator-facing clarity.

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
- `wiki/` — project documentation source that will be published to the GitHub Wiki of this repository

## Architecture at a glance


- Architectural style: modular monolith with clear application/domain/infrastructure boundaries.
- Backend pattern: ports-and-adapters with explicit use cases and append-only review/processing artifacts.
- Frontend pattern: feature-oriented React modules centered on upload, review workspace, and structured data editing.
- Runtime model: Docker-first local environment with deterministic evaluation mode and optional dev overlay.

Key design references:

- Product design: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/product-design`
- Architecture overview: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/architecture`
- Technical design: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/technical-design`
- Event architecture: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/event-architecture`
- Deployment guide: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/deployment`

Key technical decisions (ADRs):

- Modular monolith: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/ADR-modular-monolith`
- SQLite as primary database: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/ADR-sqlite-database`
- Raw SQL repository pattern: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/ADR-raw-sql-repository-pattern`
- In-process async processing: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/ADR-in-process-async-processing`
- CI complexity thresholds: `https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/ADR-complexity-gate-thresholds`

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


---

## Notes for evaluators

This exercise is intentionally structured to show:

- how product and technical design inform each other,
- how scope and risk are actively controlled,
- and how a system can scale safely in a sensitive, regulated context.

The focus is on **clarity, judgment, and maintainability**, rather than feature completeness.

## How to contribute

1. Create a branch from `main` (or continue work in the designated delivery branch).
2. Keep changes scoped and update in-repo guides when behavior/contracts change.
3. Run local quality gates listed above before opening/updating PR.
4. Prefer Docker Compose commands in examples to preserve evaluator parity.
