# Synthetic fixtures: microchip_id

This folder contains synthetic raw-text fixtures and ground truth for `microchip_id` extraction.

- Source file: `microchip_cases.json`
- Format: array of cases with `id`, `expected_microchip_id`, and `text`.
- `expected_microchip_id = null` means the extractor should not return a microchip value.
