<!-- AUTO-GENERATED from canonical source: documentation-guidelines.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Architecture and Design Documentation

Architecture and structural rules must be documented outside the code in canonical documents (not inline).

AI assistants must **NOT** invent or modify architecture or design documents unless explicitly instructed.

When explicitly requested, record non-obvious technical decisions as short ADR-style notes including:

- Decision
- Rationale
- Tradeoffs

---

## Commenting Rules

Comments must explain:

- **Why** a decision was made
- **Why** alternatives were rejected
- Domain assumptions
- Non-obvious requirements

Comments must **NOT**:

- Repeat what the code literally does
- Describe syntax-level behavior
- Drift from the implementation

Outdated comments must be removed or updated in the same change.

---
