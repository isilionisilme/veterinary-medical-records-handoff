# AGENTS — Entry Point (Token-Optimized)

Assistant entrypoint Keep reads minimal and route by intent.

## Required order
1) Read `docs/agent_router/00_AUTHORITY.md` first.
2) Load only the module(s) matching the current intent.
3) Open large docs only when routed there.

## Review fast path (`@codex review`)
- Trigger only on explicit review requests.
- Load only `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`.
- Fallback format if module is unavailable: `Severity | File:Line | Finding | Suggested fix`.

## Mandatory triggers
- Starting new work / creating branches: `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md`.
- Pull requests: `docs/agent_router/01_WORKFLOW/PULL_REQUESTS/00_entry.md`.
- Merge request: execute `docs/agent_router/03_SHARED/WAY_OF_WORKING/50_pull-requests.md`.
- Code PRs: `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`.
- User-visible changes: `docs/agent_router/02_PRODUCT/USER_VISIBLE/00_entry.md`.
- Plan audit or compliance check: `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/00_entry.md`.
- If user indicates docs changed / documentation was updated (any language or paraphrase): `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`.
  If files unspecified, run DOC_UPDATES discovery from git diff/status and normalize.

## Global rules
- **Mandatory rule override protocol.** To bypass a mandatory rule: (1) explain it, (2) ask for explicit confirmation. If confirmed, proceed.
- **No direct commits to `main` (hard rule).** All changes go through a feature branch + PR. Exception: explicit per-instance user authorization. Without it, STOP and create a branch first.
- **Branch naming convention (hard rule).** All new branches must follow the current canonical Branching module convention (currently `<category>/<slug>`). Before running `git branch`, `git switch -c`, or `git checkout -b`, load `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md` and `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md`.
- **Blocker escalation (hard rule).** If any required standard cannot be satisfied, STOP, explain the blocker, and ask for guidance.
- **Agent-user interaction rule (hard rule).** Whenever the agent needs the user to choose between options — plan-start choices, hard-gate decisions, commit proposals, or any other selection — the agent MUST prefer interactive UI option selectors (e.g., clickable option lists) when the environment supports them. Fall back to numbered text options only when the environment does not support UI selectors. This rule is IDE-agnostic: it applies to any development environment that supports structured option presentation.
- **Procedure auto-tracking.** When a canonical doc defines a **Procedure** heading with numbered steps, load them as todos and complete each after execution.
- **Code reviews: manual trigger only.**
- After modifying docs, run the DOC_UPDATES normalization pass once before finishing.
- Include final `How to test` for user-validatable changes.
- Run `git`, `gh`, and `npm` with elevation on first attempt; if unavailable, STOP and ask.

## Router files
- Files under `docs/agent_router/` marked `AUTO-GENERATED` are derived from canonical docs via `docs/agent_router/MANIFEST.yaml`.
- Regenerate with: `python scripts/docs/generate-router-files.py`.
- Never edit auto-generated router files directly; edit the canonical source instead.

## Plan execution
- **Trigger:** continuation intent or any git operation request while an active `PLAN_*.md` is attached or in progress.
- Load: `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/00_entry.md`.
  Then load only mini-files needed for the current step. Load canonical `plan-execution-protocol.md` only if router guidance is missing or ambiguous.
- Read Estado de ejecución and take the first `[ ]` step that belongs to the active agent for this chat.
- If the next unchecked step does not belong to the active agent, STOP and hand off to the required agent.
- Use token-efficiency policy during plan execution: `iterative-retrieval` before execution and `strategic-compact` at step close.
- For plan execution behavior, follow the protocol as sole source of truth.

## Fallback
If no intent matches, read `docs/agent_router/00_FALLBACK.md` for clarity.
