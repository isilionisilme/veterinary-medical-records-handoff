# US-08 — Edit structured data

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want to edit structured information extracted from a document so that it accurately reflects the original document.

**Acceptance Criteria**
- I can edit existing fields.
- I can create new fields.
- I can see which fields I have modified.
- Edits are immediate and local to the current document; no extra steps exist “to help the system”.
- Editing never blocks on confidence.
- Reprocessing resets edits by creating a new run and new machine output.

**Scope Clarification**
- This story covers veterinarian edits only.
- No reviewer workflow or schema evolution UI is introduced here.
- Editing applies to runs that have an active interpretation; this is expected for PDFs (see Technical Design Appendix E).

**Authoritative References**
- Tech: Versioning invariants (append-only interpretations): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix A3 + Appendix B2.4
- Tech: Field change log contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B2.5
- Tech: Edit endpoint contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3.1
- UX: Immediate local correction, no extra feedback steps: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Section 4
- Tech: Extraction/interpretation scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E

**Test Expectations**
- Each edit produces a new interpretation version and appends change-log entries.
- Editing is blocked only by the authoritative “active run” rule.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
