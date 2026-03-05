<!-- AUTO-GENERATED from canonical source: coding-standards.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Error Handling & Observability

### Error classification

- Classify errors clearly:
  - User-facing errors
  - Internal/system errors
- **Fail explicitly and early** when inputs or states are invalid.
- Log key operations and state transitions using **correlation identifiers**.

### Observability & metrics

- Key pipeline stages must be **measurable** (e.g., processing time per stage).
- Failures must be **attributable to specific workflow stages**.

---
