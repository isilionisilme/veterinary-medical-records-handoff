# US-30 — Change application UI language (multilingual UI)

**User Story**
As a user, I want to change the application display language so that I can use the interface in my preferred language.

**Acceptance Criteria**
- I can select the UI language from supported options in the application settings/navigation.
- Changing UI language updates visible interface text without altering stored document content or processing behavior.
- The selected UI language persists for subsequent sessions on the same account/device context.
- Language selector and translated UI remain accessible and usable on mobile and desktop.

**Scope Clarification**
- Already partially covered by US-10 only for document processing language; this story is independent and strictly about UI internationalization.
- This story does not add or change document interpretation language behavior.

**Authoritative References**
- UX: Product language and interaction patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)
- Tech: Existing document-language processing boundaries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E + Appendix B3/B3.1

**Test Expectations**
- UI text changes according to selected language while processing behavior remains unchanged.
- Language preference persists according to the selected persistence strategy.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
