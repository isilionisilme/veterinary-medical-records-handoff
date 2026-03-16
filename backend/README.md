# Backend

FastAPI service for veterinary medical record ingestion, extraction, review, and persistence.

## Scope

- API routes and request validation
- Application and domain logic (modular monolith)
- Persistence adapters (SQLite + local file storage)
- Background processing orchestration
- Backend test suite

## Main folders

- app: API, application, domain, infra, and ports
- tests: unit, integration, benchmarks, and fixtures
- data: local SQLite and runtime data (persisted by default in compose)
- storage: local document/artifact storage

## Run options

Preferred: from repository root with Docker Compose.

- Evaluation mode:
  - docker compose up --build
- Dev mode (hot reload):
  - docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

Local Python execution (from repository root):

- Start API:
  - python -m uvicorn backend.app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
- Administrative CLI:
  - python -m backend.app.cli db-schema
  - python -m backend.app.cli db-check
  - python -m backend.app.cli config-check

## Tests

From repository root:

- All backend tests in compose profile:
  - docker compose --profile test run --rm backend-tests
- Local pytest (if local environment is prepared):
  - python -m pytest backend/tests -q

## Notes

- Environment variables are documented in backend/.env.example.
- For full system quickstart and evaluator flow, use the repository root README.
