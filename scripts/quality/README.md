# scripts/quality

Quality guardrails for design consistency, architecture metrics, and CI checks.

## Scripts

| Script | Purpose |
|---|---|
| `check_design_system.mjs` | Detects frontend design-system violations such as raw tokens, inline styling escapes, unlabeled icon buttons, and disallowed bypasses. |
| `architecture_metrics.py` | Collects architecture metrics (CC, LOC, churn, hex violations, hotspots, scans) and generates `tmp/audit/metrics.json` plus `tmp/audit/metrics-report.md`. In `--check` mode it scopes enforcement to changed `backend/app/**/*.py` files, warns at `--warn-cc` (default `11`), fails at `--max-cc` (default `30`), and fails at `--max-loc` (default `500`). |

## Quick Notes

- Run these scripts from the repository root.
- `architecture_metrics.py --check --base-ref <ref>` is used by local preflight and GitHub Actions for incremental backend complexity enforcement.
- The design-system guard is frontend-oriented, while `architecture_metrics.py` is the backend architecture gate.
