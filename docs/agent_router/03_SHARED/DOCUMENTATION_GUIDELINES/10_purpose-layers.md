<!-- AUTO-GENERATED from canonical source: documentation-guidelines.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## Purpose

Documentation is a **code quality requirement**. All contributors (human and AI) must treat documentation as part of the
deliverable and keep it consistent with the implementation. These guidelines are normative for documentation quality and
review decisions.

All user-facing written communication must be in **English** (documentation, pull request titles/descriptions, review
comments, ADRs, and release notes).

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
