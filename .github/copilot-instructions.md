# Copilot Workspace Instructions

## Intent → Runbook routing

Detect the user's intent and load the matching runbook **before** acting. Keep reads minimal.

| Intent | Runbook |
|---|---|
| Start new work, create a branch, begin a task | `.github/prompts/start-work.prompt.md` |
| Create or update a pull request | `.github/prompts/pr-workflow.prompt.md` |
| Code review | `.github/prompts/code-review.prompt.md` |
| Documentation updates or doc maintenance | `.github/prompts/doc-updates.prompt.md` |
| Commit, push, or git operation during active plan | `.github/prompts/scope-boundary.prompt.md` |

## Global rules

- Never commit directly to `main`; always use a feature branch + PR unless the user explicitly authorizes otherwise.
- New branches must use `<category>/<slug>` (see `.github/prompts/start-work.prompt.md` for the category table).
- After any documentation change, run the DOC_UPDATES normalization pass (see `.github/prompts/doc-updates.prompt.md`).
- If a required standard cannot be satisfied, stop and escalate the blocker.
- Always include a `How to test` section for user-validatable changes.
