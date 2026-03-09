# Improvement Backlog — Architecture Review 2026-03-09

> Prioritized action items from the [architecture review](architecture-review-2026-03-09.md). Each item includes source phase, severity, effort estimate, and acceptance criteria.

**Generated:** 2026-03-09
**Baseline audit:** 2026-02-23
**Total items:** 24
**Distribution:** 5 Immediate, 10 Short-term, 9 Strategic

---

## Priority Levels

| Priority | Definition | Timeline |
|----------|-----------|----------|
| **IMMEDIATE** | Causes active regression or blocks quality; do now | Next sprint |
| **SHORT-TERM** | Significant gap but not actively degrading; plan soon | 2-3 sprints |
| **STRATEGIC** | Improves long-term health; schedule when capacity allows | Quarter |

---

## Immediate (5 items)

### ARCH-01: Decompose `review_service.py`

| Field | Value |
|-------|-------|
| Source | Phase 2 (P-1), Phase 3 (§3.1) |
| Severity | CRITICAL |
| Effort | L (8-16h) |
| Category | Code Principles / Code Quality |

**Problem:** 1,532 LOC, 9 distinct responsibilities, max CC 99, 15 commits since Feb. God Module pattern.

**Action:** Extract into 4+ focused modules:
1. `VisitAssignmentEngine` — visit scoping, segment extraction, clause parsing
2. `SegmentParser` + `ClauseClassifier` — replace CC-99 function with strategy-based classification
3. `AgeNormalizer` — consolidate 5 age-related functions
4. `ReviewPayloadProjector` — decouple review shape from canonical form

**Acceptance criteria:**
- No file > 400 LOC
- No function CC > 20
- All existing tests pass without modification (refactor, not rewrite)
- Public API (`review_document`, `get_canonical_review`) unchanged

---

### ARCH-02: Decompose `candidate_mining.py`

| Field | Value |
|-------|-------|
| Source | Phase 2 (P-2), Phase 3 (§3.2) |
| Severity | CRITICAL |
| Effort | L (8-16h) |
| Category | Code Principles / Code Quality |

**Problem:** 1,013 LOC, 767-LOC single function (`_mine_interpretation_candidates`), CC 163 (highest in codebase), inner closure with 25+ field-specific validation blocks.

**Action:**
1. Split into per-entity-type `FieldCandidateExtractor` strategies (labeled, heuristic, microchip, address, date)
2. Extract `CandidateValidator` with per-field validation rules
3. Move 40+ compiled regex patterns into `FieldPattern` registry
4. Replace multi-pass line iteration with single `MedicalDocumentParser`

**Acceptance criteria:**
- No function > 100 LOC
- No function CC > 20
- All existing tests pass
- `mine_candidates()` public API unchanged

---

### ARCH-03: Add CI complexity gates

| Field | Value |
|-------|-------|
| Source | Phase 3 (§6), Phase 2 (Q-2) |
| Severity | HIGH |
| Effort | S (2-4h) |
| Category | Build & CI |

**Problem:** Re-accretion pattern — decomposed files grow back into hotspots without automated guardrails.

**Action:**
1. Add `radon cc --min C` check to CI (warn on CC 11-20)
2. Add `radon cc --min E` check to CI (fail on CC > 30)
3. Add LOC gate: fail if any Python file exceeds 500 LOC
4. Document thresholds in an ADR

**Acceptance criteria:**
- CI fails on new functions with CC > 30
- CI warns on new functions with CC > 10
- CI fails on new files > 500 LOC
- Gate runs in < 30s

---

### ARCH-04: Fix infra→application dependency violation

| Field | Value |
|-------|-------|
| Source | Phase 3 (§1.3 Violation 3) |
| Severity | MEDIUM |
| Effort | S (1-2h) |
| Category | Architecture |

**Problem:** `infra/scheduler_lifecycle.py` imports directly from `application/processing`, inverting the hexagonal dependency direction.

**Action:**
1. Create `ports/scheduler_port.py` with `SchedulerPort` ABC
2. Application layer implements the port
3. `scheduler_lifecycle.py` depends on `SchedulerPort` (not application directly)
4. Wire in `main.py` composition root

**Acceptance criteria:**
- `grep -r "from backend.app.application" backend/app/infra/` returns 0 results
- All existing tests pass
- Scheduler behavior unchanged

---

### ARCH-05: Add structured logging to critical paths

| Field | Value |
|-------|-------|
| Source | Phase 2 (O-1) |
| Severity | MEDIUM |
| Effort | S (2-4h) |
| Category | Observability |

**Problem:** 22 log statements across 317 functions (7% coverage). `review_service.py` and `candidate_mining.py` have zero logging.

**Action:**
1. Add entry/exit logging to `review_document()`, `get_canonical_review()`
2. Add extraction-start/extraction-complete logging to `mine_candidates()`
3. Add error logging with context for all exception handlers in hotspot files
4. Follow existing `logging.getLogger(__name__)` pattern

**Acceptance criteria:**
- Every public function in hotspot files has at least entry-level logging
- Error handlers include contextual information (document_id, run_id)
- Log format consistent with existing codebase pattern

---

## Short-term (10 items)

### ARCH-06: Create security architecture documentation

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-001, GAP-003, GAP-005) |
| Severity | CRITICAL |
| Effort | M (4-8h) |
| Category | Documentation |

**Action:** Create `02-tech/security-architecture.md` covering:
- Authentication strategy (current state + production target)
- Threat model (STRIDE for PDF upload, API endpoints, stored data)
- Encryption strategy (TLS termination, data-at-rest for PII in SQLite)
- Rate limiting policy (current + planned)
- Upload validation strategy

---

### ARCH-07: Create production deployment documentation

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-002) |
| Severity | CRITICAL |
| Effort | M (4-8h) |
| Category | Documentation |

**Action:** Create deployment section or standalone doc covering:
- Production topology (single-server, cloud, or hybrid)
- Scaling strategy (acknowledged single-process limit from ADR-0001)
- Backup and disaster recovery for SQLite + filesystem
- Environment configuration reference

---

### ARCH-08: Expose `_shared` functions publicly

| Field | Value |
|-------|-------|
| Source | Phase 3 (encapsulation warning), Phase 2 (P-3) |
| Severity | MEDIUM |
| Effort | XS (30min) |
| Category | Code Principles |

**Action:** Re-export `_locate_visit_date_occurrences_from_raw_text` through `application/documents/__init__.py`. Update import in `api/routes_review.py`.

**Acceptance criteria:**
- No imports from `_shared` or `_`-prefixed modules in api/ layer
- All tests pass

---

### ARCH-09: Add ER diagram to technical-design.md

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-006) |
| Severity | HIGH |
| Effort | S (1-2h) |
| Category | Documentation |

**Action:** Add Mermaid ER diagram showing: Document, ProcessingRun, Artifacts, InterpretationVersion, FieldChangeLog. Include relationship cardinality and foreign keys.

---

### ARCH-10: Write missing ADRs

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-008) |
| Severity | HIGH |
| Effort | M (2-4h per ADR) |
| Category | Documentation |

**Action:** Create ADRs for at least:
- ADR-ARCH-0005: Frontend stack (React + TanStack Query + Vite)
- ADR-ARCH-0006: Confidence scoring algorithm design

---

### ARCH-11: Add monitoring/alerting strategy documentation

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-004) |
| Severity | HIGH |
| Effort | S (2-4h) |
| Category | Documentation |

**Action:** Document: what to monitor, SLO definitions (availability, error rate, processing latency), alerting rules, dashboard requirements.

---

### ARCH-12: Add capacity planning documentation

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-007) |
| Severity | HIGH |
| Effort | S (2-4h) |
| Category | Documentation |

**Action:** Document expected data volumes, storage growth projections, SQLite row limits, concurrent processing limits, maximum document count.

---

### ARCH-13: Implement production authentication

| Field | Value |
|-------|-------|
| Source | Phase 2 (S-1) |
| Severity | HIGH |
| Effort | L (8-16h) |
| Category | Security |

**Action:** Implement proper auth (OAuth2/JWT) for production. Current optional bearer token is insufficient.

**Prerequisite:** ARCH-06 (security architecture doc) should define the strategy first.

---

### ARCH-14: Add content validation for PDF uploads

| Field | Value |
|-------|-------|
| Source | Phase 2 (S-3) |
| Severity | MEDIUM |
| Effort | S (2-4h) |
| Category | Security |

**Action:** Add content-type validation (magic bytes check). Consider ClamAV integration for production deployments.

---

### ARCH-15: Explicitly declare pydantic in requirements.txt

| Field | Value |
|-------|-------|
| Source | Phase 2 (D-1) |
| Severity | LOW |
| Effort | XS (5min) |
| Category | Dependencies |

**Action:** Add `pydantic` with pinned version to requirements.txt.

---

## Strategic (9 items)

### ARCH-16: Create re-accretion prevention ADR

| Field | Value |
|-------|-------|
| Source | Phase 3 (§5.3) |
| Severity | HIGH |
| Effort | S (1-2h) |
| Category | Architecture |

**Action:** Document architectural decision: maximum file LOC (500), maximum function CC (20), enforcement via CI gates (ARCH-03). Record rationale based on observed regression pattern.

---

### ARCH-17: Simplify extraction_observability/ subsystem

| Field | Value |
|-------|-------|
| Source | Phase 2 (P-4) |
| Severity | MEDIUM |
| Effort | M (4-8h) |
| Category | Code Quality |

**Action:** Review `triage.py` (CC 64) — `_suspicious_accepted_flags` may be over-engineered. Consider simplifying classification logic or extracting into data-driven rules.

---

### ARCH-18: Extract frontend state management layer

| Field | Value |
|-------|-------|
| Source | Phase 3 (§3.4) |
| Severity | MEDIUM |
| Effort | M (4-8h) |
| Category | Frontend Architecture |

**Action:** Extract AppWorkspace's 15 useState hooks into React Context + useReducer pattern to reduce state hub concentration.

---

### ARCH-19: Create operational runbooks

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-011) |
| Severity | MEDIUM |
| Effort | M (4-8h) |
| Category | Documentation |

**Action:** Create `03-ops/runbook.md` covering: backup procedures, database maintenance, log rotation, common failure modes, recovery steps.

---

### ARCH-20: Add metrics collection infrastructure

| Field | Value |
|-------|-------|
| Source | Phase 2 (O-2) |
| Severity | MEDIUM |
| Effort | M (4-8h) |
| Category | Observability |

**Action:** Add basic metrics: request latency histogram, processing duration, document count. Consider Prometheus or OpenTelemetry.

---

### ARCH-21: Add rate limiting to write endpoints

| Field | Value |
|-------|-------|
| Source | Phase 2 (S-4) |
| Severity | LOW |
| Effort | S (1-2h) |
| Category | Security |

**Action:** Add rate limits to review, reprocess, and edit endpoints. Follow existing `slowapi` pattern.

---

### ARCH-22: Parameterize PRAGMA table_info call

| Field | Value |
|-------|-------|
| Source | Phase 2 (S-2) |
| Severity | LOW (MEDIUM pattern risk) |
| Effort | XS (30min) |
| Category | Security |

**Action:** Replace `f"PRAGMA table_info({table})"` with assertion that table is in known set, or use allowlisted table names.

---

### ARCH-23: Add configuration reference documentation

| Field | Value |
|-------|-------|
| Source | Phase 1 (GAP-014) |
| Severity | MEDIUM |
| Effort | S (1-2h) |
| Category | Documentation |

**Action:** Add comprehensive configuration reference table to backend-implementation.md covering all env vars and settings.

---

### ARCH-24: Replace wildcard re-export with explicit imports

| Field | Value |
|-------|-------|
| Source | Phase 2 (DC-1) |
| Severity | LOW |
| Effort | XS (30min) |
| Category | Code Quality |

**Action:** Replace `from backend.app.application.documents import *` in `document_service.py` with explicit named imports.

---

## Summary by Category

| Category | Items | Immediate | Short-term | Strategic |
|----------|-------|-----------|------------|-----------|
| Code Principles / Quality | 6 | 2 | 1 | 3 |
| Documentation | 7 | 0 | 5 | 2 |
| Security | 4 | 0 | 2 | 2 |
| Architecture | 2 | 1 | 0 | 1 |
| Build & CI | 1 | 1 | 0 | 0 |
| Observability | 2 | 1 | 0 | 1 |
| Dependencies | 1 | 0 | 1 | 0 |
| Frontend | 1 | 0 | 0 | 1 |
| **Total** | **24** | **5** | **10** | **9** |

## Effort Distribution

| Effort | Count | Description |
|--------|-------|-------------|
| XS (< 1h) | 4 | Quick fixes |
| S (1-4h) | 9 | Half-day tasks |
| M (4-8h) | 7 | Full-day tasks |
| L (8-16h) | 4 | Multi-day tasks |

