<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 4. Step Eligibility Rule (Hard Rule)

**If the user expresses continuation intent (for example: "continue", "go", "let's go", "proceed", "resume"):**
Interpret continuation intent semantically, not as a literal command token.
1. Read the Execution Status and find the first `[ ]` (includes lines with `⏳ IN PROGRESS` or `🚫 BLOCKED` labels).
2. Apply the **decision table in §10** to determine the action (auto-chain, stop, or report).
3. If ambiguous: STOP and ask the user for clarification.

---

## 5. Continuation-Intent-Only Rule

**When the user expresses continuation intent, the agent executes ONLY what the plan dictates.** If the user's message includes additional instructions alongside the continuation request, the agent must:
1. **Pause and request scope confirmation** (do not silently ignore extra instructions).
2. Respond with two options: continue with the exact next plan step, or switch scope and ask the planning agent to update the plan and prompt.
3. Execute only after the user explicitly confirms one option.

### Task Chaining Policy

Defines how AI assistants must behave when executing chained plan steps.

#### Default behavior in chained mode

- Do **not** auto-fix failures by default when chaining steps.
- Record the failure with evidence (what failed, which files, and error output).
- Continue to the next step only if the failure is **non-blocking** for the current step.
- **STOP and escalate** on blocking conditions.

#### Blocking conditions (must STOP)

- A required preflight or CI gate failed and the step depends on it.
- Instructions contradict a canonical document or plan constraint.
- A dependency, permission, or required tool is missing.
- A security or data-loss risk is identified.
- An explicit hard-gate in the plan requires user review before proceeding.

#### Non-blocking failures (may continue)

- Pre-existing lint/test failures unrelated to the current step.
- Cosmetic or formatting issues that do not affect correctness.
- Warnings that do not block commit/push/PR gates.

#### Auto-fix allowance

- In **interactive single-task mode** (no plan), the assistant may attempt focused auto-fixes (max 2 attempts, scoped to the current change).
- In **chained-plan mode**, auto-fix is **not default**. The assistant documents the failure and lets the plan dictate the next action (continue, escalation, or explicit fix step).
- Auto-fixes must never go beyond the current change scope or introduce unrelated refactors.
- **Never bypass quality gates** (`--no-verify`, disabling tests/checks, weakening assertions) to force a pass.

#### Required output per step

Before handoff or auto-chain to the next step, each completed step must include:

- What changed (files and commits)
- Evidence (test output, CI status, and verification)
- Risks or open items
- Next-step handoff decision (continue, STOP, or handoff)

---
