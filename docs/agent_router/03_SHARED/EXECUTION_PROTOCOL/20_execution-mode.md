<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 1. Execution Mode Defaults

Unless the active plan records a different selection in `**Execution Mode:**`, the default execution mode is **Semi-supervised**. After completing the current task according to the active mode and closure rules, the agent applies the **decision table in §10** to determine whether to chain or stop.

### Single-Chat Execution Rule (Hard Rule)

Keep execution in the current chat by default.

The agent may recommend switching chat only when:
1. expected token-efficiency benefit is significant, or
2. a hard capability blocker requires another agent/model.

In both cases, the agent MUST explain the reason briefly and wait for explicit user decision.

**Safety limit:** if the agent detects context exhaustion (truncated responses, state loss), it must stop at the current step, complete it cleanly (full SCOPE BOUNDARY) and generate the handoff.

---
