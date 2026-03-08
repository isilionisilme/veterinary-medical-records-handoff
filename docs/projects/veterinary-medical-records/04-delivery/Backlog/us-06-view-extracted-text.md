# US-06 — View extracted text

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to view the raw text extracted from a document so that I understand what the system has read before any structured interpretation is applied.

**Acceptance Criteria**
- I can view extracted raw text for a completed run (expected for PDFs).
- The UI distinguishes “not ready yet” vs “not available (e.g., extraction failed)” without blocking workflow.
- Raw text is hidden by default and shown on demand in no more than one interaction.
- Raw text is clearly framed as an intermediate artifact, not ground truth.

**Scope Clarification**
- This story is read-only.

**Authoritative References**
- Tech: Raw-text artifact endpoint + “not ready vs not available” semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- Tech: Extraction + language detection libraries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E

**Test Expectations**
- Raw text retrieval behaves correctly across run states and extraction failures.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
