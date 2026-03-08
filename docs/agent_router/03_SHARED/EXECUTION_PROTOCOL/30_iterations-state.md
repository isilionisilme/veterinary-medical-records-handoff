<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 2. Atomic Iterations

Never mix scope between plan steps.

- Execute one step objective at a time.
- A step is complete only when it is marked `[x]` in `Execution Status`.
- Operational actions are protocol behavior; they are not plan steps.

---

## 3. Extended Execution State

| State | Syntax |
|---|---|
| Pending | `- [ ] F?-? ...` |
| In progress | `- [ ] F?-? ... ⏳ IN PROGRESS (<agent>, <date>)` |
| Blocked | `- [ ] F?-? ... 🚫 BLOCKED (<reason>)` |
| Step locked | `- [ ] F?-? ... 🔒 STEP LOCKED (...)` |
| Completed | `- [x] F?-? ...` |

Rules:
1. Only `[ ]` and `[x]` checkboxes are valid.
2. Mark `⏳ IN PROGRESS` before execution.
3. Remove runtime labels when closing the step as `[x]`.
4. At most one `⏳ IN PROGRESS` or `🔒 STEP LOCKED` step at a time.
5. Do not start a new step while a `🔒 STEP LOCKED` exists.

---
