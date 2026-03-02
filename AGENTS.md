# AGENTS — Entry Point (Token-Optimized)

AI assistant entrypoint. Keep reads minimal and route by intent.

## Required order
1) Read `docs/agent_router/00_AUTHORITY.md` first.
2) Load only the module(s) matching the current intent.
3) Open large docs only when routed there.

## Review fast path (`@codex review`)
- Trigger only on explicit review requests.
- Load only `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`.
- Fallback format if module is unavailable: `Severity | File:Line | Finding | Suggested fix`.

## Mandatory triggers
- Starting new work: `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md`.
- Pull requests: `docs/agent_router/01_WORKFLOW/PULL_REQUESTS/00_entry.md`.
- Merge request: execute `docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/210_pull-requests.md`.
- Code PRs: `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`.
- User-visible changes: `docs/agent_router/02_PRODUCT/USER_VISIBLE/00_entry.md`.
- If user indicates docs changed (any language or paraphrase): `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`.
  If files are unspecified, run DOC_UPDATES discovery from git diff/status and normalize.
- If the user says documentation was updated, route to `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`.

## Global rules
- **No direct commits to `main` (hard rule).** All changes go through a feature branch + PR. The only exception is if the user gives explicit, per-instance authorization (e.g. "commitea directo a main"). Without that authorization, STOP and create a branch first.
- Manual trigger only for code reviews (never start one implicitly).
- After modifying docs, run the DOC_UPDATES normalization pass once before finishing.
- Include final `How to test` for user-validatable changes.
- Run `git`, `gh`, and `npm` with elevation on first attempt; if unavailable, STOP and ask.

## Plan execution (`Continúa`)
- Load: `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`.
- **Step completion integrity:** before any handoff or auto-chain, enforce § "Step completion integrity" (NO-BATCH, CI-FIRST-BEFORE-HANDOFF, PLAN-UPDATE-IMMEDIATO, STEP-LOCK, EVIDENCE BLOCK, AUTO-HANDOFF GUARD).- **Iteration close:** after merge, execute § "Iteration close-out protocol" in `execution-rules.md` (reconciliation, IMPLEMENTATION_HISTORY, DOC_UPDATES normalization).- Active plans: `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_*.md`; completed: `docs/projects/veterinary-medical-records/04-delivery/plans/completed/`.
- Read Estado de ejecución and take the first `[ ]` step.
- If step belongs to another agent: STOP and hand off to the exact required agent with a new chat + active PLAN + `Continúa`.
- If step belongs to current agent: execute it and apply token-efficiency (`iterative-retrieval` before execution, `strategic-compact` at step close).
- If that step belongs to the active agent for this chat: continue with the plan.
- Canonical handoff (must be exact):
  "⚠️ Este paso no corresponde al agente activo. **STOP.** El siguiente paso es de **GPT-5.3-Codex**. Abre un chat nuevo en Copilot → selecciona **GPT-5.3-Codex** → adjunta el `PLAN` activo → escribe `Continúa`."
  "⚠️ Este paso no corresponde al agente activo. **STOP.** El siguiente paso es de **Claude Opus 4.6**. Abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** → adjunta el `PLAN` activo → escribe `Continúa`."
- At step close: auto-continue only when next step is same agent and not a hard-gate; otherwise STOP and hand off.

## Fallback
If no intent matches, read `docs/agent_router/00_FALLBACK.md` and ask for clarification.
