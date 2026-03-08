<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 10. Next-Step Message (Mandatory)

On completing a step, the agent ALWAYS tells the user the next move with concrete instructions.

**Decision table:**

| Prompt exists? | Hard-gate? | Action |
|---|---|---|
| YES | NO | **AUTO-CHAIN** — execute the next step directly. |
| YES | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |
| NO | NO | **STOP** — report: "No prompt exists for F?-?. The planning agent must write one." |
| NO | YES (🚧) | **STOP** — report: "The next step is a hard-gate requiring user decision." |

---

## 11. Prompt Strategy

For prompt types and creation lifecycle, see [`plan-creation.md` §6 - Prompt Strategy](plan-creation.md#6-prompt-strategy).

### Resolution Priority (Execution-Time)

Prompt Queue -> Active Prompt -> STOP (ask the planning agent).

### Prompt Consumption (Execution Agent)

| Operation | Who | When |
|---|---|---|
| **Consume** | Execution agent | On step start, per resolution priority in this section |
| **Clean** | Execution agent | After step execution, clear `## Active Prompt` section content |

### Routing for Continuation Intent

Follow the **Step Eligibility Rule (§4)** to determine and execute the next step. After execution, run STEP F of SCOPE BOUNDARY.

---
