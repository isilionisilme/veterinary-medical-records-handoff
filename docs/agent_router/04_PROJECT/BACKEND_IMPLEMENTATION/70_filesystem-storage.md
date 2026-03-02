# Filesystem storage

## Deterministic paths (authoritative)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B5 (Filesystem Management Rules).

Store the original upload under:
- `/storage/{document_id}/original{ext}`

Where `ext` is derived from the normalized file type.

## Run-scoped artifacts (implementation)
Define deterministic run artifact paths (minimum required):
- `RAW_TEXT`: `/storage/{document_id}/runs/{run_id}/raw-text.txt`

Note:
- Step artifacts (`artifact_type = STEP_STATUS`) are DB-resident JSON; no filesystem path is required for step tracking.

## Atomicity rules
- Writes must be atomic (write temp → rename).
- Upload endpoint must avoid partial persistence:
  - no DB row without filesystem artifact on success
  - no filesystem artifact without DB row on success

Implementation guidance (paired DB + filesystem writes):
1) Pre-generate IDs needed to compute deterministic final paths (e.g., `document_id`, `run_id`).
2) Write content to a temp file adjacent to the final path (`.tmp`), flush, `fsync`, then `os.replace` temp → final.
3) Wrap DB writes in a transaction and only `COMMIT` after the final filesystem rename succeeds.
4) On any failure, best-effort cleanup:
   - delete temp file,
   - roll back DB transaction,
   - if a final file was created but DB commit failed, delete the final file best-effort.
5) Never return success unless both DB state and final filesystem paths are present.

Environment knobs (current codebase):
- Storage root override: `VET_RECORDS_STORAGE_PATH`
- DB path override: `VET_RECORDS_DB_PATH`

## Missing artifacts
If DB references an artifact but the filesystem is missing, return:
- `410 Gone` with `error_code = ARTIFACT_MISSING`

Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3.2 + Appendix B5.
