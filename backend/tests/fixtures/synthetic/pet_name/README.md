# Synthetic fixtures: pet_name

This folder contains synthetic raw-text fixtures and ground truth for `pet_name` extraction.

- Source file: `pet_name_cases.json`
- Format: array of cases with `id`, `expected_pet_name`, and `text`.
- `expected_pet_name = null` means the extractor should not return a patient name.
