# Known Limitations & Future Directions

---

## Completed improvements

Across 20 releases, **15 planned improvements** were fully resolved. See [implementation-history.md § Releases delivered](implementation-history.md#releases-delivered) for the complete delivery timeline with quality evidence and completion dates.

---

## Known limitations — conscious trade-offs

These items were evaluated and intentionally deferred. Each links to its authoritative decision record.

| # | Limitation | Decision record |
|---|---|---|
| 14 | No dedicated Compose worker profile | [ADR-in-process-async-processing](ADR-in-process-async-processing) |
| 16 | No persistent event tracing or Prometheus metrics | [ADR-structured-logging-no-metrics](ADR-structured-logging-no-metrics) |
| 17 | No PostgreSQL adapter | [ADR-sqlite-database](ADR-sqlite-database) + [ADR-raw-sql-repository-pattern](ADR-raw-sql-repository-pattern) |
| 18 | No schema migration tooling (Alembic) | [ADR-bootstrap-schema-no-migrations](ADR-bootstrap-schema-no-migrations) |
| 21 | WCAG 2.1 AA limited to critical violations | Iteration 12 resolved critical path (axe-core + aria-labels); moderate/minor deferred — see [technical-design.md §14](technical-design#14-known-limitations) |
| 23 | Human-readable logs, no `/metrics` endpoint | [ADR-structured-logging-no-metrics](ADR-structured-logging-no-metrics) |
| 24 | Single Python version CI, no deploy previews | [ADR-ci-single-python-version](ADR-ci-single-python-version) |

---

## If this were production

If this project were taken to production, our priorities could be:

### Security & access control

- **Authentication + RBAC** — Expand the current token boundary to role-based access (veterinarian, admin, auditor), with OAuth2/OIDC integration for clinic systems.
- **Secrets management + transport security** — Move credentials to a secret manager, enforce key rotation and TLS end-to-end, and harden upload boundaries with payload/rate limits and content scanning.

### Infrastructure & operations

- **PostgreSQL migration** — Replace SQLite for multi-process write concurrency, connection pooling, and production-grade operational tooling.
- **Observability stack** — Add structured logging (structlog), distributed tracing (OpenTelemetry), and Prometheus metrics for SLA monitoring and incident response.
- **Background worker hardening** — Extract processing to a dedicated worker (Compose profile or queue such as Celery/ARQ) with idempotency, retries/backoff, timeouts, and dead-letter handling.
- **Backups, disaster recovery, and data governance** — Define tested backup/restore procedures (RPO/RTO), immutable audit trails, and retention/deletion policies for medical-document data.

### Standards & compliance

- **Interoperability standards** — Align with internationally recognized standards for data exchange, clinical terminology, and medical record structure:
   - *Data interchange* — [HL7 FHIR](https://hl7.org/fhir/) for integration with hospitals, laboratories, and insurance systems.
   - *Clinical terminology* — [SNOMED CT](https://www.snomed.org/) Veterinary Extension as a universal coded vocabulary for diseases, symptoms, and procedures.
   - *Medical record structure* — The AAHA-recommended [POVMR](https://www.aaha.org/) (Problem-Oriented Veterinary Medical Record) format with SOAP progress notes.
- **Applicable international standards (ISO)** — ISO 8601 dates (already adopted), ISO 11784/11785 microchip ID validation, ISO 3166-1 country codes, ISO 639-1 language codes (already used).
- **Legal and regulatory requirements** — Record immutability (24 h freeze), GDPR compliance, EU Regulation 2019/6 (electronic veterinary prescriptions), GVP risk documentation, and full audit trail traceability.

---
