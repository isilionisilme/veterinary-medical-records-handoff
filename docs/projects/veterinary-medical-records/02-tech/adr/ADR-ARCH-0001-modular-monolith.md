# ADR-ARCH-0001: Modular Monolith over Microservices

## Status
- Accepted
- Date: 2026-02-24

## Context
This system processes veterinary medical records for a single clinic context: upload PDFs, extract structured data, and allow manual review. The team size is small (1–2 developers), and the exercise prioritizes architectural judgment, maintainability, and reproducibility.

The runtime target is a Docker-first local environment where evaluators can run the entire stack quickly and inspect behavior end-to-end.

## Decision Drivers
- Deployable with `docker compose up --build` in minutes.
- Clear logical boundaries that can evolve without immediate distributed infrastructure.
- Minimal operational overhead for a small team.
- Preserve testability and separation of concerns.

## Considered Options
### Option A — Modular monolith with hexagonal architecture
**Pros**
- Single deployable service for backend runtime simplicity.
- Explicit boundaries via ports (`Protocol`) and composition root wiring.
- Domain model stays infrastructure-agnostic.
- Future extraction path remains feasible.

**Cons**
- Shared process resources can affect latency under heavy CPU load.
- Horizontal scale boundaries are process-level, not service-level.

### Option B — Microservices (upload, extraction, review)
**Pros**
- Independent scaling and deployment per capability.
- Strong runtime isolation between workloads.

**Cons**
- Requires service-to-service contracts, discovery, retries, and observability stack.
- Higher cognitive and operational load for current scope/team.
- Slower evaluator setup and harder local debugging.

### Option C — Traditional monolith without explicit boundaries
**Pros**
- Lowest initial implementation overhead.

**Cons**
- Weak modularity and higher refactor risk.
- Harder evolution toward service extraction.

## Decision
Adopt **Option A: Modular monolith with explicit ports-and-adapters boundaries**.

## Rationale
1. `backend/app/ports/document_repository.py` defines an explicit repository `Protocol` consumed by application services.
2. `backend/app/domain/models.py` uses frozen domain models, keeping domain semantics independent of infrastructure.
3. `backend/app/main.py` acts as composition root: infrastructure implementations are wired once and injected into application services.
4. `docker-compose.yml` keeps runtime to two core services (backend/frontend), maximizing evaluator reproducibility.

This yields strong architectural clarity while avoiding premature distributed-system complexity.

## Consequences
### Positive
- Fast setup and deterministic local runs.
- Clear separation of domain/application/infrastructure concerns.
- Evolution path exists without rewriting business logic.

### Negative
- Background processing shares process lifecycle with HTTP API.
- Throughput is bounded by one backend runtime process.

### Risks
- If future requirements include multi-tenant, high parallel processing, architecture pressure increases.
- Mitigation: maintain strict port boundaries so extraction to services remains incremental.

## Code Evidence
- `backend/app/ports/document_repository.py`
- `backend/app/domain/models.py`
- `backend/app/main.py`
- `docker-compose.yml`

## Related Decisions
- [ADR-ARCH-0002: SQLite as Primary Database](ADR-ARCH-0002-sqlite-database.md)
- [ADR-ARCH-0003: Raw SQL with Repository Pattern](ADR-ARCH-0003-raw-sql-repository-pattern.md)
- [ADR-ARCH-0004: In-Process Async Processing](ADR-ARCH-0004-in-process-async-processing.md)
