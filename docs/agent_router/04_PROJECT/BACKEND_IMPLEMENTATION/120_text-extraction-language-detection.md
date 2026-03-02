# Text extraction + language detection 

## PDF extraction
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) (PyMuPDF extraction).

Implementation note: if extracted text is empty/near-empty, the run may fail as `EXTRACTION_FAILED` (per Technical Design step failure mapping; Appendix C3).

## Language detection
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) (langdetect selection and rationale).

Implementation note: if detection fails, set `language_used = "unknown"` and continue best-effort.
