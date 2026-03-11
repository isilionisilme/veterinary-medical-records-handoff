---
agent: agent
description: Run a structured code review on a pull request.
---

1. Run this workflow only when the user explicitly requests a code review. Never start a review automatically.
2. Before reading the diff, verify CI status: wait if CI is in progress; proceed only if CI is green; if CI is red, STOP and ask whether to diagnose the failures first.
3. Complete the pre-review checklist before diff reading: confirm changed paths and scope, confirm CI status and required checks, and confirm the risk profile.
4. Recommend a review depth and wait for user confirmation or override:

| Depth | When to recommend | Parallel lenses | What it covers |
|-------|-------------------|:---:|----------------|
| **Light** | Docs-only, config changes, formatting, simple renames | 1 | Correctness, consistency, no regressions |
| **Standard** | Normal code changes | 1 | Full review focus (all 7 areas below) |
| **Deep** | Security-sensitive, data-loss risk, architectural changes, critical user paths | 2 | Two parallel reviews with different lenses |
| **Deep (critical)** | User requests it, or security + architecture + data concerns overlap | 3 | Two parallel reviews with different lenses |

5. For `Deep` and `Deep (critical)`, propose review lenses, wait for user confirmation, run each lens as an independent parallel sub-agent, publish each lens as its own PR comment, then publish a final consolidated review comment that deduplicates findings and assigns the highest severity when lenses disagree.
6. Review all 7 focus areas: layering and dependency direction, maintainability, testability, simplicity over purity, CI/tooling sanity, database migration/schema safety, and UX/Brand compliance for `frontend/**` or user-visible changes.
7. Apply the entrypoint-size warning when `AGENTS.md` grows materially: report it as `Should-fix` or `Nice-to-have` only when token efficiency, routing clarity, or contract parity is at risk.
8. Classify findings with the mandatory severity criteria:

| Severity | Criteria | Blocks merge? |
|----------|----------|:---:|
| **Must-fix** | Incorrect behavior, security vulnerability, broken contract, layer violation, missing tests for changed behavior, data-loss risk | Yes |
| **Should-fix** | Naming/structure that obscures intent, duplicated logic, missing error handling, documentation drift | No (with acceptance) |
| **Nice-to-have** | Style improvements, small readability refinements, simplification ideas | No |

9. Handle pre-existing issues separately: do not classify them as `Must-fix` for the current PR; place them in a `Pre-existing issues` section and recommend follow-up when impact is significant.
10. Apply the large diff policy: docs-only PRs never trigger a size-based `Should-fix`; code or mixed PRs should get a reduced-confidence `Should-fix` when code lines exceed about `400`, with a suggested split strategy when visible.
11. Output the review using the `AI Code Review` template exactly. In deep reviews, title each lens comment `## AI Code Review — <Lens>`.

```text
## AI Code Review

### Must-fix
1. **None**
	- **File:** `N/A`
	- **Why:** <reason>
	- **Minimal change:** <comment or None.>

### Should-fix
1. **<finding title>**
	- **File:** `<path:line>`
	- **Why:** <reason>
	- **Minimal change:** <smallest acceptable fix>

### Nice-to-have
1. **<finding title>**
	- **File:** `<path:line>`
	- **Why:** <reason>
	- **Minimal change:** <optional improvement>

### Questions / assumptions
1. <question>

### Pre-existing issues
1. **None**
	- **File:** `N/A`
	- **Why:** <reason>
	- **Suggested follow-up:** <comment or None.>

### UX/Brand Compliance
- **Compliant:**
  - <evidence or `None`>
- **Non-compliant / risk:**
  - <risk or `None`>
```

12. Publish the review as a Pull Request comment or update an existing `AI Code Review` comment, return the comment URL, and treat publication as blocking completion. For remediation commits, publish and return a follow-up PR comment describing resolved, remaining, and newly introduced concerns.
13. After producing the review, STOP and wait for explicit user instruction before making code changes.
