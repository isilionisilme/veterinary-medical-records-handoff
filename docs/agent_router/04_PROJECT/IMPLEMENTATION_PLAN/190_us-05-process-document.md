# US-05 — Process document

**User Story**
As a veterinarian, I want uploaded PDF documents to be processed automatically so that I can review the system’s interpretation without changing my workflow.

**Acceptance Criteria**
- Processing starts automatically after upload and is non-blocking (PDF).
- I can see when a document is processing and when it completes.
- If processing fails or times out, failure category is visible.
- I can manually reprocess a document at any time.
- Each processing attempt is traceable and does not overwrite prior runs/artifacts.

**Scope Clarification**
- Processing follows the execution model defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B1.
- This story does not introduce external queues or worker infrastructure; processing runs in-process and is non-blocking.
- This story does not require OCR for scanned PDFs; extraction relies on embedded text when available.
- This story does not execute multiple runs concurrently for the same document.

**Authoritative References**
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix C
- Tech: Reprocess endpoint and idempotency rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B3 + Appendix B4
- Tech: Extraction library scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix E

**Test Expectations**
- Upload triggers background processing without blocking the request.
- Reprocess creates a new run and preserves prior runs/artifacts.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../TECHNICAL_DESIGN/00_entry.md) Appendix B7.
- Follow UX guidance from [docs/shared/01-product/ux-guidelines.md](../../03_SHARED/UX_GUIDELINES/00_entry.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../UX_DESIGN/00_entry.md), if applicable.
- Apply [docs/shared/01-product/brand-guidelines.md](../../03_SHARED/BRAND_GUIDELINES/00_entry.md), if applicable.

---
