# Synthetic fixtures: visit detection

This folder contains synthetic raw-text fixtures and ground truth for multi-visit detection.

- Source file: `visit_detection_cases.json`
- Format: array of cases with `id`, `variant`, `text`, `expected_unique_visit_count`, and `expected_visit_dates`.
- `expected_visit_dates` are normalized `YYYY-MM-DD` values and represent unique visit dates.
