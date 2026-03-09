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
docs/projects/veterinary-medical-records/03-ops/
└── plan-execution-protocol.md      ← YOU ARE HERE

docs/projects/veterinary-medical-records/04-delivery/plans/
├── PLAN_<date>_<slug>/             ← Active plan folder
│   ├── PLAN_<date>_<slug>.md       ← Active plan source of truth (matches folder name)
│   └── PR-*.md                     ← Optional per-PR annex
└── completed/
    └── PLAN_<date>_<slug>/         ← Completed plan folder (same file names)
```

**Active plan file:** For new plans, the agent attaches `plans/<plan-folder>/PLAN_<date>_<slug>.md` (matching the folder name) when executing a continuation-intent request (for example: "continue", "go", "let's go", "proceed", "resume").
For legacy plans, `PLAN_*.md` remains accepted during transition.
The active plan source file contains: Execution Status (checkboxes), Prompt Queue, Active Prompt, and iteration-specific context.

---
