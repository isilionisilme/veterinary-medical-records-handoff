# Contributing

Thank you for your interest in contributing to this project.

## Quick links

| Topic | Document |
|---|---|
| Documentation index | `https://github.com/isilionisilme/veterinary-medical-records-documentation` |
| Coding standards | `https://github.com/isilionisilme/veterinary-medical-records-documentation/blob/main/shared/02-tech/coding-standards.md` |
| Architecture | `https://github.com/isilionisilme/veterinary-medical-records-documentation/blob/main/projects/veterinary-medical-records/02-tech/architecture.md` |
| Technical design | `https://github.com/isilionisilme/veterinary-medical-records-documentation/blob/main/projects/veterinary-medical-records/02-tech/technical-design.md` |
| ADR index | `https://github.com/isilionisilme/veterinary-medical-records-documentation/blob/main/projects/veterinary-medical-records/02-tech/adr/index.md` |

## Getting started

1. **Clone and run**
   ```bash
   git clone <repo-url>
   cd veterinary-medical-records
   docker compose up --build
   ```
2. **Verify** — Frontend at `http://localhost:5173`, API at `http://localhost:8000`, OpenAPI docs at `http://localhost:8000/docs`.
3. **Run local quality gates** before pushing:
   ```powershell
   ./scripts/ci/test-L1.ps1   # lint + type-check
   ./scripts/ci/test-L2.ps1   # unit + integration tests
   ./scripts/ci/test-L3.ps1   # full preflight (E2E + Docker + coverage)
   ```

## Branch and commit conventions

- Branch format: `<category>/<slug>` (e.g., `feature/upload-validation`, `fix/snapshot-cc`).
- Commit messages: `<type>: <description>` — types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.
- See the separate documentation repository for the full workflow and merge gates.

## Architecture rules

- **Hexagonal architecture**: `domain/` → `ports/` → `application/` → `api/` / `infra/`.
- Domain layer must have zero outbound cross-layer imports.
- All persistence goes through port interfaces (`DocumentRepository`, `FileStorage`, `SchedulerPort`).
- See the separate documentation repository for the complete rule set.

## CI gates

| Gate | Threshold |
|---|---|
| Backend coverage | ≥ 85% |
| Frontend coverage | ≥ 80% |
| Max cyclomatic complexity | 30 per function |
| Max file size | 500 LOC |

## Submitting a PR

1. Create a feature branch from `main`.
2. Make your changes and ensure all L2 gates pass locally.
3. Push and open a PR against `main`.
4. PRs require passing CI and at least one review.
