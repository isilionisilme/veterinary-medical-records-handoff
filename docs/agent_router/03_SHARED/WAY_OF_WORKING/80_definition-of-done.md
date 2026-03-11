<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 9. Definition of Done

A change is considered done when it satisfies the criteria that apply to its type.

### For user stories

- Before asking the user to validate behavior manually, the agent must start the project in **dev mode with hot reload
  enabled** and verify endpoints are reachable.
- Use the **project-specific canonical dev-start command and checks** defined in that project's ops documentation.
- If a project does not define a canonical command/check set, STOP and ask the user to confirm the execution command
  before requesting validation.

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
- For any testable change, the final response must include **clear step-by-step validation instructions** from the
  end-user point of view.
- When end-user testing is not possible, explicitly state that and provide the best alternative verification method.
- **Code review gate.** When all tasks of a plan or Pull Request are completed and the change includes code, the agent
  must check whether a code review has been performed. If not, offer one to the user with a recommended review depth
  (see Section 6 — Review Depth) and justification. Do not proceed to merge until the user explicitly accepts or
  declines the review.
- The change is merged into `main` via Pull Request.
- CI has run and passed successfully.
- `main` remains in a **green (passing)** state after the merge.
- Every implementation must be validated explicitly against this Definition of Done before considering the change
  complete.
