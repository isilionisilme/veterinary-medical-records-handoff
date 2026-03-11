<!-- AUTO-GENERATED from canonical source: coding-standards.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Naming Conventions

> Git naming conventions (branches, commits, Pull Requests) are defined in
> [way-of-working.md §2–§5](../03-ops/way-of-working.md).

### API and endpoints

- Use clear, predictable REST conventions, for example:
  - `POST /documents/upload`
  - `GET /documents/{id}`
  - `GET /documents/{id}/download`
  - `GET /documents/{id}/text`
  - `PUT /documents/{id}/structured-data`

### Domain concepts and models

- Use explicit, domain-oriented names for core concepts, such as:
  - `Document`
  - `ProcessingStatus`
  - `ExtractedText`
  - `StructuredMedicalRecord`
  - `FieldEvidence`
  - `RecordRevision`

### Lifecycle states

- Lifecycle states must be enums using **UPPERCASE_SNAKE_CASE**, for example:
  - `UPLOADED`
  - `TEXT_EXTRACTED`
  - `STRUCTURED`
  - `READY_FOR_REVIEW`

### Persistence artifacts

- Use consistent, descriptive table names, such as:
  - `documents`
  - `document_status_history`
  - `document_text_artifacts`
  - `document_structured_artifacts`
  - `field_evidence`

---
