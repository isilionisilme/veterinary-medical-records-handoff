# ARCH-04 — Fix infra→application Dependency Violation

**Status:** Planned

**Type:** Architecture Improvement (hexagonal architecture)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 3 (§1.3 Violation 3)

**Severity:** MEDIUM  
**Effort:** S (1-2h)

**Problem Statement**
`infra/scheduler_lifecycle.py` imports directly from `application/processing`, inverting the hexagonal dependency direction.

**Action**
1. Create `ports/scheduler_port.py` with `SchedulerPort` ABC
2. Application layer implements the port
3. `scheduler_lifecycle.py` depends on `SchedulerPort` (not application directly)
4. Wire in `main.py` composition root

**Acceptance Criteria**
- `grep -r "from backend.app.application" backend/app/infra/` returns 0 results
- All existing tests pass
- Scheduler behavior unchanged

**Dependencies**
- None.
