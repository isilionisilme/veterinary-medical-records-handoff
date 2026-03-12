# AGENTS — Operational Entry Point

Start with the matching operational runbook for the current intent. Keep reads minimal.

## Runbooks
- Start new work or create a branch → `.github/prompts/start-work.prompt.md`
- Create or update a pull request → `.github/prompts/pr-workflow.prompt.md`
- Code review → `.github/prompts/code-review.prompt.md`
- Documentation updates or doc maintenance → `.github/prompts/doc-updates.prompt.md`
- Commit-task scope boundary or handoff → `.github/prompts/scope-boundary.prompt.md`

## Global Rules
- No direct commits to `main`; use a feature branch + PR unless the user explicitly authorizes otherwise.
- New branches must use `<category>/<slug>` and follow `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md`.
- If docs changed, documentation was updated, or the user mentions documentation updates in any language or paraphrase, load `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md` and run the DOC_UPDATES normalization pass once before finishing.
- If a required standard cannot be satisfied, stop and escalate the blocker.
- Include final `How to test` for user-validatable changes.

## Router References
- Non-operational routing and fallback remain in `docs/agent_router/00_AUTHORITY.md` and `docs/agent_router/00_FALLBACK.md`.
- Shared standards and project references remain in `docs/agent_router/03_SHARED/00_entry.md` and `docs/agent_router/04_PROJECT/00_entry.md`.
- Router files marked `AUTO-GENERATED` must be edited through their canonical source and regenerated with `python scripts/docs/generate-router-files.py`.
