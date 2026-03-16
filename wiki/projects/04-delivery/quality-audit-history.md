# Quality & Architecture Audit History

The codebase has undergone multiple audit cycles throughout development — from early maintainability layering and CI baseline setup, through formal 9-category structured audits, to targeted architecture hygiene passes. This document consolidates the findings and resolution status across all cycles.

## Executive Summary

The project follows a continuous **audit → remediate → verify** cycle. The latest full audit is **Audit-05: 9.3/10**, run fresh against the remediated codebase at commit `2ace7d93`, with zero critical or high findings remaining.

This page now shows the direct score produced by each audit cycle in the main evolution table. Remediation campaigns, deterministic re-evaluations, and post-audit corrections remain documented inside the corresponding per-audit sections below.

Five audit cycles using 9-category automated analysis (security, build, architecture, quality, dependencies, dead code, observability, concurrency, lifecycle), plus 12-Factor compliance assessment and post-implementation architectural review, progressively raised the engineering baseline.

---

## Score Evolution

| Category | Audit-01 | Audit-02 | Audit-03 | Audit-04 | Audit-05 |
|---|:-:|:-:|:-:|:-:|:-:|
| Security | 3.5 | 5.8 | 9.1 | 10.0 | **10.0** |
| Build & CI | 7.5 | 5.6 | 8.5 | 9.4 | **9.4** |
| Architecture & Design | 7.5 | 9.0 | 6.6 | 7.0 | **9.0** |
| Code Quality | 5.5 | 9.0 | 2.5 | 6.5 | **9.0** |
| Dependencies | 8.0 | 6.9 | 0.4 | 8.2 | **8.8** |
| Dead Code | 9.0 | 7.8 | 8.1 | 9.4 | **9.3** |
| Observability | 3.0 | 6.8 | 8.4 | 9.5 | **9.3** |
| Concurrency | 9.5 | 8.4 | 7.9 | 7.6 | **9.6** |
| Lifecycle | 4.5 | 7.6 | 9.1 | 9.3 | **9.6** |
| **Overall** | **~6.4** | **7.4** | **6.7** | **8.5** | **9.3** |

> "Architecture & Design" merges the former "Code Principles" (Audit-01/02/04) and "Architecture" (Audit-03) categories — same concerns (ln-623 worker), renamed between cycles. Scores shown here are the direct audit outputs for each cycle; remediation-adjusted details remain documented in the per-audit sections below.

---

## Audit-03 — Clean-Slate Discovery & Remediation

Audit-03 used a clean-slate approach (no prior findings shown to the auditor) to avoid anchoring bias. 9 specialized workers found **83 findings** (0 Critical, 13 High, 31 Medium, 39 Low), scoring **6.7/10**.

The two weakest dimensions:
- **Dependencies & Reuse: 0.4** — 5 packages multiple major versions behind (0 CVEs)
- **Code Quality: 2.5** — 7 HIGH findings: CC>25 functions, god component, prop drilling

A 12-PR remediation campaign (PRs #25–#36) then resolved 63 of 83 findings, eliminated all critical and high items, and established the baseline later verified by subsequent fresh audits.


### Remediation campaign

**Phase 1 — Category-wide remediation (PRs #25–#31)**

| PR | Branch | Scope | Status |
|---|---|---|---|
| [#25](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/25) | `chore/dependency-upgrades` | All dependency upgrades (dev + production + frontend) | ✅ Merged |
| [#26](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/26) | `fix/backend-quick-wins` | Security hardening, lifecycle fixes, observability fixes | ✅ Merged |
| [#27](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/27) | `refactor/frontend-cleanup` | Type consolidation, dead code removal, console guard | ✅ Merged |
| [#28](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/28) | `refactor/backend-complexity` | CC>25 hotspot refactors, orchestrator step lifecycle, constants | ✅ Merged |
| [#29](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/29) | `refactor/route-di-boilerplate` | Route DI (`Depends`), `require_document()`, legacy shim removal | ✅ Merged |
| [#30](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/30) | `refactor/workspace-context` | WorkspaceContext, prop-drilling elimination (30→<10 props) | ✅ Merged |
| [#31](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/31) | `fix/async-concurrency` | `asyncio.to_thread()` for orchestrator/scheduler, async upload | ✅ Merged |

**Phase 2 — Code Quality deep refactoring (PRs #32–#36)**

Targeted the remaining Code Quality findings via cyclomatic complexity reduction, function extraction, and nesting reduction.

| PR | Branch | Scope | Status |
|---|---|---|---|
| [#32](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/32) | `refactor/postprocess-weights` | Q-3: decompose `postprocess_weights` CC=26→2 | ✅ Merged |
| [#33](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/33) | `refactor/signature-cleanup` | Q-15, Q-16, Q-24, Q-25: NamedTuple + typed signatures | ✅ Merged |
| [#34](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/34) | `refactor/domain-cc-phase1` | Q-8: `populate_visit_scoped_fields` CC=24→8; Q-10: `apply_interpretation_edits` CC=20→8 | ✅ Merged |
| [#35](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/35) | `refactor/domain-cc-phase2` | Q-9: `extract_owner_nombre_candidates` CC=22→12; Q-11: `_build_visit_roster` CC=20→10; + `name_normalization.py` extraction | ✅ Merged |
| [#36](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/36) | `refactor/code-quality-final` | Q-13: tokenizer nesting depth reduced; Q-16, Q-17: bounded O(n²) eliminated | ✅ Merged |

**Severity profile shift:**

| Severity | Before | After Phase 1 | After Phase 2 | Re-evaluation (final) |
|---|---:|---:|---:|---:|
| Critical | 0 | 0 | 0 | 0 |
| High | 13 | 1 | 0 | **0** |
| Medium | 31 | 12 | 9 | **5** |
| Low | 39 | 19 | 10 | **15** |
| **Total** | **83** | **32** | **19** | **20** |

**Key design decisions:**
- `Depends()` over manual `cast()`: FastAPI native DI replaces 18× boilerplate
- `WorkspaceContext` + `useWorkspace()` hook: 3 components drop from 29-30 props to <10
- `asyncio.to_thread()` for orchestrator: wraps sync pipeline instead of rewriting as async
- Dispatch table / chain-of-responsibility patterns for CC>25 functions
- Extract-and-delegate pattern for CC>20 domain functions: helper extraction + NamedTuple returns
- `name_normalization.py` module extraction to maintain `date_parsing.py` under 500-LOC gate
- PR #36: tokenizer nesting reduction + O(n²) elimination for Q-13, Q-16, Q-17

**Remaining 20 findings (deliberate exclusions):**

| Finding | Sev | Rationale |
|---|---|---|
| Q-12: `create_app` 165 LOC | M | App factory — inherent glue, low CC |
| A-2: Guard-clause pattern ×9 | M | Minor, localized pattern |
| B-1: `review_payload_projector.py` 72% coverage | M | Separate test authoring effort |
| O-1: No Prometheus metrics | M | Requires infra, monolith scope |
| O-2: No OpenTelemetry tracing | M | Requires infra decision |
| Q-14: 10+ magic thresholds | L | Extraction heuristics — documented inline, low CC |
| Q-19..Q-22: Informational baselines | L | Below action threshold |
| A-5: Observability check ×4 | L | Low impact |
| B-2, B-3: Transitive dep warnings | L | External / upstream |
| B-5: Coverage near threshold | L | Near threshold |
| DC-6..DC-8: Legacy aliases / compat re-exports | L | Intentional backward compatibility |
| C-3: Non-atomic lru_cache | L | Mitigated (frozen dataclass) |
| C-4: Advisory TOCTOU | L | Low risk, documented |
| C-5: Implicit single-instance | L | Deployment model constraint |

> Outcome summary: 63 of 83 findings resolved, with 20 deliberate exclusions (5M + 15L) documented with rationale.

---

## Audit-04 — Full ln-620 Audit & Targeted Remediation

Audit-04 ran all 9 specialized workers against commit `337061f3` with stricter detection than previous cycles, finding **39 findings** (0 Critical, 0 High, 16 Medium, 23 Low), scoring **8.5/10**. The main weaknesses were visit scoping complexity (Code Quality), DRY opportunities in repository/config (Code Principles), and TOCTOU races in file operations (Concurrency).

A focused 4-PR remediation campaign (PRs #37–#40) then resolved 14 findings, primarily across Code Principles, Code Quality, and Concurrency, and this set was later validated by the fresh Audit-05 run.

### Remediation campaign (PRs #37–#40)

| PR | Branch | Scope | Status |
|---|---|---|---|
| [#37](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/37) | `refactor/row-mappers` | Extract `_row_to_document()` + `_row_to_run_details()` helpers (CP-001, CP-002) | ✅ Merged |
| [#38](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/38) | `refactor/config-consolidation` | Consolidate `_read_env_bool()`, inline float parser, `_UNASSIGNED_VISIT_SORT_DATE` constant (CP-003, CP-004, CQ-010) | ✅ Merged |
| [#39](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/39) | `fix/error-codes-toctou-atomic` | `route_constants.py` enum, TOCTOU try-except, atomic `os.replace()` (CP-007, CC-001..004) | ✅ Merged |
| [#40](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/40) | `refactor/visit-scoping-decompose` | VisitRoster dataclass, `_resolve_target_visit()`, `_classify_fields_into_scopes()`, nesting reduction (CQ-001, CQ-002, CQ-004, CQ-005) | ✅ Merged |

### Severity profile shift

| Severity | Before | After |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 0 | 0 |
| Medium | 16 | **4** |
| Low | 23 | **21** |
| **Total** | **39** | **25** |

**Remaining 25 findings (deliberate exclusions):** CQ-003 WorkspaceContext size (M), DEP-001/002 PDF lib versions (2M), OBS-001 Prometheus (M), plus 21 LOW items (deprecation warnings, minor DRY/quality, backward-compat shims, SQLite config, dev-only SIGINT). All documented with rationale in `codebase-audit-04.md`.

> Outcome summary: 14 findings resolved (12 Medium, 2 Low), with no critical or high findings introduced.

---

## Audit-05 — Fresh Full Audit (Post-Remediation Verification)

Audit-05 ran all 9 specialized workers fresh against commit `2ace7d93` (after PRs #37–#40 remediation) to obtain **real scores** rather than deterministic re-evaluation projections. Result: **20 findings** (0 Critical, 0 High, 6 Medium, 14 Low), scoring **9.3/10**.

This confirms the Audit-04 re-evaluation projection (also 9.3) was accurate. The 4-PR remediation campaign effectively resolved 14 findings and no new issues were introduced.

| Category | Score | Findings | Key items |
|---|---:|---|---|
| Security | **10.0** | C:0 H:0 M:0 L:0 | All checks passed |
| Build Health | **9.4** | C:0 H:0 M:0 L:3 | SWIG warnings, CI minor items |
| Code Principles | **9.0** | C:0 H:0 M:2 L:0 | SQL field list duplication (2 repos) |
| Code Quality | **9.0** | C:0 H:0 M:1 L:3 | WorkspaceContext size, borderline CC |
| Dependencies | **8.8** | C:0 H:0 M:1 L:2 | PyMuPDF input risk, slowapi maintenance |
| Dead Code | **9.3** | C:0 H:0 M:1 L:1 | Unused constant, compat aliases |
| Observability | **9.3** | C:0 H:0 M:1 L:1 | Missing Prometheus metrics |
| Concurrency | **9.6** | C:0 H:0 M:0 L:2 | Minor TOCTOU inconsistency |
| Lifecycle | **9.6** | C:0 H:0 M:0 L:2 | SIGINT dev-only, signal handler I/O |
| **Overall** | **9.3** | C:0 H:0 M:6 L:14 | |

### Remediation set verified by Audit-05

Audit-05 did not trigger a new remediation phase. Its purpose was to verify the effectiveness of the Audit-04 remediation set already merged into `main`.

| PR | Branch | Scope verified by Audit-05 | Status |
|---|---|---|---|
| [#37](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/37) | `refactor/row-mappers` | Row mapper extraction for document/run repositories | ✅ Verified |
| [#38](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/38) | `refactor/config-consolidation` | Config parser consolidation and sentinel constant extraction | ✅ Verified |
| [#39](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/39) | `fix/error-codes-toctou-atomic` | Error-code normalization, TOCTOU removals, atomic writes | ✅ Verified |
| [#40](https://github.com/isilionisilme/veterinary-medical-records-handoff/pull/40) | `refactor/visit-scoping-decompose` | Visit scoping decomposition, signature cleanup, nesting reduction | ✅ Verified |

### Verification outcome vs Audit-04 baseline

| Metric | Audit-04 baseline | Audit-05 fresh audit | Delta |
|---|---:|---:|---:|
| Critical | 0 | 0 | = |
| High | 0 | 0 | = |
| Medium | 16 | **6** | -10 |
| Low | 23 | **14** | -9 |
| **Total findings** | **39** | **20** | **-19** |
| **Overall score** | **8.5** | **9.3** | **+0.8** |

### Residual backlog after verification

| Area | Remaining items | Notes |
|---|---|---|
| Code Principles | 2M | SQL field list duplication remains in 2 repositories |
| Code Quality | 1M + 3L | WorkspaceContext size remains the main structural item |
| Dependencies | 1M + 2L | PyMuPDF parsing risk and low-maintenance packages |
| Dead Code | 1M + 1L | One unused constant plus intentional compat aliases |
| Observability | 1M + 1L | Prometheus/metrics still deferred |
| Concurrency | 2L | Minor consistency issues only |
| Lifecycle | 2L | Dev-only SIGINT / signal-handler nuances |

**Layer 2 re-evaluation:** 18 false positives removed across 4 workers (627, 629, 624, 625 — typical subagent over-detection). All findings verified against actual code at commit `2ace7d93`.

> **Score: 9.3/10** — real fresh audit confirms the remediation projection. Audit cycle complete.

---

## Previous Audit Cycles

### Audit-01 — Deep Automated Analysis

9 specialized audit workers. Scored **6.4/10** (3 critical, 8 high). A 7-track remediation campaign then addressed code quality, security, lifecycle, observability, and dependency CVEs, resolving 17 findings and eliminating all critical items.

### Audit-02 — Stricter Re-evaluation & Targeted Fixes

Stricter criteria applied, scoring **7.4/10**. Two targeted PRs then resolved 5 findings (security headers, SIGTERM handler, debug gate, body limits, dead code shim).

### Initial Maintainability Audit

Repository-only read-only assessment. **15/15 findings resolved** — including 2 critical monolith decompositions (`App.tsx`, `processing_runner.py`), 4 high-severity fixes, and CI/tooling gaps across 9 categories.


---

## 12-Factor Compliance

**Scope:** Backend FastAPI + frontend React, local Docker Compose deployment model.

| Factor | Initial Status | Resolution |
|---|---|---|
| I. Codebase | ✅ Strong | — |
| II. Dependencies | ✅ Strong | — |
| III. Config | Partial | ✅ Centralized settings module validates all runtime env vars; infra adapters consume resolved settings. |
| IV. Backing services | ✅ Strong | — |
| V. Build, release, run | Partial | ✅ Release metadata surface (commit/version/build date) added and verified in CI. |
| VI. Processes | Partial | ✅ Scheduler bootstrap decoupled from API composition root via processing runner boundary. |
| VII. Port binding | ✅ Strong | — |
| VIII. Concurrency | Partial | Explicitly out of scope — single-machine Compose target. Optional worker profile documented in future improvements. |
| IX. Disposability | ✅ Strong | — |
| X. Dev/prod parity | ✅ Strong | — |
| XI. Logs | ✅ Strong | — |
| XII. Admin processes | Partial | ✅ Explicit admin CLI commands for schema check, diagnostics, and maintenance. |

**Result: 4/5 partial items resolved; 1 explicitly out of scope with rationale.**

---

## Technical Review

**Context:** Post-implementation review after all initial phases completed (61 commits, 149 files changed).

### First walkthrough

| Step | Signal |
|---|---|
| README → runs system in 3 commands | ✅ Positive |
| Opens `backend/app/` → hexagonal structure | ✅ Positive |
| Opens `docs/.../02-tech/adr/` → 8 well-structured ADRs | ✅ Positive |
| Runs tests → 680+ green, 87%+ backend coverage | ✅ Strong |
| Browses delivery summary → quantitative evidence | ✅ Strong |
| Uploads a PDF → processes, review works | ✅ Positive |

### Strengths Identified

- **Architecture clarity**: Hexagonal boundaries visible immediately — `domain/`, `ports/`, `infra/`, composition root in `main.py`.
- **Docker quickstart**: 3 commands to running system with healthchecks and test profiles.
- **Documentation quality**: Reading order, 8 ADRs with code evidence, audit trail.
- **Refactor execution**: 3 monolithic files decomposed with zero behavioral changes — before/after evidence in delivery summary.
- **CI discipline**: 10 CI jobs covering lint, format, type-check, tests, coverage, Docker packaging.
- **Incremental delivery evidence**: 61+ commits, phase-by-phase execution log.
- **Tooling completeness**: ESLint 9 + Prettier + ruff + pre-commit + coverage reporting.

### Residual Gaps and Planned Improvements

| Gap | Status | Plan |
|---|---|---|
| `AppWorkspace.tsx` exceeds 500-LOC cap | Acknowledged | Planned decomposition into ReviewWorkspace, StructuredDataView, PdfViewerContainer — documented in future-improvements.md. Deprioritized vs. 3 critical monolith decompositions already completed. |
| Frontend coverage gaps (SourcePanel 0%, AddFieldDialog 30%) | Partial | Incremental coverage expansion tracked in delivery backlog. |
| `extraction_observability.py` modularity | ✅ Resolved | Split into focused sub-modules. |

---

## Audit Process

For the methodology used to trigger and execute these audits, see [Architecture Audit Process](architecture-audit-process).
