# ADR-structured-logging-no-metrics: Human-Readable Logging without Metrics Endpoint

## Context

The backend emits structured log entries (with `document_id`, `run_id`, `step_name`, `event_type`) via Python's standard `logging` module in human-readable format. Production-grade systems typically use JSON-formatted logs (`structlog`) and expose Prometheus `/metrics` endpoints for SLA monitoring and distributed tracing (OpenTelemetry).

## Decision Drivers

- Evaluator reads logs directly in `docker compose logs` — human-readable format is more useful than JSON.
- No monitoring infrastructure (Grafana, Prometheus, Loki) exists in the evaluation environment.
- Structured field emission (consistent keys) is already in place, making a future migration to JSON straightforward.

## Considered Options

### Option A — Python `logging` with structured fields, human-readable (current)

#### Pros

- Readable in terminal and Docker logs without tooling.
- Consistent field keys (`document_id`, `run_id`, etc.) enable grep-based debugging.
- Zero additional dependencies.

#### Cons

- Not machine-parseable without regex.
- No `/metrics` endpoint for automated monitoring.

### Option B — `structlog` JSON output + Prometheus `/metrics`

#### Pros

- Machine-parseable logs for log aggregation (ELK, Loki).
- Prometheus endpoint enables SLA dashboards and alerting.
- Industry standard for production observability.

#### Cons

- JSON logs are unreadable in `docker compose logs` without `jq`.
- Prometheus endpoint requires scraping infrastructure to be useful.
- Adds `structlog` + `prometheus-client` dependencies.

### Option C — OpenTelemetry distributed tracing

#### Pros

- Request-level tracing across service boundaries.
- Correlation IDs propagated automatically.

#### Cons

- Requires collector infrastructure (Jaeger/Zipkin).
- Single-service architecture gains limited value from distributed tracing.

## Decision

Adopt **Option A: human-readable structured logging** with no metrics endpoint for current scope.

## Rationale

1. `backend/app/logging_config.py` configures consistent log formatting with structured fields.
2. Processing modules emit logs with `document_id` and `run_id` context — the structured fields are already present, only the output format would change.
3. The migration path to `structlog` is mechanical: replace `logging.getLogger` calls with `structlog.get_logger` and configure JSON rendering — no architectural changes required.
4. A `/metrics` endpoint can be added via `prometheus-fastapi-instrumentator` as a single middleware registration.

## Consequences

### Positive

- Logs are immediately readable during local evaluation.
- No monitoring infrastructure to provision or maintain.

### Negative

- No automated alerting or SLA tracking.
- Log analysis relies on manual grep/search.

### Risks

- Production deployment without observability stack would impair incident response.
- Mitigation: the evolution path (structlog + Prometheus + OpenTelemetry) is documented in technical-design.md §9.2 and requires no architectural changes.

## Code Evidence

- `backend/app/logging_config.py` — log configuration
- `backend/app/application/processing/orchestrator.py` — structured log emission with `run_id`
- `backend/app/application/processing/` — step-level logging with `document_id`

## Related Decisions

- [ADR-modular-monolith: Modular Monolith over Microservices](ADR-modular-monolith)