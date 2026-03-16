# Veterinary Medical Records Processing — Technical Exercise

![CI](https://github.com/isilfrith/veterinary-medical-records/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18-61dafb)
![License](https://img.shields.io/badge/license-MIT-blue)

> **Stack:** Python 3.11 · FastAPI · React 18 · TypeScript · SQLite · Docker · Playwright · GitHub Actions

A technical exercise demonstrating **product thinking, architectural judgment, and a scalable approach to document interpretation** for veterinary medical records in a regulated domain.

---

## Quickstart

Prerequisites: Docker Desktop with Docker Compose v2.

```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- Backend API / OpenAPI docs: http://localhost:8000/docs
- Published Wiki: https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki

Stop:
```bash
docker compose down
```

Convenience wrappers:
- PowerShell: `./scripts/up-app.ps1` / `./scripts/down-app.ps1`
- Windows: `start-app.cmd` / `stop-app.cmd`
- macOS/Linux: `./start-app.sh` / `./stop-app.sh` (run `chmod +x` on first use)

---

## Repository structure

| Folder | Purpose | Details |
|---|---|---|
| `backend/` | FastAPI API, persistence, processing, tests | [`backend/README.md`](backend/README.md) |
| `frontend/` | React app for upload, review, and field editing | [`frontend/README.md`](frontend/README.md) |
| `shared/` | Global schema contract shared between backend and frontend | |
| `scripts/` | CI preflight, dev helpers, quality guards | [`scripts/README.md`](scripts/README.md) |
| `wiki/` | Documentation source published to the GitHub Wiki | [GitHub Wiki](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki) |

---

## Documentation (Wiki)

All detailed documentation lives in the [GitHub Wiki](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki). The README is intentionally concise to avoid drift.

**Evaluator reading path:**

| Axis | Pages |
|---|---|
| First steps | [Deployment](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/deployment) → [User Guide](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/user-guide) |
| Product | [Executive Summary](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/product-design-executive) → [Product Design](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/product-design) |
| Architecture | [Architecture](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/architecture) → [Technical Design](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/technical-design) → [ADRs](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/adr-index) |
| Quality | [Extraction Quality](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/extraction-quality) → [Event Architecture](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/event-architecture) |
| Delivery | [Implementation Plan](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/implementation-plan) → [Implementation History](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/implementation-history) → [Post Mortem](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/post-mortem) |
| Deep dive | [Staff Engineer Guide](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/staff-engineer-guide) (15/30/45 min paths) |

---

## Dev mode

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Hot reload for backend (uvicorn) and frontend (Vite). See [Deployment wiki](https://github.com/isilionisilme/veterinary-medical-records-handoff/wiki/deployment) for details, reset instructions, and WSL2 notes.

## Tests

```bash
# Backend tests
docker compose --profile test run --rm backend-tests

# Frontend unit tests (from frontend/)
npm run test

# E2E tests (Playwright, requires running stack)
cd frontend && npx playwright test
```

## Local quality gates

Three preflight levels before commit/push/PR:

```bash
./scripts/ci/test-L1.ps1   # Quick — before commit
./scripts/ci/test-L2.ps1   # Push — before push
./scripts/ci/test-L3.ps1   # Full — before PR
```

Install hooks: `./scripts/ci/install-pre-commit-hook.ps1` and `./scripts/ci/install-pre-push-hook.ps1`. See [`scripts/ci/README.md`](scripts/ci/README.md) for flags and details.

---

## How to contribute

1. Create a branch from `main` using `<category>/<slug>` naming.
2. Keep changes scoped; update in-repo guides when behavior/contracts change.
3. Run local quality gates before opening/updating a PR.
4. Prefer Docker Compose commands in examples to preserve evaluator parity.
