<!-- AUTO-GENERATED from canonical source: documentation-guidelines.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

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
- [ ] All rule changes (**R**) are propagated to the owning canonical document.
- [ ] Documentation and implementation are consistent.
- [ ] Docstrings match current behavior of the code they describe.
- [ ] No outdated comments remain.
