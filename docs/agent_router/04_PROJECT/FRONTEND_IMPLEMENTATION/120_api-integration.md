# API Integration

Server state is managed exclusively via **TanStack Query**.

## Contract authority (backend)
- Endpoint paths, payload shapes, and error semantics are owned by [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) (Appendix B3/B3.2).
- This document references contracts for implementation convenience only; if any conflict exists, [`technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) wins.

## Error handling (authoritative rule)
The frontend MUST branch on `error_code` (and optional `details.reason`) only.
It must not branch on HTTP status alone, message strings, or backend stack traces.

Implement a single API wrapper that:
- Parses the normative error response shape `{ error_code, message, details? }` (Appendix B2.6).
- Throws/returns a typed error that downstream UI code can switch on via `error_code` and `details.reason`.

Patterns:
- `useQuery` for fetching:
  - document lists,
  - document status,
  - document interpretations.
- `useMutation` for:
  - persisting field edits,
  - marking documents as reviewed.
- query invalidation is used to keep UI state consistent after mutations.

No custom caching or duplication of server state logic is introduced.

---
