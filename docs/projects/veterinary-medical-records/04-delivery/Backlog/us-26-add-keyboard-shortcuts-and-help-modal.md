# US-26 — Add keyboard shortcuts and help modal

**User Story**
As a user, I want keyboard shortcuts for frequent actions so that I can work faster, and I want a quick way to discover them.

**Acceptance Criteria**
- A defined shortcut set exists for frequent actions and excludes destructive actions by default unless confirmed.
- Pressing `?` opens a shortcuts help modal listing available shortcuts by context.
- Shortcuts do not trigger while typing in inputs/textareas or when they conflict with PDF viewer interactions.
- The modal is keyboard accessible (open, focus trap, close with `Escape`, and return focus to trigger context).

**Scope Clarification**
- This story does not require user-customizable shortcut remapping.

**Authoritative References**
- UX: Keyboard accessibility and modal behavior: [`docs/shared/01-product/ux-guidelines.md`](../../../../shared/01-product/ux-guidelines.md)
- UX: Project interaction patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Frequent actions can be executed through shortcuts outside typing contexts.
- Shortcut help modal is discoverable and keyboard-operable.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
