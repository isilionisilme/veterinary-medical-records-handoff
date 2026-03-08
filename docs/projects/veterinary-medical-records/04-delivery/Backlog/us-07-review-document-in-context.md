# US-07 — Review document in context

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to review the system’s interpretation while viewing the original document so that I can verify it.

**Acceptance Criteria**
- I can see structured extracted data and the original document together.
- Confidence is visible and non-blocking (guides attention, not decisions).
- Evidence is available per field as page + snippet, accessible with minimal interaction.
- Highlighting in the document is progressive enhancement: review remains usable if highlighting fails.
- I can optionally view raw extracted text from the review context.
- Reviewer/governance concepts are not exposed to veterinarians.

**Scope Clarification**
- No approval/gating flows are introduced.
- This story does not require exact coordinate evidence.
- Review requires a completed run with an active interpretation; this is expected for PDFs (see Technical Design Appendix E).

**Authoritative References**
- UX: Review flow + confidence meaning: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md) Sections 2–4
- Tech: Review endpoint semantics (latest completed run): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3.1
- Tech: Structured interpretation schema + evidence model: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix D + D6
- Tech: Extraction/interpretation scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E

**Test Expectations**
- Review uses the latest completed run rules.
- Lack of a completed run yields the normative conflict behavior.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
