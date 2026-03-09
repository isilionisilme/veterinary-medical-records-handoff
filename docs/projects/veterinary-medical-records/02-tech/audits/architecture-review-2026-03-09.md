# Architecture Review — 2026-03-09

> **Comprehensive architecture evaluation of the veterinary-medical-records codebase.** Covers documentation completeness, code health across 9 categories, coupling analysis, and hotspot detection. Includes methodology for reproducibility and comparison with Feb 23, 2026 baseline.

**Status:** Final  
**Date:** 2026-03-09  
**Scope:** Full re-audit (not delta)  
**Depth:** Exhaustive  
**Stack:** FastAPI 0.115.14 (Python 3.11.9), React 18.3 + TypeScript 5.5, SQLite WAL, Docker Compose  
**Architecture:** Modular monolith, hexagonal/ports-and-adapters  
**Baseline:** [codebase-audit.md](../../99-archive/codebase-audit.md) (2026-02-23)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Overall Health Dashboard](#2-overall-health-dashboard)
3. [Architecture Documentation Audit](#3-architecture-documentation-audit)
4. [Codebase Audit (9 Categories)](#4-codebase-audit-9-categories)
5. [Coupling & Hotspot Analysis](#5-coupling--hotspot-analysis)
6. [Evolution Since Feb 2026](#6-evolution-since-feb-2026)
7. [Risk Matrix](#7-risk-matrix)
8. [Recommendations](#8-recommendations)
9. [Methodology](#9-methodology)

---

## 1. Executive Summary

The veterinary-medical-records system has **strong architectural foundations** — clean hexagonal layers, robust lifecycle management, minimal dependencies, and zero dead code. The Feb 2026 audit's 15 findings drove meaningful improvements: 7 of 9 code health categories improved, and the 3 monolithic hotspots were successfully decomposed.

However, **two critical concerns** have emerged:

1. **Re-accretion pattern:** Two files born from the Feb decomposition have grown into new hotspots — `review_service.py` (1532 LOC, 9 responsibilities, CC 99) and `candidate_mining.py` (1013 LOC, CC 163). Without complexity guardrails (CI gates, LOC budgets), decomposition alone doesn't prevent future accumulation.

2. **Documentation gaps in security and deployment:** The architecture documentation scores 34/100 — not because the *existing* documentation is poor (V6 Integration 85/100, V10 Decisions 82/100), but because *entire viewpoints* are missing. There is no security architecture section (V7: 28/100) and no production deployment documentation (V4: 42/100).

### Key Numbers

| Dimension | Score | Status |
|-----------|-------|--------|
| Documentation Health | 34/100 | CRITICAL — missing viewpoints |
| Code Health (avg 9 categories) | 8.4/10 | GOOD — 7 categories ≥ 9.0 |
| Hexagonal Compliance | 96% clean | 3 violations (1 MEDIUM, 2 LOW) |
| Critical Hotspots | 2 files | review_service.py, candidate_mining.py |
| Max Cyclomatic Complexity | 163 | candidate_mining.py (grade F) |
| Backend Test Coverage | ≥91% | HEALTHY |
| Frontend Test Coverage | ≥87% | HEALTHY |

---

## 2. Overall Health Dashboard

### 2.1 Code Health by Category

| Category | Score | Feb 23 | Delta | Key Finding |
|----------|-------|--------|-------|-------------|
| Security | 7.8/10 | 7.2 | +0.6 ↑ | Rate limiting added; auth still optional |
| Build & CI | 9.8/10 | 8.4 | +1.4 ↑ | 10 CI jobs, 0 lint errors |
| Code Principles | 5.0/10 | 7.8 | −2.8 ↓ | 2 new God Modules emerged |
| Code Quality | 5.0/10 | 5.8 | −0.8 ↓ | CC 163 max; 54 functions above threshold |
| Dependencies | 9.8/10 | 6.7 | +3.1 ↑ | Minimal surface, all pinned |
| Dead Code | 9.8/10 | 6.2 | +3.6 ↑ | Zero TODOs, zero commented code |
| Observability | 9.0/10 | 7.4 | +1.6 ↑ | 17 loggers; no metrics/tracing |
| Concurrency | 9.5/10 | 6.4 | +3.1 ↑ | WAL + busy_timeout; proper async |
| Lifecycle | 10/10 | 8.1 | +1.9 ↑ | Lifespan + crash recovery + graceful shutdown |
| **Average** | **8.4** | **7.1** | **+1.3** | **7 of 9 improved** |

### 2.2 Documentation Health by Viewpoint

| Viewpoint | Score | Status |
|-----------|-------|--------|
| V7: Security Architecture | 28/100 | CRITICAL |
| V4: Deployment Topology | 42/100 | AT RISK |
| V8: Operational Concerns | 48/100 | AT RISK |
| V12: Event Architecture | 55/100 | AT RISK |
| V9: Cross-Cutting Concerns | 68/100 | ADEQUATE |
| V5: Data Architecture | 70/100 | ADEQUATE |
| V1: Context & Scope | 72/100 | ADEQUATE |
| V3: Component Design | 74/100 | ADEQUATE |
| V2: Container Architecture | 80/100 | HEALTHY |
| V10: Decision Record | 82/100 | HEALTHY |
| V6: Integration & APIs | 85/100 | HEALTHY |

### 2.3 Severity Summary (All Phases)

| Severity | Doc Gaps | Code Findings | Coupling | Total |
|----------|----------|---------------|----------|-------|
| CRITICAL | 2 | 3 | 0 | **5** |
| HIGH | 6 | 4 | 0 | **10** |
| MEDIUM | 7 | 7 | 2 | **16** |
| LOW | 2 | 4 | 2 | **8** |
| **Total** | **17** | **18** | **4** | **39** |

---

## 3. Architecture Documentation Audit

*Full details: `tmp/audit/phase1-doc-audit.md`*

### 3.1 Scope

9 documents audited (~3,800 lines): architecture.md, technical-design.md, backend-implementation.md, frontend-implementation.md, extraction-quality.md, and 4 ADRs. Evaluated against 188-item checklist across 14 viewpoints.

### 3.2 Health Score: 34/100 (CRITICAL)

The low score reflects **documentation completeness**, not documentation quality. What exists is well-organized and accurate. The score is driven by:
- **V7 Security (28/100):** No security architecture section. Auth is mentioned as "optional bearer-token" scattered across 3 documents. No threat model, no encryption strategy, no RBAC design.
- **V4 Deployment (42/100):** Only Docker Compose dev configuration documented. No production deployment strategy, scaling plan, or disaster recovery.

### 3.3 Key Gaps (17 total)

| Priority | Gap | Viewpoint | Effort |
|----------|-----|-----------|--------|
| CRITICAL | No security architecture section | V7 | 4-8h |
| CRITICAL | No production deployment docs | V4 | 4-8h |
| HIGH | No threat model (STRIDE) | V7 | 4-8h |
| HIGH | No monitoring/alerting strategy | V8 | 2-4h |
| HIGH | No encryption documentation | V7 | 1-2h |
| HIGH | No ER diagram | V5 | 1-2h |
| HIGH | No capacity planning | V4/V8 | 2-4h |
| HIGH | Incomplete ADR coverage (5+ missing) | V10 | 2-4h/ADR |

### 3.4 Anti-Patterns Detected (6)

| ID | Pattern | Severity |
|----|---------|----------|
| AA-12 | View Vacuum (missing security viewpoint) | CRITICAL |
| AA-17 | Observability Omission (no monitoring strategy) | HIGH |
| AA-18 | SLO Silence (no formal SLO definitions) | HIGH |
| AA-20 | Capacity Blindness (no capacity planning) | HIGH |
| AA-14 | Prose Overload (2047-line spec, minimal diagrams) | MEDIUM |
| AA-10 | ADR Amnesia (5+ undocumented decisions) | MEDIUM |

### 3.5 Strengths

- **V6 Integration (85/100):** API contracts are detailed with endpoint specs, request/response formats, error codes, and conflict semantics.
- **V10 Decisions (82/100):** MADR-format ADRs cover the foundational architecture decisions with clear rationale and consequences.
- **V2 Container (80/100):** Mermaid system diagram matches actual architecture. Layer responsibilities well-described.

---

## 4. Codebase Audit (9 Categories)

*Full details: `tmp/audit/phase2-codebase-audit.md`*

### 4.1 Security — 7.8/10

| # | Sev | Finding |
|---|-----|---------|
| S-1 | HIGH | No production auth strategy. Optional bearer token; unauthenticated when `AUTH_TOKEN` unset. |
| S-2 | MED | f-string in `PRAGMA table_info({table})` — low risk (internal callers only) but bad pattern. |
| S-3 | MED | PDF upload: no content scanning beyond size limit (20MB). |
| S-4 | LOW | Rate limiting only on upload/download; review/reprocess have none. |

**Strengths:** All secrets via env vars. UUID validation on all document params. No hardcoded credentials.

### 4.2 Build & CI — 9.8/10

| # | Sev | Finding |
|---|-----|---------|
| B-1 | LOW | 2 NOQA suppressions (both justified, lack explanatory comments). |

**Strengths:** ~395 backend tests (≥91%), ~287 frontend tests (≥87%), 64 E2E specs, 10 CI jobs, 0 lint errors.

### 4.3 Code Principles — 5.0/10

| # | Sev | Finding |
|---|-----|---------|
| P-1 | CRIT | `review_service.py`: 1532 LOC, 9 responsibilities — God Module. |
| P-2 | CRIT | `candidate_mining.py`: 767-LOC single function, inner closure with 25+ conditional blocks. |
| P-3 | MED | `_shared` module imported from API layer — private encapsulation violation. |
| P-4 | MED | `extraction_observability/` — 962 LOC across 4 files, CC up to 64. Complexity rivals features it observes. |

### 4.4 Code Quality — 5.0/10

| # | Sev | Finding |
|---|-----|---------|
| Q-1 | CRIT | 2 functions exceed CC 100: `_mine_interpretation_candidates` (163), `_normalize_canonical_review_scoping` (99). |
| Q-2 | HIGH | Average CC across 54 analyzed blocks is D (25.07). Industry targets CC < 10. |
| Q-3 | HIGH | 5 functions with CC 40-64 (triage, reporting, snapshot, review, candidate modules). |
| Q-4 | HIGH | 2 functions exceed 300 LOC in a single body. |

**Complexity grade distribution:** 82% of all 317 functions are A/B grade (CC ≤ 10). The problem is concentrated in 7 F-grade and 5 E-grade functions.

### 4.5 Dependencies — 9.8/10

| # | Sev | Finding |
|---|-----|---------|
| D-1 | LOW | `pydantic` imported but not in requirements.txt (transitive via FastAPI). |

**Strengths:** Minimal surface (7 backend, 14 frontend). All pinned. No unused deps. All imports verified against declarations.

### 4.6 Dead Code — 9.8/10

| # | Sev | Finding |
|---|-----|---------|
| DC-1 | LOW | Wildcard re-export in `document_service.py` obscures what's actually exported. |

**Strengths:** Zero TODOs/FIXMEs. Zero commented-out code. Clean import hygiene.

### 4.7 Observability — 9.0/10

| # | Sev | Finding |
|---|-----|---------|
| O-1 | MED | 22 log statements across 317 functions (7% coverage). Critical paths have zero logging. |
| O-2 | MED | No metrics collection (Prometheus/StatsD/OpenTelemetry). |

**Strengths:** 17 loggers via `getLogger(__name__)`. Extraction observability excellent (20-run ring buffer). Health endpoint. Event taxonomy.

### 4.8 Concurrency — 9.5/10

| # | Sev | Finding |
|---|-----|---------|
| C-1 | MED | Per-request DB connections (no pooling). Fine now; potential bottleneck at scale. |

**Strengths:** WAL + busy_timeout=5000ms. asyncio.Event for coordination. Task lifecycle management. Thread offloading for CPU. No global mutable state.

### 4.9 Lifecycle — 10/10

No findings. Proper lifespan handler with schema init, crash recovery (orphaned runs), scheduler start/stop.

---

## 5. Coupling & Hotspot Analysis

*Full details: `tmp/audit/phase3-coupling-hotspots.md`*

### 5.1 Hexagonal Compliance

| Layer | Status | Violations |
|-------|--------|------------|
| domain/ | ✅ CLEAN | Zero outbound cross-layer imports |
| ports/ | ✅ CLEAN | Zero outbound cross-layer imports |
| application/ | ✅ CLEAN | Imports only from domain/, ports/, config (all allowed) |
| api/ | ⚠️ 2 violations | api→infra rate_limiter (LOW), api→infra database (LOW) |
| infra/ | ⚠️ 1 violation | infra→application scheduler (MEDIUM — inverts dependency) |

**Verdict:** Core layers (domain, ports, application) are clean. The 3 violations are pragmatic exceptions, not structural rot. The most architecturally significant is `infra/scheduler_lifecycle.py → application/processing` which inverts the dependency direction and should be fixed with a `SchedulerPort` interface.

### 5.2 Critical Hotspots

#### `review_service.py` — 🔴 CRITICAL (New since Feb audit)

| Metric | Value |
|--------|-------|
| LOC | 1,532 |
| Max CC | 99 (F) |
| Commits (since Feb) | 15 |
| Responsibilities | 9 |

Born from `document_service.py` decomposition. Accumulated review lifecycle, interpretation normalization, microchip sync, age derivation, visit scoping, text segment extraction, clause normalization, medical record projection, and weight aggregation — all in one file.

**Decomposition strategy:** VisitAssignmentEngine + SegmentParser/ClauseClassifier + AgeNormalizer + ReviewPayloadProjector → 4 files, each < 400 LOC.

#### `candidate_mining.py` — 🔴 CRITICAL

| Metric | Value |
|--------|-------|
| LOC | 1,013 |
| Max CC | 163 (F — highest in codebase) |
| Commits (since Feb) | 10 |
| Largest function | 767 LOC (single function) |

Contains `_mine_interpretation_candidates()` — a 767-LOC function with CC 163 that embeds 25+ field-specific extraction branches via an inner closure.

**Decomposition strategy:** Per-entity-type FieldCandidateExtractor strategy pattern + CandidateValidator + regex FieldPattern registry → ~5 files.

### 5.3 High Hotspots

| File | LOC | Max CC | Key Issue |
|------|-----|--------|-----------|
| pdf_extraction_nodeps.py | 878 | 28 (D) | PDF complexity is partially inherent; state machine pattern could help |
| routes_review.py | 522 | 32 (E) | Complex route handlers; could extract validation logic |
| field_normalizers.py | 468 | 16 (C) | High churn (9 commits); normalizer rules may benefit from data-driven approach |
| AppWorkspace.tsx | 790 | N/A | 15 useState hooks; state hub pattern (down from 5760 LOC in Feb) |

### 5.4 Regression Pattern

The Feb audit found 3 monoliths that were decomposed. But **2 of the successor files have already re-accreted into hotspots**. This pattern suggests:

> **Decomposition without guardrails leads to re-accretion.** LOC budgets, CC gates in CI, and architectural fitness functions are needed to sustain the improvement.

---

## 6. Evolution Since Feb 2026

### 6.1 What Improved (7 categories)

| Area | Feb → Mar | Evidence |
|------|-----------|----------|
| Dead Code | 62 → 98 | Zero TODOs, zero commented code, zero test duplication |
| Dependencies | 67 → 98 | All pinned, minimal surface, no unused imports |
| Concurrency | 64 → 95 | WAL + busy_timeout, proper async patterns, task lifecycle |
| Lifecycle | 81 → 100 | Lifespan handler, crash recovery, graceful shutdown |
| Observability | 74 → 90 | Structured logging, event taxonomy, extraction observability |
| Build & CI | 84 → 98 | 10 CI jobs, clean linting, comprehensive test suites |
| Security | 72 → 78 | Rate limiting added, upload size checks, secrets in env vars |

### 6.2 What Regressed (2 categories)

| Area | Feb → Mar | Root Cause |
|------|-----------|------------|
| Code Principles | 78 → 50 | Post-decomposition re-accretion in review_service.py and candidate_mining.py |
| Code Quality | 58 → 50 | CC 163 and CC 99 functions; 54 functions above CC 10 threshold |

### 6.3 Feb Decomposition Results

| Feb Target | Action Taken | Current State |
|------------|-------------|---------------|
| App.tsx (5760 LOC) | ✅ Decomposed | AppWorkspace.tsx at 790 LOC (−86%) |
| processing_runner.py | ✅ Decomposed | Split into orchestrator, scheduler, candidate_mining |
| document_service.py | ✅ Decomposed | Split into review_service, edit_service, query_service, upload_service |

**Net assessment:** Decomposition worked but successor files need a second round of refactoring (review_service.py, candidate_mining.py).

---

## 7. Risk Matrix

| Risk | Likelihood | Impact | Mitigation | Priority |
|------|-----------|--------|------------|----------|
| Re-accretion continues without CI gates | HIGH | HIGH | Add radon CC + LOC CI checks | IMMEDIATE |
| Security incident without auth/encryption | MEDIUM | CRITICAL | Create security architecture; implement auth before production | HIGH |
| Untestable functions (CC > 100) grow | HIGH | MEDIUM | Decompose 2 critical hotspots | IMMEDIATE |
| Production deploy without runbooks | LOW | HIGH | Write deployment + operational docs | MEDIUM |
| State management debt in frontend | MEDIUM | LOW | Extract context/reducer in AppWorkspace | LOW |

---

## 8. Recommendations

### 8.1 Immediate (next sprint)

1. **Decompose `review_service.py`** → 4 modules, each < 400 LOC, no function CC > 20
2. **Decompose `candidate_mining.py`** → strategy pattern per entity type, no function > 100 LOC
3. **Add CI complexity gates** → `radon cc --min C` warns; `radon cc --min E` fails; `wc -l` gate at 500 LOC

### 8.2 Short-term (next 2-3 sprints)

4. **Create security-architecture.md** — auth strategy, threat model (STRIDE), encryption, rate limiting policy
5. **Create deployment documentation** — production topology, scaling, disaster recovery, backup strategy
6. **Fix infra→application violation** — extract `SchedulerPort` interface; inject via DI
7. **Expose `_shared` functions** — re-export through `application.documents.__init__`
8. **Add structured logging** to review and extraction critical paths (currently 0 log statements)
9. **Add ER diagram** — Mermaid diagram in technical-design.md for 5 core entities
10. **Write missing ADRs** — frontend stack, confidence scoring algorithm (minimum)

### 8.3 Strategic

11. **Prevent re-accretion ADR** — document LOC/CC budgets as architectural decision with CI enforcement
12. **Simplify `extraction_observability/`** — triage.py (CC 64) may be over-engineered
13. **Frontend state management** — extract React Context + useReducer from AppWorkspace
14. **Operational runbooks** — backup, database maintenance, log rotation, failure modes
15. **Metrics collection** — Prometheus/OpenTelemetry for production observability

---

## 9. Methodology

### 9.1 Process

This audit followed a 4-phase process designed for reproducibility:

| Phase | Goal | Tool/Skill | Output |
|-------|------|-----------|--------|
| 1 | Documentation completeness | `architecture-doc-auditor` (188-item, 14 viewpoints) | Document health score + gap inventory |
| 2 | Code health (9 categories) | `ln-620-codebase-auditor` (9 workers, adapted) | Per-category scores + finding inventory |
| 3 | Coupling & hotspots | Manual analysis (imports, radon, git log, LOC) | Hex compliance + hotspot table |
| 4 | Synthesis | Cross-phase synthesis | This report + improvement backlog |

### 9.2 Scoring

**Documentation (Phase 1):** Viewpoint scores (0-100) based on 188-item checklist. Overall score = weighted average − severity penalties (capped at -30).

**Code Health (Phase 2):** Per-category scoring formula: `penalty = (C×2.0) + (H×1.0) + (M×0.5) + (L×0.2); score = max(0, 10 - penalty)`. Normalized to 0-100 for comparison with Feb baseline.

**Hotspots (Phase 3):** 4-signal scoring (LOC > 500, CC > 10, imports > 8, churn > 8 commits). Files flagged as hotspot when ≥ 2 signals triggered.

### 9.3 Tools Used

| Tool | Purpose |
|------|---------|
| `radon cc` | Cyclomatic complexity analysis (Python) |
| `Select-String` / `Get-ChildItem` | Pattern scanning (secrets, SQL, TODOs, imports) |
| `git log --oneline --since` | Churn analysis (commit frequency) |
| `wc -l` / `Measure-Object` | Lines of code measurement |
| Python import parsing | Cross-layer dependency mapping |
| `get_errors()` | Compile/lint error verification |

### 9.4 Reproducing This Audit

To reproduce or update this audit:

1. **Phase 1:** Read all 9 docs in `02-tech/` + `02-tech/adr/`. Apply `architecture-doc-auditor` skill with parameters: `audit_depth=exhaustive, include_debt_assessment=true, include_anti_patterns=true`.

2. **Phase 2:** Run security scan (secrets + SQL patterns), TODO scan, dependency verification, import mapping, concurrency pattern check, logging count, lifecycle review. Score each of 9 categories using the penalty formula.

3. **Phase 3:** Extract all Python imports, map to hexagonal layers, verify allowed directions. Run `radon cc -s -n C backend/app/` for complexity. Run `git log --oneline --since=<baseline_date>` for churn. Score files against 4-signal hotspot criteria.

4. **Phase 4:** Synthesize phases 1-3 into this report format. Compare with previous baseline.

### 9.5 Companion Documents

| Document | Content |
|----------|---------|
| [improvement-backlog-2026-03-09.md](improvement-backlog-2026-03-09.md) | Prioritized action items with effort estimates |
| `tmp/audit/phase1-doc-audit.md` | Full Phase 1 raw output |
| `tmp/audit/phase2-codebase-audit.md` | Full Phase 2 raw output |
| `tmp/audit/phase3-coupling-hotspots.md` | Full Phase 3 raw output |
