<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Purpose

This protocol governs how AI agents execute plan steps in a structured, auditable, and semi-unattended manner. It defines execution rules, completion integrity, CI verification, handoff conventions, and the full iteration lifecycle.

### Role taxonomy (availability-safe)

- **Planning agent**: owns plan authoring/updates, hard-gate decisions, and prompt preparation.
- **Execution agent**: owns implementation steps from pre-written prompts.

All routing and handoff rules in this document MUST use role labels (not model or vendor names).

AI assistants must stop and report the blocker when a protocol step cannot be completed as defined.

---

## File Structure

```
docs/projects/veterinary-medical-records/04-delivery/plans/
├── plan-execution-protocol.md      ← YOU ARE HERE
├── IMPLEMENTATION_HISTORY.md       ← Timeline of all iterations
├── PLAN_<date>_<slug>.md           ← Active iteration plans
├── completed/                      ← Finished iterations
│   └── COMPLETED_<date>_<slug>.md
```

**Active plan file:** The agent attaches the relevant `PLAN_*.md` file when executing a continuation-intent request (for example: "continue", "go", "let's go", "proceed", "resume").
Each plan file contains: Execution Status (checkboxes), Prompt Queue, Active Prompt, and iteration-specific context.

---
