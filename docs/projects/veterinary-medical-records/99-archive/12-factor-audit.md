# F1-A — 12-Factor audit (single-machine Docker Compose scope)

> **⚠️ Historical snapshot (2026-02-23).** All 5 prioritized backlog items were resolved in Iterations 2–11. See [DELIVERY_SUMMARY](delivery-summary.md) for current state.

Date: 2026-02-23
Scope: backend FastAPI + frontend React, local Docker Compose deployment model

## Compliance summary

| Factor | Status | Evidence |
|---|---|---|
| I. Codebase | Strong | Single repo with clear app boundaries (`backend/`, `frontend/`, `docs/`), CI validates both stacks in one pipeline (`.github/workflows/ci.yml`). |
| II. Dependencies | Strong | Explicit pinned backend deps (`backend/requirements.txt`), deterministic frontend install (`frontend/package.json` + `npm ci` in CI/Docker). |
| III. Config | Partial | Env vars used consistently, but config parsing/validation is distributed (e.g., `backend/app/config.py`, infra adapters reading env directly in `backend/app/infra/database.py` and `backend/app/infra/file_storage.py`). |
| IV. Backing services | Strong | DB/storage treated as attached resources via env-configurable paths (`VET_RECORDS_DB_PATH`, `VET_RECORDS_STORAGE_PATH`) and Compose wiring (`docker-compose.yml`). |
| V. Build, release, run | Partial | Build/run are reproducible (Dockerfiles + compose), but release metadata/version is not promoted as an explicit release artifact boundary. |
| VI. Processes | Partial | Web API process also owns long-running scheduler lifecycle (`backend/app/main.py` with `processing_scheduler`), coupling request-serving and background workload. |
| VII. Port binding | Strong | Backend and frontend expose/bind ports explicitly (`Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`). |
| VIII. Concurrency | Partial | No independent worker process type in compose for scheduler load; concurrency relies on in-process async task and single backend service. |
| IX. Disposability | Strong | Graceful startup/shutdown path exists, including stop event for scheduler in app lifespan (`backend/app/main.py`). |
| X. Dev/prod parity | Strong | Docker-first eval path and explicit dev overlay (`docker-compose.dev.yml`) keep parity high while allowing hot reload. |
| XI. Logs | Strong | App uses stdout/stderr-oriented runtime (uvicorn + Python logging), compatible with container log aggregation. |
| XII. Admin processes | Partial | Operational scripts and tests exist, but no explicit one-off admin command interface for recurring data maintenance/migrations. |

## Out-of-scope notes (explicit)

- Multi-host horizontal scaling and distributed worker topologies are out of scope for this exercise (single-machine Compose target).
- Recommendations avoid microservices, cloud-specific orchestration, and managed infrastructure changes.

## Partial/Weak findings table

| Factor | Finding | File/Location | Impact | Effort (S/M/L) | Acceptance Criterion |
|---|---|---|---|---|---|
| III | Configuration responsibility is split across app + infra modules, making validation drift likely | `backend/app/config.py`, `backend/app/infra/database.py`, `backend/app/infra/file_storage.py` | Medium | S | One centralized settings module defines and validates all runtime env vars; infra adapters consume resolved settings instead of raw env reads. |
| V | Build/release/run boundary lacks explicit release metadata (version/revision surface) | `Dockerfile.backend`, `Dockerfile.frontend`, `.github/workflows/ci.yml` | Medium | S | Add immutable build/release metadata exposure (e.g., commit/version in API metadata and container labels) verified in CI. |
| VI | Background processing lifecycle is coupled to API process | `backend/app/main.py`, `backend/app/application/processing_runner.py` | Medium | M | Scheduler bootstrap/ownership is abstracted behind a runner boundary and can be disabled or moved without API-layer changes. |
| VIII | No dedicated worker process type for processing queue pressure | `docker-compose.yml` (`backend` only), `backend/app/main.py` | Low | M | Compose provides optional worker profile using same app code path, leaving default evaluator flow unchanged. |
| XII | Missing explicit admin command set for recurring ops tasks | repository-level scripts/CLI surface | Low | S | Document and expose one-off admin commands (schema check/migrate, orphan recovery, diagnostics) with deterministic invocation. |

## Prioritized backlog (top 5)

1. Centralize runtime settings and env validation behind a single typed settings module consumed by infra adapters.
2. Add release metadata surface (commit/version/build date) and verify in CI.
3. Decouple scheduler bootstrap from API composition root with an explicit processing runner boundary.
4. Add optional worker process profile in Compose for queue processing without changing default evaluator flow.
5. Define and document explicit admin one-off commands for schema/maintenance/diagnostics.
