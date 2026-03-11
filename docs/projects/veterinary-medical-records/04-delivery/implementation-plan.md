---
title: "Implementation Plan"
type: reference
status: active
audience: contributor
last-updated: 2026-03-08
---

# Note for readers:

**Breadcrumbs:** [Docs](../../../README.md) / [Projects](../../README.md) / veterinary-medical-records / 04-delivery

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [Purpose](#purpose)
  - [How to use this document](#how-to-use-this-document)
  - [Contract boundary (non-negotiable)](#contract-boundary-non-negotiable)
  - [Scope](#scope)
  - [Execution Rules](#execution-rules)
- [Implementation Plan](#implementation-plan)
  - [Release 1 — Document upload & access](#release-1--document-upload--access)
    - [Goal](#goal)
    - [Scope](#scope-1)
    - [User Stories (in order)](#user-stories-in-order)
  - [Release 2 — Automatic processing & traceability](#release-2--automatic-processing--traceability)
    - [Goal](#goal-1)
    - [Scope](#scope-2)
    - [Format support note](#format-support-note)
    - [User Stories (in order)](#user-stories-in-order-1)
  - [Release 3 — Extraction transparency (trust & debuggability)](#release-3--extraction-transparency-trust--debuggability)
    - [Goal](#goal-2)
    - [Scope](#scope-3)
    - [User Stories (in order)](#user-stories-in-order-2)
  - [Release 4 — Assisted review in context (high value / higher risk)](#release-4--assisted-review-in-context-high-value--higher-risk)
    - [Goal](#goal-3)
    - [Scope](#scope-4)
    - [User Stories (in order)](#user-stories-in-order-3)
  - [Release 5 — Editing & learning signals (human corrections)](#release-5--editing--learning-signals-human-corrections)
    - [Goal](#goal-4)
    - [Scope](#scope-5)
    - [User Stories (in order)](#user-stories-in-order-4)
  - [Release 6 — Explicit overrides & workflow closure](#release-6--explicit-overrides--workflow-closure)
    - [Goal](#goal-5)
    - [Scope](#scope-6)
    - [User Stories (in order)](#user-stories-in-order-5)
  - [Release 7 — Edit workflow hardening](#release-7--edit-workflow-hardening)
    - [Goal](#goal-6)
    - [Scope](#scope-7)
    - [User Stories (in order)](#user-stories-in-order-6)
  - [Release 8 — Evidence navigation & document interaction](#release-8--evidence-navigation--document-interaction)
    - [Goal](#goal-7)
    - [Scope](#scope-8)
    - [User Stories (in order)](#user-stories-in-order-7)
  - [Release 9 — Extraction quality & language](#release-9--extraction-quality--language)
    - [Goal](#goal-8)
    - [Scope](#scope-9)
    - [User Stories (in order)](#user-stories-in-order-8)
  - [Release 10 — UX polish & upload ergonomics](#release-10--ux-polish--upload-ergonomics)
    - [Goal](#goal-9)
    - [Scope](#scope-10)
    - [User Stories (in order)](#user-stories-in-order-9)
  - [Release 11 — Help, content externalization & i18n](#release-11--help-content-externalization--i18n)
    - [Goal](#goal-10)
    - [Scope](#scope-11)
    - [User Stories (in order)](#user-stories-in-order-10)
  - [Release 12 — Additional formats & OCR](#release-12--additional-formats--ocr)
    - [Goal](#goal-11)
    - [Scope](#scope-12)
    - [User Stories (in order)](#user-stories-in-order-11)
  - [Release 13 — Schema evolution (isolated reviewer workflows)](#release-13--schema-evolution-isolated-reviewer-workflows)
    - [Goal](#goal-12)
    - [Scope](#scope-13)
    - [User Stories (in order)](#user-stories-in-order-12)
  - [Release 14 — Research & operational readiness](#release-14--research--operational-readiness)
    - [Goal](#goal-13)
    - [Scope](#scope-14)
    - [User Stories (in order)](#user-stories-in-order-13)
  - [Release 15 — Extraction field expansion (golden loops)](#release-15--extraction-field-expansion-golden-loops)
    - [Goal](#goal-14)
    - [Scope](#scope-15)
    - [User Stories (in order)](#user-stories-in-order-14)
  - [Release 16 — Multi-visit detection & per-visit extraction](#release-16--multi-visit-detection--per-visit-extraction)
    - [Goal](#goal-15)
    - [Scope](#scope-16)
    - [User Stories (in order)](#user-stories-in-order-15)
  - [Release 17 — Engineering quality & project governance](#release-17--engineering-quality--project-governance)
    - [Goal](#goal-16)
    - [Scope](#scope-17)
    - [User Stories (in order)](#user-stories-in-order-16)
  - [Release 18 — Frontend observability for evaluators](#release-18--frontend-observability-for-evaluators)
    - [Goal](#goal-17)
    - [Scope](#scope-18)
    - [User Stories (in order)](#user-stories-in-order-17)
  - [Release 19 — Critical architecture remediation](#release-19--critical-architecture-remediation)
    - [Goal](#goal-18)
    - [Scope](#scope-19)
    - [Items (in order)](#items-in-order)
  - [Release 20 — Architecture hardening](#release-20--architecture-hardening)
    - [Goal](#goal-19)
    - [Scope](#scope-20)
    - [Items (in order)](#items-in-order-1)
  - [Release 21 — Architecture polish & operational maturity](#release-21--architecture-polish--operational-maturity)
    - [Goal](#goal-20)
    - [Scope](#scope-21)
    - [Items (in order)](#items-in-order-2)
- [Backlog Index](Backlog/README.md)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

This document is intended to provide structured context to an AI Coding Assistant during implementation.

The version of this document written for evaluators and reviewers is available here:
https://docs.google.com/document/d/1b1rvBJu9bGjv8Z42OdDz9qwjecbqDbpilkn0KkYuD-M

Reading order, document authority, and precedence rules are defined in [`docs/README.md`](../../../README.md).
If any conflict is detected, **STOP and ask before proceeding**.

# Introduction

## Purpose

This document is the **release sequencing authority** for the project.

It defines:
- the **order of implementation**,
- the **release assignment** of each user story and improvement,
- the **backlog references** that own story-level scope and acceptance criteria.

This document does **not** define:
- product meaning or governance,
- UX semantics or interaction contracts,
- architecture, system invariants, or API contracts,
- cross-cutting implementation principles,
- backend/frontend implementation details.

Those are defined in their respective authoritative documents as described in [`docs/README.md`](../../../README.md).

Features or behaviors not explicitly listed here are not part of this plan.

---

## How to use this document

The AI Coding Assistant must:
- enter via [`AGENTS.md`](../../../../AGENTS.md) and load only the router module(s) relevant to the current task/story,
- implement user stories **strictly in the order defined here**,
- treat the acceptance criteria in the linked backlog item files as **exit conditions**, not suggestions.

Ordering rule:
- Story order is defined by the **order of release sections and item lists in this document**, not by story numeric identifiers.

If a user story appears underspecified or conflicts with an authoritative document,
**STOP and ask before implementing**.

---

## Contract boundary (non-negotiable)

This plan MUST NOT specify or restate cross-cutting technical contracts, even as “examples”:
- endpoint paths, request/response payload shapes, or per-endpoint semantics,
- error codes or error semantics,
- persistence schemas/tables/entities or field-level models,
- structured interpretation schema fields,
- logging `event_type` values,
- library/framework choices, module structure, or code patterns.

If a story depends on any of the above, it MUST include an **Authoritative References** section naming the canonical doc and section (e.g. "TECHNICAL_DESIGN Appendix B3").
At execution time, the agent MUST NOT open those canonical docs directly; instead, enter via [`AGENTS.md`](../../../../AGENTS.md) and load only the router module that covers the needed section.

---

## Scope

This plan defines releases and backlog item ordering.
Work is implemented sequentially following the release/item order in this document.

All scope boundaries, acceptance criteria, and story-specific references must be expressed in each backlog item file under [`Backlog/`](Backlog/README.md).
If a behavior is not described by the currently scheduled stories, it should be introduced via a dedicated user story (and any required design updates).

---

## Execution Rules

- Work is executed **one user story at a time**
- A story is complete only when all acceptance criteria pass
- No story may redefine contracts owned elsewhere
- Any change to contracts requires updating the authoritative document first

---

# Implementation Plan
## Release 1 — Document upload & access

### Goal
Allow users to upload documents and access them reliably, establishing a stable and observable foundation.

### Scope
- Upload documents
- Persist original documents
- Initialize and expose document status
- Download and preview original documents
- List uploaded documents with their status

### User Stories (in order)
- [US-01 — Upload document (API)](Backlog/us-01-upload-document-api.md)
- [US-02 — View document status](Backlog/us-02-view-document-status.md)
- [US-03 — Download / preview original document](Backlog/us-03-download-preview-original-document.md)
- [US-04 — List uploaded documents and their status](Backlog/us-04-list-uploaded-documents-and-their-status.md)

---

## Release 2 — Automatic processing & traceability

### Goal
Automatically process uploaded **PDF** documents in a **non-blocking** way, with full traceability and safe reprocessing.

### Scope
- Automatic processing after upload (PDF)
- Explicit processing states
- Failure classification
- Manual reprocessing
- Append-only processing history

### Format support note
Supported upload types are defined by [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../02-tech/technical-design.md) Appendix B3. DOCX and image format expansion are sequenced as the final stories (US-19 and US-20).

### User Stories (in order)
- [US-05 — Process document](Backlog/us-05-process-document.md)
- [US-21 — Upload medical documents (end-user UI)](Backlog/us-21-upload-medical-documents-end-user-ui.md)
- [US-11 — View document processing history](Backlog/us-11-view-document-processing-history.md)

---

## Release 3 — Extraction transparency (trust & debuggability)

### Goal
Make visible and explainable **what the system has read**, before any interpretation is applied.

### Scope
- Raw text extraction visibility
- Language visibility
- Persistent extraction artifacts
- On-demand access via progressive disclosure

### User Stories (in order)
- [US-06 — View extracted text](Backlog/us-06-view-extracted-text.md)

---

## Release 4 — Assisted review in context (high value / higher risk)

### Goal
Enable veterinarians to review the system’s interpretation **in context**, side-by-side with the original document.

### Scope
- Structured extracted data
- Per-field confidence signals
- Evidence via page + snippet (approximate by design)
- Side-by-side document review
- Progressive enhancement (review usable even if highlighting fails)
- Non-blocking, explainable UX

### User Stories (in order)
- [US-07 — Review document in context](Backlog/us-07-review-document-in-context.md)
- [US-34 — Search & filters in Structured Data panel](Backlog/us-34-search-filters-in-structured-data-panel.md)
- [US-35 — Resizable splitter between PDF Viewer and Structured Data panel](Backlog/us-35-resizable-splitter-between-pdf-viewer-and-structur.md)
- [US-38 — Mark document as reviewed (toggle)](Backlog/us-38-mark-document-as-reviewed-toggle.md)

---

## Release 5 — Editing & learning signals (human corrections)

### Goal
Allow veterinarians to correct structured data naturally, while capturing append-only correction signals—without changing their workflow.

### Scope
- Edit existing structured fields
- Create new structured fields
- Versioned structured records
- Field-level change logs
- Capture append-only correction signals (no behavior change)

### User Stories (in order)
- [US-36 — Lean design system (tokens + primitives)](Backlog/us-36-lean-design-system-tokens-primitives.md)
- [US-08 — Edit structured data](Backlog/us-08-edit-structured-data.md)
- [US-09 — Capture correction signals](Backlog/us-09-capture-correction-signals.md)
- [US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal](Backlog/us-41-show-top-5-candidate-suggestions-in-field-edit-mod.md)
- [US-39 — Align veterinarian confidence signal with mapping confidence policy](Backlog/us-39-align-veterinarian-confidence-signal-with-mapping.md)
- [US-40 — Implement field-level confidence tooltip breakdown](Backlog/us-40-implement-field-level-confidence-tooltip-breakdown.md) (Implemented 2026-02-18)

---

## Release 6 — Explicit overrides & workflow closure

### Goal
Focus this release on visit-grouped review rendering (contract-driven) and evaluator-ready workflow closure.

### Scope
- Visit-grouped rendering when `canonical contract` with deterministic ordering and no UI heuristics
- Evaluator-friendly installation and execution packaging/runbook

### User Stories (in order)
- [US-32 — Align review rendering to Global Schema template](Backlog/us-32-align-review-rendering-to-global-schema-template.md) (Implemented 2026-02-17)
- [US-44 — Medical Record MVP: Update Extracted Data panel structure, labels, and scope](Backlog/us-44-medical-record-mvp-update-extracted-data-panel-str.md) (Implemented 2026-02-20)
- [US-43 — Render “Visitas” agrupadas cuando `canonical contract` (contract-driven, no heuristics)](Backlog/us-43-render-visitas-agrupadas-cuando-canonical-contract.md)
- [US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement)](Backlog/us-45-visit-detection-mvp-deterministic-contract-driven.md) (Implemented 2026-02-21)
- [US-46 — Deterministic Visit Assignment Coverage MVP (Schema)](Backlog/us-46-deterministic-visit-assignment-coverage-mvp-schema.md)
- [US-42 — Provide evaluator-friendly installation & execution (Docker-first)](Backlog/us-42-provide-evaluator-friendly-installation-execution.md) (Implemented 2026-02-19)

---

## Release 7 — Edit workflow hardening

### Goal
Make field editing robust and predictable, preventing data loss and ensuring correct modification semantics.

### Scope
- Dirty state tracking and discard confirmation in field edit dialog
- Reset individual fields or all fields to originally detected values
- Correct modification tracking when saving the originally suggested value
- Confidence refresh after editing a reopened reviewed document

### User Stories (in order)
- [US-47 — Prevent losing unsaved field edits (dirty state + confirm discard)](Backlog/us-47-prevent-losing-unsaved-field-edits-dirty-state-con.md)
- [US-48 — Reset field(s) to original detected value](Backlog/us-48-reset-field-s-to-original-detected-value.md)
- [US-49 — Treat save of originally suggested value as unmodified](Backlog/us-49-treat-save-of-originally-suggested-value-as-unmodi.md)
- [US-59 — Refresh visible confidence after edits on reopened document](Backlog/us-59-refresh-visible-confidence-after-edits-on-reopened.md)

---

## Release 8 — Evidence navigation & document interaction

### Goal
Enable precise evidence inspection and text search within the document viewer.

### Scope
- Click-to-navigate from structured field to exact location in document viewer
- Full-text search within the PDF viewer
- PDF zoom controls

### User Stories (in order)
- [US-50 — Navigate to and highlight field evidence in document viewer](Backlog/us-50-navigate-to-and-highlight-field-evidence-in-docume.md)
- [US-51 — Text search in PDF viewer](Backlog/us-51-text-search-in-pdf-viewer.md)
- [US-33 — PDF Viewer Zoom](Backlog/us-33-pdf-viewer-zoom.md)

---

## Release 9 — Extraction quality & language

### Goal
Improve extraction coverage, visit detection, clinical utility, and language support.

### Scope
- Visit detection heuristic improvements
- General extraction heuristic improvements
- Patient history summary field (antecedentes)
- Document language override and reprocessing

### User Stories (in order)
- [US-52 — Improve visit detection heuristics](Backlog/us-52-improve-visit-detection-heuristics.md)
- [US-53 — Improve general extraction heuristics](Backlog/us-53-improve-general-extraction-heuristics.md)
- [US-54 — Patient history summary field (antecedentes)](Backlog/us-54-patient-history-summary-field-antecedentes.md)
- [US-10 — Change document language and reprocess](Backlog/us-10-change-document-language-and-reprocess.md)

---

## Release 10 — UX polish & upload ergonomics

### Goal
Improve document interaction ergonomics and visual polish without changing core workflow semantics.

### Scope
- Document list readability and navigation
- Upload convenience (drag-and-drop + bulk)
- Toast behavior

### User Stories (in order)
- [US-23 — Improve document list filename visibility and tooltip details](Backlog/us-23-improve-document-list-filename-visibility-and-tool.md)
- [US-24 — Support global drag-and-drop PDF upload across relevant screens](Backlog/us-24-support-global-drag-and-drop-pdf-upload-across-rel.md)
- [US-25 — Upload a folder of PDFs (bulk)](Backlog/us-25-upload-a-folder-of-pdfs-bulk.md)
- [US-29 — Improve toast queue behavior](Backlog/us-29-improve-toast-queue-behavior.md)

---

## Release 11 — Help, content externalization & i18n

### Goal
Provide comprehensive in-app help, externalize UI texts for editing/translation, and add multilingual UI support.

### Scope
- Keyboard shortcuts and help modal
- In-app help wiki and entry point
- Contextual help icons throughout UI
- UI text externalization
- Document lifecycle management (soft-delete)
- Multilingual UI and externalized settings

### User Stories (in order)
- [US-26 — Add keyboard shortcuts and help modal](Backlog/us-26-add-keyboard-shortcuts-and-help-modal.md)
- [US-27 — Add in-app help wiki and entry point](Backlog/us-27-add-in-app-help-wiki-and-entry-point.md)
- [US-55 — Contextual help icons with wiki links throughout UI](Backlog/us-55-contextual-help-icons-with-wiki-links-throughout-u.md)
- [US-56 — Externalize UI texts to editable files](Backlog/us-56-externalize-ui-texts-to-editable-files.md)
- [US-28 — Delete uploaded document from list (soft-delete/archive)](Backlog/us-28-delete-uploaded-document-from-list-soft-delete-arc.md)
- [US-30 — Change application UI language (multilingual UI)](Backlog/us-30-change-application-ui-language-multilingual-ui.md)
- [US-31 — Externalize configuration and expose settings in UI](Backlog/us-31-externalize-configuration-and-expose-settings-in-u.md)

---

## Release 12 — Additional formats & OCR

### Goal
Expand format support beyond PDF and add optional OCR for scanned documents.

### Scope
- DOCX and image format end-to-end support
- Optional OCR for scanned PDFs and images (depends on image support)

### User Stories (in order)
- [US-19 — Add DOCX end-to-end support](Backlog/us-19-add-docx-end-to-end-support.md)
- [US-20 — Add Images end-to-end support](Backlog/us-20-add-images-end-to-end-support.md)
- [US-22 — Optional OCR support for scanned medical records (PDF/Image)](Backlog/us-22-optional-ocr-support-for-scanned-medical-records-p.md)

---

## Release 13 — Schema evolution (isolated reviewer workflows)

### Goal
Introduce reviewer-facing governance for global schema evolution, fully isolated from veterinarian workflows.

### Scope
- Aggregation of pending structural change candidates
- Reviewer-facing inspection, filtering, and prioritization
- Approval, rejection, and deferral
- Canonical schema evolution governance (prospective only)
- Append-only governance audit trail

### User Stories (in order)
- [US-13 — Review aggregated pending structural changes](Backlog/us-13-review-aggregated-pending-structural-changes.md)
- [US-14 — Filter and prioritize pending structural changes](Backlog/us-14-filter-and-prioritize-pending-structural-changes.md)
- [US-15 — Approve structural changes into the global schema](Backlog/us-15-approve-structural-changes-into-the-global-schema.md)
- [US-16 — Reject or defer structural changes](Backlog/us-16-reject-or-defer-structural-changes.md)
- [US-17 — Govern critical (non-reversible) structural changes](Backlog/us-17-govern-critical-non-reversible-structural-changes.md)
- [US-18 — Audit trail of schema governance decisions](Backlog/us-18-audit-trail-of-schema-governance-decisions.md)

---

## Release 14 — Research & operational readiness

### Goal
Investigate field standardization opportunities and define operational policies for production readiness.

### Scope
- Research ISO and international standards applicability to structured fields
- Define production DB reset policy for reviewed documents

### User Stories (in order)
- [US-57 — Research field standardization (ISO, international recommendations)](Backlog/us-57-research-field-standardization-iso-international-r.md)
- [US-58 — Define production DB reset policy for reviewed documents](Backlog/us-58-define-production-db-reset-policy-for-reviewed-doc.md)

---

## Release 15 — Extraction field expansion (golden loops)

### Goal
Expand extraction coverage to all critical patient and clinic fields via the golden loop pattern, ensuring each field has dedicated fixtures, benchmark tests, labeled patterns, and normalization.

### Scope
- Pet name extraction hardening
- Clinic name extraction hardening
- Clinic address extraction hardening
- Bidirectional clinic enrichment (name ↔ address)
- Date of birth (DOB) extraction hardening
- Microchip ID extraction hardening
- Owner address extraction (active)

### User Stories (in order)
- [US-69 — Extract pet name accurately](Backlog/us-69-extract-pet-name-accurately.md) (Implemented 2026-03-02)
- [US-70 — Extract clinic name accurately](Backlog/us-70-extract-clinic-name-accurately.md) (Implemented 2026-03-03)
- [US-71 — Extract clinic address accurately](Backlog/us-71-extract-clinic-address-accurately.md) (Implemented 2026-03-04)
- [US-72 — Complete clinic address from name (and vice versa) on demand](Backlog/us-72-complete-clinic-address-from-name-and-vice-versa-o.md) (Implemented 2026-03-04)
- [US-61 — Extract patient date of birth accurately](Backlog/us-61-extract-patient-date-of-birth-accurately.md) (Implemented 2026-03-05)
- [US-62 — Extract patient microchip number accurately](Backlog/us-62-extract-patient-microchip-number-accurately.md) (Implemented 2026-03-04)
- [US-63 — Extract owner address without confusing it with clinic address](Backlog/us-63-extract-owner-address-without-confusing-it-with-th.md)

---

## Release 16 — Multi-visit detection & per-visit extraction

### Goal
Detect all visits in a medical document from raw text boundaries and assign clinical data to each specific visit, with observability for debugging assignment problems.

### Scope
- Multi-visit detection from raw text boundaries
- Per-visit field extraction from segment text
- Visit scoping observability and documentation (conditional)

### User Stories (in order)
- [US-64 — Detect all visits in the document even when dates are not in explicit fields](Backlog/us-64-detect-all-visits-in-the-document-even-when-dates.md) (Implemented 2026-03-06)
- [US-65 — View clinical data assigned to each specific visit](Backlog/us-65-view-clinical-data-assigned-to-each-specific-visit.md)
- [US-66 — Diagnose visit-to-data assignment problems (conditional)](Backlog/us-66-diagnose-visit-to-data-assignment-problems-conditi.md)

---

## Release 17 — Engineering quality & project governance

### Goal
Establish modular architecture, comprehensive test coverage, production hardening, local validation pipelines, canonical documentation, and consistent project governance conventions.

### Scope
- Architecture audit, modularization, and component decomposition
- Automated test and E2E coverage in CI
- Security, performance, and resilience hardening
- L1/L2/L3 local validation pipeline
- Canonical documentation restructuring and derivation automation
- Worktree-prefixed branch naming convention
- Documentation improvement (wiki audit, restructure, standardization)

### User Stories (in order)
- [US-73 — Modular architecture and maintainable code](Backlog/us-73-modular-architecture-and-maintainable-code.md) (Implemented)
- [US-74 — Automated test and E2E coverage in CI](Backlog/us-74-automated-test-and-e2e-coverage-in-ci.md) (Implemented)
- [US-75 — Production security, performance, and resilience](Backlog/us-75-production-security-performance-and-resilience.md) (Implemented)
- [US-76 — Functional L1/L2/L3 local validation pipeline on Windows](Backlog/us-76-functional-l1-l2-l3-local-validation-pipeline-on-w.md) (Implemented)
- [US-77 — Canonical documentation as source of truth with automatic derivation](Backlog/us-77-canonical-documentation-as-source-of-truth-with-au.md) (Implemented)
- [US-68 — Identify the source worktree of each branch at a glance](Backlog/us-68-identify-the-source-worktree-of-each-branch-at-a-g.md) (Implemented 2026-03-06)
- [US-67 — Auditable, navigable, and consistent project documentation](Backlog/us-67-auditable-navigable-and-consistent-project-documen.md)
- [US-79 — Architecture health evaluation with quantified metrics and remediation path](Backlog/us-79-architecture-health-evaluation-with-quantified-metr.md) (In Progress)
- [IMP-01 — Canonical Operational Execution Policy Alignment](Backlog/completed/imp-01-canonical-operational-execution-policy-alignment.md) (Implemented)
- [IMP-02 — Router and DOC_UPDATES Contract Synchronization](Backlog/completed/imp-02-router-and-doc-updates-contract-synchronization.md) (Implemented)
- [IMP-03 — Plan Execution Guard Enforcement (Local + CI)](Backlog/completed/imp-03-plan-execution-guard-enforcement-local-ci.md) (Implemented)
- [IMP-04 — Active Plan Migration and Global Index Cleanup](Backlog/imp-04-active-plan-migration-and-global-index-cleanup.md) (Planned)
- [IMP-05 — Plan Root File Naming Alignment](Backlog/imp-05-plan-root-file-naming-alignment.md) (Implemented)
- [IMP-06 — Preflight Wrapper Integrity and L3 Entrypoint Hardening](Backlog/imp-06-preflight-wrapper-integrity-and-l3-entrypoint-hardening.md) (Planned)

---

## Release 18 — Frontend observability for evaluators

### Goal
Enhance the frontend to provide evaluators with clear, informative processing history including state badges, per-run durations, and per-run raw text access.

### Scope
- Processing history UI enhancements (frontend-only, no backend changes)

### User Stories (in order)
- [US-78 — Enhanced processing history UI for evaluator observability](Backlog/us-78-enhanced-processing-history-ui-for-evaluator-obser.md)

---

## Release 19 — Critical architecture remediation

### Goal
Address the highest-impact architecture findings: decompose God Modules, add CI complexity gates, and close critical documentation gaps (security architecture, production deployment).

### Scope
- Backend God Module decomposition (review_service.py, candidate_mining.py)
- CI complexity and LOC gates
- Security architecture and production deployment documentation

### Items (in order)
- [ARCH-03 — Add CI Complexity Gates](Backlog/arch-03-add-ci-complexity-gates.md) (Planned)
- [ARCH-01 — Decompose `review_service.py`](Backlog/completed/arch-01-decompose-review-service.md) (Implemented)
- [ARCH-02 — Decompose `candidate_mining.py`](Backlog/completed/arch-02-decompose-candidate-mining.md) (Done)
- [ARCH-06 — Create Security Architecture Documentation](Backlog/arch-06-create-security-architecture-documentation.md) (Planned)
- [ARCH-07 — Create Production Deployment Documentation](Backlog/arch-07-create-production-deployment-documentation.md) (Planned)

---

## Release 20 — Architecture hardening

### Goal
Fix remaining hexagonal violations, improve code hygiene, add missing ADRs, close documentation gaps, and implement production security improvements.

### Scope
- Hexagonal architecture violation fixes
- Structured logging for critical paths
- Missing ADRs and documentation (ER diagram, monitoring, ADRs)
- Production authentication, dependency hygiene, and security patterns

### Items (in order)
- [ARCH-04 — Fix infra→application Dependency Violation](Backlog/arch-04-fix-infra-application-hex-violation.md) (Planned)
- [ARCH-08 — Expose `_shared` Functions Publicly](Backlog/completed/arch-08-expose-shared-functions-publicly.md) (Done)
- [ARCH-15 — Explicitly Declare pydantic in requirements.txt](Backlog/arch-15-declare-pydantic-in-requirements.md) (Planned)
- [ARCH-22 — Parameterize PRAGMA table_info Call](Backlog/arch-22-parameterize-pragma-table-info.md) (Planned)
- [ARCH-24 — Replace Wildcard Re-export with Explicit Imports](Backlog/arch-24-replace-wildcard-re-export.md) (Planned)
- [ARCH-05 — Add Structured Logging to Critical Paths](Backlog/arch-05-add-structured-logging-critical-paths.md) (Planned)
- [ARCH-09 — Add ER Diagram to technical-design.md](Backlog/arch-09-add-er-diagram-to-technical-design.md) (Planned)
- [ARCH-10 — Write Missing ADRs](Backlog/arch-10-write-missing-adrs.md) (Planned)
- [ARCH-16 — Create Re-accretion Prevention ADR](Backlog/arch-16-create-re-accretion-prevention-adr.md) (Planned)
- [ARCH-11 — Add Monitoring/Alerting Strategy Documentation](Backlog/arch-11-add-monitoring-alerting-strategy-docs.md) (Planned)
- [ARCH-13 — Implement Production Authentication](Backlog/arch-13-implement-production-authentication.md) (Planned)

---

## Release 21 — Architecture polish & operational maturity

### Goal
Complete remaining architecture improvements: capacity planning, content validation, frontend state management, runtime observability, operational runbooks, and configuration documentation.

### Scope
- Capacity planning and configuration reference documentation
- PDF upload content validation
- Frontend state management refactor
- Runtime metrics collection and rate limiting
- Operational runbooks

### Items (in order)
- [ARCH-12 — Add Capacity Planning Documentation](Backlog/arch-12-add-capacity-planning-documentation.md) (Planned)
- [ARCH-23 — Add Configuration Reference Documentation](Backlog/arch-23-add-configuration-reference-docs.md) (Planned)
- [ARCH-14 — Add Content Validation for PDF Uploads](Backlog/arch-14-add-content-validation-pdf-uploads.md) (Planned)
- [ARCH-17 — Simplify extraction_observability/ Subsystem](Backlog/arch-17-simplify-extraction-observability.md) (Planned)
- [ARCH-19 — Create Operational Runbooks](Backlog/arch-19-create-operational-runbooks.md) (Planned)
- [ARCH-18 — Extract Frontend State Management Layer](Backlog/arch-18-extract-frontend-state-management.md) (Planned)
- [ARCH-20 — Add Metrics Collection Infrastructure](Backlog/arch-20-add-metrics-collection-infrastructure.md) (Planned)
- [ARCH-21 — Add Rate Limiting to Write Endpoints](Backlog/arch-21-add-rate-limiting-write-endpoints.md) (Planned)

---

> For detailed User Story and Improvement specifications, see [Backlog Index](Backlog/README.md).
