# Way of Working

> **Canonical source of truth.**
> This document is the single authoritative reference for all operational workflow rules in this project.
>
> **Governance:**
> - This file is a canonical document maintained by humans.
> - Router files under `docs/agent_router/` are derived outputs generated from this canonical source.
> - Flow is **canonical → router only**. Router files MUST NOT be edited directly.
> - Any direct edit to a router file may be overwritten during the next regeneration cycle.

---

## Purpose

This document defines the **mandatory operational workflow** for all contributors (human and AI).
It covers the full lifecycle: starting work → branching → committing → preflight → pull request → code review → merge → done.

AI assistants must stop and explain the conflict before proceeding when instructions contradict these workflow rules.
Do not bypass reviews, tests, or workflow rules to accelerate delivery.

---

## 1. Starting New Work (Branch First)

Before making any new changes (code, docs, config, etc.), create a new branch off the appropriate base (default: `main`) using the branch naming conventions defined below.

**STOP** and ask for confirmation only if the repository state is unsafe or ambiguous (examples: uncommitted changes, merge/rebase in progress, conflicts, or it is unclear whether the current branch already corresponds to the intended work item).

### Procedure

1. Confirm repository state is safe:
   - Working tree is clean (no uncommitted changes).
   - No merge/rebase in progress.
   - If not safe, STOP and ask before proceeding.
2. Ensure the correct base branch:
   - Default base is `main` unless the user explicitly specifies another base.
   - Switch to base and update it (`git switch main` then `git pull origin main`).
3. Create the branch before editing any files:
   - If already on a correctly named branch for the same work item, proceed.
   - Otherwise, create a new branch from the updated base (`git switch -c <branch-name>`).
   - If it is ambiguous whether the current branch is the correct work branch, STOP and ask.

---

## 2. Branching Strategy

- The default branching strategy is **Feature Branching**.
- Work is developed in **short-lived branches** on top of a stable `main` branch.
- `main` always reflects a **runnable, test-passing state**.
- **No direct commits to `main`.** All changes must go through a feature branch and a pull request.
- Each change is implemented in a dedicated branch.
- Branches are merged once the change is complete and reviewed.

### Branch Naming Conventions

**User stories:**
- `feature/<ID>-<short-representative-slug>`
- The slug must be concise and describe the purpose of the user story.

**User-facing improvements (to previous implementations):**
- `improvement/<short-slug>`

**Technical non-user-facing work:**
- `refactor/<short-slug>`
- `chore/<short-slug>`
- `ci/<short-slug>`
- `docs/<short-slug>`
- `fix/<short-slug>`

Branches must be **short-lived** and focused on a single user story or a single technical concern.

---

## 3. Commit Discipline

- Commits are **small** and scoped to a **single logical change**.
- A commit must **never** span multiple user stories.
- A change may be implemented through **multiple commits**.
- Commit history must remain **readable** to support reasoning and review.

### Commit Message Conventions

**User stories:**
- `Story <ID>: <short imperative description>`

**Technical work:**
- `<type>: <short imperative description>`
- Allowed types: `refactor`, `chore`, `ci`, `docs`, `test`, `build`, `fix`

Commit messages must be clear, specific, and written in **imperative form**.
Each commit should represent a **coherent logical step**.

---

## 4. Local Preflight Levels

Use the local preflight system with three levels before pushing changes.

### L1 — Quick (before commit)

- Entry points: `scripts/ci/test-L1.ps1` / `scripts/ci/test-L1.bat`
- Purpose: catch obvious lint/format/doc guard failures with minimal delay.

### L2 — Push (before every push)

- Entry points: `scripts/ci/test-L2.ps1` / `scripts/ci/test-L2.bat`
- Frontend checks run only when frontend-impact paths changed, unless `-ForceFrontend` is provided.
- Enforced by git hook: `.githooks/pre-push`.

### L3 — Full (before Pull Request creation)

- Entry points: `scripts/ci/test-L3.ps1` / `scripts/ci/test-L3.bat`
- Runs path-scoped backend/frontend/docker checks by default.
- Use `-ForceFull` to execute full backend/frontend/docker scope regardless of diff.
- Use `-ForceFrontend` to force frontend checks even when frontend-impact paths did not change.
- E2E runs only for frontend-impact changes, unless `-ForceFrontend` or `-ForceFull` is provided.

### Preflight Rules

- For interactive local commits, run **L1** by default.
- Before every `git push`, **L2** must run (automatically via pre-push hook).
- Before opening a Pull Request, run **L3**.
- Before PR creation/update, run **L3**.
- After the Pull Request exists, rely on its CI for subsequent updates unless an explicit local rerun is requested.
- L3 runs path-scoped by default for day-to-day development branches.
- Before merge to `main`, verify CI is green.
- If a level fails, **STOP** and resolve failures (or explicitly document why a failure is unrelated/pre-existing).

### Preflight Auto-Fix Policy

Auto-fix policy when preflight fails: apply focused fixes and rerun the same level.
Maximum automatic remediation loop: 2 attempts.

When a preflight level (L1/L2/L3) fails:

- AI assistants must attempt focused fixes automatically before proceeding.
- Auto-fixes must stay within the current change scope and avoid unrelated refactors.
- Maximum automatic remediation loop: **2 attempts** (fix + rerun the failed level).
- **Never bypass quality gates** (`--no-verify`, disabling tests/checks, weakening assertions) to force a pass.
- If failures persist after the limit, STOP and report root cause, impacted files, and next-action options.

---

## 5. Pull Request Workflow

- Every user story or technical change requires **at least one Pull Request**. A single story or change may be split across multiple Pull Requests when the scope justifies it.
- Pull Requests are opened once the change (or the slice covered by that Pull Request) is **fully implemented** and **all automated tests are passing**.
- Each Pull Request must be small enough to be reviewed comfortably in isolation and should focus on a **single user story or a single technical concern**.

### Pull Request Title Conventions

**User stories:**
- `Story <ID> — <Full User Story Title>`

**Technical work:**
- `<type>: <short description>`

### Pull Request Body Requirements

- Pull Request title, body, and review comments must be written in **English**.
- When setting the Pull Request description/body from CLI, use real multiline content (heredoc or file input), not escaped `\n` sequences.
- Preferred patterns:
  - `gh pr create --body-file <path-to-markdown-file>`
  - PowerShell here-string assigned to a variable and passed to `--body`

### Pull Request Classification

Classify the Pull Request by file types:

| Type | File patterns |
|------|--------------|
| **Docs-only** | `docs/**`, `*.md`, `*.txt`, `*.rst`, `*.adoc` only |
| **Code** | Any `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.css`, `*.scss`, `*.html`, `*.sql` |
| **Non-code, non-doc** | `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.env` |

### Pull Request Procedure

1. Confirm repository state (branch, base, working tree).
2. Create/update the Pull Request targeting `main`.
3. Apply the preflight rules from Section 4 before Pull Request creation and for subsequent updates.
4. Check CI status (pending, passing, or failing).
5. For Pull Requests that change `frontend/**` or user-visible behavior:
   - Review canonical UX/brand sources before implementation/review.
   - Add a `UX/Brand compliance` section to the Pull Request description.
6. Include end-user validation steps when applicable.
7. Before requesting merge, if the Pull Request includes code changes and no code review has been performed, ask the user whether a review should be done. Include a recommended review depth (see Section 6 — Review Depth) with a brief justification.

### Plan-Level Pull Request Roadmap

Compatibility note: this section is also referenced as **Plan-level PR Roadmap** in legacy router contracts.

When a plan spans multiple Pull Requests, it must include a **Pull Request Roadmap** section:
- Table with columns: **Pull Request**, **Branch**, **Phases**, **Scope**, **Depends on**.
- Each phase belongs to exactly one Pull Request.
- Each phase belongs to exactly one PR.
- Each execution step carries a `**[PR-X]**` tag.
- Each execution step in the Execution Status must carry a `**[PR-X]**` tag.
- A Pull Request is merged only when all its assigned phases pass CI and user review.

### Post-Merge Cleanup Procedure

After a Pull Request is merged into `main`:
1. Ensure the working tree is clean.
2. Check for stashes related to the merged branch; clean up where safe.
3. Switch to `main` and pull latest changes.
4. Delete the local branch (safe deletion first; force-delete only if verified no unique commits).
5. Do NOT delete remote branches unless explicitly requested.

---

## 6. Code Review Workflow

### Manual trigger only (hard rule)

Code reviews run **only** when explicitly requested by the user. Never start a code review automatically.

### CI prerequisite (hard rule)

Before starting a code review, the agent must verify CI status:
- **CI in progress:** wait for it to complete before proceeding.
- **CI green:** proceed with the review.
- **CI red:** do NOT start the review. Inform the user that CI is failing and ask whether they want the agent to diagnose and fix the failures first. Only start the review after CI is green.

### Review Depth

When suggesting or starting a review, the agent recommends a depth level based on the Pull Request's risk profile. The user confirms, adjusts, or overrides before the review begins.

| Depth | When to recommend | Parallel lenses | What it covers |
|-------|-------------------|:---:|----------------|
| **Light** | Docs-only, config changes, formatting, simple renames | 1 | Correctness, consistency, no regressions |
| **Standard** | Normal code changes | 1 | Full review focus (all 7 areas below) |
| **Deep** | Security-sensitive, data-loss risk, architectural changes, critical user paths | 2 | Two parallel reviews with different lenses |
| **Deep (critical)** | User requests it, or agent recommends when security + architecture + data concerns overlap | 3 | Two parallel reviews with different lenses |

**Deep / Deep (critical) review Procedure:**

1. The orchestrating agent proposes review lenses based on context (e.g., maintainability-first + security-first, or architecture-first + regression-first + data-integrity-first). The user confirms or adjusts the lenses before the reviews start.
2. Each lens runs as an independent sub-agent in parallel.
3. Each sub-agent publishes its own findings as a **separate Pull Request comment**, tagged with the lens name (e.g., `## Code Review — Security-First Lens`). This ensures all raw findings are permanently recorded.
4. After all sub-agent reviews are posted, a **consolidation agent** reads all review comments and publishes a final **consolidated review comment** that:
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

1. **Layering and dependency direction** — `domain/` has no framework/db imports; `application/` depends only on `domain/` + `ports/`; `api/` is thin; `infra/` is persistence/IO only.
2. **Maintainability** — clear naming, low duplication, cohesive modules, correct layer placement.
3. **Testability** — core logic testable without frameworks; unit + integration tests.
4. **Simplicity over purity** — flag overengineering; prefer removing complexity.
5. **CI/tooling sanity** — reproducible lint/tests, justified dependency/config changes.
6. **Database migrations/schema safety** — reversible or explicit rollback plan, no unintended data loss.
7. **UX/Brand compliance** — for `frontend/**` or user-visible changes.

### Severity Classification

Compatibility note: this section is also referenced as **Severity classification criteria** in legacy router contracts.

| Severity | Criteria | Blocks merge? |
|----------|----------|:---:|
| **Must-fix** | Incorrect behavior, security vulnerability, broken contract, layer violation, missing tests for changed behavior, data-loss risk | Yes |
| **Should-fix** | Naming/structure that obscures intent, duplicated logic, missing error handling, documentation drift | No (with acceptance) |
| **Nice-to-have** | Style improvements, small readability refinements, simplification ideas | No |

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

After producing a PR code review, the AI assistant must publish the review output as a comment in the Pull Request (or update an existing `AI Code Review` comment), using the mandatory review output format.

For `frontend/**` or user-visible changes, that PR review comment must include a dedicated `UX/Brand Compliance` section.

### Mandatory publication protocol (blocking)

Blocking execution sequence:
1. Publish the review as a Pull Request comment.
2. Return the published PR comment URL.
3. When remediation commits are pushed, publish a follow-up PR comment.
4. Return the follow-up PR comment URL.

A review is blocking until the PR comment URL is returned to the user.
- A follow-up PR comment is required after remediation commits.
- This follow-up must be published automatically as part of the remediation workflow (do not wait for a separate user prompt).

- The review MUST be published as a Pull Request comment.
- A review is not complete until the Pull Request comment is posted and the URL is returned.
- **Follow-up verification (hard rule).** When commits address review findings, the agent MUST post a follow-up Pull Request comment confirming which findings are resolved, which remain open, and which introduced new concerns. A review cycle is not closed until this follow-up comment is posted.

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

## 7. Delivery Model

- Work is delivered using **vertical slices**, referred to as **releases**.
- A release represents a **complete increment of user-facing value**.
- A release may span multiple user stories across different epics.
- Each release must be **coherent, end-to-end, and meaningful** from a user perspective.
- Releases must NOT be isolated technical components.
- Always prefer completing a **smaller, well-defined** user story over partially implementing a larger one.

Each release must result in:
- A runnable and testable system state
- Clear, observable user-facing behavior
- Explicitly persisted data and state transitions
- Automated test coverage for the delivered functionality

---

## 8. User Story Kickoff Procedure

Before implementing each user story (US-XX):

1. Read the story requirements and relevant authoritative design requirements.
2. Identify **decision points** not explicitly specified (e.g., file size limits, storage roots, timeout values, retry counts, error code enums, default configuration values).
3. Resolve **discoverable facts** by inspecting the repository first (code/config/docs). Do not ask the user questions that can be answered by reading the repo.
4. Ask the user to confirm or choose for **non-discoverable preferences/tradeoffs**. Present 2–4 meaningful options and recommend a default. Do not proceed while any high-impact ambiguity remains; **STOP and ask**.
5. Record the resulting decisions/assumptions explicitly in the Pull Request description (and/or ADR-style note when requested).

---

## 9. Definition of Done

A change is considered done when it satisfies the criteria that apply to its type.

### For user stories
- Before asking the user to validate behavior manually, the agent must start the project in **dev mode with hot reload enabled** and verify endpoints are reachable.
- Use the **project-specific canonical dev-start command and checks** defined in that project's ops documentation.
- If a project does not define a canonical command/check set, STOP and ask the user to confirm the execution command before requesting validation.

- It delivers a **complete vertical slice** of user-facing value.
- It is documented (README and/or ADR if a design decision was made).
- If user-visible behavior is affected, UX guidance is applied.
- If visual identity or user-facing copy is affected, brand guidance is applied.
- When the story is completed, the implementation plan is updated with `**Status**: Implemented (YYYY-MM-DD)`.

### For technical non-user-facing changes

- The change intent and scope are explicitly documented in the Pull Request.
- Behavior is preserved, or any intended behavior change is clearly explained and justified.

### For all changes

- The resulting code remains easy to understand, extend, and evolve.
- Automated tests pass, and test coverage is updated where applicable.
- For any testable change, the final response must include **clear step-by-step validation instructions** from the end-user point of view.
- When end-user testing is not possible, explicitly state that and provide the best alternative verification method.
- **Code review gate.** When all tasks of a plan or Pull Request are completed and the change includes code, the agent must check whether a code review has been performed. If not, offer one to the user with a recommended review depth (see Section 6 — Review Depth) and justification. Do not proceed to merge until the user explicitly accepts or declines the review.
- The change is merged into `main` via Pull Request.
- CI has run and passed successfully.
- `main` remains in a **green (passing)** state after the merge.
- Every implementation must be validated explicitly against this Definition of Done before considering the change complete.
