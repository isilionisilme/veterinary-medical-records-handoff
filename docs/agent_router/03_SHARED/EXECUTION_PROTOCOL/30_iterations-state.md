<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 2. Atomic Iterations

Never mix scope between steps. Each step in Execution Status is an atomic unit: execute its objective and mark progress. Commit behavior is governed by the plan's automation mode (see §7 — Automation Mode Selection): `Supervisado` requires explicit user confirmation before each commit; `Semiautomatico` and `Automatico` permit automatic commits scoped to the active step. Push is always manual. If a step fails, report — do not continue to the next one.

**Plan-mode governance (hard rule):** While a plan is active, all git operations (commit, push, branch) are governed by this protocol. Ad-hoc user requests that imply git operations are interpreted through the lens of the active plan step and routed to SCOPE BOUNDARY (§13). There is no "just commit and push" shortcut.

---

## 3. Extended Execution State

For visibility and traceability, mark the active step with the appropriate label **without changing the base checkbox**.

| State | Syntax |
|-------|--------|
| Pending | `- [ ] F?-? ...` |
| In progress | `- [ ] F?-? ... ⏳ IN PROGRESS (<agent>, <date>)` |
| Blocked | `- [ ] F?-? ... 🚫 BLOCKED (<short reason>)` |
| Step locked | `- [ ] F?-? ... 🔒 STEP LOCKED (code committed, awaiting CI + plan update)` |
| Completed | `- [x] F?-? ...` |

**Mandatory rules:**
1. Do not use `[-]`, `[~]`, `[...]` or variants: only `[ ]` or `[x]`.
2. Before executing a `[ ]` step, mark it `⏳ IN PROGRESS (<agent>, <date>)`.
3. `IN PROGRESS` and `BLOCKED` are text labels, not checkbox states.
4. On completion, remove any label and mark `[x]`.
5. On completion, **append the code commit short SHA** for traceability: `- [x] F?-? — Description — ✅ \`abc1234f\``. If the step produced no code change (e.g., a verification or check step), use `✅ \`no-commit (<reason>)\`` instead of a SHA.
6. For `BLOCKED`, include brief reason and next action.
7. After code commit but before CI green + plan update, mark `🔒 STEP LOCKED`.

---
