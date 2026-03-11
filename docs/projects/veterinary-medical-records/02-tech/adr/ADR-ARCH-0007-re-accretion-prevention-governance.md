---
title: "ADR-ARCH-0007: Re-accretion Prevention Governance"
type: adr
status: active
audience: all
last-updated: 2026-03-11
---

# ADR-ARCH-0007: Re-accretion Prevention Governance

## Status

- Accepted
- Date: 2026-03-11

## Context

The architecture review from 2026-03-09 identified a repeatable regression
pattern: files decomposed during the Feb 2026 cleanup re-accumulated
responsibilities and complexity within a few weeks. Two successor modules became
new hotspots:

- `review_service.py` at 1,532 LOC with max CC 99
- `candidate_mining.py` at 1,013 LOC with max CC 163

This is not a one-off implementation issue. It is an architectural governance
issue: decomposition reduces complexity at a point in time, but without
explicit budgets and continuous enforcement, large orchestrators and
branch-heavy functions grow back through normal feature work.

ARCH-03 already introduced CI complexity gates and changed-file enforcement in
`scripts/quality/architecture_metrics.py`, but that ADR focuses on the
enforcement mechanism. We still need an explicit architectural policy
describing what "too large" means and why those limits exist.

## Decision Drivers

- Preserve decomposition gains over time instead of treating refactors as one-time cleanups.
- Define a repository-wide architectural budget that reviewers can apply consistently.
- Link architectural policy to the existing ARCH-03 enforcement mechanism.
- Keep the policy simple enough to use during routine code review.

## Considered Options

### Option A - Record explicit complexity budgets with CI enforcement linkage

#### Pros

- Creates a stable architectural policy independent of any single implementation detail.
- Makes re-accretion visible during design and review, not only after a hotspot appears.
- Reuses the existing ARCH-03 gate as the operational control.

#### Cons

- Requires teams to interpret a policy budget and a CI backstop together.

### Option B - Rely only on ARCH-03 CI thresholds

#### Pros

- No additional documentation to maintain.

#### Cons

- Captures only the enforcement mechanics, not the architectural intent.
- Encourages teams to optimize for the hard fail line instead of the design target.

### Option C - Keep hotspot management as an audit-only activity

#### Pros

- Zero process overhead for day-to-day changes.

#### Cons

- Repeats the failure mode already observed in the codebase.
- Detects regressions after they become expensive to unwind.

## Decision

Adopt **Option A: explicit re-accretion prevention governance linked to ARCH-03 enforcement**.

The architectural budgets for decomposed or newly created backend modules are:

- Maximum file size: `500 LOC`
- Maximum function cyclomatic complexity: `20`

These budgets define the preferred steady-state design ceiling. ARCH-03
remains the enforcement mechanism in CI and local preflight:

- `CC >= 11` warns
- `CC > 30` fails
- `LOC > 500` fails

This creates a two-tier control model:

1. **Architectural budget:** design and review should keep functions at `CC <= 20` and files at `LOC <= 500`.
2. **CI backstop:** ARCH-03 blocks severe regressions mechanically and warns
   before functions approach the architectural ceiling.

## Rationale

1. `500 LOC` is the point where backend files in this repository have
   repeatedly started to blend orchestration, transformation, validation, and
   projection concerns.
2. `CC > 20` is above the range where functions remain straightforward to
   review, test, and decompose incrementally.
3. The observed re-accretion pattern shows that decomposition alone is not
   durable unless the repository also defines budgets for successor modules.
4. Keeping ARCH-03 as the enforcement mechanism avoids duplicating tooling
   while still documenting the architectural intent behind the thresholds.

## Consequences

### Positive

- Future decomposition work has a clear finish line for successor modules.
- Reviewers can challenge growth before a file becomes a visible hotspot again.
- The repository now has both architectural policy and CI enforcement, closing
  the governance gap identified in the audit.

### Negative

- Some legitimate orchestrator functions may require additional extraction earlier than teams would otherwise choose.
- CI does not hard-fail at `CC > 20`, so review discipline is still required between the warning and failure bands.

### Risks

- Contributors may interpret the CI hard-fail threshold (`CC > 30`) as the preferred design target.
- Mitigation: treat this ADR as the source of truth for architecture budgets
  and treat ADR-ARCH-0005 as the enforcement implementation detail.

## Code Evidence

- `scripts/quality/architecture_metrics.py`
- `scripts/ci/preflight-ci-local.ps1`
- `.github/workflows/ci.yml`

## Related Decisions

- [ADR-ARCH-0005: Complexity Gate Thresholds for CI Enforcement](ADR-ARCH-0005-complexity-gate-thresholds.md)
- [ADR-ARCH-0001: Modular Monolith over Microservices](ADR-ARCH-0001-modular-monolith.md)
- [Architecture Review 2026-03-09](../audits/architecture-review-2026-03-09.md)
- [ARCH-03 backlog item](../../04-delivery/Backlog/completed/arch-03-add-ci-complexity-gates.md)
