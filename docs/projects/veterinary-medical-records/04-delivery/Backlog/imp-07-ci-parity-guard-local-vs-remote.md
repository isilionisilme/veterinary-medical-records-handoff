# IMP-07 — CI Parity Guard: Local vs Remote

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** TBD

**PR strategy:** Single dedicated PR (guard script + CI integration + documentation)

**Technical Outcome**
Prevent CI failures caused by drift between local preflight scripts and the remote GitHub Actions workflow by adding an exhaustive parity guard that detects discrepancies before push.

**Problem Statement**
The existing `Config sync guard` in `preflight-ci-local.ps1` checks configuration file parity but does not verify that the **gates themselves** (jobs, steps, path filters, commands) match between the remote CI workflow (`.github/workflows/ci.yml`) and the local preflight pipeline (`test-L1.ps1`, `test-L2.ps1`, `test-L3.ps1`, `preflight-ci-local.ps1`). When a local script is updated without propagating the change to the remote workflow (or vice versa), pushes pass locally but fail in CI — wasting time and creating false confidence.

**Scope**

### Parity analysis engine

Build a guard that:

1. Parses `.github/workflows/ci.yml` — extracts jobs, `if` conditions, path filters, and commands.
2. Parses local wrappers — `test-L1.ps1`, `test-L2.ps1`, `test-L3.ps1`, and `preflight-ci-local.ps1` (Mode Quick/Push/Full and effective steps).
3. Produces a classification table:

   | Classification | Meaning |
   |---|---|
   | `Equivalent` | Same gate exists in both local and remote |
   | `Remote-only` | Gate runs in CI but has no local equivalent |
   | `Local-only` | Gate runs locally but has no CI equivalent |

4. Emits a verdict: `PARITY_OK` or `PARITY_GAP`.

### Integration

- Add the parity guard as a step in L2 (`preflight-ci-local.ps1` Push mode).
- On `PARITY_GAP`: fail with actionable output listing the specific discrepancies and minimum actions to close the gap.
- On `PARITY_OK`: emit a single-line pass message (consistent with existing guard output format).

### Context-aware risk assessment

For the files changed in the current branch, assess whether any `PARITY_GAP` items are relevant:
- If changed files match a remote-only gate's path filter → elevated risk.
- If changed files match a local-only gate → no remote coverage risk.

**Out of Scope**
- No changes to the remote CI workflow itself (this guard detects drift, not fixes it).
- No changes to business/domain behavior.
- No new frontend/backend product functionality.

**Acceptance Criteria**
- A parity guard script exists that parses `ci.yml` and local preflight scripts.
- Running L2 includes the parity guard and emits `PARITY_OK` or `PARITY_GAP`.
- When a deliberate discrepancy is introduced (e.g., a new CI job with no local equivalent), the guard fails with a clear message identifying the gap.
- The guard output includes a classification table (Equivalent / Remote-only / Local-only) with command and source file references.
- Changed-files risk assessment flags elevated risk when modified files match a remote-only gate's path filter.
- Documentation in `scripts/ci/README.md` describes the parity guard behavior.

**Validation Checklist**
- Introduce a dummy job in `ci.yml` with no local equivalent → verify `PARITY_GAP` with actionable output.
- Add a local-only guard step → verify it appears as `Local-only` in the classification table.
- Run L2 on a clean branch → verify `PARITY_OK`.
- Modify a file matching a remote-only gate's path filter → verify elevated risk warning.
- Confirm the guard does not modify any files or make commits.

**Risks and Mitigations**
- Risk: YAML parsing of `ci.yml` may not handle all GitHub Actions syntax (matrix, reusable workflows, composite actions).
  - Mitigation: start with direct job/step parsing; extend incrementally. Flag unparseable sections as warnings, not failures.
- Risk: False positives from intentional asymmetries (e.g., deployment jobs that should only run in CI).
  - Mitigation: support an allowlist of known intentional asymmetries in a configuration file (e.g., `parity-allowlist.json`).
- Risk: Guard adds latency to L2.
  - Mitigation: parity check is a static file comparison — no network calls, no test execution. Should complete in under 2 seconds.

**Dependencies**
- Depends on existing L1/L2/L3 preflight pipeline conventions.
- Should remain aligned with IMP-03 (Plan Execution Guard Enforcement) and IMP-06 (Preflight Wrapper Integrity).
- The existing `Config sync guard` may be subsumed or complemented by this guard.
