# Track Plan T3 (AUDIT-01-T3): Backend Lifecycle & Graceful Shutdown

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.
>
> **Master plan:** [AUDIT-01 Master](PLAN_2026-03-12_AUDIT-01-CODEBASE-QUALITY-MASTER.md)

**Branch:** improvement/audit-01-t3-backend-lifecycle
**Worktree:** D:/Git/worktrees/codex-permanent-1
**Execution Mode:** Autonomous
**Model Assignment:** GPT-5.4
**PR:** Pending (PR created on explicit user request)
**Related item ID:** `AUDIT-01-T3`
**Prerequisite:** None (independent track)

**Implementation Report:** [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T3-BACKEND-LIFECYCLE](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T3-BACKEND-LIFECYCLE.md)

---

## TL;DR

Fix two lifecycle issues: (1) `SchedulerLifecycle.stop()` awaits its task without a timeout, risking indefinite hang on SIGTERM; (2) add separated `/health/live` and `/health/ready` probes for container orchestration. Also add `--timeout-graceful-shutdown` to the Dockerfile CMD and `stop_grace_period` to docker-compose.

---

## Context

### Problem 1: Missing Shutdown Timeout (A3)

**File:** `backend/app/infra/scheduler_lifecycle.py`, lines 27–40
**Current code:**
```python
async def stop(self) -> None:
    if self._task is None or self._stop_event is None:
        self._task = None
        self._stop_event = None
        return
    self._stop_event.set()
    try:
        await self._task          # ← No timeout — can hang forever
    finally:
        self._task = None
        self._stop_event = None
```

If the scheduler task is stuck (e.g., waiting on an external call), `stop()` never returns. Docker sends SIGKILL after `stop_timeout` (default 10s), but uvicorn's lifespan handler has no timeout either, so the entire shutdown path hangs.

### Problem 2: No Liveness/Readiness Probe Split (B4)

**File:** `backend/app/api/routes_health.py` — single `/health` endpoint.

Container orchestrators (Docker Compose healthcheck, Kubernetes) benefit from separated probes:
- `/health/live` — process is alive (always 200 if the server can respond)
- `/health/ready` — dependencies are functional (DB + storage checks)

The current `/health` does dependency checks, which means during startup (before DB is ready) it returns 503, potentially causing premature container restart.

### Problem 3: Missing Docker Graceful Shutdown Config

**`Dockerfile.backend` CMD** (line 33):
```dockerfile
CMD ["python", "-m", "uvicorn", "backend.app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```
Missing: `--timeout-graceful-shutdown 30`

**`docker-compose.yml`** backend service: No `stop_grace_period` defined (Docker default: 10s, which is too short for graceful drain).

---

## Scope Boundary

- **In scope:** A3 (scheduler stop timeout), B4 (liveness/readiness probes), Docker graceful shutdown config
- **Out of scope:** Kubernetes manifests, health probe dashboards, metrics integration, startup dependency ordering changes

---

## Design Decisions

### DD-1: 15-second timeout for scheduler stop
**Rationale:** The scheduler runs periodic processing tasks. 15 seconds is enough for a processing cycle to notice the stop event and exit cleanly. Combined with uvicorn's 30s graceful shutdown and Docker's 45s grace period, this gives a layered timeout cascade: scheduler (15s) < uvicorn (30s) < Docker (45s).

### DD-2: Liveness as trivial 200, readiness with dependency checks
**Rationale:** Standard pattern per Kubernetes liveness/readiness probe documentation. Liveness should never include dependency checks to avoid restart cascades.

### DD-3: Keep existing `/health` as-is, add `/health/live` and `/health/ready`
**Rationale:** Backward compatibility. The existing `/health` endpoint is used in `docker-compose.yml` healthcheck. We add new endpoints without breaking existing monitoring.

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~80 | 400 | ✅ |
| Code files changed | 4 | 15 | ✅ |
| Scope classification | code + config | — | ✅ |
| Semantic risk | LOW (additive + timeout addition) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — Infrastructure hardening. No user-facing changes.

---

## Steps

### Phase 1 — A3: Scheduler Shutdown Timeout

**AGENTE: GPT-5.4**

#### Step 1: Add timeout to `stop()` method

In `backend/app/infra/scheduler_lifecycle.py`, replace:
```python
try:
    await self._task
```
With:
```python
try:
    await asyncio.wait_for(self._task, timeout=15.0)
except asyncio.TimeoutError:
    logger.warning("Scheduler task did not stop within 15s, cancelling")
    self._task.cancel()
    try:
        await self._task
    except asyncio.CancelledError:
        pass
```

Add `import asyncio` and `import logging` / `logger = logging.getLogger(__name__)` if not already present.

#### Step 2: Add unit test for shutdown timeout

**AGENTE: GPT-5.4**

Create a test that:
- Starts the scheduler with a mock task that never completes
- Calls `stop()` and verifies it returns within ~16 seconds
- Verifies the task was cancelled

### Phase 2 — B4: Liveness/Readiness Probes

**AGENTE: GPT-5.4**

#### Step 3: Add `/health/live` endpoint

In `backend/app/api/routes_health.py`, add:

```python
@router.get("/health/live", summary="Liveness probe")
def liveness() -> dict[str, str]:
    """Trivial liveness check — returns 200 if the process can serve requests."""
    return {"status": "alive"}
```

#### Step 4: Add `/health/ready` endpoint

**AGENTE: GPT-5.4**

Refactor existing health check logic into a readiness probe:

```python
@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Readiness probe",
    description="Check that all dependencies (database, storage) are functional.",
)
def readiness(response: Response) -> HealthResponse:
    """Readiness check — verifies database and storage are accessible."""
    # (Same logic as current /health endpoint)
    ...
```

The existing `/health` endpoint continues to work as-is for backward compatibility.

#### Step 5: Add tests for new endpoints

**AGENTE: GPT-5.4**

- Test `/health/live` returns 200 with `{"status": "alive"}`
- Test `/health/ready` returns 200 when deps are healthy
- Test `/health/ready` returns 503 when DB is unavailable

### Phase 3 — Docker Configuration

**AGENTE: GPT-5.4**

#### Step 6: Add `--timeout-graceful-shutdown` to Dockerfile

In `Dockerfile.backend`, update CMD:
```dockerfile
CMD ["python", "-m", "uvicorn", "backend.app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "30"]
```

#### Step 7: Add `stop_grace_period` to docker-compose

**AGENTE: GPT-5.4**

In `docker-compose.yml`, add to backend service:
```yaml
stop_grace_period: 45s
```

#### Step 8: Update healthcheck to use `/health/ready`

**AGENTE: GPT-5.4**

In `docker-compose.yml`, update backend healthcheck:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/ready', timeout=3)"]
```

### Phase 4 — Validation

**AGENTE: GPT-5.4**

#### Step 9: Full test suite

- `python -m pytest backend/tests/ -x --tb=short -q` — all 709+ pass
- `ruff check backend/` — 0 errors
- `ruff format --check backend/` — 0 diffs

---

## Execution Status

### Phase 0 — Preflight

- [x] P0-A 🔄 — Create branch `improvement/audit-01-t3-backend-lifecycle` from latest `main`. Verify clean worktree. **AGENTE: GPT-5.4**

### Phase 1 — A3: Shutdown Timeout

- [x] P1-A 🔄 — Add `asyncio.wait_for` timeout to `stop()`. **AGENTE: GPT-5.4**
- [x] P1-B 🔄 — Add unit test for shutdown timeout behavior. **AGENTE: GPT-5.4**
- [x] P1-C 🚧 — Checkpoint: present diff for user review. **AGENTE: GPT-5.4**

### Phase 2 — B4: Probes

- [x] P2-A 🔄 — Add `/health/live` endpoint. **AGENTE: GPT-5.4**
- [x] P2-B 🔄 — Add `/health/ready` endpoint. **AGENTE: GPT-5.4**
- [x] P2-C 🔄 — Add tests for new endpoints. **AGENTE: GPT-5.4**
- [x] P2-D 🚧 — Checkpoint: present diff for user review. **AGENTE: GPT-5.4**

### Phase 3 — Docker Config

- [x] P3-A 🔄 — Update Dockerfile CMD with `--timeout-graceful-shutdown 30`. **AGENTE: GPT-5.4**
- [x] P3-B 🔄 — Add `stop_grace_period: 45s` to docker-compose.yml. **AGENTE: GPT-5.4**
- [x] P3-C 🔄 — Update healthcheck to use `/health/ready`. **AGENTE: GPT-5.4**
- [x] P3-D 🚧 — Checkpoint: present diff for user review. **AGENTE: GPT-5.4**

### Phase 4 — Final

- [x] P4-A 🔄 — Full validation (tests + lint). **AGENTE: GPT-5.4**
- [x] P4-B 🚧 — Present commit proposal to user. **AGENTE: GPT-5.4**

---

## Relevant Files

| File | Action |
|------|--------|
| `backend/app/infra/scheduler_lifecycle.py` | MODIFY (A3 — add timeout) |
| `backend/app/api/routes_health.py` | MODIFY (B4 — add live/ready) |
| `Dockerfile.backend` | MODIFY (add graceful shutdown flag) |
| `docker-compose.yml` | MODIFY (add stop_grace_period + healthcheck) |
| `backend/tests/unit/test_scheduler_shutdown.py` | CREATE |
| `backend/tests/unit/test_health_probes.py` | CREATE (or extend existing) |

---

## Acceptance Criteria

- [x] `stop()` returns within 16 seconds even if scheduler task is stuck
- [x] `/health/live` returns 200 unconditionally
- [x] `/health/ready` returns 200/503 based on dependency status
- [x] `/health` continues to work (backward compatible)
- [x] Dockerfile CMD includes `--timeout-graceful-shutdown 30`
- [x] docker-compose.yml includes `stop_grace_period: 45s`
- [x] 709+ tests pass, ≥91% coverage
- [x] `ruff check` + `ruff format` clean
