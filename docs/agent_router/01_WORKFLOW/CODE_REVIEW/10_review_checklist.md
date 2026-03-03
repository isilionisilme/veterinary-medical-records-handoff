# Review Checklist (Minimal)

Focus on:
- Pre-review gates (CI status, PR description/scope, plan-linked PR tags when applicable)
- Correctness and edge cases
- Clarity and maintainability
- Consistency with existing patterns
- Tests (happy path + meaningful failures)
- Database migration/schema safety when schema changes are present
- UX/Brand compliance for `frontend/**` or user-visible changes
- Output format conformance with `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md` (heading order, numbered findings, and required fields per finding)
- Pre-existing issues are separated and not treated as current-PR must-fix blockers

If a required rule is missing or ambiguous, STOP and ask.

