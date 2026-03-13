# Synthetic fixtures: owner_address

This folder contains synthetic raw-text fixtures and ground truth for `owner_address` extraction.

- Source file: `owner_address_cases.json`
- Format: object with metadata plus `cases` array containing `id`, `expected_owner_address`, and `text`.
- `expected_owner_address = null` means the extractor should not return an owner address value.
- Includes owner-labeled positives, contextual positives, abbreviation variants, multiline addresses, and clinic-address traps.
