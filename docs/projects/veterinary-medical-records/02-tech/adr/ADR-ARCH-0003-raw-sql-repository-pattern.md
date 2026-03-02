# ADR-ARCH-0003: Raw SQL with Repository Pattern (No ORM)

## Status
- Accepted
- Date: 2026-02-24

## Context
The backend requires explicit relational queries for run-state guards, append-only artifacts, and calibration upserts. The domain model is intentionally immutable/frozen to preserve deterministic behavior and clean domain boundaries.

## Decision Drivers
- Preserve frozen domain model semantics.
- Keep SQL control for atomic guards and upserts.
- Ensure application layer remains persistence-agnostic via ports.
- Minimize runtime dependencies and hidden abstractions.

## Considered Options
### Option A — Raw SQL + Repository Pattern
**Pros**
- Full control over query semantics and transaction boundaries.
- Natural expression of SQLite-specific guards and conflict handling.
- Clear mapping from rows to immutable domain models.

**Cons**
- More handwritten SQL and mapping code.
- Schema evolution requires explicit migration logic.

### Option B — SQLAlchemy ORM
**Pros**
- Rich ORM ecosystem and model-centric workflows.
- Built-in session and relationship patterns.

**Cons**
- ORM state management conflicts with frozen domain model style.
- Adds conceptual overhead and potential impedance mismatch.

### Option C — SQL query builder / SQLAlchemy Core
**Pros**
- Less ORM coupling while reducing raw SQL strings.

**Cons**
- Extra abstraction layer and dependency cost.
- Limited net value for current explicit-query needs.

## Decision
Adopt **Option A: Raw SQL in infrastructure repositories implementing port interfaces**.

## Rationale
1. `backend/app/ports/document_repository.py` defines repository behavior as a `Protocol`, independent of SQL implementation.
2. `backend/app/infra/sqlite_document_repository.py` centralizes SQL logic and explicit row-to-domain mapping.
3. `backend/app/domain/models.py` keeps immutable domain models free from ORM lifecycle concerns.
4. Current query patterns (atomic guards, `ON CONFLICT`, append-only history) are direct and transparent in SQL.

## Consequences
### Positive
- Predictable query behavior and explicit transaction semantics.
- No hidden ORM side effects or session lifecycle complexity.
- Tight control of persistence performance hotspots.

### Negative
- Higher maintenance burden for SQL statements and mappings.
- No auto-generated migration chain from ORM metadata.

### Risks
- Repository modules can grow if not split by aggregate boundaries.
- Mitigation: continue decomposition by use case and keep Protocol surface explicit.

## Code Evidence
- `backend/app/ports/document_repository.py`
- `backend/app/infra/sqlite_document_repository.py`
- `backend/app/domain/models.py`
- `backend/app/infra/database.py`

## Related Decisions
- [ADR-ARCH-0001: Modular Monolith over Microservices](ADR-ARCH-0001-modular-monolith.md)
- [ADR-ARCH-0002: SQLite as Primary Database](ADR-ARCH-0002-sqlite-database.md)
- [ADR-ARCH-0004: In-Process Async Processing](ADR-ARCH-0004-in-process-async-processing.md)
