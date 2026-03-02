# Known Limitations & Future Directions

> After 12 iterations, this project has reached its target quality bar. The items
> below represent conscious scope decisions — not gaps. Each was evaluated and
> deferred because the ROI did not justify the effort for a portfolio/demo project.

---

## Completed improvements (summary)

Across 12 iterations, **15 planned improvements** were fully resolved. For the complete timeline with metrics, see [implementation-history.md](implementation/implementation-history.md).

<details>
<summary>Completed items (click to expand)</summary>

| # | Improvement | Iteration |
|---|---|---|
| 1 | SQLite WAL mode + busy timeout | Iter 2 |
| 2 | CI coverage threshold gates | Iter 10 |
| 3 | Centralize env reads in Settings | Iter 11 |
| 4 | Frontend utils error-path coverage | Iter 8 |
| 5 | AddFieldDialog + SourcePanel tests | Iter 11 |
| 6 | Known limitations in TECHNICAL_DESIGN §14 | Iter 9 |
| 7a | Backend routes decomposition (912 → 18 LOC aggregator) | Iter 6 |
| 7b | AppWorkspace decomposition (6,100 → 2,221 LOC, −62%) | Iters 3+7+8 |
| 8 | Extraction observability modularization | Iter 7 |
| 8a | Interpretation module decomposition (−82%) | Iters 7+8 |
| 8b | PDF extraction decomposition (−91%) | Iter 7 |
| 8c | DRY constants consolidation | Iter 7 |
| 9 | Streaming upload guard | Iter 3 |
| 10 | Backend failure-path test expansion | Iter 11 |
| 11 | SourcePanel + UploadDropzone test suites | Iter 11 |
| 12 | Shared PdfViewer mock helpers | Iter 11 |
| 13 | Repository split by aggregate | Iter 11 |
| 15 | Minimal auth/token boundary | Iter 3 |
| 19 | Performance benchmarks (P50/P95) | Iter 11 |
| 20 | Error UX mapping | Iter 11 |
| 22 | OpenAPI auto-generated docs | Iter 11 |
| 24 | CI dependency caching + path filtering | Iter 10 |

</details>

---

## Known limitations — conscious trade-offs

These items were evaluated and intentionally deferred. They do not represent oversights.

### 14 — Optional Compose worker profile

**We chose not to** add a dedicated worker service for background processing. The in-process async model ([ADR-ARCH-0004](adr/ADR-ARCH-0004-in-process-async-processing.md)) is sufficient for single-evaluator load, and a worker profile adds operational complexity without demonstrated need at this scale.

### 16 — Persistent event tracing and metrics

**We chose not to** implement structured tracing or Prometheus metrics. The current structured logging is adequate for a demo context. Production-grade observability is documented in technical-design.md §9 as a known evolution path.

### 17 — PostgreSQL adapter

**We chose not to** implement a second database adapter. SQLite with WAL mode handles the target workload. The repository protocol ([ADR-ARCH-0003](adr/ADR-ARCH-0003-raw-sql-repository-pattern.md)) is designed for adapter swapping — adding PostgreSQL would follow the existing interface without architectural changes.

### 18 — Schema migration tooling

**We chose not to** introduce Alembic or similar migration tooling. The bootstrap schema approach works for a portfolio project with a stable schema. Migration tooling becomes essential only when schema evolution frequency increases in production.

### 21 — WCAG 2.1 AA full audit

**We chose not to** pursue a full WCAG audit beyond the quick wins implemented in Iteration 12 (axe-core integration, critical violation fixes). Remaining moderate/minor violations are documented but do not affect core functionality.

### 23 — Structured logging + Prometheus endpoint

**We chose not to** replace `logging.info` with `structlog` JSON output or expose a `/metrics` endpoint. The current log format is human-readable and sufficient for local evaluation. JSON logs and Prometheus are production concerns.

### 24 (remaining) — Python version matrix + deploy previews

**We chose not to** add Python 3.12 CI matrix testing or PR deploy previews. Single-version CI (3.11) keeps pipeline fast. Deploy previews require hosting infrastructure beyond the scope of a technical exercise.

---

## If this were production

If this project were taken to production, the first priorities would be:

1. **PostgreSQL migration** — Replace SQLite for multi-process write concurrency and connection pooling. The repository protocol makes this a clean swap.
2. **Authentication + RBAC** — Expand the token boundary to role-based access (veterinarian, admin, auditor). OAuth2/OIDC integration for clinic systems.
3. **Observability stack** — Structured logging (structlog), distributed tracing (OpenTelemetry), and Prometheus metrics for SLA monitoring.
4. **Background worker** — Extract processing pipeline to a dedicated worker via Compose profile or task queue (Celery/ARQ), enabling horizontal scaling independent of API response times.

---

_This document was reframed from an active backlog to a permanent "known limitations" reference as part of Iteration 12 project close-out (2026-02-27)._