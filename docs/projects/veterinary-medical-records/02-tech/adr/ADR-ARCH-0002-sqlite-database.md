# ADR-ARCH-0002: SQLite as Primary Database

## Status
- Accepted
- Date: 2026-02-24

## Context
The system persists document metadata, processing run state, review artifacts, and calibration aggregates for a single-clinic operational context. The exercise requires a fast Docker-first setup with minimal infrastructure and high local reproducibility.

## Decision Drivers
- Zero additional infrastructure containers for baseline execution.
- No external provisioning step before runtime.
- Sufficient consistency and durability for a single backend process.
- Explicit upgrade path to PostgreSQL if scale demands it.

## Considered Options
### Option A — SQLite (stdlib `sqlite3`)
**Pros**
- Zero external service dependency.
- Single file persistence is simple for backups and local recovery.
- Fast setup and low operational complexity.

**Cons**
- Serialized write constraints under concurrent multi-process workloads.
- Fewer operational features than a full RDBMS.

### Option B — PostgreSQL
**Pros**
- Better multi-process concurrency and scaling features.
- Mature observability and operational tooling.

**Cons**
- Adds provisioning, driver, and migration/tooling complexity.
- Increases evaluator setup and maintenance burden for current scope.

### Option C — MongoDB
**Pros**
- Flexible document-oriented schema.

**Cons**
- Additional infra and driver complexity.
- Weaker fit for current relational patterns and query semantics.

## Decision
Adopt **Option A: SQLite** as primary datastore for current scope.

## Rationale
1. `backend/app/infra/database.py` uses standard-library `sqlite3` and schema bootstrap helpers.
2. `backend/app/settings.py` centralizes default DB path and runtime config.
3. `docker-compose.yml` persists DB through backend-mounted data directory without separate DB service.
4. Current domain scale (single clinic, moderate volume) does not justify DB infrastructure overhead.
5. Repository port abstraction keeps migration path controlled.

## Consequences
### Positive
- One-command local startup with persistent data.
- Minimal dependencies and simpler operations.
- Deterministic environment for technical evaluation.

### Negative
- Write concurrency is constrained for multi-process scaling.
- Advanced database operational features are limited.

### Risks
- Future multi-tenant or high write throughput scenarios can hit locking pressure.
- Mitigation: keep `DocumentRepository` interface stable and introduce a Postgres adapter behind the same port.

## Code Evidence
- `backend/app/infra/database.py`
- `backend/app/settings.py`
- `backend/app/ports/document_repository.py`
- `docker-compose.yml`
- `backend/requirements.txt`

## Related Decisions
- [ADR-ARCH-0001: Modular Monolith over Microservices](ADR-ARCH-0001-modular-monolith.md)
- [ADR-ARCH-0003: Raw SQL with Repository Pattern](ADR-ARCH-0003-raw-sql-repository-pattern.md)
- [ADR-ARCH-0004: In-Process Async Processing](ADR-ARCH-0004-in-process-async-processing.md)
