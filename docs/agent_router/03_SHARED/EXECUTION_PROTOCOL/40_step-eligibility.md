<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 4. Step Eligibility Rule (Hard Rule)

On continuation intent:
1. Read `Execution Status`.
2. Pick first pending `[ ]` step (including labeled in-progress/blocked lines).
3. If next step belongs to another agent role, stop and hand off.
4. Apply decision table from §10.

---

## 5. Continuation-Intent-Only Rule

If continuation intent includes extra scope requests:
1. Pause execution.
2. Ask user to choose: continue plan as-is or update plan scope first.
3. Resume only after explicit choice.

---
