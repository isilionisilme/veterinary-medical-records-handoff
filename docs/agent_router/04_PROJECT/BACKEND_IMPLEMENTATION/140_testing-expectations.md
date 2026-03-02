# Testing expectations 
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B7 (Testability Expectations).

## Unit tests (minimum)
- `document_status` derivation from latest run state
- persistence guard: cannot produce two `RUNNING` runs for the same document
- interpretation versioning: append-only + single active version per run
- error mapping: stable `error_code` and `details.reason`

## Integration tests (minimum)
- upload → background processing → review view
- reprocess creates queued run; scheduler starts oldest; no parallel running
- crash recovery transitions orphaned RUNNING to FAILED with `PROCESS_TERMINATED`
- missing artifact returns 410 with `ARTIFACT_MISSING`
