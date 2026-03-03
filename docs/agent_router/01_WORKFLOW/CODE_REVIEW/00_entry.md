# Code Review (Entry)

This module is the operational procedure for code reviews in this repo.

## Manual trigger only: hard gate
- Do not start a code review unless the user explicitly asks to run one.
- Explicit trigger examples: "Do a code review for PR #...", "Review the diff for ...", "Run a code review now".
- Starting a review includes: fetching PR context for review, reading diffs for review, generating formal review output/comment, suggesting review commits, or any multi-step review run.
- If review seems needed/helpful, you may propose it, but STOP and wait for explicit instruction.
- This gate takes precedence over any workflow hint that would otherwise auto-start review-related actions.

## Review input
- `git diff main...HEAD`

## Pre-review gate (required before diff reading)
- CI is green or failures are explicitly explained.
- PR description exists and matches declared scope.
- Scope is one user story or one technical concern.
- If plan-linked, `**[PR-X]**` tags align with PR Roadmap.

If any gate fails, report it under `Must-fix` first.

## Review focus (maintainability-first)
1) Layering and dependency direction (domain/app/api/infra boundaries)
2) Maintainability (clear responsibilities, low duplication, cohesive units)
3) Testability (core logic testable without frameworks; integration tests for wiring)
4) Simplicity over purity (flag overengineering; prefer removing complexity)
5) CI/tooling sanity (reproducible lint/tests, justified deps/config/env changes)
6) Database migrations/schema safety (rollback intent, no unintended data loss, explicit null/default decisions)
7) UX/Brand compliance for `frontend/**` or user-visible changes (against UX and Brand docs)

## Severity criteria (for consistent classification)
- `Must-fix`: correctness/security/contract/layering breaks, missing tests for changed behavior, data-loss risks.
- `Should-fix`: maintainability risks that do not immediately block merge.
- `Nice-to-have`: optional readability/style refinements.

## Output format (mandatory)
The PR review comment must follow this exact structure and heading names:

```md
## AI Code Review

### Must-fix
1. **<short finding title>**
   - **File:** `<path>:<line>` (or `N/A` if it is not file-specific)
   - **Why:** <short rationale>
   - **Minimal change:** <smallest concrete fix>

### Should-fix
1. **<short finding title>**
   - **File:** `<path>:<line>` (or `N/A`)
   - **Why:** <short rationale>
   - **Minimal change:** <smallest concrete fix>

### Nice-to-have
1. **<short finding title>**
   - **File:** `<path>:<line>` (or `N/A`)
   - **Why:** <short rationale>
   - **Minimal change:** <smallest concrete fix>

### Questions / assumptions
1. <question>

### Pre-existing issues
1. **<short finding title>**
  - **File:** `<path>:<line>` (or `N/A`)
  - **Why:** <why it predates the current PR>
  - **Suggested follow-up:** <issue/debt item recommendation>

### UX/Brand Compliance
- **Compliant:**
  - <item>
- **Non-compliant / risk:**
  - <item>
```

Rules:
- Keep section order exactly as above.
- Number findings/questions (`1.`, `2.`, ...), do not use bullets for those lists.
- For `Must-fix` / `Should-fix` / `Nice-to-have`, every item must include all three fields: `File`, `Why`, `Minimal change`.
- If pre-existing issues are found, use `Pre-existing issues` and do not block current PR merge with those findings.
- `UX/Brand Compliance` is mandatory for `frontend/**` or any user-visible change. If not applicable, include:
  - `- **Compliant:**`
  - `  - N/A (non-user-visible change).`
  - `- **Non-compliant / risk:**`
  - `  - None.`

## Mandatory publication protocol (blocking)
- If the review is for a PR (or PR id can be resolved), you MUST publish the review output as a PR comment before finishing.
- A code review is not complete until:
  1) the PR comment is posted, and
  2) the PR comment URL is returned to the user.
- If one or more findings are later addressed in commits, you MUST publish a follow-up PR comment summarizing addressed points and include the follow-up comment URL in your response.
- This follow-up publication rule applies whenever you perform a code review (always), regardless of how the review was initiated.
- If PR id/reference is missing, resolve it first. If it cannot be resolved or auth is missing, STOP and ask.

## Safety rule
After producing the review, STOP and wait for explicit user instruction before making code changes.

Next: `docs/agent_router/01_WORKFLOW/CODE_REVIEW/10_review_checklist.md`
Next: `docs/agent_router/01_WORKFLOW/CODE_REVIEW/20_pr_commenting.md`
