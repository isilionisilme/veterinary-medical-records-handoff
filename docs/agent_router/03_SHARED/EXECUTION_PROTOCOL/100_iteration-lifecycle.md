<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 14. Iteration Lifecycle Protocol

```
Branch creation -> Plan steps -> Pre-PR history review -> PR (user-triggered) -> User merge approval -> Close-out
```

Rules:
1. Create/switch to plan branch before first step.
2. Execute steps until all `[x]` and validations pass.
3. Perform mandatory pre-PR history review.
4. Create/update PR only when requested by user.
5. Merge only with explicit user approval.
6. Close-out includes moving plan to `completed/` and final plan documentation commit.

---
