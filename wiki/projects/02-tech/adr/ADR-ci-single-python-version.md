# ADR-ci-single-python-version: Single Python Version CI (No Matrix)

## Context

CI pipelines can test against multiple Python versions (matrix strategy) or pin to a single version matching the Docker runtime. The project also considered PR deploy previews for visual feedback.

## Decision Drivers

- Pipeline speed: matrix testing multiplies CI duration by the number of versions.
- Docker runtime pins Python 3.11 — only one version runs in production-like environments.
- Deploy previews require external hosting infrastructure beyond exercise scope.

## Considered Options

### Option A — Single-version CI matching Docker runtime (current)

#### Pros

- Fast pipeline: one test run per push.
- No version-compatibility surprises — CI matches the runtime exactly.
- No hosting infrastructure needed.

#### Cons

- Does not detect regressions on Python 3.12+ (type hints, deprecations).
- No visual preview for PR reviewers.

### Option B — Python version matrix (3.11 + 3.12)

#### Pros

- Catches forward-compatibility issues early.

#### Cons

- Doubles CI time for a single-runtime project.
- Maintenance burden for version-specific test workarounds.

### Option C — PR deploy previews (Vercel/Netlify/GitHub Pages)

#### Pros

- Visual feedback on frontend changes per PR.

#### Cons

- Requires hosting account, preview URL management, and cleanup.
- Disproportionate setup cost for a portfolio exercise evaluated locally.

## Decision

Adopt **Option A: single Python version (3.11) CI** with no deploy previews.

## Rationale

1. The `Dockerfile.backend` pins `python:3.11-slim` — CI should match the actual runtime.
2. CI already includes Ruff lint, type checking, and full test suites; adding versions increases cost without catching bugs relevant to the pinned runtime.
3. Deploy previews are valuable for team collaboration but unnecessary when the evaluator runs `docker compose up` locally.

## Consequences

### Positive

- CI completes in ~2 minutes (backend + frontend, cached).
- No external hosting dependencies.

### Negative

- Python 3.12+ compatibility is untested.

### Risks

- If the project upgrades to Python 3.12, a matrix becomes necessary for the transition period.
- Mitigation: add a matrix row only when the Docker base image is updated.

## Code Evidence

- `.github/workflows/` — CI workflow files
- `Dockerfile.backend` — Python version pin
- `pyproject.toml` — `requires-python = ">=3.11"`

## Related Decisions

- [ADR-complexity-gate-thresholds: Complexity Gate Thresholds for CI Enforcement](ADR-complexity-gate-thresholds)