<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 9. Format-Before-Commit (Mandatory)

Before every commit:
1. Run formatter/lint/preflight for changed scope (L1 minimum).
2. Fix blocking issues.
3. Commit only after checks pass or user explicitly approves an allowed exception.

Local minimum gates:
- Before commit: `scripts/ci/test-L1.ps1 -BaseRef HEAD`
- Before push: `scripts/ci/test-L2.ps1 -BaseRef main`
- Before PR create/update: `scripts/ci/test-L3.ps1 -BaseRef main`

---
