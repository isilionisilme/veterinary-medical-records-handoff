# AGENTS — Operational Entry Point

Keep reads minimal and apply the global repository rules.

## Global Rules
- No direct commits to `main`; use a feature branch + PR unless the user explicitly authorizes otherwise.
- New branches must use `<category>/<slug>`.
- If a required standard cannot be satisfied, stop and escalate the blocker.
- Include final `How to test` for user-validatable changes.
