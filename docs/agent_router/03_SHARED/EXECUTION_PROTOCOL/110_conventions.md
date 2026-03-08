<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 15. Plan Todo Projection (Chat) (Hard Rule)

During execution:
1. Project pending plan steps as chat todos.
2. Keep exactly one todo `in_progress`.
3. Mark todo completed only when corresponding step is `[x]`.
4. If divergence is detected, reconcile from plan file immediately.

---

## 16. Token-Efficiency Policy

Use:
1. `iterative-retrieval` before each step.
2. `strategic-compact` at step close.
3. Minimal necessary context loading.

---

## 17. Commit Conventions

Use:
`<type>(plan-<id>): <short description>`

Examples:
- `feat(plan-p1): owner_address extraction hardening`
- `test(plan-p3): benchmark and regression evidence`
- `docs(plan-d6): wiki documentation update`

---

## 18. How to Add a New User Story

When adding a user story, update `IMPLEMENTATION_PLAN.md`:
1. Story order under release section.
2. Full story detail block with acceptance criteria and dependencies.
