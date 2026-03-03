# Code Reviews

Apply the following rules by default to every future code review in this repo unless explicitly overridden.

- Reviews focus on:
  - Correctness and alignment with the intended behavior
  - Clarity, readability, and maintainability
  - Adherence to the Engineering Guidelines and architectural intent
  - Explicit handling of edge cases, errors, and state transitions
  - Test coverage and test quality

## Code Review stance

- Reviews must be constructive and pragmatic.
- Prioritize shared understanding and long-term code health over stylistic preferences.
- Optimize for clarity, testability, and low coupling.
- Prefer small, high-impact fixes over large refactors.
- Avoid overengineering suggestions.
- Do not propose new dependencies or new architectural patterns unless explicitly required.

## Pre-review checklist

Before reading the code diff, verify:
- [ ] CI status is green (or failures are explicitly explained)
- [ ] PR description exists and matches declared scope
- [ ] PR scope remains a single user story or single technical concern
- [ ] If plan-linked, each step carries a valid `**[PR-X]**` tag aligned with the PR Roadmap

If any item fails, report it as Must-fix before continuing the code-level review.

## Severity classification criteria

Use these criteria to classify findings consistently:

**Must-fix** (blocks merge):
- incorrect behavior or logic error
- security vulnerability or data leak
- broken contract (API/schema mismatch, missing validation)
- layer violation (domain imports infra/framework, business logic in API handlers)
- missing or broken tests for changed behavior
- data loss risk or silent overwrite of human edits

**Should-fix** (strong recommendation, merge can proceed with explicit acceptance):
- naming or structure that obscures intent
- duplicated logic likely to drift
- missing error handling for realistic failure modes
- tests that do not validate meaningful behavior
- documentation drift from implemented behavior

**Nice-to-have** (optional improvements):
- style-level improvements within existing conventions
- small readability refinements
- simplification ideas that do not affect correctness

## Code Review Guidelines

When performing code reviews in this repository, use a **maintainability-focused** review style.

Review emphasis:
- Keep changes within the requested scope.
- Keep the dependency footprint minimal; add dependencies only when needed.
- Keep architecture consistent with the agreed design; introduce new patterns only when a story/design requires it.
- Keep solutions lightweight and easy to explain to evaluators.

Primary review focus (in order):
1) Layering and dependency direction:
   - `domain` has no framework/db imports
   - `application` depends only on `domain` + `ports`
   - `api` is thin (HTTP + mapping only; no SQL/business logic)
   - `infra` contains persistence/IO only
2) Maintainability:
   - clear naming and responsibilities
   - low duplication
   - small, cohesive modules/functions
   - logic located in the correct layer
3) Testability:
   - core application logic testable without FastAPI or sqlite
   - presence and quality of unit tests for services
   - integration tests cover HTTP + wiring
4) Simplicity over purity:
   - flag overengineering risks
   - prefer removing complexity over adding abstraction
5) CI and tooling sanity:
   - workflows valid
   - tests and lint runnable and reproducible
   - new environment variables documented with safe defaults
   - dependency changes in `pyproject.toml` / requirements are justified
   - Docker/container changes do not break local dev or CI
6) Database migrations and schema changes:
   - migration is reversible or has explicit rollback plan
   - schema change does not cause unintended data loss
   - defaults and nullability choices are explicit and intentional
   - migration order matches dependency chain

## Code Review Output Format

Produce the review using this mandatory output format:
   - Must-fix (blocking maintainability or correctness issues)
   - Should-fix (strong recommendations)
   - Nice-to-have (optional improvements)
   - Questions / assumptions

For PRs that include `frontend/**` or user-visible behavior/copy changes, include:
   - UX/Brand Compliance (mandatory section)
   - Any UX/Brand non-compliance must be reported under Must-fix.

Each finding must include:
- File reference(s)
- Short rationale
- Minimal suggested change

## Test review criteria

When evaluating tests in the PR:
- tests assert externally observable behavior, not implementation details
- test names clearly describe scenario and expected outcome
- changed behavior includes happy path and at least one meaningful failure case
- tests are independent of execution order and shared mutable state
- mocks/stubs are minimal and concentrated at infrastructure boundaries

## Large diff policy

If the PR diff exceeds approximately 400 lines of non-generated code:
- report a Should-fix noting reduced review confidence due to size
- suggest a split strategy when a clear split is visible
- continue the review and clearly state any confidence limitations

## Pre-existing issues policy

If you find issues that clearly predate the PR:
- do not classify them as Must-fix for the current PR
- report them in a separate "Pre-existing issues" section
- recommend a follow-up issue when impact is significant

## Code Review Safety rule

After producing a PR code review, STOP and wait for explicit user instruction before making any code changes.

Do not modify code as part of the review step unless explicitly asked to do so.
