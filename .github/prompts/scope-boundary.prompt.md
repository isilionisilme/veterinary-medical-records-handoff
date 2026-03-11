---
agent: agent
description: Execute commit or push during active plan execution.
---

1. Activate this procedure for any `commit`, `push`, or other git-operation request during active plan execution. Treat it as a SCOPE BOUNDARY trigger, not as an isolated command.
2. STEP 0 — Branch verification: read `**Branch:**` from the plan and compare it with `git branch --show-current`. If the plan branch is unresolved, create or select the proper branch first and record it in the plan. If the current branch does not match the plan branch, STOP immediately.
3. If branch transition is required mid-plan, follow the full protocol: verify the target branch exists in the PR Roadmap, create a `WIP:` commit if uncommitted changes exist, update `**Branch:**` in the plan, switch branches, and report the new active branch.
4. Before every `git commit`, always run project formatters or the unified preflight. The preferred command is `scripts/ci/test-L1.ps1 -BaseRef HEAD`, which covers formatting, linting, and doc guards.
5. Apply the local preflight integration table:

| SCOPE BOUNDARY moment | Min. level | Command |
|---|---|---|
| Before commit (STEP A) | L1 | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
| Before push (STEP C) | L2 | `scripts/ci/test-L2.ps1 -BaseRef main` |
| Before PR creation/update | L3 | `scripts/ci/test-L3.ps1 -BaseRef main` |
| Before merge to main | CI green | No local run needed |

6. If a preflight level fails, apply focused fixes within the current scope and rerun the same level. Maximum automatic remediation loop: 2 attempts. Never bypass quality gates.
7. STEP A — Commit code: stage only files inside the active implementation scope and commit implementation files first. Never stage unrelated files.
8. STEP B — Commit plan update: apply completion rules, then stage and commit the plan file separately. This is the mandatory two-commit strategy when both implementation files and the plan file changed.
9. STEP C — Push both commits only if the user explicitly requested push in the current step. Before push, run `scripts/ci/test-L2.ps1 -BaseRef main`.
10. STEP D — Create or update the PR only if push occurred and the user explicitly requested PR work. Before PR creation or update, run `scripts/ci/test-L3.ps1 -BaseRef main`.
11. STEP E — If push occurred, check CI and wait/retry according to protocol; report failures instead of guessing.
12. For manual user validation requests, first start the project in dev mode with hot reload using `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`, then verify backend `http://localhost:8000/health` and frontend `http://localhost:5173` both return HTTP 200. If either fails, STOP and report the blocker.
13. In any `🚧` hard-gate, present options using the Agent-user interaction rule and require an explicit user selection before proceeding.
14. After commit or push handling, apply the next-step decision table and either auto-chain or STOP.
