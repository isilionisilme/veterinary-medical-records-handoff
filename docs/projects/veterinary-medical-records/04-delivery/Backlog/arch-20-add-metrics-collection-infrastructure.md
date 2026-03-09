# ARCH-20 — Add Metrics Collection Infrastructure

**Status:** Planned

**Type:** Architecture Improvement (observability)

**Target release:** Release 21 — Architecture polish & operational maturity

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 2 (O-2)

**Severity:** MEDIUM  
**Effort:** M (4-8h)

**Problem Statement**
No runtime metrics collection exists beyond health endpoints.

**Action**
Add basic metrics: request latency histogram, processing duration, document count. Consider Prometheus or OpenTelemetry.

**Acceptance Criteria**
- At least 3 core metrics are collected (latency, processing time, document count)
- Metrics endpoint or export mechanism exists
- No performance regression on hot paths

**Dependencies**
- None.
