<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 8. Step Completion Integrity (Hard Rules)

1. A step counts as completed only when marked `[x]` (no runtime labels).
2. Required evidence must exist before closure when the plan/protocol asks for it.
3. If evidence is missing, keep step pending/blocked and do not proceed.
4. Chat todo projection must remain synchronized with plan checkboxes.

---
