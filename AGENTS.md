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
- Merge request: execute `docs/agent_router/03_SHARED/WAY_OF_WORKING/50_pull-requests.md`.
- Code PRs: `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`.
- User-visible changes: `docs/agent_router/02_PRODUCT/USER_VISIBLE/00_entry.md`.
- If user indicates docs changed / documentation was updated (any language or paraphrase): `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`.
  If files unspecified, run DOC_UPDATES discovery from git diff/status and normalize.

## Global rules
- **Mandatory rule override protocol.** When the user asks to bypass a rule marked as mandatory (e.g., "Never", "must not", "hard rule") in any canonical document, the assistant must: (1) explain which rule would be violated, (2) ask for explicit confirmation. If the user confirms, proceed. Never silently skip a mandatory rule, but never permanently block the user either.
- **No direct commits to `main` (hard rule).** See `docs/shared/03-ops/way-of-working.md` §1. All changes go through a feature branch + PR. The only exception is if the user gives explicit, per-instance authorization. Without that authorization, STOP and create a branch first.
- **Blocker escalation (hard rule).** If any standard, instruction, or requirement from a canonical document cannot be satisfied, STOP — explain the blocker and ask for guidance before proceeding. Never silently skip or partially comply.
- **Procedure auto-tracking.** When a canonical document defines a **Procedure** (a section whose heading contains the word "Procedure" followed by a numbered step list), the agent must load those steps as planned todos before starting execution. Each numbered step becomes one todo item. Mark each todo as completed immediately after finishing it.
- **Code reviews: manual trigger only** (see `docs/shared/03-ops/way-of-working.md` §6 for full workflow).
- After modifying docs, run the DOC_UPDATES normalization pass once before finishing.
- Include final `How to test` for user-validatable changes.
- Run `git`, `gh`, and `npm` with elevation on first attempt; if unavailable, STOP and ask.

## Router files
- Files under `docs/agent_router/` marked `AUTO-GENERATED` are derived from canonical docs via `docs/agent_router/MANIFEST.yaml`.
- Regenerate with: `python scripts/docs/generate-router-files.py`.
- Never edit auto-generated router files directly; edit the canonical source instead.

## Plan execution
- **Trigger:** continuation intent ("Continúa", "continue", "go", "proceed", "resume") OR any git operation request (commit, push, branch, merge) while an active `PLAN_*.md` is attached or its execution is in progress in the current conversation.
- Load: `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`.
- Read Estado de ejecución and take the first `[ ]` step that belongs to the active agent for this chat.
- If the next unchecked step does not belong to the active agent, STOP and hand off to the required agent.
- Use token-efficiency policy during plan execution: `iterative-retrieval` before execution and `strategic-compact` at step close.
- For plan execution behavior, follow the protocol as the sole source of truth (do not duplicate plan-operational rules here).

## Fallback
If no intent matches, read `docs/agent_router/00_FALLBACK.md` and ask for clarification.
