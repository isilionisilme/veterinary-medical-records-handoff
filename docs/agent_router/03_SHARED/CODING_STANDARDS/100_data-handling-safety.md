<!-- AUTO-GENERATED from canonical source: coding-standards.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Data Handling & Safety

- Treat **external inputs as untrusted by default**.
- Validate file **type and size before processing**.
- Store **raw files outside the database**; persist only references.
- Persist metadata, states, structured outputs, and audit information in the database.

---
