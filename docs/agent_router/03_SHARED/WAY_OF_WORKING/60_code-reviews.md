<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 6. Code Review Workflow

### Manual trigger only (hard rule)

Code reviews run **only** when explicitly requested by the user. Never start a code review automatically.

### CI prerequisite (hard rule)

Before starting a code review, the agent must verify CI status:

- **CI in progress:** wait for it to complete before proceeding.
- **CI green:** proceed with the review.
- **CI red:** do NOT start the review. Inform the user that CI is failing and ask whether they want the agent to
  diagnose and fix the failures first. Only start the review after CI is green.

### Review Depth

When suggesting or starting a review, the agent recommends a depth level based on the Pull Request's risk profile. The
user confirms, adjusts, or overrides before the review begins.

| Depth               | When to recommend                                                                          | Parallel lenses | What it covers                             |
| ------------------- | ------------------------------------------------------------------------------------------ | :-------------: | ------------------------------------------ |
| **Light**           | Docs-only, config changes, formatting, simple renames                                      |        1        | Correctness, consistency, no regressions   |
| **Standard**        | Normal code changes                                                                        |        1        | Full review focus (all 7 areas below)      |
| **Deep**            | Security-sensitive, data-loss risk, architectural changes, critical user paths             |        2        | Two parallel reviews with different lenses |
| **Deep (critical)** | User requests it, or agent recommends when security + architecture + data concerns overlap |        3        | Two parallel reviews with different lenses |

**Deep / Deep (critical) review Procedure:**

1. The orchestrating agent proposes review lenses based on context (e.g., maintainability-first + security-first, or
   architecture-first + regression-first + data-integrity-first). The user confirms or adjusts the lenses before the
   reviews start.
2. Each lens runs as an independent sub-agent in parallel.
3. Each sub-agent publishes its own findings as a **separate Pull Request comment**, tagged with the lens name (e.g.,
   `## Code Review — Security-First Lens`). This ensures all raw findings are permanently recorded.
4. After all sub-agent reviews are posted, a **consolidation agent** reads all review comments and publishes a final
   **consolidated review comment** that:
   - Deduplicates equivalent findings across lenses.
   - Assigns the highest severity when lenses disagree.
   - Uses the standard Review Output Format.
   - References the original lens comments for traceability.

### Review Focus (maintainability-first)

### Pre-review checklist

Pre-review gate (required before diff reading):

Before reading the diff, complete a pre-review checklist:

- Confirm scope and changed paths.
- Confirm CI status and required checks.
- Confirm risk profile and review depth.

1. **Layering and dependency direction** — `domain/` has no framework/db imports; `application/` depends only on
   `domain/` + `ports/`; `api/` is thin; `infra/` is persistence/IO only.
2. **Maintainability** — clear naming, low duplication, cohesive modules, correct layer placement.
3. **Testability** — core logic testable without frameworks; unit + integration tests.
4. **Simplicity over purity** — flag overengineering; prefer removing complexity.
5. **CI/tooling sanity** — reproducible lint/tests, justified dependency/config changes.
6. **Database migrations/schema safety** — reversible or explicit rollback plan, no unintended data loss.
7. **UX/Brand compliance** — for `frontend/**` or user-visible changes.

### Severity Classification

Compatibility note: this section is also referenced as **Severity classification criteria** in legacy router contracts.

| Severity         | Criteria                                                                                                                         |    Blocks merge?     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- | :------------------: |
| **Must-fix**     | Incorrect behavior, security vulnerability, broken contract, layer violation, missing tests for changed behavior, data-loss risk |         Yes          |
| **Should-fix**   | Naming/structure that obscures intent, duplicated logic, missing error handling, documentation drift                             | No (with acceptance) |
| **Nice-to-have** | Style improvements, small readability refinements, simplification ideas                                                          |          No          |

### Review Output Format

Review comments must follow the `AI Code Review` template exactly.

In deep reviews, use `## AI Code Review — <Lens>` as title.

Template (copy/paste):

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

### Review Publication

### Pull Request review visibility

After producing a PR code review, the AI assistant must publish the review output as a comment in the Pull Request (or
update an existing `AI Code Review` comment), using the mandatory review output format.

For `frontend/**` or user-visible changes, that PR review comment must include a dedicated `UX/Brand Compliance`
section.

### Mandatory publication protocol (blocking)

Blocking execution sequence:

1. Publish the review as a Pull Request comment.
2. Return the published PR comment URL.
3. When remediation commits are pushed, publish a follow-up PR comment.
4. Return the follow-up PR comment URL.

A review is blocking until the PR comment URL is returned to the user.

- A follow-up PR comment is required after remediation commits.
<!-- markdownlint-disable-next-line MD013 -->
- This follow-up must be published automatically as part of the remediation workflow (do not wait for a separate user prompt).

- The review MUST be published as a Pull Request comment.
- A review is not complete until the Pull Request comment is posted and the URL is returned.
- **Follow-up verification (hard rule).** When commits address review findings, the agent MUST post a follow-up Pull
  Request comment confirming which findings are resolved, which remain open, and which introduced new concerns. A review
  cycle is not closed until this follow-up comment is posted.

### Safety Rule

After producing a review, **STOP** and wait for explicit user instruction before making code changes.

### Pre-Existing Issues

Compatibility note: this section is also referenced as **Pre-existing issues policy** in legacy router contracts.

Issues that clearly predate the Pull Request:

- Do NOT classify as Must-fix for the current Pull Request.
- Report in a separate "Pre-existing issues" section.
- Recommend a follow-up issue when impact is significant.

### Large Diff Policy

Compatibility note: this section is also referenced as **Large diff policy** in legacy router contracts.

If the Pull Request diff exceeds ~400 lines of non-generated code:

- Report a Should-fix noting reduced review confidence.
- Suggest a split strategy when visible.
- Continue the review with stated confidence limitations.

---
