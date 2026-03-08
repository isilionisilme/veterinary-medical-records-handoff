<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 6. Rollback Procedure

If a completed step introduces regressions:
1. Revert/fix code safely.
2. Return affected plan step from `[x]` to `[ ]`.
3. Report blocker and recovery path.

---

## 7. Plan Governance

### Scope and structure

- `PLAN_*.md` must not include operational tasks (`commit-task`, `create-pr`, `merge-pr`, `CT-*` checkboxes).
- Commit guidance is inline recommendation under implementation steps (when/scope/message/validation).
- Every active plan must include a documentation-wiki step that closes either:
  - with delivered docs, or
  - with `no-doc-needed` rationale.

### Git policy by automation mode

- `commit`:
  - `Supervisado`: requires explicit user confirmation.
  - `Semiautomatico`: may be executed automatically.
  - `Automatico`: may be executed automatically.
- `push`: always manual/user-triggered in all modes.
- Merge: always explicit user approval.

### PR policy

- PR is required before merge.
- PR creation/update is user-triggered only.
- Agent never auto-creates PR unless user explicitly requests it in that moment.

### Pre-PR Commit History Review (Hard Rule)

Before recommending PR creation/update:
1. Review actual branch history.
2. Ensure commit grouping tells a coherent technical narrative.
3. Reorder/squash/split only with explicit user confirmation.
4. If history quality is poor, stop and propose cleanup first.

---
