# ADR-complexity-gate-thresholds: Complexity Gate Thresholds for CI Enforcement

## Context
The architecture review from 2026-03-09 identified sustained re-accretion risk in backend complexity hotspots. The current backend contains functions up to CC 163 and multiple Python files above 500 LOC. Without automated enforcement, decomposition work from ARCH-01 and ARCH-02 would reduce complexity only temporarily.

Manual review is not a sufficient control. Complexity regressions can be introduced incrementally across pull requests, especially in large review, extraction, and normalization flows where local behavior is hard to reason about from diff size alone.

The repository already includes `scripts/quality/architecture_metrics.py`, but until now it was an audit/reporting utility rather than a targeted CI gate for changed backend Python files.

## Decision Drivers
- Prevent re-accretion after future decomposition work.
- Enforce deterministic backend-only complexity checks in CI and local preflight.
- Warn early before code reaches failure thresholds.
- Keep the gate fast enough to run on every backend-impacting pull request.

## Considered Options
### Option A — Warning + failure thresholds on changed backend Python files
**Pros**
- Blocks only new or modified backend hotspots instead of existing legacy debt.
- Gives developers early warning before code crosses the hard-fail threshold.
- Aligns with pull-request review scope and remains fast enough for CI.

**Cons**
- Existing hotspots remain until separate remediation work is completed.

### Option B — Fail the whole repository against global thresholds immediately
**Pros**
- Maximally strict enforcement.

**Cons**
- Not mergeable with current legacy debt.
- Would block unrelated backend changes and undermine incremental remediation.

### Option C — Keep metrics as a report-only tool
**Pros**
- Zero friction for contributors.

**Cons**
- Does not prevent new hotspots.
- Depends on manual vigilance and inconsistent review behavior.

## Decision
Adopt **Option A: warning + failure thresholds enforced on changed backend Python files**.

The gate is implemented with these thresholds:
- Warn at `CC >= 11`
- Fail at `CC > 30`
- Fail at `LOC > 500`
- Scope only `backend/app/**/*.py` files changed relative to the active base ref
- Runtime target: `<30s` for the full backend scan

Warnings do not fail CI. Failures block the local preflight and the pull request workflow.

## Rationale
1. `CC >= 11` is the first level where complexity is materially harder to review and extend safely.
2. `CC > 30` indicates functions that are too difficult to reason about mechanically and should be decomposed before merge.
3. `LOC > 500` identifies backend files that are likely accumulating multiple responsibilities.
4. Changed-file scoping allows the team to prevent new debt without freezing delivery on historical hotspots already tracked by ARCH-01 and ARCH-02.

## Consequences
### Positive
- New backend complexity regressions are blocked automatically in CI.
- Developers get early warning signals before crossing the hard-fail threshold.
- The gate can be used locally in preflight, reducing CI-only surprises.

### Negative
- Existing hotspots are tolerated temporarily until planned decomposition work lands.
- Complexity warnings may require developer triage even when CI remains green.

### Risks
- Thresholds may need calibration if false positives accumulate.
- Mitigation: adjust thresholds only through a follow-up ADR and keep scope limited to changed backend Python files.

## Code Evidence
- `scripts/quality/architecture_metrics.py`
- `scripts/ci/preflight-ci-local.ps1`
- `.github/workflows/ci.yml`

## Related Decisions
- [ADR-modular-monolith: Modular Monolith over Microservices](ADR-modular-monolith)
- [ADR-in-process-async-processing: In-Process Async Processing](ADR-in-process-async-processing)
- [ARCH-03 backlog item](implementation-plan)
