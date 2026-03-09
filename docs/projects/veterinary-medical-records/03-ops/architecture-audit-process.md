# Architecture Audit Process

This document defines when to run architecture audits, which audit depth to choose, and how to execute each audit type consistently.

## Purpose

Use this process to:
- Detect architecture regressions early.
- Keep technical debt visible and measurable over time.
- Convert findings into tracked delivery backlog items.
- Maintain reproducible audit evidence across iterations.

## Audit Triggers

Run an architecture audit when one or more of these triggers occur:
- New release planning starts.
- A major module is refactored or introduced.
- A new architectural pattern, toolchain, or dependency policy is adopted.
- CI quality signals degrade (complexity, file size, lint, or test stability).
- Architectural debt backlog reaches a planned re-audit checkpoint.
- A technical assessment milestone requires objective health evidence.

## Audit Types

### Complete audit

Use when broad confidence is required (new baseline, milestone, or large architectural change).

Scope:
- Documentation architecture audit.
- Full codebase architecture audit.
- Coupling and hotspot analysis.
- Synthesis report + prioritized backlog.
- Delivery integration (formal backlog items).

Expected duration: 1-3 working days depending on churn and artifact quality.

### Partial audit

Use after implementation waves that changed architecture-relevant code.

Scope:
- Codebase architecture audit.
- Coupling and hotspot analysis.
- Delta synthesis against previous baseline.

Expected duration: 0.5-1 day.

### Quick check audit

Use for routine control between larger audit cycles.

Scope:
- Automated metrics collection and thresholds only.
- Spot-check top hotspots and violations.

Expected duration: 5-30 minutes.

## Procedure: Complete audit

1. Confirm active branch/worktree and execution protocol context.
2. Collect current architecture docs and ADR inventory.
3. Execute documentation architecture audit.
4. Execute full codebase architecture audit.
5. Run coupling and hotspot analysis.
6. Generate consolidated architecture review report.
7. Generate prioritized improvement backlog (ARCH namespace).
8. Convert approved items into formal delivery backlog files.
9. Update release plan grouping.
10. Run documentation validation checks.
11. Archive evidence paths and command outputs in the report.

Deliverables:
- `docs/projects/veterinary-medical-records/02-tech/audits/architecture-review-<date>.md`
- `docs/projects/veterinary-medical-records/02-tech/audits/improvement-backlog-<date>.md`
- `docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-*.md` (approved subset)

## Procedure: Partial audit

1. Confirm baseline reference date and latest completed audit.
2. Run codebase architecture audit on current head.
3. Run coupling and hotspot analysis.
4. Compare key metrics against baseline.
5. Update review findings and backlog priorities.
6. Update release planning if priorities changed.

Deliverables:
- Updated architecture review delta section or new dated review.
- Updated improvement backlog priorities and mappings.

## Procedure: Quick check audit

1. Run the metrics script in report mode.
2. Run the metrics script in `--check` mode for gate validation.
3. Record threshold violations and top hotspots.
4. Open/update backlog entries only if a new regression appears.

Commands:
- `.venv/Scripts/python scripts/quality/architecture_metrics.py --baseline <yyyy-mm-dd>`
- `.venv/Scripts/python scripts/quality/architecture_metrics.py --baseline <yyyy-mm-dd> --check`

Deliverables:
- `tmp/audit/metrics.json`
- `tmp/audit/metrics-report.md`

## Post-implementation Re-audit Guide

Use these checkpoints after architecture backlog implementation:
- After top 5 ARCH items: run quick check audit.
- After about 15 ARCH items: run partial audit.
- After all ARCH items in current wave: run complete audit and establish a new baseline.

Record before/after comparison for:
- Maximum cyclomatic complexity.
- Number of hotspots.
- Number of hexagonal dependency violations.
- Documentation coverage gaps.

## File Locations and Ownership

Primary audit artifacts:
- Reviews and backlogs: `docs/projects/veterinary-medical-records/02-tech/audits/`
- Delivery backlog items: `docs/projects/veterinary-medical-records/04-delivery/Backlog/`
- Release planning: `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`
- Operational process docs: `docs/projects/veterinary-medical-records/03-ops/`
- Metrics automation: `scripts/quality/architecture_metrics.py`

## Metrics Script Maintenance Notes

Keep `scripts/quality/architecture_metrics.py` aligned with project reality:
- Revisit thresholds when the codebase size or architecture strategy changes.
- Keep parser and detector rules deterministic and side-effect free.
- Keep output schema stable (`metrics.json` and Markdown report) for CI and report consumers.
- Re-run lint and check-mode validation after any script change.
- Document behavior changes in `scripts/quality/README.md`.

## Related References

- Execution protocol: [plan-execution-protocol.md](plan-execution-protocol.md)
- Compatibility execution rules: [execution-rules.md](execution-rules.md)
- Current architecture review: [architecture-review-2026-03-09.md](../02-tech/audits/architecture-review-2026-03-09.md)
