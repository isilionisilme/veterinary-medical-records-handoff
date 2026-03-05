<!-- AUTO-GENERATED from canonical source: coding-standards.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## State Management & Workflow Safety

- Model **lifecycle states explicitly** and persist them.
- State transitions must be **deterministic and safe to retry**.
- Every state change must be **observable and auditable**.

---
