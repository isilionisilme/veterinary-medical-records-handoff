---
agent: agent
description: Resume execution of an active plan.
---

1. Trigger this runbook only on continuation intent (`continue`, `go`, `proceed`, `resume`, and semantic equivalents). Interpret continuation intent semantically, not as a literal token.
2. Read `Execution Status` and find the first `[ ]` step, including entries labeled `⏳ IN PROGRESS` or `🚫 BLOCKED`. If ambiguous, STOP and ask.
3. If the user message includes extra instructions in addition to continuation intent, pause and request scope confirmation. Offer exactly two choices: continue with the next plan step, or switch scope and ask the Planning agent to update the plan and prompt.
4. If the first open step is `🚫 BLOCKED`, report the blocker and STOP. If it is `⏳ IN PROGRESS`, resume that exact step; otherwise mark the first unchecked step `⏳ IN PROGRESS (<agent>, <date>)` before executing it.
5. Resolve the prompt source in this priority order: `Prompt Queue`, then `Active Prompt`, then STOP and ask the Planning agent to provide a prompt.
6. Apply the mandatory decision table before execution and again after step close:

| Prompt exists? | Hard-gate? | Action |
|---|---|---|
| YES | NO | **AUTO-CHAIN** — execute the next step directly. |
| YES | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |
| NO | NO | **STOP** — report: "No prompt exists for F?-?. The planning agent must write one." |
| NO | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |

7. Execute only the current step scope. Never mix scope between steps, batch unrelated work, or expand into opportunistic refactors.
8. In chained-plan mode, auto-fix is not the default. Record failures with evidence and continue only when the failure is non-blocking. STOP on blocking conditions: failed required gates, contradiction with canonical docs or plan constraints, missing dependency/permission/tool, security or data-loss risk, or any explicit hard-gate.
9. Non-blocking failures may be carried forward only when unrelated to the current step, cosmetic, or warning-only. Never bypass quality gates (`--no-verify`, disabled tests/checks, weakened assertions) to force a pass.
10. Run the per-task validation gate required by the selected execution mode, and respect the token-efficiency policy: load only current state before the step and summarize only delta, validation, risks, and next move at step close.
11. When closing the step, mark it `[x]` with `✅ <SHA>` or `✅ no-commit (<reason>)` as required by the plan conventions. Do not batch unrelated plan steps into a single commit.
12. Every completion message must include the mandatory evidence block:

```text
📋 Evidence:
- Step: F?-?
- Code commit: <SHA>
- Plan commit: <SHA>
```

13. Before handoff or auto-chain, report what changed, evidence, risks/open items, and the next-step decision (`continue`, `STOP`, or handoff).
