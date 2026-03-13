# Golden raw_text fixtures (2-doc mini dataset)

These fixtures are a regression mini dataset built from the only two real source documents currently available in this repository.

## Why minimal excerpts

- Keep fixtures stable and CI-friendly.
- Avoid carrying full raw text payloads in tests.
- Preserve only the patterns needed for extraction heuristics and regressions.

## Fixture coverage

- `docA.txt`
  - Covers chip-like numeric content (`00023035139`) and date-like strings.
  - Includes owner-context mentions (`PROPIETARIA`) and vet-responsible lines.

- `docB.txt`
  - Covers owner name + address adjacency (`NOMBRE DEMO` + `C/ CALLE DEMO...`) used by owner trimming tests.
  - Covers date-like and microchip-like numeric patterns.
  - Includes a `Vet` line for vet-context handling.

- `docB_multi_visit_rich.txt`
  - Synthetic multi-visit text with two visit segments (`11/02/2026` and `18/02/2026`).
  - Contains rich clinical language (symptoms, diagnosis, medication, procedure) for staged per-visit extraction rollout.
  - Used as baseline fixture to assert visits are detected but start with empty `fields` before phase-specific extraction logic is enabled.