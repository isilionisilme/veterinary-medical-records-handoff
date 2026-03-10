<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Purpose

This protocol governs how AI agents execute plan steps in a structured, auditable manner using the plan's configured execution mode. It defines execution rules, completion integrity, CI verification, handoff conventions, and the full iteration lifecycle.

### Role taxonomy (availability-safe)

- **Planning agent**: owns plan authoring/updates, hard-gate decisions, and prompt preparation.
- **Execution agent**: owns implementation steps from pre-written prompts.

All routing and handoff rules in this document MUST use role labels (not model or vendor names).

AI assistants must stop and report the blocker when a protocol step cannot be completed as defined.

---

## File Structure

```
docs/projects/veterinary-medical-records/03-ops/
└── plan-execution-protocol.md      ← YOU ARE HERE

docs/projects/veterinary-medical-records/04-delivery/plans/
├── PLAN_<YYYY-MM-DD>_<SLUG>.md     ← Active plan (single flat file)
└── completed/
    └── PLAN_<YYYY-MM-DD>_<SLUG>.md ← Completed plan
```

**Active plan file:** For new plans, the agent attaches `plans/PLAN_<YYYY-MM-DD>_<SLUG>.md` when executing a continuation-intent request (for example: "continue", "go", "let's go", "proceed", "resume").
New plans are single flat files — no plan folders, no annex files. Legacy folder-based active plans remain accepted during migration while any active branch still resolves to `plans/<plan-folder>/PLAN_<YYYY-MM-DD>_<SLUG>.md`. Active-plan resolution searches for a matching `PLAN_*.md` outside `completed/`, regardless of nesting.
See [`plan-creation.md` §1](plan-creation.md#1-how-to-create-a-plan) for naming and location conventions.
The active plan source file contains: Execution Status (checkboxes), Prompt Queue, Active Prompt, and iteration-specific context.

---
