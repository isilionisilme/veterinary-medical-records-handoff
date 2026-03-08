<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 9. Format-Before-Commit (Mandatory)

**Before every `git commit`, the agent ALWAYS runs the project formatters:**
1. `cd frontend && npx prettier --write 'src/**/*.{ts,tsx,css}' && cd ..`
2. `ruff check backend/ --fix --quiet && ruff format backend/ --quiet`
3. If commit fails: re-run formatters, re-add, retry ONCE. Second failure: STOP.

> **Tip:** Running `scripts/ci/test-L1.ps1 -BaseRef HEAD` covers formatting, linting, and doc guards in a single command.

### Local Preflight Integration

| SCOPE BOUNDARY moment | Min. level | Command |
|---|---|---|
| Before commit (STEP A) | L1 | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| Before push (STEP C) | L2 | `scripts/ci/test-L2.ps1 -BaseRef main` |
| Before PR creation/update | L3 | `scripts/ci/test-L3.ps1 -BaseRef main` |
| Before merge to main | CI green | No local run needed |

### User Validation Environment (Mandatory)

When the agent asks the user to validate or test behavior manually, the agent MUST first start the project in **dev mode with hot reload enabled**.

Canonical command (this project):
1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`

Canonical stop command (this project):
1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml down`

Mandatory checks before asking user validation:
1. Backend reachable: `http://localhost:8000/health` returns HTTP 200.
2. Frontend reachable: `http://localhost:5173` returns HTTP 200.
3. If either check fails, STOP and report the blocker instead of asking the user to test.

---
