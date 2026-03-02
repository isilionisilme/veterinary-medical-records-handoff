# API implementation 

## Authoritative API contracts (do not duplicate)
- Endpoint map: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3 (+ B3.1)
- Run resolution per endpoint: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3.1
- Error response format: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B2.6
- Endpoint error semantics & error codes: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3.2

Implementation guidance (wiring and enforcement):
- Keep routers thin adapters: parse/validate → call an `application` use case → map to response schema.
- Centralize error handling so the Technical Design error contract is enforced by default:
  - Prefer a shared `AppError` type plus FastAPI exception handlers that emit `{error_code, message, details?}`.
  - Avoid per-route ad-hoc error payloads.
- When returning `409 CONFLICT`, ensure `details.reason` uses the Technical Design closed set (e.g., `NO_COMPLETED_RUN`, `REVIEW_BLOCKED_BY_ACTIVE_RUN`).

## Editing while active run exists 
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3.2 (Conflict reasons and error semantics).

Implementation guidance:
- When a workflow is blocked by an active run, return the authoritative conflict response using `details.reason = REVIEW_BLOCKED_BY_ACTIVE_RUN`.
