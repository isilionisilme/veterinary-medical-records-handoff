> [!WARNING]
> **Fictional document.** I created these guidelines as a design context for developing the application. They do **not** meant to represent the actual guidelines of Barkibu.

---

# Documentation Guidelines

## Purpose

Documentation is a **code quality requirement**. All contributors (human and AI) must treat documentation as part of the deliverable and keep it consistent with the implementation. These guidelines are normative for documentation quality and review decisions.

All user-facing written communication must be in **English** (documentation, pull request titles/descriptions, review comments, ADRs, and release notes).

Document:

- Intent and responsibility
- Contracts and schemas
- Design decisions and tradeoffs

Do **not** restate obvious code behavior.

Documentation is reviewed together with the code.

---

## Documentation Layers

The project uses three complementary documentation layers. All must stay consistent:

1. **In-code documentation** — docstrings and type annotations
2. **API documentation** — auto-generated from FastAPI + schemas
3. **Repository and architecture documentation** — canonical docs, ADR-style notes when explicitly requested

---

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

## API Documentation Rules

For every HTTP endpoint, ensure:

- Route includes **summary and description**.
- Explicit **request and response models** are defined.
- Schema fields include **meaningful descriptions**.

API documentation is generated automatically from:

- Route metadata (summaries, descriptions)
- Model/schema field descriptions
- Type annotations

This auto-generated API documentation is considered part of the deliverable.

---

## Public Interface Documentation

For any public interface (API, service, adapter, or module boundary):

- Add a short summary.
- Add a behavior description if not obvious.
- Document input/output contracts.
- Add parameter/field descriptions where they add clarity.
- Prefer metadata compatible with automatic documentation generators when available.

---

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

## When Documentation Must Be Updated

When a change modifies any of the following, the corresponding documentation must be updated **in the same change set**:

- Public behavior
- Contracts
- Data schemas
- Module responsibilities

**A change is not complete if implementation and documentation diverge.**

---

## Change Classification

Every documentation change falls into one of three categories:

| Code  | Classification | Definition                                                                        |
| ----- | -------------- | --------------------------------------------------------------------------------- |
| **R** | Rule change    | Affects behavior or process. Must be propagated to the owning canonical document. |
| **C** | Clarification  | No behavior change. Improves readability or precision.                            |
| **N** | Navigation     | Structure, links, or organization changes only.                                   |

Mixed classification is allowed within one file (e.g., a change that both clarifies wording and modifies a rule).

---

## Documentation Verification Checklist

Before considering a documentation change complete, verify:

- [ ] Links are not broken.
- [ ] Markdown fences are balanced.
- [ ] No duplicated rules across documents.
- [ ] Documentation and implementation are consistent.
- [ ] Docstrings match current behavior of the code they describe.
- [ ] No outdated comments remain.