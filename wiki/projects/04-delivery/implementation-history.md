# Implementation History

> Incremental delivery timeline organized by release. Each release delivers a coherent capability to end users or development teams.
>
> For the full release plan with user stories and acceptance criteria, see [implementation-plan.md](implementation-plan).
> For known trade-offs and deferred items, see [future-improvements.md](future-improvements).

---

## Current state

| Metric | Value |
|--------|-------|
| Backend tests | ~820 (>90% coverage, ≥85% enforced) |
| Frontend tests | 356 across 56 spec files (~87% coverage, ≥80% enforced) |
| E2E tests | ~80 across 21 Playwright specs |
| CI pipeline | 13 jobs (lint, test, coverage gates, security audit, E2E) |
| Lint issues | 0 (ESLint + Prettier + ruff enforced in CI and pre-commit) |
| Accessibility | axe-core WCAG 2.1 AA: 0 critical violations |
| Architecture | Hexagonal backend, modular frontend, all components < 300 LOC |

---

## Releases delivered

### For the veterinarian (end user)

| Release | Goal | Quality evidence |
|---------|------|------------------|
| 1 — Document upload & access | Allow users to upload documents and access them reliably, establishing a stable and observable foundation | File-type validation, persistent storage, status lifecycle |
| 2 — Automatic processing | Automatically process uploaded PDF documents in a non-blocking way, with full traceability and safe reprocessing | Append-only processing history, classified error states |
| 3 — Extraction transparency | Make visible and explainable what the system has read, before any interpretation is applied | Progressive disclosure — available on demand, never in the way |
| 4 — Assisted review in context | Enable veterinarians to review the system's interpretation in context, side-by-side with the original document | Per-field confidence scores ([ADR](ADR-confidence-scoring-algorithm)), search & filters, resizable panels |
| 5 — Editing & corrections | Allow veterinarians to correct structured data naturally, while capturing append-only correction signals — without changing their workflow | Top-5 candidate suggestions, edit audit trail, confidence tooltips |
| 6 — Visit-grouped review | See extracted data organized by veterinary visit, matching the clinical document structure | Deterministic visit grouping driven by schema contract |
| 7 — Safe editing experience | Make field editing robust and predictable, preventing data loss and ensuring correct modification semantics | Unsaved-change warnings, per-field reset, confidence auto-refresh |
| 8 — Evidence navigation | Enable precise evidence inspection and text search within the document viewer | Direct traceability from structured data to source evidence |
| 9 — Better extraction coverage | Improve extraction coverage, visit detection, clinical utility, and language support | Improved clinical utility for multi-visit records |
| 10 — UX polish & upload ergonomics | Improve document interaction ergonomics and visual polish without changing core workflow semantics | Drag-and-drop, folder upload, reduced clicks |
| 15 — Extraction field expansion | Expand extraction coverage to all critical patient and clinic fields via the golden loop pattern, ensuring each field has dedicated fixtures, benchmark tests, labeled patterns, and normalization | 100% exact match on synthetic benchmarks (pet name 15/15, clinic 11/11) |
| 16 — Multi-visit detection | Detect all visits in a medical document from raw text boundaries and assign clinical data to each specific visit, with observability for debugging assignment problems | Boundary detection from raw text, not just explicit date headers |

### For the developer and QA team

| Release | Goal | Quality evidence |
|---------|------|------------------|
| 17 — Engineering quality | Establish modular architecture, comprehensive test coverage, production hardening, local validation pipelines, canonical documentation, and consistent project governance conventions (12/14 items) | 13 CI jobs, coverage thresholds enforced, pre-commit hooks |
| 19 — Critical architecture remediation | Address the highest-impact architecture findings: decompose God Modules, add CI complexity gates, and close critical documentation gaps | CI complexity gates, hexagonal dependency enforcement |
| 20 — Architecture hardening | Fix remaining hexagonal violations, improve code hygiene, add missing ADRs, close documentation gaps, and implement production security improvements (2/11 items) | In progress |

### Conscious trade-offs (not yet implemented)

| Release | Deferred capability | Rationale |
|---------|-------------------|-----------|
| 11 | Provide comprehensive in-app help, externalize UI texts for editing/translation, and add multilingual UI support | Not required for core veterinary review workflow |
| 12 | Expand format support beyond PDF and add optional OCR for scanned documents | PDF covers the primary use case for medical records |
| 13 | Introduce reviewer-facing governance for global schema evolution, fully isolated from veterinarian workflows | Designed for multi-user production; out of scope for current deployment model |
| 14 | Investigate field standardization opportunities and define operational policies for production readiness | Standards research and production DB policies — future production concern |
| 18 | Enhance the frontend to provide evaluators with clear, informative processing history | Current processing history is functional |
| 21 | Complete remaining architecture improvements: capacity planning, content validation, frontend state management, runtime observability, operational runbooks | Future operational maturity — not blocking current delivery |

> Detailed rationale for each trade-off in [future-improvements.md](future-improvements).
