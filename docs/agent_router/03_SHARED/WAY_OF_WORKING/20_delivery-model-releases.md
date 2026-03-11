<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 7. Delivery Model

- Work is delivered using **vertical slices**, referred to as **releases**.
- A release represents a **complete increment of user-facing value**.
- A release may span multiple user stories across different epics.
- Each release must be **coherent, end-to-end, and meaningful** from a user perspective.
- Releases must NOT be isolated technical components.
- Always prefer completing a **smaller, well-defined** user story over partially implementing a larger one.

Each release must result in:

- A runnable and testable system state
- Clear, observable user-facing behavior
- Explicitly persisted data and state transitions
- Automated test coverage for the delivered functionality

---
