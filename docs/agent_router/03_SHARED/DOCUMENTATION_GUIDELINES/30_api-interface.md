<!-- AUTO-GENERATED from canonical source: documentation-guidelines.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## API Documentation Rules

For every HTTP endpoint, ensure:

- Route includes **summary and description**.
- Explicit **request and response models** are defined.
- Schema fields include **meaningful descriptions**.

API documentation is generated via OpenAPI/Swagger from:

- FastAPI route metadata
- Pydantic model field descriptions
- Type annotations

This auto-generated API documentation is considered part of the deliverable.

---

## Public Interface Documentation

For any public interface (API, service, adapter, or module boundary):

- Add a short summary.
- Add a behavior description if not obvious.
- Document input/output contracts.
- Add parameter/field descriptions where they add clarity.
- Prefer metadata compatible with automatic documentation generators when available.

---
