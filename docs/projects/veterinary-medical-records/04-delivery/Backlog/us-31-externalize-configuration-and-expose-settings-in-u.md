# US-31 — Externalize configuration and expose settings in UI

**User Story**
As an operator, I want key runtime configuration externalized and visible in-app so that I can verify system settings without reading source code.

**Acceptance Criteria**
- Relevant runtime configuration is loaded from an external configuration source/file instead of hardcoded values.
- The application exposes a read-only settings page showing selected effective configuration values in the web UI.
- The settings page clearly indicates which values are informational only and not editable in this story.
- If live edit/reload is not implemented, the UI explicitly states that changing values requires deployment or restart flow.

**Scope Clarification**
- Initial scope is read-only visibility in UI; inline editing and hot-reload are out of scope unless explicitly scheduled later.
- This story may require follow-up hardening for secrets redaction and environment-specific visibility controls.

**Authoritative References**
- Tech: Runtime contracts and operational constraints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md)
- UX: Settings readability and information architecture: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Effective externalized configuration values are rendered consistently in the read-only settings page.
- Out-of-scope edit/reload behavior is explicitly communicated to users.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
