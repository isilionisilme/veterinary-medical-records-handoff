# US-25 — Upload a folder of PDFs (bulk)

**User Story**
As a user, I want to upload an entire folder of PDFs so that I can ingest many records quickly.

**Acceptance Criteria**
- The UI offers a folder selection flow for bulk upload where supported by the browser/platform.
- Only supported PDFs inside the selected folder are queued; unsupported files are skipped with clear feedback.
- When folder selection is unsupported, the UI presents a clear multi-file upload fallback.
- Progress and completion feedback summarize total selected, uploaded, skipped, and failed items.

**Scope Clarification**
- Already partially covered by US-21 (single upload UX), but this story adds folder-based bulk ingestion.
- Recursive subfolder behavior must be explicitly defined during implementation and reflected in UX copy.

**Authoritative References**
- Tech: Upload validation and failure behavior: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- UX: Bulk upload feedback and fallback behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../01-product/ux-design.md)

**Test Expectations**
- Supported environments can upload a folder of PDFs end-to-end.
- Unsupported environments fall back to multi-file selection without blocking upload.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
