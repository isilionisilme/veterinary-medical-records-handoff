# ADR-bootstrap-schema-no-migrations: Bootstrap Schema without Migration Tooling

## Context

The persistence layer creates tables via declarative DDL executed at application startup. As a portfolio-scope project with a stable schema, the question is whether to introduce a migration framework (Alembic, yoyo-migrations) for schema versioning.

## Decision Drivers

- Schema has been stable since Iteration 2 (WAL mode + busy timeout); no migrations have been needed.
- Evaluator setup must remain a single `docker compose up` with no manual migration steps.
- Migration tooling adds files, CLI commands, and a version-history table that increase onboarding friction.

## Considered Options

### Option A — Bootstrap DDL at startup (current)

#### Pros

- Zero-config: tables created on first run, idempotent via `IF NOT EXISTS`.
- No migration history to manage or debug.
- Minimal surface area for a stable schema.

#### Cons

- No automated rollback or incremental ALTER support.
- Schema changes require manual DDL coordination if the schema diverges across environments.

### Option B — Alembic migration framework

#### Pros

- Industry-standard versioned migrations with rollback.
- Auto-generation of ALTER scripts from model diffs.

#### Cons

- Adds `alembic/` directory, `alembic.ini`, and CLI dependency.
- Requires a migration for every schema change, even trivial ones.
- Overhead unjustified while schema is stable and single-environment.

## Decision

Adopt **Option A: bootstrap DDL at startup** for current project scope.

## Rationale

1. `backend/app/infra/sqlite_document_repository.py` executes `CREATE TABLE IF NOT EXISTS` statements at connection initialization — idempotent and self-contained.
2. The schema has not changed since the initial design; migration tooling would add complexity without demonstrated benefit.
3. The repository protocol ([ADR-raw-sql-repository-pattern](ADR-raw-sql-repository-pattern)) isolates all DDL behind the infrastructure layer, so introducing Alembic later requires changes only in `infra/`.

## Consequences

### Positive

- Evaluator setup remains `docker compose up` with no migration steps.
- Schema definition lives alongside the repository implementation — single source of truth.

### Negative

- If schema evolution frequency increases, manual DDL changes become error-prone.

### Risks

- Production use with multiple environments would need versioned migrations.
- Mitigation: Alembic can be introduced behind the existing repository interface without architectural changes.

## Code Evidence

- `backend/app/infra/sqlite_document_repository.py` — bootstrap DDL
- `backend/app/infra/database.py` — connection factory

## Related Decisions

- [ADR-sqlite-database: SQLite as Primary Database](ADR-sqlite-database)
- [ADR-raw-sql-repository-pattern: Raw SQL with Repository Pattern](ADR-raw-sql-repository-pattern)