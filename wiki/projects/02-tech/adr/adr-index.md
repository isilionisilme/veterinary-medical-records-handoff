# Architecture Decision Records

## Core architecture

| ADR | Title |
|-----|-------|
| [ADR-modular-monolith](ADR-modular-monolith) | Modular Monolith over Microservices |
| [ADR-sqlite-database](ADR-sqlite-database) | SQLite as Primary Database |
| [ADR-in-process-async-processing](ADR-in-process-async-processing) | In-Process Async Processing (No External Task Queue) |

## Implementation decisions

| ADR | Title |
|-----|-------|
| [ADR-raw-sql-repository-pattern](ADR-raw-sql-repository-pattern) | Raw SQL with Repository Pattern (No ORM) |
| [ADR-frontend-stack-react-tanstack-query-vite](ADR-frontend-stack-react-tanstack-query-vite) | Frontend Stack (React + TanStack Query + Vite) |
| [ADR-confidence-scoring-algorithm](ADR-confidence-scoring-algorithm) | Confidence Scoring Algorithm Design |
| [ADR-bootstrap-schema-no-migrations](ADR-bootstrap-schema-no-migrations) | Bootstrap Schema without Migration Tooling |

## Operational decisions

| ADR | Title |
|-----|-------|
| [ADR-complexity-gate-thresholds](ADR-complexity-gate-thresholds) | Complexity Gate Thresholds for CI Enforcement |
| [ADR-re-accretion-prevention-governance](ADR-re-accretion-prevention-governance) | Re-accretion Prevention Governance |
| [ADR-structured-logging-no-metrics](ADR-structured-logging-no-metrics) | Human-Readable Logging without Metrics Endpoint |
| [ADR-ci-single-python-version](ADR-ci-single-python-version) | Single Python Version CI (No Matrix) |