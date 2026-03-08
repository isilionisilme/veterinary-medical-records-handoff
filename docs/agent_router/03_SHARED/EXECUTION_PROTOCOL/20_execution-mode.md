<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 1. Semi-Unattended Execution (Default Mode)

Default behavior is semi-unattended execution controlled by plan steps and hard-gates.

### Mandatory Plan-Start Choices (before Step 1)

Before executing the first step of any plan, collect and record in plan metadata:

1. Execution worktree.
2. CI mode.
3. Automation mode:
   - `Supervisado`: commit manual, push manual, pause at hard-gates.
   - `Semiautomatico`: commit automatic allowed, push manual, pause at hard-gates.
   - `Automatico`: commit automatic allowed, push manual, pause at hard-gates (including final pre-PR gate).

If UI supports option selectors, use selector UI. If not, use textual fallback.

---
