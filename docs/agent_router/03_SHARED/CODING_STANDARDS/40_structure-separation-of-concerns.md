<!-- AUTO-GENERATED from canonical source: coding-standards.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Structure & Separation of Concerns

- Keep **domain logic independent** from frameworks and infrastructure.
- FastAPI routes must act as **thin adapters only**, limited to:
  - Input validation
  - Orchestration
  - Response mapping
- **Business rules must live in domain services**, never in API handlers.
- Access persistence, file storage, and external services **only through explicit interfaces or adapters**.

---
