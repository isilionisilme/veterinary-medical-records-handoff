# ADR-ARCH-0004: In-Process Async Processing (No External Task Queue)

## Status
- Accepted
- Date: 2026-02-24

## Context
PDF processing (extraction + interpretation) is the heaviest workload and must not block HTTP request handling. The project favors a minimal infrastructure footprint and reproducible evaluator flow with Docker Compose.

## Decision Drivers
- API responsiveness during long-running document processing.
- No additional broker/worker services in baseline setup.
- Explicit lifecycle handling for startup, shutdown, and recovery.
- Operational simplicity for single-clinic scope.

## Considered Options
### Option A — In-process async scheduler with DB-backed queue
**Pros**
- Zero external queue/broker infrastructure.
- Shared process lifecycle with FastAPI startup/shutdown hooks.
- Queue and run history persisted in database.

**Cons**
- Process crash interrupts in-flight tasks.
- Throughput scaling limited by single-process model.

### Option B — Celery + Redis/RabbitMQ
**Pros**
- Mature distributed worker model and retries.
- Better horizontal scalability options.

**Cons**
- Requires broker + worker services and added ops complexity.
- Heavier setup for current problem scale.

### Option C — Redis Queue alternatives (RQ/arq/Dramatiq)
**Pros**
- Simpler than full Celery in some configurations.

**Cons**
- Still requires broker infrastructure and operational overhead.

## Decision
Adopt **Option A: In-process async scheduler with persistent run states in DB**.

## Rationale
1. `backend/app/infra/scheduler_lifecycle.py` wires scheduler lifecycle with app startup/shutdown.
2. `backend/app/application/processing/scheduler.py` provides tick-based queue consumption with bounded per-tick execution.
3. `backend/app/application/processing/orchestrator.py` enforces run orchestration, timeout, and state transitions.
4. `backend/app/main.py` coordinates recovery hooks and lifecycle integration.
5. Background CPU-heavy work uses thread offloading where needed, preserving event-loop responsiveness.

## Consequences
### Positive
- Maintains API responsiveness while processing runs asynchronously.
- Zero-ops baseline architecture for evaluator setup.
- Full run history and observability via persisted run states.

### Negative
- In-flight work is tied to backend process stability.
- Retries and advanced queue semantics are simpler than broker-based systems.

### Risks
- Crash during processing may leave orphaned run states without explicit recovery.
- Mitigation: startup recovery marks/reconciles orphaned runs before new scheduling proceeds.

## Code Evidence
- `backend/app/infra/scheduler_lifecycle.py`
- `backend/app/application/processing/scheduler.py`
- `backend/app/application/processing/orchestrator.py`
- `backend/app/main.py`
- `backend/app/infra/sqlite_document_repository.py`

## Related Decisions
- [ADR-ARCH-0001: Modular Monolith over Microservices](ADR-ARCH-0001-modular-monolith.md)
- [ADR-ARCH-0002: SQLite as Primary Database](ADR-ARCH-0002-sqlite-database.md)
- [ADR-ARCH-0003: Raw SQL with Repository Pattern](ADR-ARCH-0003-raw-sql-repository-pattern.md)
