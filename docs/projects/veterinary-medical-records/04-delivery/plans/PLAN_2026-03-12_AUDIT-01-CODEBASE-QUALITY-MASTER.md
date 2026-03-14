# Master Plan (AUDIT-01): Codebase Quality Remediation

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.

**Branch:** docs/audit-01-codebase-quality-plans
**Worktree:** D:/Git/worktrees/codex-permanent-1
**Execution Mode:** Supervisado (plans only — execution in separate chats)
**Model Assignment:** Mixed (see Agent Assignment below)
**PR:** Pending (plans only — PR created on explicit user request)
**Related item ID:** `AUDIT-01`

---

## TL;DR

Comprehensive codebase quality remediation plan based on a 9-dimension audit (security, build, code principles, code quality, dependencies, dead code, observability, concurrency, lifecycle). Current weighted average: **~6.4/10**. Target after all tracks complete: **~8.2/10**. Work is split into 7 parallel tracks with mapped dependencies and specific agent assignments.

---

## Audit Baseline (2026-03-12)

### Automated Checks (all on `main` @ `84acb3efd`)

| Check | Result |
|-------|--------|
| `ruff check backend/` | 0 errors |
| `ruff format --check backend/` | 159 files formatted |
| `eslint + tsc` | 0 errors |
| `prettier --check` | 0 diffs |
| `pytest` | 709 passed, 2 xfailed, 91.66% coverage |
| `vitest` | 345 passed, 86.96/76.88/90.98/87.52% |
| `pip-audit` | 2 vulns in starlette 0.46.2 |

### Worker Audit Scores

| Dimension | Score | Key Findings |
|-----------|-------|--------------|
| Security (ln-621) | 3.5/10 | 2 starlette CVEs, Content-Disposition injection, static bearer token, CORS |
| Build (ln-622) | 7.5/10 | Missing ruff rule categories, npm audit soft-fail, eslint override |
| Code Principles (ln-623) | 7.5/10 | 15 repetitive fetch functions (DRY-1.1), config parsing duplication (DRY-1.2) |
| Code Quality (ln-624) | 5.5/10 | `_suspicious_accepted_flags` CC=32, ~20 magic numbers, AppWorkspace 1460 LOC, 13-param function |
| Dependencies (ln-625) | 8.0/10 | Starlette upgrade needed, framer-motion possibly unused |
| Dead Code (ln-626) | 9.0/10 | Clean — 1 unused test helper only |
| Observability (ln-627) | 3.0/10 | No metrics, no correlation IDs, unstructured logging, no live/ready split |
| Concurrency (ln-628) | 9.5/10 | Excellent — no issues found |
| Lifecycle (ln-629) | 4.5/10 | No scheduler shutdown timeout, missing graceful shutdown config, no live/ready split |

**Weighted Average:** ~6.4/10

---

## Track Summary

| Track | ID | Name | Steps | Agent | Depends On |
|-------|-----|------|-------|-------|-----------|
| T1 | AUDIT-01-T1 | Backend Quality | A1 → A2 | GPT-5.4 (A1), Claude (A2) | — |
| T2 | AUDIT-01-T2 | Backend Security | A4 + A5 | GPT-5.4 | — |
| T3 | AUDIT-01-T3 | Backend Lifecycle | A3 + B4 | GPT-5.4 | — |
| T4 | AUDIT-01-T4 | Frontend DRY | B1 | Claude | — |
| T5 | AUDIT-01-T5 | Backend Config/DI | B2 + B3 | GPT-5.4 | — |
| T6 | AUDIT-01-T6 | Observability | C1 → C2 + C3 | Claude (C1), GPT-5.4 (C2+C3) | — |
| T7 | AUDIT-01-T7 | Dependencies & CI | D1 + D2 + D3 | GPT-5.4 | — |

### Track Handoff Artifacts

- T1 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T1-BACKEND-QUALITY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T1-BACKEND-QUALITY.md)
- T2 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T2-BACKEND-SECURITY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T2-BACKEND-SECURITY.md)
- T3 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T3-BACKEND-LIFECYCLE](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T3-BACKEND-LIFECYCLE.md)
- T4 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T4-FRONTEND-DRY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T4-FRONTEND-DRY.md)
- T5 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T5-BACKEND-CONFIG-DI](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T5-BACKEND-CONFIG-DI.md)
- T6 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T6-OBSERVABILITY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T6-OBSERVABILITY.md)
- T7 implementation handoff report: [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T7-DEPS-CI](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T7-DEPS-CI.md)

### Dependency Graph

```
T1: A1 (constants) ──→ A2 (triage refactor, uses constants from A1)
T2: A4 ─┬─ (independent)
    A5 ─┘
T3: A3 ─┬─ (independent)
    B4 ─┘
T4: B1 (standalone)
T5: B2 ─┬─ (independent)
    B3 ─┘
T6: C1 (correlation ID) ──→ C2 + C3 (logging, uses correlation ID from C1)
T7: D1 ─┬─ (all independent)
    D2 ─┤
    D3 ─┘

Cross-track: NONE — all 7 tracks are fully independent of each other.
```

---

## Step Inventory

### Block A — Code Quality & Security (T1 + T2)

| Step | Description | Files | Risk | Impact |
|------|-------------|-------|------|--------|
| A1 | Extract magic numbers to `extraction_constants.py` | `triage.py`, `field_normalizers.py`, `extraction_quality.py`, NEW `extraction_constants.py` | LOW | Quality 5.5→6.5 |
| A2 | Refactor `_suspicious_accepted_flags` (CC=32 → ≤10) | `triage.py` | MEDIUM | Quality 6.5→7.5 |
| A4 | Sanitize Content-Disposition header (RFC 5987) | `routes_documents.py` | LOW | Security 3.5→5.0 |
| A5 | Override default HTTPException handler (Starlette XSS) | `main.py` | LOW | Security 5.0→6.0 |

### Block B — DRY & Refactoring (T4 + T5)

| Step | Description | Files | Risk | Impact |
|------|-------------|-------|------|--------|
| B1 | Extract fetch wrapper in `documentApi.ts` (14 functions → DRY) | `documentApi.ts` | MEDIUM | Principles 7.5→8.5 |
| B2 | DRY config parsing in `config.py` | `config.py` | LOW | Principles 8.0→8.5 |
| B3 | Replace `_build_structured_field` 13-param with dataclass | `confidence_scoring.py` | LOW | Quality 7.5→8.0 |

### Block C — Observability (T6)

| Step | Description | Files | Risk | Impact |
|------|-------------|-------|------|--------|
| C1 | Add correlation ID middleware (X-Request-ID) | `main.py`, NEW `middleware.py` | MEDIUM | Observability 3.0→5.0 |
| C2 | Configure JSON structured logging | `main.py`, `settings.py` | LOW | Observability 5.0→6.5 |
| C3 | Add LOG_LEVEL env var | `settings.py` | LOW | Observability 6.5→7.0 |

### Block D — Dependencies & CI (T7)

| Step | Description | Files | Risk | Impact |
|------|-------------|-------|------|--------|
| D1 | Upgrade starlette (fix 2 CVEs) | `requirements.txt` | LOW | Security 6.0→7.5 |
| D2 | Remove `continue-on-error` from npm audit in CI | `ci.yml` | LOW | Build 7.5→8.0 |
| D3 | Verify and remove framer-motion if unused | `package.json` | LOW | Dependencies 8.5→9.0 |

---

## Agent Assignment Strategy

### Claude Opus 4.6 (3 tasks — high complexity, design decisions)

| Task | Rationale |
|------|-----------|
| A2 (triage refactor CC=32→≤10) | Requires understanding of domain logic, strategy pattern selection, maintaining all 709 test passes |
| B1 (fetch wrapper DRY extraction) | Requires TypeScript generic design, error type preservation, 345 vitest passes |
| C1 (correlation ID middleware) | Requires ASGI middleware design, contextvars for propagation, integration with existing auth middleware |

### GPT-5.4 (11 tasks — mechanical, well-defined)

| Task | Rationale |
|------|-----------|
| A1 (constants extraction) | Mechanical move — no design decisions |
| A4 (header sanitize) | Well-defined RFC 5987 pattern |
| A5 (HTTPException override) | Documented Starlette fix |
| B2 (config DRY) | Simple extract-helper refactor |
| B3 (13-param → dataclass) | Mechanical — create dataclass, update callers |
| A3/B4 (lifecycle) | Follow uvicorn/docker docs, add timeout + probes |
| C2+C3 (JSON logging + LOG_LEVEL) | Standard `logging.config.dictConfig` pattern |
| D1 (starlette upgrade) | `pip install --upgrade` + test |
| D2 (npm audit gate) | Remove one YAML line |
| D3 (framer-motion check) | Grep + remove if unused |

---

## Merge Order

All 7 tracks are cross-independent. Recommended merge sequence to minimize conflict:

1. **T7** (D1+D2+D3) — Deps/CI, tiny diff, zero code conflict risk
2. **T3** (A3+B4) — Lifecycle, touches `main.py` lifespan + Docker files
3. **T2** (A4+A5) — Security, touches `main.py` + `routes_documents.py`
4. **T5** (B2+B3) — Config/DI, isolated files
5. **T1** (A1→A2) — Backend Quality, largest refactor
6. **T6** (C1→C2+C3) — Observability, touches `main.py` middleware stack
7. **T4** (B1) — Frontend, zero backend conflict

> If T3, T2, and T6 are merged close together they may conflict on `main.py`. Resolve by rebasing onto latest main between merges.

---

## Projected Impact

| Dimension | Before | After | Delta |
|-----------|--------|-------|-------|
| Security | 3.5 | 7.5 | +4.0 |
| Build | 7.5 | 8.0 | +0.5 |
| Code Principles | 7.5 | 8.5 | +1.0 |
| Code Quality | 5.5 | 8.0 | +2.5 |
| Dependencies | 8.25 | 9.0 | +0.75 |
| Dead Code | 9.0 | 9.0 | 0 |
| Observability | 3.0 | 7.0 | +4.0 |
| Concurrency | 9.5 | 9.5 | 0 |
| Lifecycle | 4.5 | 7.5 | +3.0 |
| **Weighted Average** | **~6.4** | **~8.2** | **+1.8** |

---

## Out of Scope (Deliberate Exclusions)

| Item | Reason |
|------|--------|
| AppWorkspace.tsx decomposition (1460 LOC) | High regression risk, requires deep React state analysis |
| i18n / externalized strings | Feature work, not quality remediation |
| Prometheus metrics infrastructure | Requires Prometheus server, too large for this remediation |
| Sentry / frontend error reporting | Requires external service setup |
| Production authentication upgrade | Separate security initiative (ARCH-13) |

---

## Execution Protocol

1. Each track executes in a **separate chat session**
2. Each chat receives its **track plan** as context + link to this master plan
3. Each track creates its own branch: `improvement/audit-01-t<N>-<slug>`
4. Each track produces a **single PR** (validated by PR Partition Gate in track plan)
5. PRs are merged in the order specified above
6. After all 7 PRs are merged, run full audit re-evaluation to confirm ≥8.0 average

---

## Validation Criteria (Post-Merge)

- [ ] `ruff check backend/` — 0 errors
- [ ] `ruff format --check backend/` — 0 diffs
- [ ] `pytest` — 709+ passed, ≥91% coverage
- [ ] `eslint + tsc` — 0 errors
- [ ] `vitest` — 345+ passed, ≥80% coverage
- [ ] `pip-audit` — 0 vulnerabilities
- [ ] `npm audit --audit-level=high` — 0 vulnerabilities (enforced)
- [ ] `radon cc -n C backend/app/` — 0 functions with CC > 10
- [ ] No magic numbers in `triage.py`, `field_normalizers.py`, `extraction_quality.py`
- [ ] Correlation ID present in all log output
- [ ] `/health/live` and `/health/ready` endpoints respond correctly
- [ ] Graceful shutdown completes within 30s under load
