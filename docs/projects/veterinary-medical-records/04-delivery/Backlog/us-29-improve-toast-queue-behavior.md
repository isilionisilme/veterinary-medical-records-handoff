# US-29 — Improve toast queue behavior

**User Story**
As a user, I want notification toasts to behave predictably when multiple events happen so that messages are readable and not lost.

**Acceptance Criteria**
- New toasts are enqueued without resetting timers of already visible toasts.
- At most three toasts are visible simultaneously.
- When a fourth toast arrives, the oldest visible toast is removed first.
- Toasts remain accessible (announced for assistive technologies and dismissible via keyboard).

**Scope Clarification**
- Already partially covered by US-21 (upload feedback states), but this story defines global queue/timing behavior for all toast notifications.

**Authoritative References**
- UX: Notification feedback and accessibility patterns: [`docs/shared/01-product/ux-guidelines.md`](../../../../shared/01-product/ux-guidelines.md)
- UX: Project-wide interaction consistency: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Rapid successive events preserve per-toast duration behavior and queue ordering.
- Toast visibility limit and eviction order remain stable across screen sizes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
