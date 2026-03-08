# US-10 — Change document language and reprocess

**User Story**
As a veterinarian, I want to change the detected language of a document so that it can be reprocessed correctly if automatic detection was wrong.

**Acceptance Criteria**
- The user can see the language used for the latest processing attempt.
- The user can set or clear a language override.
- The user can trigger reprocessing after changing the override.
- The system clearly indicates which language was used for each run.
- Language override does not block review or editing and affects only subsequent runs.

**Scope Clarification**
- Changing the language does not automatically reprocess.

**Authoritative References**
- Tech: Language detection rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E
- Tech: Language override endpoint + rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.1
- Tech: Run persistence of `language_used`: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B2.2

**Test Expectations**
- New runs created after setting an override persist the overridden `language_used`.
- Existing runs remain unchanged.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
