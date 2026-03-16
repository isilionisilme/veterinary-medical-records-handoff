# Copilot Workspace Instructions

## Intent → Runbook routing

Detect the user's intent and load the matching runbook **before** acting. Keep reads minimal.

Source of truth: keep this file behaviorally aligned with `AGENTS.md`. If intent routing or shared rules change, update both files in the same change and keep the contract test green.

| Intent | Runbook |
|---|---|
| Start new work or create a branch | `.github/prompts/start-work.prompt.md` |
| Create or update a pull request | `.github/prompts/pr-workflow.prompt.md` |
| Code review | `.github/prompts/code-review.prompt.md` |
| Documentation updates or doc maintenance | `.github/prompts/doc-updates.prompt.md` |
| Commit-task scope boundary or handoff | `.github/prompts/scope-boundary.prompt.md` |

## Global Rules

- No direct commits to `main`; use a feature branch + PR unless the user explicitly authorizes otherwise.
- New branches must use `<category>/<slug>`.
- If a required standard cannot be satisfied, stop and escalate the blocker.
- Include final `How to test` for user-validatable changes.

## Validation

When this file changes, validate routing behavior with a fresh Copilot Chat conversation and keep the AGENTS/copilot-instructions contract test passing.
