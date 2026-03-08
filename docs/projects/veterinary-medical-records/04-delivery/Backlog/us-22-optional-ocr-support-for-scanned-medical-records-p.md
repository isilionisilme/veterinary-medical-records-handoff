# US-22 — Optional OCR support for scanned medical records (PDF/Image)

**User Story**
As a user, I want optional OCR support for scanned records so that documents without a usable text layer can still be reviewed when quality is sufficient.

**Acceptance Criteria**
- Given a scanned PDF/image without usable text layer, the system can run OCR and produce readable extracted text for review when OCR quality is sufficient.
- OCR is only applied when no usable text layer exists or text extraction fails the quality gate.
- If OCR is disabled, unavailable, or times out, processing fails explicitly (`EXTRACTION_FAILED` or `EXTRACTION_LOW_QUALITY`) and the document is not marked Ready for review.
- Logs indicate extraction path and OCR usage (including per-page behavior when available).

**Scope Clarification**
- This is a low-priority enhancement.
- Language default is Spanish (`es`) with future extension for language auto-detection.
- OCR should be applied at page level where possible (only failing pages), not necessarily entire-document OCR.
- This story depends on:
  - US-05 (processing pipeline),
  - US-06 (extracted text visibility),
  - US-20 (image support, when applicable).

**Authoritative References**
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Sections 3–4 + Appendix A2
- Tech: Endpoint surface and failure semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix B3/B3.2
- Tech: Step model and failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix C
- Tech: Extraction/OCR library decisions: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../../02-tech/technical-design.md) Appendix E

**Story-specific technical requirements**
- OCR output is treated as Unicode text and must not pass through PDF font-decoding logic.
- OCR execution must be bounded by configurable timeout/fail-fast rules.
- Final readiness still requires passing the extracted-text quality gate.

**Test Expectations**
- Fixture-based tests validate OCR path activation and quality-gate behavior on scanned inputs.
- Tests verify explicit failure behavior when OCR is unavailable/disabled or low-quality.
- Tests verify logs include extractor path and OCR usage signals.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../../shared/01-product/brand-guidelines.md).

---
