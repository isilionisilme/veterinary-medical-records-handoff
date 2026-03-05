<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 3. Commit Discipline

- Commits are **small** and scoped to a **single logical change**.
- A commit must **never** span multiple user stories.
- A change may be implemented through **multiple commits**.
- Commit history must remain **readable** to support reasoning and review.
- **Agent commit confirmation (hard rule):** Outside of an active plan with an explicit commit-task (`CT-*`), AI agents must present the staged files and proposed commit message to the user and wait for explicit confirmation before running `git commit`. Auto-commit is only permitted when executing a pre-approved commit-task in a plan.

### Commit Message Conventions

**User stories:**
- `Story <ID>: <short imperative description>`

**Technical work:**
- `<type>: <short imperative description>`
- Allowed types: `refactor`, `chore`, `ci`, `docs`, `test`, `build`, `fix`

Commit messages must be clear, specific, and written in **imperative form**.
Each commit should represent a **coherent logical step**.

---
