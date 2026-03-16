# AGENTS — Operational Entry Point

Start with the matching operational runbook for the current intent. Keep reads minimal.

## Runbooks
- Start new work or create a branch → `.github/prompts/start-work.prompt.md`
- Create or update a pull request → `.github/prompts/pr-workflow.prompt.md`
- Code review → `.github/prompts/code-review.prompt.md`
- Commit-task scope boundary or handoff → `.github/prompts/scope-boundary.prompt.md`

## Global Rules
- No direct commits to `main`; use a feature branch + PR unless the user explicitly authorizes otherwise.
- New branches must use `<category>/<slug>`.
- If a required standard cannot be satisfied, stop and escalate the blocker.
- Include final `How to test` for user-validatable changes.
