<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 10. Next-Step Message (Mandatory)

After each step, state next action using:

| Prompt exists? | Hard-gate? | Action |
|---|---|---|
| YES | NO | Auto-chain next step |
| YES | YES | Stop for user decision |
| NO | NO | Stop and request planning prompt |
| NO | YES | Stop for user decision |

---

## 11. Prompt Strategy

Resolution order: Prompt Queue -> Active Prompt -> stop and request planning update.

After executing a step, clear or refresh `Active Prompt` according to plan state.

---
