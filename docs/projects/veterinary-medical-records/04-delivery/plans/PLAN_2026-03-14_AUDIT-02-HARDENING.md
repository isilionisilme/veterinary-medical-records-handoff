# Plan: AUDIT-02 Hardening

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.

**Branch:** `fix/security-lifecycle-hardening`
**PR:** See ## PR Roadmap
**User Story:** N/A — audit-driven hardening pass
**Prerequisite:** `origin/main` @ `ebf9b47e` (clean, all CI green, PR #22 merged)
**Worktree:** `D:/Git/worktrees/security-lifecycle-hardening`
**Execution Mode:** In-place execution from dedicated worktree
**Model Assignment:** Claude Opus 4.6

---

## Context

A formal 9-category codebase re-evaluation (ln-621 through ln-629) was executed on 2026-03-14 against `origin/main` @ `ebf9b47e`, scoring **7.4/10 unweighted average**. The evaluation surfaced 8 High-severity findings across Security, Lifecycle, Observability, and Dead Code categories. The most impactful gaps are missing security response headers, no SIGTERM handler, and a legacy re-export shim.

Score baseline:

| Category | Score |
|---|---:|
| Security (ln-621) | 5.8 |
| Build & CI (ln-622) | 5.6 |
| Code Principles (ln-623) | 9.0 |
| Code Quality (ln-624) | 9.0 |
| Dependencies (ln-625) | 6.9 |
| Dead Code (ln-626) | 7.8 |
| Observability (ln-627) | 6.8 |
| Concurrency (ln-628) | 8.4 |
| Lifecycle (ln-629) | 7.6 |

---

## Objective

Raise the audit score by resolving the highest-ROI findings: security hardening (headers, debug gate, body limits), lifecycle robustness (SIGTERM handler), and dead code elimination (processing_runner.py shim). Target: 6 High-severity findings resolved, overall score from 7.4 to ~8.0+.

---

## Scope Boundary

**In scope:**
- Security response headers middleware (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- SIGTERM signal handler
- Gate debug endpoints behind `VET_RECORDS_DEBUG_ENDPOINTS` setting
- POST body size limits on non-upload endpoints
- `processing_runner.py` legacy shim removal (redirect 15 test imports to direct `processing.*` modules)

**Out of scope:**
- mypy adoption (high effort, low evaluator ROI)
- ESLint rule expansion (existing gates sufficient)
- npm audit level change (risk of transitive breakage)
- Prometheus /metrics endpoint (deferred — 4h effort, separate plan)
- Frontend changes of any kind
- Architectural changes
- New features

---

## PR Roadmap

Delivery split into 2 sequential PRs.
Merge strategy: Sequential.

| PR | Branch | Scope | Depends on | Status | URL |
|---|---|---|---|---|---|
| PR-1 | `fix/security-lifecycle-hardening` | Security headers + SIGTERM handler + debug endpoint gate + POST body limits | None | In progress | — |
| PR-2 | `chore/remove-processing-runner-shim` | Remove `processing_runner.py`, redirect 15 test imports | PR-1 | Not started | — |

### Partition gate evidence

#### PR-1 (security + lifecycle hardening)

| Metric | Value | Threshold | Result |
|---|---:|---|---|
| Code files (est.) | 5 (main.py, settings.py, routes_review.py, routes_calibration.py, middleware test) | 15 | Under |
| Code lines (est.) | ~120 (security headers ~30, SIGTERM ~20, debug gate ~40, body limits ~30) | 400 | Under |
| Semantic risk | Backend-only, single axis (infra hardening) | Mixed axes | None |

#### PR-2 (dead code cleanup)

| Metric | Value | Threshold | Result |
|---|---:|---|---|
| Code files (est.) | 16 (1 deleted shim + 15 test files with import redirect) | 15 | Over by 1 |
| Code lines (est.) | ~80 (1 file deleted ~45 LOC, 15 import lines changed) | 400 | Under |
| Semantic risk | Backend test-only, mechanical import redirect | Mixed axes | None |

PR-2 exceeds the file count threshold by 1. All 15 test file changes are single-line mechanical import redirects (zero logic change). The deleted file has 0 production importers. Decision gate required: Option A (single PR, mechanical) vs Option B (further split).

---

## Design decisions

- **Security headers as Starlette middleware, not FastAPI middleware:** Headers must apply to all responses (including error responses and non-API routes like /health). A Starlette `@app.middleware("http")` ensures full coverage.
- **SIGTERM via `signal` module, not uvicorn hook:** The signal handler registers on the event loop so the lifespan `finally` block still runs.
- **Debug gate via setting, not route removal:** Keeps debug endpoints available in dev when explicitly enabled.
- **processing_runner.py full delete, not deprecation warning:** The shim has zero production importers. All 15 remaining importers are test files.

---

## Execution Status

### Phase 0 — Plan-start preflight

- [x] Record plan-start snapshot

### Phase 1 — Security response headers [PR-1]

- [x] **[PR-1] P1-A:** Add security headers middleware in `backend/app/main.py` after CORS middleware. Headers to set on every response:
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy: default-src 'self'`
  - `Referrer-Policy: strict-origin-when-cross-origin`

### Phase 2 — SIGTERM signal handler [PR-1]

- [x] **[PR-1] P2-A:** Register SIGTERM handler inside the lifespan context.

### Phase 3 — Gate debug endpoints [PR-1]

- [x] **[PR-1] P3-A:** Add `vet_records_debug_endpoints: str | None` to `Settings` in `backend/app/settings.py`.
- [x] **[PR-1] P3-B:** Add helper `debug_endpoints_enabled() -> bool` in `backend/app/config.py`.
- [x] **[PR-1] P3-C:** Gate the two review debug endpoints with 403 when disabled.

### Phase 4 — POST body size limits [PR-1]

- [x] **[PR-1] P4-A:** Add reusable body-size-limit helper.
- [x] **[PR-1] P4-B:** Apply the guard to POST endpoints in `routes_review.py` and `routes_calibration.py`.

> Commit checkpoint — Phases 1–4 complete. Suggested message: `fix(security): add response headers, SIGTERM handler, debug gate, body limits`.

### Phase 5 — Documentation task [PR-1]

- [x] **[PR-1] P5-A:** Verify whether wiki or doc updates are needed for PR-1 changes. Result: `no-doc-needed` — the repo has no authoritative runtime env-var inventory for this class of backend-only hardening flag, and the response-header/body-limit changes are internal security behavior changes rather than user-operable workflow changes.

### Phase 6 — Remove processing_runner.py shim [PR-2]

- [ ] **[PR-2] P6-A:** Redirect the 15 test imports to direct `processing.*` modules.
- [ ] **[PR-2] P6-B:** Delete `backend/app/application/processing_runner.py`.
- [ ] **[PR-2] P6-C:** Run full test suite (`pytest`, `vitest`) to confirm zero breakage.

### Phase 7 — Documentation task [PR-2]

- [ ] **[PR-2] P7-A:** Verify whether wiki or doc updates are needed for PR-2 changes.

---

## Acceptance criteria

1. All existing tests pass.
2. Security response headers present on all HTTP responses.
3. SIGTERM triggers graceful shutdown on Linux/macOS.
4. Debug endpoints return 403 when `VET_RECORDS_DEBUG_ENDPOINTS` is unset.
5. Debug endpoints return 200 when `VET_RECORDS_DEBUG_ENDPOINTS=true`.
6. POST body >1 MB on non-upload endpoints returns 413.
7. `processing_runner.py` deleted; no imports reference it.
8. L2 preflight passes for both PRs.

---

## How to test

**PR-1:**
```bash
curl -I http://localhost:8000/health
VET_RECORDS_DEBUG_ENDPOINTS=true uvicorn backend.app.main:app
pytest backend/tests -q
```

**PR-2:**
```bash
pytest backend/tests -q
```

---

## Prompt Queue

| Phase | Prompt summary | Agent role |
|---|---|---|
| P1-P4 | Implement security headers, SIGTERM, debug gate, body limits in backend | Execution agent |
| P6 | Redirect 15 test imports and delete shim | Execution agent |

---

## Active Prompt

Execute PR-1 Phases 1-4 from the dedicated worktree.
