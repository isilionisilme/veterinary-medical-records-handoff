<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 8. Step Completion Integrity (Hard Rules)

### NO-BATCH
**Prohibited: batching unrelated plan steps in a single commit.**

Commits must remain coherent to the currently closed implementation step(s) and their validated scope.

### EVIDENCE BLOCK (Mandatory on Every Step Close)

Every step completion message **MUST** include:

```
📋 Evidence:
- Step: F?-?
- Code commit: <SHA>
- Plan commit: <SHA>
```

If any field is missing, the step is NOT considered completed.

---
