<!-- AUTO-GENERATED from canonical source: documentation-guidelines.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## In-Code Documentation Rules

### When to add docstrings

Add docstrings to:

- Public modules
- Domain and application services
- Public functions and methods
- Non-trivial orchestration logic
- Integration and adapter boundaries

### Docstring content

Docstrings must include when relevant:

- Purpose and responsibility
- Inputs and outputs
- Requirements and invariants
- Error conditions and exceptions
- Side effects and state changes

### Docstring style

- Use **Google-style** docstrings.
- Follow **PEP 257** structure.
- First line: short summary sentence.
- Then structured sections when applicable: `Args`, `Returns`, `Raises`, `Side Effects`, `Notes`.

### When NOT to add docstrings

Do NOT add docstrings for:

- Trivial helpers
- Self-explanatory one-liners
- Simple pass-through logic
- Code already fully clear from names and types

---

## Types and Contracts

- All public functions and methods must include **type hints**.
- Treat **type annotations, signatures, and schemas** as part of the documentation contract.
- Ensure all public interfaces include explicit types or schemas when supported.
- Do **not** duplicate type information in docstrings when already explicit in signatures.

---
