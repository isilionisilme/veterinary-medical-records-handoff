# Synthetic fixtures: dob (date of birth)

This folder contains synthetic raw-text fixtures and ground truth for `dob` extraction.

- Source file: `dob_cases.json`
- Format: array of cases with `id`, `expected_dob`, and `text`.
- `expected_dob = null` means the extractor should not return a date of birth value.
