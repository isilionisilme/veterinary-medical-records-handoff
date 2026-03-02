# 13. Security Boundary

Authentication and authorization are **minimal and optional** for the current exercise.

The backend supports an optional bearer-token boundary via `AUTH_TOKEN`:

- If `AUTH_TOKEN` is unset or empty, authentication is disabled and evaluator behavior is unchanged.
- If `AUTH_TOKEN` is set, endpoints under `/api/*` require `Authorization: Bearer <AUTH_TOKEN>`.

This preserves low-friction local evaluation while enabling a minimal access gate.

## Design decisions
- Optional auth middleware only for `/api/*`, disabled by default.
- Upload validation covers file-type and content-type, not identity.
- No rate limiting — single-user model.

## Production path
1. Token-based auth (OAuth 2.0 / JWT) at API gateway.
2. Role-based authorization on document/processing endpoints.
3. Rate limiting middleware.
4. Audit logging on protected resources.
5. Streaming upload with early size rejection (roadmap #9).

Architecture supports this: hexagonal ports/adapters allow inserting auth without domain changes. Roadmap: future-improvements.md #15.
