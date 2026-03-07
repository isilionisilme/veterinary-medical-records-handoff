---
title: "Implementation Plan"
type: reference
status: active
audience: contributor
last-updated: 2026-03-02
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
    - [Scope](#scope-15a)
    - [User Stories (in order)](#user-stories-in-order-14)
  - [Release 16 — Multi-visit detection & per-visit extraction](#release-16--multi-visit-detection--per-visit-extraction)
    - [Goal](#goal-15)
    - [Scope](#scope-16a)
    - [User Stories (in order)](#user-stories-in-order-15)
  - [Release 17 — Engineering quality & project governance](#release-17--engineering-quality--project-governance)
    - [Goal](#goal-16)
    - [Scope](#scope-17)
    - [User Stories (in order)](#user-stories-in-order-16)
  - [Release 18 — Frontend observability for evaluators](#release-18--frontend-observability-for-evaluators)
    - [Goal](#goal-17)
    - [Scope](#scope-18)
    - [User Stories (in order)](#user-stories-in-order-17)
- [User Story Details](#user-story-details)
  - [US-01 — Upload document (API)](#us-01--upload-document-api)
  - [US-02 — View document status](#us-02--view-document-status)
  - [US-03 — Download / preview original document](#us-03--download--preview-original-document)
  - [US-04 — List uploaded documents and their status](#us-04--list-uploaded-documents-and-their-status)
  - [US-05 — Process document](#us-05--process-document)
  - [US-21 — Upload medical documents (end-user UI)](#us-21--upload-medical-documents-end-user-ui)
  - [US-11 — View document processing history](#us-11--view-document-processing-history)
  - [US-06 — View extracted text](#us-06--view-extracted-text)
  - [US-07 — Review document in context](#us-07--review-document-in-context)
  - [US-38 — Mark document as reviewed (toggle)](#us-38--mark-document-as-reviewed-toggle)
  - [US-34 — Search & filters in Structured Data panel](#us-34--search--filters-in-structured-data-panel)
  - [US-35 — Resizable splitter between PDF Viewer and Structured Data panel](#us-35--resizable-splitter-between-pdf-viewer-and-structured-data-panel)
  - [US-36 — Lean design system (tokens + primitives)](#us-36--lean-design-system-tokens--primitives)
  - [US-08 — Edit structured data](#us-08--edit-structured-data)
  - [US-09 — Capture correction signals](#us-09--capture-correction-signals)
  - [US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal](#us-41--show-top-5-candidate-suggestions-in-field-edit-modal)
  - [US-10 — Change document language and reprocess](#us-10--change-document-language-and-reprocess)
  - [US-32 — Align review rendering to Global Schema template](#us-32--align-review-rendering-to-global-schema-template)
  - [US-44 — Medical Record MVP: Update Extracted Data panel structure, labels, and scope](#us-44--medical-record-mvp-update-extracted-data-panel-structure-labels-and-scope)
    - [User Story](#user-story)
    - [Scope](#scope-15)
    - [Acceptance Criteria](#acceptance-criteria)
    - [Story-specific technical requirements](#story-specific-technical-requirements)
    - [Dependencies / Placement](#dependencies--placement)
  - [US-43 — Render “Visitas” agrupadas cuando `canonical contract` (contract-driven, no heuristics)](#us-43--render-visitas-agrupadas-cuando-canonical-contract-contract-driven-no-heuristics)
    - [User Story](#user-story-1)
    - [Scope](#scope-16)
    - [Acceptance Criteria](#acceptance-criteria-1)
    - [Story-specific technical requirements](#story-specific-technical-requirements-1)
    - [Authoritative References](#authoritative-references)
  - [US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement)](#us-45--visit-detection-mvp-deterministic-contract-driven-coverage-improvement)
    - [Context / Problem](#context--problem)
    - [Objective](#objective)
    - [User Story](#user-story-2)
    - [Scope (MVP)](#scope-mvp)
    - [Contractual rules / Non-negotiables](#contractual-rules--non-negotiables)
    - [Acceptance Criteria (testable)](#acceptance-criteria-testable)
    - [Dependencies](#dependencies)
    - [Risks / Watch-outs](#risks--watch-outs)
  - [US-46 — Deterministic Visit Assignment Coverage MVP (Schema)](#us-46--deterministic-visit-assignment-coverage-mvp-schema)
    - [Context](#context)
    - [Objective](#objective-1)
    - [User Story](#user-story-3)
    - [Scope (MVP)](#scope-mvp-1)
    - [Acceptance Criteria (testable)](#acceptance-criteria-testable-1)
    - [Documentation Requirement](#documentation-requirement)
    - [Authoritative References](#authoritative-references-1)
  - [US-39 — Align veterinarian confidence signal with mapping confidence policy](#us-39--align-veterinarian-confidence-signal-with-mapping-confidence-policy)
  - [US-40 — Implement field-level confidence tooltip breakdown](#us-40--implement-field-level-confidence-tooltip-breakdown)
  - [US-13 — Review aggregated pending structural changes](#us-13--review-aggregated-pending-structural-changes)
  - [US-14 — Filter and prioritize pending structural changes](#us-14--filter-and-prioritize-pending-structural-changes)
  - [US-15 — Approve structural changes into the global schema](#us-15--approve-structural-changes-into-the-global-schema)
  - [US-16 — Reject or defer structural changes](#us-16--reject-or-defer-structural-changes)
  - [US-17 — Govern critical (non-reversible) structural changes](#us-17--govern-critical-non-reversible-structural-changes)
  - [US-18 — Audit trail of schema governance decisions](#us-18--audit-trail-of-schema-governance-decisions)
  - [US-19 — Add DOCX end-to-end support](#us-19--add-docx-end-to-end-support)
  - [US-20 — Add Images end-to-end support](#us-20--add-images-end-to-end-support)
  - [US-22 — Optional OCR support for scanned medical records (PDF/Image)](#us-22--optional-ocr-support-for-scanned-medical-records-pdfimage)
  - [US-23 — Improve document list filename visibility and tooltip details](#us-23--improve-document-list-filename-visibility-and-tooltip-details)
  - [US-24 — Support global drag-and-drop PDF upload across relevant screens](#us-24--support-global-drag-and-drop-pdf-upload-across-relevant-screens)
  - [US-25 — Upload a folder of PDFs (bulk)](#us-25--upload-a-folder-of-pdfs-bulk)
  - [US-26 — Add keyboard shortcuts and help modal](#us-26--add-keyboard-shortcuts-and-help-modal)
  - [US-27 — Add in-app help wiki and entry point](#us-27--add-in-app-help-wiki-and-entry-point)
  - [US-28 — Delete uploaded document from list (soft-delete/archive)](#us-28--delete-uploaded-document-from-list-soft-deletearchive)
  - [US-29 — Improve toast queue behavior](#us-29--improve-toast-queue-behavior)
  - [US-30 — Change application UI language (multilingual UI)](#us-30--change-application-ui-language-multilingual-ui)
  - [US-31 — Externalize configuration and expose settings in UI](#us-31--externalize-configuration-and-expose-settings-in-ui)
  - [US-33 — PDF Viewer Zoom](#us-33--pdf-viewer-zoom)
  - [US-47 — Prevent losing unsaved field edits (dirty state + confirm discard)](#us-47--prevent-losing-unsaved-field-edits-dirty-state--confirm-discard)
  - [US-48 — Reset field(s) to original detected value](#us-48--reset-fields-to-original-detected-value)
  - [US-49 — Treat save of originally suggested value as unmodified](#us-49--treat-save-of-originally-suggested-value-as-unmodified)
  - [US-59 — Refresh visible confidence after edits on reopened document](#us-59--refresh-visible-confidence-after-edits-on-reopened-document)
  - [US-50 — Navigate to and highlight field evidence in document viewer](#us-50--navigate-to-and-highlight-field-evidence-in-document-viewer)
  - [US-51 — Text search in PDF viewer](#us-51--text-search-in-pdf-viewer)
  - [US-52 — Improve visit detection heuristics](#us-52--improve-visit-detection-heuristics)
  - [US-53 — Improve general extraction heuristics](#us-53--improve-general-extraction-heuristics)
  - [US-54 — Patient history summary field (antecedentes)](#us-54--patient-history-summary-field-antecedentes)
  - [US-55 — Contextual help icons with wiki links throughout UI](#us-55--contextual-help-icons-with-wiki-links-throughout-ui)
  - [US-56 — Externalize UI texts to editable files](#us-56--externalize-ui-texts-to-editable-files)
  - [US-57 — Research field standardization (ISO, international recommendations)](#us-57--research-field-standardization-iso-international-recommendations)
  - [US-58 — Define production DB reset policy for reviewed documents](#us-58--define-production-db-reset-policy-for-reviewed-documents)
  - [US-42 — Provide evaluator-friendly installation & execution (Docker-first)](#us-42--provide-evaluator-friendly-installation--execution-docker-first)
  - [US-61 — Extract patient date of birth accurately](#us-61--extract-patient-date-of-birth-accurately)
  - [US-62 — Extract patient microchip number accurately](#us-62--extract-patient-microchip-number-accurately)
  - [US-63 — Extract owner address without confusing it with clinic address](#us-63--extract-owner-address-without-confusing-it-with-clinic-address)
  - [US-64 — Detect all visits in the document even when dates are not in explicit fields](#us-64--detect-all-visits-in-the-document-even-when-dates-are-not-in-explicit-fields)
  - [US-65 — View clinical data assigned to each specific visit](#us-65--view-clinical-data-assigned-to-each-specific-visit)
  - [US-66 — Diagnose visit-to-data assignment problems (conditional)](#us-66--diagnose-visit-to-data-assignment-problems-conditional)
  - [US-67 — Auditable, navigable, and consistent project documentation](#us-67--auditable-navigable-and-consistent-project-documentation)
  - [US-68 — Identify the source worktree of each branch at a glance](#us-68--identify-the-source-worktree-of-each-branch-at-a-glance)
  - [US-69 — Extract pet name accurately](#us-69--extract-pet-name-accurately)
  - [US-70 — Extract clinic name accurately](#us-70--extract-clinic-name-accurately)
  - [US-71 — Extract clinic address accurately](#us-71--extract-clinic-address-accurately)
  - [US-72 — Complete clinic address from name (and vice versa) on demand](#us-72--complete-clinic-address-from-name-and-vice-versa-on-demand)
  - [US-73 — Modular architecture and maintainable code](#us-73--modular-architecture-and-maintainable-code)
  - [US-74 — Automated test and E2E coverage in CI](#us-74--automated-test-and-e2e-coverage-in-ci)
  - [US-75 — Production security, performance, and resilience](#us-75--production-security-performance-and-resilience)
  - [US-76 — Functional L1/L2/L3 local validation pipeline on Windows](#us-76--functional-l1l2l3-local-validation-pipeline-on-windows)
  - [US-77 — Canonical documentation as source of truth with automatic derivation](#us-77--canonical-documentation-as-source-of-truth-with-automatic-derivation)
  - [US-78 — Enhanced processing history UI for evaluator observability](#us-78--enhanced-processing-history-ui-for-evaluator-observability)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

This document is intended to provide structured context to an AI Coding Assistant during implementation.

The version of this document written for evaluators and reviewers is available here:
https://docs.google.com/document/d/1b1rvBJu9bGjv8Z42OdDz9qwjecbqDbpilkn0KkYuD-M

Reading order, document authority, and precedence rules are defined in [`docs/README.md`](../README.md).
If any conflict is detected, **STOP and ask before proceeding**.

# Introduction 

## Purpose

This document is the **sequencing and scope authority** for the project.

It defines:
- the **order of implementation**,
- the **scope boundaries** of each user story,
- the **acceptance criteria** that determine completion.

This document does **not** define:
- product meaning or governance,
- UX semantics or interaction contracts,
- architecture, system invariants, or API contracts,
- cross-cutting implementation principles,
- backend/frontend implementation details.

Those are defined in their respective authoritative documents as described in [`docs/README.md`](../README.md).

Features or behaviors not explicitly listed here are not part of this plan.

---

## How to use this document

The AI Coding Assistant must:
- enter via [`AGENTS.md`](../../AGENTS.md) and load only the router module(s) relevant to the current task/story,
- implement user stories **strictly in the order defined here**,
- treat acceptance criteria as **exit conditions**, not suggestions.

Ordering rule:
- Story order is defined by the **order of story sections in this document**, not by story numeric identifiers.

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
At execution time, the agent MUST NOT open those canonical docs directly; instead, enter via [`AGENTS.md`](../../AGENTS.md) and load only the router module that covers the needed section.

---

## Scope

This plan defines releases and user stories, in execution order.
Work is implemented sequentially following the release/story order in this document.

All scope boundaries must be expressed inside each user story’s **Scope Clarification** section.
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
- US-01 — Upload document (API)
- US-02 — View document status
- US-03 — Download / preview original document
- US-04 — List uploaded documents and their status

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
Supported upload types are defined by [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3. DOCX and image format expansion are sequenced as the final stories (US-19 and US-20).

### User Stories (in order)
- US-05 — Process document
- US-21 — Upload medical documents (end-user UI)
- US-11 — View document processing history

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
- US-06 — View extracted text

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
- US-07 — Review document in context
- US-34 — Search & filters in Structured Data panel
- US-35 — Resizable splitter between PDF Viewer and Structured Data panel
- US-38 — Mark document as reviewed (toggle)

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
- US-36 — Lean design system (tokens + primitives)
- US-08 — Edit structured data
- US-09 — Capture correction signals
- US-41 — Show Top-5 candidate suggestions in Field Edit Modal
- US-39 — Align veterinarian confidence signal with mapping confidence policy
- US-40 — Implement field-level confidence tooltip breakdown (Implemented 2026-02-18)

---

## Release 6 — Explicit overrides & workflow closure

### Goal
Focus this release on visit-grouped review rendering (contract-driven) and evaluator-ready workflow closure.

### Scope
- Visit-grouped rendering when `canonical contract` with deterministic ordering and no UI heuristics
- Evaluator-friendly installation and execution packaging/runbook

### User Stories (in order)
- US-32 — Align review rendering to Global Schema template (Implemented 2026-02-17)
- US-44 — Medical Record MVP: Update Extracted Data panel structure, labels, and scope (Implemented 2026-02-20)
- US-43 — Render “Visitas” agrupadas cuando `canonical contract` (contract-driven, no heuristics)
- US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement) (Implemented 2026-02-21)
- US-46 — Deterministic Visit Assignment Coverage MVP (Schema)
- US-42 — Provide evaluator-friendly installation & execution (Docker-first) (Implemented 2026-02-19)

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
- US-47 — Prevent losing unsaved field edits (dirty state + confirm discard)
- US-48 — Reset field(s) to original detected value
- US-49 — Treat save of originally suggested value as unmodified
- US-59 — Refresh visible confidence after edits on reopened document

---

## Release 8 — Evidence navigation & document interaction

### Goal
Enable precise evidence inspection and text search within the document viewer.

### Scope
- Click-to-navigate from structured field to exact location in document viewer
- Full-text search within the PDF viewer
- PDF zoom controls

### User Stories (in order)
- US-50 — Navigate to and highlight field evidence in document viewer
- US-51 — Text search in PDF viewer
- US-33 — PDF Viewer Zoom

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
- US-52 — Improve visit detection heuristics
- US-53 — Improve general extraction heuristics
- US-54 — Patient history summary field (antecedentes)
- US-10 — Change document language and reprocess

---

## Release 10 — UX polish & upload ergonomics

### Goal
Improve document interaction ergonomics and visual polish without changing core workflow semantics.

### Scope
- Document list readability and navigation
- Upload convenience (drag-and-drop + bulk)
- Toast behavior

### User Stories (in order)
- US-23 — Improve document list filename visibility and tooltip details
- US-24 — Support global drag-and-drop PDF upload across relevant screens
- US-25 — Upload a folder of PDFs (bulk)
- US-29 — Improve toast queue behavior

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
- US-26 — Add keyboard shortcuts and help modal
- US-27 — Add in-app help wiki and entry point
- US-55 — Contextual help icons with wiki links throughout UI
- US-56 — Externalize UI texts to editable files
- US-28 — Delete uploaded document from list (soft-delete/archive)
- US-30 — Change application UI language (multilingual UI)
- US-31 — Externalize configuration and expose settings in UI

---

## Release 12 — Additional formats & OCR

### Goal
Expand format support beyond PDF and add optional OCR for scanned documents.

### Scope
- DOCX and image format end-to-end support
- Optional OCR for scanned PDFs and images (depends on image support)

### User Stories (in order)
- US-19 — Add DOCX end-to-end support
- US-20 — Add Images end-to-end support
- US-22 — Optional OCR support for scanned medical records (PDF/Image)

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
- US-13 — Review aggregated pending structural changes
- US-14 — Filter and prioritize pending structural changes
- US-15 — Approve structural changes into the global schema
- US-16 — Reject or defer structural changes
- US-17 — Govern critical (non-reversible) structural changes
- US-18 — Audit trail of schema governance decisions

---

## Release 14 — Research & operational readiness

### Goal
Investigate field standardization opportunities and define operational policies for production readiness.

### Scope
- Research ISO and international standards applicability to structured fields
- Define production DB reset policy for reviewed documents

### User Stories (in order)
- US-57 — Research field standardization (ISO, international recommendations)
- US-58 — Define production DB reset policy for reviewed documents

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
- US-69 — Extract pet name accurately (Implemented 2026-03-02)
- US-70 — Extract clinic name accurately (Implemented 2026-03-03)
- US-71 — Extract clinic address accurately (Implemented 2026-03-04)
- US-72 — Complete clinic address from name (and vice versa) on demand (Implemented 2026-03-04)
- US-61 — Extract patient date of birth accurately (Implemented 2026-03-05)
- US-62 — Extract patient microchip number accurately (Implemented 2026-03-04)
- US-63 — Extract owner address without confusing it with clinic address

---

## Release 16 — Multi-visit detection & per-visit extraction

### Goal
Detect all visits in a medical document from raw text boundaries and assign clinical data to each specific visit, with observability for debugging assignment problems.

### Scope
- Multi-visit detection from raw text boundaries
- Per-visit field extraction from segment text
- Visit scoping observability and documentation (conditional)

### User Stories (in order)
- US-64 — Detect all visits in the document even when dates are not in explicit fields (Implemented 2026-03-06)
- US-65 — View clinical data assigned to each specific visit
- US-66 — Diagnose visit-to-data assignment problems (conditional)

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
- US-73 — Modular architecture and maintainable code (Implemented)
- US-74 — Automated test and E2E coverage in CI (Implemented)
- US-75 — Production security, performance, and resilience (Implemented)
- US-76 — Functional L1/L2/L3 local validation pipeline on Windows (Implemented)
- US-77 — Canonical documentation as source of truth with automatic derivation (Implemented)
- US-68 — Identify the source worktree of each branch at a glance (Implemented 2026-03-06)
- US-67 — Auditable, navigable, and consistent project documentation

---

## Release 18 — Frontend observability for evaluators

### Goal
Enhance the frontend to provide evaluators with clear, informative processing history including state badges, per-run durations, and per-run raw text access.

### Scope
- Processing history UI enhancements (frontend-only, no backend changes)

### User Stories (in order)
- US-78 — Enhanced processing history UI for evaluator observability

---

# User Story Details

Each story below contains only:
- user intent
- user-observable acceptance criteria
- story-specific scope boundaries
- authoritative references
- story-specific test expectations (high-level)

All contracts (API map, persistence model, schema, error semantics, invariants, logging taxonomy) MUST be taken from authoritative docs.

---

## US-01 — Upload document (API)

**Status**: Implemented (2026-02-16)

**User Story**
As a developer, I want an API endpoint that accepts and persists a document so that it is stored and available for processing.

**Acceptance Criteria**
- A supported document type can be uploaded via the API (e.g. Swagger UI, curl, or developer tools).
- The API returns immediate confirmation that the document was persisted (without waiting on processing).
- The document appears in the system with the initial derived status.

**Scope Clarification**
- This story delivers the **backend ingestion API only** — no end-user UI. Verification is done through Swagger UI, curl, or equivalent developer tools.
- This story does not start processing. Background processing is introduced later (US-05).
- This story supports the upload types defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3; format expansion is introduced via later user stories.
- The end-user upload experience (dropzone, feedback copy, error messages) is introduced in US-21.

**Authoritative References**
- Tech: API surface + upload requirements + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Derived document status: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A1.2
- Tech: Filesystem rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B5

**Test Expectations**
- Uploading a supported type succeeds and persists the document.
- Uploading an unsupported type fails with the normative error contract.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-02 — View document status

**Status**: Implemented (2026-02-16)

**User Story**
As a user, I want to see the current status of a document so that I understand its processing state.

**Acceptance Criteria**
- I can view the current derived status of a document at any time.
- I can see whether processing has succeeded, failed, or timed out.
- If processing fails, the UI can explain the failure category in non-technical terms.
- Pending review and schema governance concepts never block veterinarians and are not exposed in veterinarian UI.

**Scope Clarification**
- This story does not start or control processing.
- This story does not expose run history or per-step details (US-11 covers history).

**Authoritative References**
- Tech: Derived status rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A1.2
- Tech: Failure types and mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C3
- UX: Separation of responsibilities: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 1 and 8

**Test Expectations**
- Derived status matches the latest run state across all states.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-03 — Download / preview original document

**Status**: Implemented (2026-02-16)

**User Story**
As a user, I want to download and preview the original uploaded document so that I can access the source material.

**Acceptance Criteria**
- I can access the original uploaded file for a document.
- Preview is supported for PDFs.
- If the stored file is missing, the system returns the normative missing-artifact behavior.
- Accessing the original file is non-blocking and does not depend on processing success.

**Scope Clarification**
- This story does not implement evidence overlays or highlighting.

**Authoritative References**
- Tech: API surface + errors: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Filesystem artifact rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B5

**Test Expectations**
- Successful download works for an uploaded document.
- Missing artifact behavior matches the Technical Design contract.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-04 — List uploaded documents and their status

**Status**: Implemented (2026-02-16)

**User Story**
As a user, I want to list uploaded documents and see their status so that I can navigate my work.

**Acceptance Criteria**
- I can see a stable list of documents.
- Each item includes basic metadata and derived status.
- The list remains accessible regardless of processing state.

**Scope Clarification**
- This story does not add filtering/search (future concern).

**Authoritative References**
- Tech: Listing semantics and run resolution: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.1
- Tech: Derived status rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A1.2

**Test Expectations**
- Documents with no runs show the correct derived status.
- Documents with queued/running/latest terminal runs show the correct derived status.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-05 — Process document

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want uploaded PDF documents to be processed automatically so that I can review the system’s interpretation without changing my workflow.

**Acceptance Criteria**
- Processing starts automatically after upload and is non-blocking (PDF).
- I can see when a document is processing and when it completes.
- If processing fails or times out, failure category is visible.
- I can manually reprocess a document at any time.
- Each processing attempt is traceable and does not overwrite prior runs/artifacts.

**Scope Clarification**
- Processing follows the execution model defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B1.
- This story does not introduce external queues or worker infrastructure; processing runs in-process and is non-blocking.
- This story does not require OCR for scanned PDFs; extraction relies on embedded text when available.
- This story does not execute multiple runs concurrently for the same document.

**Authoritative References**
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C
- Tech: Reprocess endpoint and idempotency rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3 + Appendix B4
- Tech: Extraction library scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E

**Test Expectations**
- Upload triggers background processing without blocking the request.
- Reprocess creates a new run and preserves prior runs/artifacts.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-21 — Upload medical documents (end-user UI)

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to upload medical documents through a proper application interface — without needing Swagger, curl, or any developer tool — so that the system can start processing them.

**Acceptance Criteria**
- The UI provides a clear upload affordance (dropzone / file picker) accessible to non-technical users.
- The UI clearly communicates which document formats are supported (PDF only for the current scope).
- After submitting a document, the UI provides clear success/failure feedback without exposing internal technical details.
- The UI communicates that processing is assistive and may be incomplete, without blocking the user.
- When automatic processing-on-upload is enabled (US-05), uploading via the UI triggers that flow non-blockingly; the UI relies only on the API response and derived status rules.

**Scope Clarification**
- This story is **frontend-only**: it builds the end-user upload experience on top of the API delivered by US-01. No new endpoints or backend ingestion logic.
- Sequenced in Release 2 (after US-05) so the UI can show processing feedback states that depend on the processing pipeline existing.
- Limited to PDFs; additional formats are introduced only via dedicated format expansion stories.
- Does not add preview/rendering, raw-text visibility, or review/edit experiences.

**Authoritative References**
- UX: Global upload experience and feedback heuristics: [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md)
- UX: Project interaction contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 1–4
- UX: User-facing copy tone: [`docs/shared/01-product/brand-guidelines.md`](../../../shared/01-product/brand-guidelines.md)
- Tech: API contract consumed by the UI: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2

**Test Expectations**
- Upload via the UI succeeds for supported PDFs and shows the expected feedback states.
- Upload failure cases render user-friendly messages without leaking internal details.
- Upload triggers background processing without blocking the UI (per the processing model).

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-11 — View document processing history

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to see the processing history of a document so that I can understand which steps were executed and whether any failures occurred.

**Acceptance Criteria**
- I can see a chronological history of processing runs and their steps.
- Each step shows status and timestamps.
- Failures are clearly identified and explained in non-technical terms.
- The history is read-only and non-blocking.

**Scope Clarification**
- This story does not introduce actions from the history view.

**Authoritative References**
- Tech: Processing history endpoint contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3.1
- Tech: Step artifacts are the source of truth: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C4

**Test Expectations**
- History reflects persisted step artifacts accurately.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-06 — View extracted text

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to view the raw text extracted from a document so that I understand what the system has read before any structured interpretation is applied.

**Acceptance Criteria**
- I can view extracted raw text for a completed run (expected for PDFs).
- The UI distinguishes “not ready yet” vs “not available (e.g., extraction failed)” without blocking workflow.
- Raw text is hidden by default and shown on demand in no more than one interaction.
- Raw text is clearly framed as an intermediate artifact, not ground truth.

**Scope Clarification**
- This story is read-only.

**Authoritative References**
- Tech: Raw-text artifact endpoint + “not ready vs not available” semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Extraction + language detection libraries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E

**Test Expectations**
- Raw text retrieval behaves correctly across run states and extraction failures.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-07 — Review document in context

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to review the system’s interpretation while viewing the original document so that I can verify it.

**Acceptance Criteria**
- I can see structured extracted data and the original document together.
- Confidence is visible and non-blocking (guides attention, not decisions).
- Evidence is available per field as page + snippet, accessible with minimal interaction.
- Highlighting in the document is progressive enhancement: review remains usable if highlighting fails.
- I can optionally view raw extracted text from the review context.
- Reviewer/governance concepts are not exposed to veterinarians.

**Scope Clarification**
- No approval/gating flows are introduced.
- This story does not require exact coordinate evidence.
- Review requires a completed run with an active interpretation; this is expected for PDFs (see Technical Design Appendix E).

**Authoritative References**
- UX: Review flow + confidence meaning: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 2–4
- Tech: Review endpoint semantics (latest completed run): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3.1
- Tech: Structured interpretation schema + evidence model: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D + D6
- Tech: Extraction/interpretation scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E

**Test Expectations**
- Review uses the latest completed run rules.
- Lack of a completed run yields the normative conflict behavior.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-38 — Mark document as reviewed (toggle)

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian reviewer, I want to mark a document as reviewed and unmark it later so that I can manage my review queue without losing my corrections.

**Acceptance Criteria**
- In document view, I can use a single action button labeled `Mark as reviewed`.
- When a document is marked reviewed:
  - The left sidebar item status indicator changes from the current dot to a checkmark.
  - The sidebar status label changes to `Reviewed` (instead of `Ready`).
  - Reviewed documents remain visible in the sidebar, visually separated (e.g., grouped under a `Reviewed` label/section) and visually muted.
- When a document is marked as Reviewed, structured data is rendered in read-only mode.
- Reopening is only possible from the document view using the explicit `Reopen` action.
- The sidebar checkmark is a visual indicator only and is not interactive.
- While Reviewed, structured data is read-only (no editing), safe interactions (e.g., text selection/copy) remain available without toasts, and a non-blocking informational toast is shown only on edit attempts.
- Visual styling clearly indicates non-editable state (e.g., muted text styling, no edit affordances).
- When reopened from the document view, the document returns to the non-reviewed state and re-enters the to-review subset.
- Toggling reviewed/reopened status does not remove or reset extracted/corrected field values.
- Reviewed status is independent from processing status.
- Reprocessing does not change review status.

**Scope Clarification**
- In scope: veterinarian-facing reviewed toggle behavior in document view and sidebar list status representation.
- In scope: reversible reviewed state transitions (`to_review` ↔ `reviewed`) from document view only, without field-value loss.
- In scope: reviewed documents remain discoverable in the sidebar via visual separation from the to-review subset.
- In scope: reviewed documents are non-editable until explicitly reopened.

**Out of Scope**
- Automatic reopening triggered by edits.
- Reopen interactions from the sidebar list/checkmark.
- Implicit state transitions from field interaction while reviewed.
- Reviewer/governance workflows or schema evolution behavior.

**UX Behavior**
- Primary action in document view: `Mark as reviewed`.
- Reviewed state is represented in sidebar list by non-interactive checkmark + `Reviewed` label, visually separated from the to-review subset and visually muted.
- While reviewed, structured data appears visually muted/non-editable and does not show edit affordances.
- Safe interactions (e.g., text selection/copy) do not show toasts; an edit attempt is any interaction that would enter edit mode or change a field value; only edit attempts show a non-blocking informational toast; reopening requires explicit `Reopen` in document view.
- Reopen from document view returns the document to the non-reviewed state and re-enters the to-review subset.
- Future enhancement (not required in this story): add a `Show reviewed` toggle to reveal reviewed items inline.

**Data / State Notes**
- Persist review state via `review_status` (`to_review` or `reviewed`).
- Persist `reviewed_at` timestamp when entering reviewed state.
- `reviewed_by` is optional and recorded when user identity is available.
- Reopen clears or updates reviewed-state metadata per authoritative contract while preserving extracted/corrected field content.

**Authoritative References**
- UX: Veterinarian review flow and status visibility: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 1, 4, and section **Review UI Rendering Rules (Global Schema Template)**.
- Product: Human-in-the-loop and non-blocking workflow principles: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) Sections 2 and 5.
- Tech: Review status model and transition rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A1.3 + Appendix B4.

**Test Expectations**
- Sidebar status icon/label switches correctly between non-reviewed and reviewed states.
- Mark reviewed keeps the document visible in the sidebar, visually separated from the to-review subset and visually muted.
- Reopen from document view returns the document to the non-reviewed state and re-enters the to-review subset.
- While reviewed, fields are non-editable; safe interactions (e.g., text selection/copy) do not show toasts; edit attempts trigger a non-blocking informational toast.
- Repeated toggle actions are idempotent and do not lose field edits/corrections.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-34 — Search & filters in Structured Data panel

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian, I want to quickly narrow down structured fields using search and simple filters so that I can focus on the most relevant data during review.

**Acceptance Criteria**
- A compact control bar is available under the `Datos estructurados` header.
- The control bar includes:
  - Search input with a magnifying-glass icon.
  - Confidence filter chips: `Baja`, `Media`, `Alta`.
  - Toggles: `Solo CRÍTICOS`, `Solo con valor`.
- Filtering applies to rendered Global Schema fields in fixed order.
- Search is case-insensitive and matches field label, schema key, and rendered value (when present).
- Confidence bucket semantics are:
  - `Baja` when confidence < 0.50
  - `Media` when confidence is 0.50–0.75
  - `Alta` when confidence >= 0.75
- Filters combine with logical AND.
- Repeatable fields:
  - Match search when at least one item matches.
  - Match `Solo con valor` when list length is > 0.
- Section behavior:
  - Without filters/search, all sections are shown.
  - With any filter/search active, sections with 0 matches are hidden/collapsed.
- If no fields match, the panel shows: `No hay resultados con los filtros actuales.`
- Search uses debounce between 150 and 250 ms.

**Scope Clarification**
- This story does not change Global Schema keys or ordering.
- This story does not add or modify endpoints.
- This story does not change interpretation persistence semantics.
- Changes should remain localized to the review panel UI and related filtering logic.

**Authoritative References**
- Product: Canonical field authority and order: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) section **Global Schema (Canonical Field List)**.
- UX: Review rendering baseline and deterministic missing/empty behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) section **Review UI Rendering Rules (Global Schema Template)**.
- Brand: UI controls and visual consistency: [`docs/shared/01-product/brand-guidelines.md`](../../../shared/01-product/brand-guidelines.md).
- Frontend context: review rendering backbone: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](frontend-implementation.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Unit tests cover search matching behavior (label/key/rendered value).
- Unit tests cover confidence bucket classification boundaries.
- Review panel keeps Global Schema order deterministic while filters are applied.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-35 — Resizable splitter between PDF Viewer and Structured Data panel

**Status**: Implemented (2026-02-16)

**User Story**
As a veterinarian reviewer, I want to resize the PDF and structured-data panels so that I can optimize my workspace for reading the document or validating fields.

**Objective**
- Make side-by-side review adaptable to desktop monitor sizes and reviewer tasks without introducing new workflow modes.

**Acceptance Criteria**
- A vertical splitter handle allows pointer drag resizing between the PDF Viewer and Structured Data panels.
- The splitter has a generous hit area and resize cursor.
- Sane width constraints are enforced:
  - PDF panel has a minimum width that preserves readability.
  - Structured panel has a minimum width that preserves field readability.
  - Neither panel can be resized to fully collapse the other.
- Default layout can be restored via double-click on the splitter handle.
- Reset behavior is provided via double-click on the splitter handle (without an additional reset button).
- Preferred behavior: persist split ratio in local storage so it survives page refresh on the same device.
- Resizing keeps Global Schema rendering deterministic (field order/position remains canonical).
- Resizing does not break panel scroll/focus behavior and does not interfere with PDF interactions or structured data filtering/search.
- Any icon-only control introduced for splitter actions includes an accessible name.

**Scope Clarification**
- This story keeps the existing three-area layout (documents sidebar, PDF Viewer, structured data panel).
- This story is limited to review-layout resizing behavior and local persistence.
- This story does not change endpoint contracts, persistence schema, or interpretation semantics.

**Out of Scope**
- New review modes, alternate workflows, or additional panel types.
- Reordering/redefining Global Schema fields.
- Non-desktop-specific layout redesign.

**UX Notes**
- The splitter should be subtle at rest and more visible on hover/focus.
- Dragging must feel stable and avoid jitter or layout jumps.
- Interaction should remain fast and tool-like.

**Edge Cases**
- Very narrow container widths should gracefully clamp to a safe split.
- Loading/empty/error states must keep layout integrity and not break splitter behavior.
- Pinned source panel mode must keep splitter behavior stable for PDF vs Structured Data.

**Authoritative References**
- UX: Side-by-side review interaction baseline: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 2–4.
- Product: Global Schema canonical ordering invariants: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) section **Global Schema (Canonical Field List)**.
- Frontend context: review rendering backbone and deterministic structure: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](frontend-implementation.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Splitter drag updates panel widths while honoring min/max constraints.
- Default reset behavior restores baseline split.
- Stored split ratio is restored on reload when available and valid.
- Structured panel keeps deterministic Global Schema order under resize and existing filters.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-36 — Lean design system (tokens + primitives)

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian reviewing claims, I want a consistent UI foundation (tokens and reusable primitives) so that interactions remain predictable and future editable-field work does not introduce visual drift.

**Objective**
Introduce a minimal, consistent UI foundation to prevent ad-hoc styling and enable editable structured fields without UI drift.

**Acceptance Criteria**
- All UI work touched in this story uses design tokens (no scattered hex values in implementation files).
- Icon-only interactive controls are implemented via `IconButton` with required `label`; raw icon-only `<button>` / `<Button>` are forbidden unless documented as explicit allowlisted exceptions.
- Tooltip behavior is standardized (top placement + portal rendering to avoid clipping) and remains keyboard-accessible.
- At least one key review area adopts the primitives and wrappers (viewer toolbar icon actions + one structured-data section).
- Document status indicators are unified through a reusable `DocumentStatusCluster`, with the primary signal in the document list/sidebar and no redundant duplicate status surfaces.
- `docs/projects/veterinary-medical-records/01-product/design-system.md` exists and is linked from project docs navigation.
- Design-system guidance is reflected consistently in operational assistant modules.
- CI/local design-system check exists and runs.

**Scope Clarification**
- Define and wire a lean token set (surfaces/backgrounds, text, borders, spacing, radius, subtle shadow, semantic statuses for confidence/critical/missing).
- Ensure shadcn/ui + Radix-based primitives are available and used for button, tooltip, tabs, separator, input, toggle-group, and scroll-area.
- Add lightweight app wrappers: `IconButton`, `Section` / `SectionHeader`, `FieldRow` / `FieldBlock`, `ConfidenceDot`, `CriticalBadge`, `RepeatableList`.
- Add and adopt `DocumentStatusCluster` for consistent document status rendering in sidebar/list as the primary status signal.
- Migrate only touched review areas needed to prove adoption.

**Out of Scope**
- Full UI redesign.
- Broad re-theming beyond the minimum token setup.
- Large refactors of unrelated screens.

**Authoritative References**
- UX: Review interaction contract and confidence behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Sections 2–4 and section **Review UI Rendering Rules (Global Schema Template)**.
- Shared UX boundaries: [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md).
- Brand constraints and tokenization requirement: [`docs/shared/01-product/brand-guidelines.md`](../../../shared/01-product/brand-guidelines.md).
- Design system implementation contract: [`docs/projects/veterinary-medical-records/01-product/design-system.md`](design-system.md).

**Test Expectations**
- Design-system guard script flags forbidden patterns and passes on compliant code.
- Viewer toolbar icon actions and structured-data field rendering continue to function with wrappers.
- Tooltips remain keyboard accessible and visible without clipping.
- Unified Document Status Cluster renders consistent status semantics in sidebar/list without redundant duplicate status messaging.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Lint/tests pass for touched frontend scope.
- Docs updated and normalized.
- PR summary verifies each acceptance criterion.

---

## US-08 — Edit structured data

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want to edit structured information extracted from a document so that it accurately reflects the original document.

**Acceptance Criteria**
- I can edit existing fields.
- I can create new fields.
- I can see which fields I have modified.
- Edits are immediate and local to the current document; no extra steps exist “to help the system”.
- Editing never blocks on confidence.
- Reprocessing resets edits by creating a new run and new machine output.

**Scope Clarification**
- This story covers veterinarian edits only.
- No reviewer workflow or schema evolution UI is introduced here.
- Editing applies to runs that have an active interpretation; this is expected for PDFs (see Technical Design Appendix E).

**Authoritative References**
- Tech: Versioning invariants (append-only interpretations): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A3 + Appendix B2.4
- Tech: Field change log contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.5
- Tech: Edit endpoint contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3.1
- UX: Immediate local correction, no extra feedback steps: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Section 4
- Tech: Extraction/interpretation scope (PDF): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E

**Test Expectations**
- Each edit produces a new interpretation version and appends change-log entries.
- Editing is blocked only by the authoritative “active run” rule.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-09 — Capture correction signals

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want the system to record my normal corrections as append-only signals so the system can improve later, without asking me for feedback.

**Acceptance Criteria**
- Corrections do not require extra steps.
- Recording signals does not change system behavior.
- No confidence adjustment is visible or used for decisions.
- No new veterinarian UI is introduced for “learning” or “feedback”.

**Scope Clarification**
- Capture-only in this story: no confidence adjustment, no model training, no schema changes.

**Authoritative References**
- Product: Learning and governance principles: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) Section 6
- Tech: Field change log is append-only and can serve as correction signal storage: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.5
- UX: No explicit feedback flows: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Section 4

**Test Expectations**
- Corrections are persisted append-only and do not alter current review/edit workflows.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-41 — Show Top-5 Candidate Suggestions in Field Edit Modal

**Status**: Implemented (2026-02-19)

**User Story**
As a veterinarian reviewer, I want to see a small list of alternative extracted candidates when editing a field, so that I can correct values faster by selecting a suggestion while still being able to type any manual correction.

**Acceptance Criteria**
Data contract (standard review payload)
- The standard review payload includes optional per-field `candidate_suggestions` as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) section **Field Candidate Suggestions (standard review payload)**.
- Backwards compatible: clients MAY ignore `candidate_suggestions`.

UI (existing edit modal only)
- In the existing field edit modal, when `candidate_suggestions` exist for the field (and there is at least one alternative different from the current displayed value; trimmed string equality), show a section:
  - Title: `Sugerencias (N)`
  - Subtitle: `Selecciona una sugerencia o escribe tu propia corrección.`
- Show up to 5 candidates in a compact clickable list (per Technical Design; current max length is 5).
- The top-1 candidate is labeled `Sugerido`.
- Clicking a candidate copies its value into the input (does not auto-save).
- The input remains fully editable; manual typing overrides any prior selection.
- Validation behavior remains unchanged: Save remains disabled unless existing `validateFieldValue(...)` is OK.
- If there are no candidates (or only the current value), the `Sugerencias` section is not shown.

No layout disruption
- Global Schema layout remains stable; do not add inline expansion in the report view. Only the edit modal changes.

**Scope Clarification**
- Does not change confidence computation logic, confidence tooltip breakdown, or `mapping_confidence` semantics.
- Does not add new review modes or new screens.
- Does not add new validation rules; reuses existing validators/normalizers.
- Candidates may be derived from existing debug candidate logic, but must be surfaced via the standard payload contract referenced above (not gated by debug env flag).

**Authoritative References**
- [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)
- [`docs/projects/veterinary-medical-records/01-product/design-system.md`](design-system.md)
- [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md)
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) section **Field Candidate Suggestions (standard review payload)**

**Test Expectations**
Backend:
- Unit tests verify ordering, truncation to max length 5, and optional presence (per Technical Design contract).
Frontend:
- Tests verify suggestions render only when present, click copies value, manual typing works, and validation/save-disable remains unchanged.

**Definition of Done (DoD)**
- Acceptance criteria met.
- No regressions in report-like density (no new always-visible blocks).
- Backend + frontend tests added/updated per repo conventions.

---

## US-10 — Change document language and reprocess

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
- Tech: Language detection rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E
- Tech: Language override endpoint + rules: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.1
- Tech: Run persistence of `language_used`: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.2

**Test Expectations**
- New runs created after setting an override persist the overridden `language_used`.
- Existing runs remain unchanged.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-32 — Align review rendering to Global Schema template

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want the review view to always use the full Global Schema template so that scanning is consistent across documents.

**Acceptance Criteria**
- The UI renders the complete Global Schema in fixed order and by sections, regardless of how many fields were extracted.
- Non-extracted keys render explicit placeholders (no blank gaps).
- While structured data is loading, the UI shows a loading state and does not render missing placeholders yet.
- Repeatable fields render as lists and show an explicit empty-list state when no items are present.
- Extracted keys outside Global Schema are rendered in a separate section named `Other extracted fields`.
- Veterinarian-facing copy does not expose governance terminology such as `pending_review`, `reviewer`, or `governance`.

**Scope Clarification**
- This story does not introduce new endpoints.
- This story does not change persistence schema.
- This story does not redefine error codes.
- This story does not change run semantics; it defines review rendering behavior only.

**Authoritative References**
- Product: Global schema authority and field list: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) section **Global Schema (Canonical Field List)**.
- UX: Rendering and placeholder behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) section **Review UI Rendering Rules (Global Schema Template)**.
- Tech: Structured interpretation schema and partial payload boundary: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D.
- Frontend implementation notes: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](frontend-implementation.md) section **Review Rendering Backbone (Global Schema)**.

**Test Expectations**
- Review screens always show the same section/key structure, independent of extraction completeness.
- Missing scalar values, missing repeatable values, and loading states are visually distinguishable and deterministic.
- Non-schema extracted keys are visible under `Other extracted fields`.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-44 — Medical Record MVP: Update Extracted Data panel structure, labels, and scope

**Status:** Implemented (2026-02-20)  
**Owner:** Platform / Frontend (UX-led)  
**Type:** UX/UI behavior + mapping (contract-driven)

### User Story
As a **veterinarian reviewer**,  
I want the “Extracted Data / Informe” panel to present a **clinical medical record** with clear sections and field labels,  
so that I can review and edit clinical information quickly in a clinical-only panel.

### Scope

**In scope**
1) **Panel purpose and scope (MVP)**
  - The Extracted Data panel represents a **clinical Medical Record**.
  - The panel is clinical-only.

2) **Section structure (MVP)**
  - The panel renders sections in this exact order:
    1) **Centro Veterinario**
    2) **Paciente**
    3) **Propietario**
    4) **Visitas**
    5) **Notas internas**
    6) **Otros campos detectados**
    7) **Detalles del informe**

3) **Field label changes (display-only)**
  - Display labels are updated for clarity in the review panel.
  - “NHC” is shown as **NHC** with tooltip “Número de historial clínico”.

**Out of scope**
- Introducing new clinical extraction logic beyond what the contract already provides.
- Normalizing clinical terms (e.g., SNOMED coding) in MVP UI.
- Any non-clinical claim UI (this story explicitly excludes it).

### Acceptance Criteria

1) The reviewer sees the Extracted Data panel as a **clinical-only** view, without financial/claim concepts.
2) The reviewer sees the seven sections in this exact order: Centro Veterinario, Paciente, Propietario, Visitas, Notas internas, Otros campos detectados, Detalles del informe.
3) The reviewer sees updated labels in the panel:
  - “Identificación del caso” is shown as “Centro Veterinario”.
  - Clinic and owner names are shown as “Nombre”.
  - Address fields are shown as “Dirección”.
  - Date of birth is shown as “Nacimiento”.
4) The reviewer sees “NHC” with tooltip “Número de historial clínico”.
5) If NHC is expected but no value is available, the reviewer still sees the NHC row with placeholder “—”.
6) In “Propietario”, “Dirección” shows an address value; identifier-like values are not presented as addresses.
7) The reviewer sees “Otros campos detectados” as a separate section for additional detected data.
8) The reviewer sees “Visitas” grouped by visit, without mixed data between different visits.

### Story-specific technical requirements
- Keep contract authority in `docs/projects/veterinary-medical-records/02-tech/technical-design.md` (Appendix D9 or equivalent authoritative section); do not redefine contract structure in this plan.
- Keep copy/labels/empty states aligned with `docs/projects/veterinary-medical-records/01-product/ux-design.md`.
- Use contract-driven rendering for visit grouping and “Otros campos detectados”; no UI-side heuristics or reclassification.
- If required contract capabilities are missing (e.g., explicit “other” bucket or owner address concept), this story is blocked until TECHNICAL_DESIGN is updated and backend output is aligned.
- Add/adjust UI tests for section order, clinical-only scope, NHC behavior, and owner address labeling.

### Dependencies / Placement
- Depends on UX copy/spec being updated in `docs/projects/veterinary-medical-records/01-product/ux-design.md`.
- **Placement:** implement **US-44 before US-43** (US-44 remains separate).

---

## US-43 — Render “Visitas” agrupadas cuando `canonical contract` (contract-driven, no heuristics)
**Status:** Planned  
**Owner:** Platform / Frontend

### User Story
Como **veterinario revisor**, quiero ver los datos clínicos **agrupados por visita** cuando un documento contiene múltiples visitas, para revisar cada episodio de forma clara y evitar mezclar información de visitas distintas.

### Scope
In scope:
1) For documents with multiple visits, the reviewer sees a separate block per visit in the “Visitas” section.
2) The reviewer sees visit information only inside its visit block, and non-visit document information outside visit blocks.
3) Information is not mixed across visit blocks.
4) Visit order is stable and consistent for the reviewer.
5) Search and filters only affect row visibility within existing containers and do not change visit grouping.
6) Review status (“reviewed/not reviewed”) continues to apply at document level.
7) Clinical-only scope: this story does not include financial or billing concepts.

Out of scope:
- UI heuristics to infer visits or move items.
- “Reviewed per visit”.
- Backend changes beyond the existing canonical visit-grouped contract.

### Acceptance Criteria
1) When multiple visits exist, the reviewer sees one block per visit in the “Visitas” section.
2) Each visit block shows only information for that visit and does not mix information from other visits.
3) Information shown outside visit blocks is not repeated inside any visit block.
4) Visit order is deterministic and remains stable across reloads for the same document.
5) If an “unassigned” block exists, the reviewer sees it as a differentiated block with UX-defined copy.
6) If no visits are detected, the reviewer sees the UX-defined empty state for “Visitas”.
7) Search and filters do not change visit grouping or block order.
8) The review workflow remains document-level.
9) For documents without visit structure, the current experience remains without visible regressions.

### Story-specific technical requirements
- Mantener la autoridad de contrato en `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9; no redefinir payloads en esta historia.
- Contract-driven rendering and placement boundaries must follow `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9.
- Implementar render sin heurísticas: no crear, fusionar, reasignar ni inferir visitas desde frontend.
- Mantener reglas de separación entre datos de documento y datos de visita según D9.
- Mantener comportamiento de search/filter de US-34 sin reagrupación.
- Añadir cobertura de pruebas para orden estable, bloque sin asignar, estado vacío de visitas y regresión de experiencia vigente.

### Authoritative References
- `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9
- `docs/projects/veterinary-medical-records/01-product/ux-design.md`

---

## US-45 — Visit Detection MVP (Deterministic, Contract-Driven Coverage Improvement)

**Status:** Implemented (2026-02-21)

### Context / Problem
With US-43, the UI is strictly contract-driven: it renders `active_interpretation.data.visits[]` when `canonical contract`, without inferring or grouping visits client-side.

Current issue: in documents that visually contain multiple episodes/visits, the backend often returns only:
- `visits = [{ visit_id: "unassigned", ... }]`
or an empty grouping, making “Extracted Data > Visits” operationally unhelpful.

This is a backend grouping coverage issue, not a UI issue.

### Objective
Improve coverage of the `Structured Interpretation Schema (visit-grouped)` contract so that:

When there is sufficient deterministic evidence of distinct clinical episodes, the backend produces real VisitGroups (`visit_id != "unassigned"`) with `visit_date` populated when appropriate, preserving determinism and safety.

This story does NOT guarantee “≥1 visit” for all documents.
If evidence is insufficient, it is correct for everything to remain in `unassigned`.

### User Story
As a veterinarian reviewer,
I want the Visits section to show clinical episodes grouped when the document contains clear evidence of multiple visits,
so I can review and edit information per episode with lower cognitive load and better clinical context.

### Scope (MVP)

In scope
1) Deterministic visit detection (backend)
- If the document contains sufficient evidence of at least one identifiable clinical episode:
  - Backend produces `visits[]` with ≥ 1 group where `visit_id != "unassigned"`.
  - `visit_date` is populated when supported by the “sufficient evidence” definition in TECHNICAL_DESIGN.
- If evidence is insufficient:
  - Everything remains in `unassigned`.

2) Assignment of visit-scoped fields
- Visit-scoped fields (per TECHNICAL_DESIGN Appendix D9) should be placed into `visits[].fields[]` when assignment is consistent.
- If a field cannot be associated with sufficient evidence or is ambiguous:
  - it falls into `unassigned`.

3) Determinism (same input → same output)
- Same input yields the same `visits[]` structure (IDs, ordering, assignments), except for intentional pipeline changes.
- `visits[]` ordering follows the rules documented in TECHNICAL_DESIGN Appendix D9.

Out of scope
- High-coverage grouping of all visits.
- Complex ambiguity resolution beyond contract-defined basic rules.
- ML/LLM inference for visits.
- UI changes (contract-driven rendering is covered by US-43).

### Contractual rules / Non-negotiables
- UI does not invent visits or regroup data.
- Anything not assignable with sufficient evidence → `unassigned`.
- `visit_date` is VisitGroup metadata (not a field in `fields[]`).
- This story references (does not redefine) the canonical visit-grouped contract in TECHNICAL_DESIGN Appendix D9.

### Acceptance Criteria (testable)

1) Agreed multi-visit fixture
- Given a stable fixture (PDF or equivalent) with multiple visits and clear clinical dates,
- When processed,
- Then `active_interpretation.data.visits[]` contains at least one group with:
  - `visit_id != "unassigned"`,
  - and `visit_date` populated when supported by the “sufficient evidence” definition in TECHNICAL_DESIGN.

2) No structural scoping regression
- No visit-scoped keys appear in `data.fields[]` (per TECHNICAL_DESIGN Appendix D9).
- Visit-scoped keys appear in `visits[].fields[]` or in `unassigned` (based on evidence/assignment).

3) UI outcome
- In Visits, the user sees at least one “Visit <date>” block when the contract produces an assigned VisitGroup, plus the “Unassigned” block if applicable.

4) Determinism
- Reprocessing the same fixture yields the same `visits[]` structure (IDs, order, assignments).

5) Regression guardrail
- A backend integration test fails if, for the agreed fixture, everything ends up in `unassigned`.

### Dependencies
- Define and version a stable multi-visit fixture.
- TECHNICAL_DESIGN must document what constitutes “sufficient evidence” to create a VisitGroup and populate `visit_date` (do not define it in this US).

### Risks / Watch-outs
- False positives by confusing dates (DOB, report issue date, invoice date) with clinical visit dates.
- Documents with multiple dates but a single clinical episode (over-segmentation).
- Extraction/canonicalization changes causing regressions; guardrail must catch it.

---

## US-46 — Deterministic Visit Assignment Coverage MVP (Schema)

**Status:** Planned  
**Owner:** Platform / Backend (contract-driven)

### Context
- US-43: UI renders `visits[]` contract-driven (no client-side grouping).
- US-45 (implemented): backend can create assigned VisitGroups when sufficient deterministic evidence exists, with safe fallback to `unassigned`.
- Current problem: even when multiple visits exist, relevant clinical information still appears as “unassigned/not associated to a visit”, reducing coherence and increasing cognitive load.

### Objective
Improve clinical coherence per visit by safely increasing the proportion of visit-scoped clinical information shown under the correct visit **when evidence is consistent**, without weakening safety.

### User Story
As a veterinarian reviewer,  
I want to see visit-scoped clinical fields (per TECHNICAL_DESIGN Appendix D9; e.g., diagnosis/medication/procedure when present) within the correct visit when evidence allows it,  
so I can review each episode with clear clinical context and lower cognitive load.

### Scope (MVP)

**In scope**
- Improve deterministic assignment of visit-scoped clinical fields to **existing** VisitGroups (created by US-45), only when evidence is consistent.
- Preserve the possibility that some information remains in the `unassigned` bucket when evidence is insufficient.

**Out of scope**
- Creating new VisitGroups or changing how they are created (owned by US-45).
- Advanced ambiguity resolution beyond the deterministic criteria documented in TECHNICAL_DESIGN.
- ML/LLM.
- UI changes (beyond contract-driven rendering already covered by US-43).

### Acceptance Criteria (testable)

**User-facing**
1) **Per-visit coherence**
- Given a document with multiple visits and an assigned VisitGroup present,
- When I open the “Visits” section,
- Then I see visit-scoped clinical fields (per D9; e.g., diagnosis/medication/procedure when present) inside specific visits when evidence supports it, instead of all being shown under the unassigned bucket.

2) **Transparency when evidence is insufficient**
- If some visit-scoped fields cannot be clearly associated to a visit,
- Then they remain shown under the unassigned bucket (label/copy as defined in `docs/projects/veterinary-medical-records/01-product/ux-design.md`), without forcing doubtful assignments.

3) **Measurable improvement (fixture-bound + frozen baseline)**
- Define a stable fixture `mixed_multi_visit_assignment` and a versioned baseline expected-output snapshot.
- On that fixture, increase by **≥ +2** the number of visit-scoped fields moved from unassigned to assigned visits (vs the frozen baseline).
- Ensure at least **1** key clinical field (diagnosis/medication/procedure when present with sufficient evidence) is assigned to a **non-unassigned** VisitGroup.

4) **Reproducibility**
- Reprocessing the same fixture yields the same VisitGroups and the same field→visit assignments.

**Non-user-facing guardrails (testable)**
5) **No new visits created**
- For the agreed fixture, the set of VisitGroups (visit_ids/dates and ordering) must remain unchanged vs the frozen baseline snapshot.

6) **No leakage**
- Visit-scoped keys (per D9) must not appear in top-level `data.fields[]`; they must appear only in `visits[].fields[]` or in the unassigned bucket.

7) **Safety guardrail**
- Administrative/non-visit dates (DOB, report/invoice emission, microchip/admin identifiers, etc.) must not force visit assignment.

8) **Regression guardrail**
- Integration test fails if:
  - there is no improvement vs baseline, or
  - new visits are created for the fixture, or
  - leakage occurs to `data.fields[]`, or
  - administrative contexts force assignment.

### Documentation Requirement
- Document the deterministic assignment criteria in `docs/projects/veterinary-medical-records/02-tech/technical-design.md` (Appendix D9 or an adjacent note). This story references the contract; it does not redefine it.

### Authoritative References
- `docs/projects/veterinary-medical-records/02-tech/technical-design.md` — Appendix D9 (visit grouping + visit-scoped keys + ordering rules)
- `docs/projects/veterinary-medical-records/01-product/ux-design.md` — unassigned label/copy and any relevant empty-state or wording

---

## US-39 — Align veterinarian confidence signal with mapping confidence policy

**Status**: Implemented (2026-02-17)

**User Story**
As a veterinarian, I want confidence dots/colors in the review UI to reflect mapping confidence policy so that the signal is consistent, explainable, and reliable for triage.

**Acceptance Criteria**
- Existing confidence dots/colors in veterinarian UI represent `field_mapping_confidence` (not candidate/legacy confidence).
- Low/medium/high confidence bands are derived from backend-provided `policy_version` + confidence band cutoffs.
- The UI does not use hardcoded confidence thresholds.
- If `policy_version` or confidence band cutoffs are missing, UI does not crash, explicitly indicates missing policy configuration (degraded mode), and emits a diagnostic/telemetry event without inventing fallback thresholds.

**Scope Clarification**
- This story aligns veterinarian-facing confidence semantics and display only.
- This story does not redefine policy contracts, persistence shape, or backend threshold logic.
- This story depends on the backend exposing `policy_version` + confidence band cutoffs in the document/schema payload per [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md).

**Authoritative References**
- Product: Confidence meaning and veterinarian-facing signal intent: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md).
- UX: Confidence visualization behavior in review surfaces: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md).
- Tech: Policy-provided confidence configuration and response semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md).
- Frontend context: Confidence rendering implementation points: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](frontend-implementation.md).

**Test Expectations**
- Confidence dot/color mapping uses `field_mapping_confidence` with backend-provided confidence band cutoffs.
- Missing policy configuration triggers explicit degraded-mode UI behavior and a diagnostic/telemetry event without app crash.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-40 — Implement field-level confidence tooltip breakdown

**Status**: Implemented (2026-02-18)

**User Story**
As a veterinarian, I want to understand why a field confidence looks the way it does so I can triage and review faster.

**Acceptance Criteria**
- Tooltip renders consistently for all fields that expose confidence dot/band.
- Tooltip is implemented with the shared wrapper and is keyboard accessible on focus/hover.
- Tooltip shows overall confidence percentage, explanatory copy, and breakdown lines for candidate confidence and review history adjustment.
- Adjustment semantic styling follows positive/negative/zero rules using existing tokens/classes.
- Edge cases are rendered deterministically: no history shows adjustment `0`; missing extraction reliability shows `No disponible`.
- Dot/band behavior remains unchanged and continues to use `field_mapping_confidence` as the primary visible signal.
- Confidence computation/propagation behavior is unchanged.
- Tooltip copy and structure align with [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) section **4.3 Confidence Tooltip Breakdown (Veterinarian UI)**.

**Scope Clarification**
- Implements the confidence tooltip pattern defined in UX + Design System for veterinarian review fields.
- `field_mapping_confidence` remains the primary visible signal (dot + band); tooltip is explanatory.
- Frontend consumes backend-provided breakdown values as render-only input.
- This story does not change confidence computation or propagation.
- This story does not add analytics/chart views, document-level confidence policy UI, recalibration mechanics, field reordering, layout shifts, or governance terminology in veterinarian-facing copy.

**Data Assumptions / Dependencies**
- Review payload includes field-level `field_mapping_confidence` (0–1).
- Review payload may include `text_extraction_reliability` (0–1, nullable); it must not be inferred from `candidate_confidence`.
- Review payload includes deterministic `field_review_history_adjustment` (signed percentage points), with `0` when no history is available.
- Exact payload shape and sourcing are governed by the authoritative technical docs referenced below.

**Out of Scope**
- Calibration/policy management UI.
- Document-level confidence policy UI.
- Charts, analytics, or historical dashboards.
- Recalibration logic changes or any confidence algorithm change.

**Authoritative References**
- UX tooltip contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) section **4.3 Confidence Tooltip Breakdown (Veterinarian UI)**.
- Design system tooltip pattern: [`docs/projects/veterinary-medical-records/01-product/design-system.md`](design-system.md).
- Technical contract and visibility invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md).
- Backend sourcing responsibilities: [`docs/projects/veterinary-medical-records/02-tech/backend-implementation.md`](backend-implementation.md).
- Frontend rendering responsibilities: [`docs/projects/veterinary-medical-records/02-tech/frontend-implementation.md`](frontend-implementation.md).

**Test Expectations**
- Confidence tooltip appears on all confidence-bearing fields with consistent structure and accessibility behavior.
- Positive/negative/zero adjustment styling uses existing semantic tokens/classes with no new color system.
- No-history and missing-extraction edge cases render as defined without fallback computation in frontend.
- No regressions to existing dot/band behavior, field ordering, or review interaction flow.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-13 — Review aggregated pending structural changes

**User Story**
As a reviewer, I want to review aggregated pending structural changes so that I can validate or reject schema-level evolution based on recurring patterns.

**Acceptance Criteria**
- I can see pending structural change candidates grouped by pattern, not by individual documents.
- Each candidate includes summary, occurrence counts, and representative evidence.
- This review flow never blocks veterinarians or document processing.
- This flow is reviewer-facing only and not exposed in veterinarian UI.

**Scope Clarification**
- No retroactive changes to past documents.

**Authoritative References**
- Product: Separation of responsibilities and governance boundary: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) Sections 5 and 4.3
- Tech: Governance invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A7
- Tech: Governance persistence + endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.8–B2.9 + Appendix B3.1

**Test Expectations**
- Candidates are isolated from document workflows and apply prospectively only.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-14 — Filter and prioritize pending structural changes

**User Story**
As a reviewer, I want to filter and prioritize pending structural changes so I can focus on the most impactful candidates.

**Acceptance Criteria**
- I can filter candidates by status and basic attributes.
- I can prioritize candidates by frequency and criticality.
- Filtering/prioritization never blocks veterinarians.

**Scope Clarification**
- This story does not introduce automatic decisions.

**Authoritative References**
- Product: Critical keys policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) CRITICAL_KEYS
- Tech: Critical concept derivation: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D7.4
- Tech: Governance endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3

**Test Expectations**
- Filters do not change underlying candidate data; they only change views.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-15 — Approve structural changes into the global schema

**User Story**
As a reviewer, I want to approve structural changes so that future interpretations use an updated canonical schema.

**Acceptance Criteria**
- I can approve a candidate.
- Approval creates a new canonical schema contract snapshot.
- Approved changes apply prospectively to new runs only.
- Past documents and past runs remain unchanged.
- Approval does not trigger implicit reprocessing.

**Scope Clarification**
- No automatic promotion without explicit reviewer action.

**Authoritative References**
- Tech: Schema contract persistence and current schema rule: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.7
- Tech: `schema_contract_used` persisted per run: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.2
- Tech: Governance invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A7

**Test Expectations**
- Approval creates a new schema contract snapshot and new runs use it.
- Existing runs retain their historical schema association.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-16 — Reject or defer structural changes

**User Story**
As a reviewer, I want to reject or defer structural changes so that unsafe or low-quality candidates do not become part of the canonical schema.

**Acceptance Criteria**
- I can reject a candidate.
- I can defer a candidate.
- Decisions are auditable and append-only.
- Decisions do not affect veterinarian workflows.

**Scope Clarification**
- Rejection/deferral does not delete candidate history.

**Authoritative References**
- Tech: Governance decision log: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.9
- Tech: Governance endpoints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3
- Tech: Governance invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A7

**Test Expectations**
- Decisions append to the audit trail and update candidate status consistently.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-17 — Govern critical (non-reversible) structural changes

**User Story**
As a reviewer, I want stricter handling for critical structural changes so that high-risk evolutions require deliberate review.

**Acceptance Criteria**
- Critical candidates are clearly distinguished from non-critical candidates.
- Critical candidates are not auto-promoted.
- Critical decisions are explicitly recorded and auditable.
- Critical governance is isolated from veterinarian workflows.

**Scope Clarification**
- No veterinarian friction is introduced.

**Authoritative References**
- Product: Critical concept policy: [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) Section 4
- Tech: Critical derivation rule: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D7.4
- UX: Sensitive changes never add veterinarian friction: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) Section 6

**Test Expectations**
- Critical designation affects reviewer prioritization only; it does not block veterinarian workflows.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-18 — Audit trail of schema governance decisions

**User Story**
As a reviewer, I want to see an audit trail of schema governance decisions so that structural evolution is transparent and traceable.

**Acceptance Criteria**
- I can see a chronological list of governance decisions.
- Each entry shows decision type, reviewer identity, and timestamp.
- The audit trail is read-only, immutable, and append-only.

**Scope Clarification**
- This story provides visibility only.

**Authoritative References**
- Tech: Governance decision log persistence: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B2.9
- Tech: Audit trail endpoint: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3
- Tech: Audit immutability and separation: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix A8

**Test Expectations**
- Audit trail ordering is chronological and records are immutable.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-19 — Add DOCX end-to-end support

**User Story**
As a user, I want to upload, access, and process DOCX documents so that the same workflow supported for PDFs applies to Word documents.

**Acceptance Criteria**
- I can upload supported `.docx` documents.
- I can download the original DOCX at any time without blocking on processing.
- DOCX documents are processed in the same step-based, non-blocking pipeline as PDFs (extraction → interpretation), producing the same visibility and artifacts.
- Review-in-context and editing behave the same as for PDFs once extracted text exists.

**Scope Clarification**
- This story changes format support only; the processing pipeline, contracts, versioning rules, and review workflow semantics remain unchanged.
- This story does not require preview for DOCX; if preview is unavailable, the UI must clearly fall back to download-only without blocking workflows.
- This story requires updating the authoritative format support contract in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) (supported upload types and any related filesystem rules).

**Authoritative References**
- Tech: Endpoint surface and error semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C
- UX: Review flow guarantees and rendering contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) sections **Confidence — UX Definition**, **Veterinarian Review Flow**, **Review-in-Context Contract**, and **Review UI Rendering Rules (Global Schema Template)**.

**Story-specific technical requirements**
- Add server-side type detection for DOCX based on server-side inspection.
- Add DOCX text extraction using a minimal dependency surface (choose one library during implementation and document the choice; candidates include `python-docx` or `mammoth`).
- Store the original under the deterministic path rules with the appropriate extension (e.g., `original.docx`).

**Test Expectations**
- DOCX inputs behave like PDFs for upload/download/status visibility.
- Extraction produces a raw-text artifact for DOCX runs, enabling the same review/edit endpoints once processing completes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-20 — Add Images end-to-end support

**User Story**
As a user, I want to upload, access, and process image documents so that scans and photographs can be handled in the same workflow.

**Acceptance Criteria**
- I can upload supported image types (at minimum PNG and JPEG).
- I can download and preview the original image at any time without blocking on processing.
- Image documents are processed in the same step-based, non-blocking pipeline as PDFs, producing the same visibility and artifacts.
- Extraction for images uses OCR to produce raw text suitable for downstream interpretation and review.
- Review-in-context and editing behave the same as for PDFs once extracted text exists.

**Scope Clarification**
- This story changes format support only; the processing pipeline, contracts, versioning rules, and review workflow semantics remain unchanged.
- This story requires updating the authoritative format support contract in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) (supported upload types and any related filesystem rules).

**Authoritative References**
- Tech: Endpoint surface and error semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Sections 3–4 + Appendix A2
- Tech: Step model + failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C
- Tech: Extraction library decisions (appendix): [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E
- UX: Review flow guarantees and rendering contract: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) sections **Confidence — UX Definition**, **Veterinarian Review Flow**, **Review-in-Context Contract**, and **Review UI Rendering Rules (Global Schema Template)**.

**Story-specific technical requirements**
- Add server-side type detection for images based on server-side inspection.
- Define the OCR extraction approach in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E during this story, then implement it.
- Store the original under the deterministic path rules with the appropriate extension (e.g., `original.png`, `original.jpg`).

**Test Expectations**
- Image inputs behave like PDFs for upload/download/status visibility.
- OCR extraction produces a raw-text artifact for image runs, enabling the same review/edit endpoints once processing completes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-22 — Optional OCR support for scanned medical records (PDF/Image)

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
- Tech: Processing model and run invariants: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Sections 3–4 + Appendix A2
- Tech: Endpoint surface and failure semantics: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- Tech: Step model and failure mapping: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix C
- Tech: Extraction/OCR library decisions: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E

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
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-23 — Improve document list filename visibility and tooltip details

**User Story**
As a user, I want document names to be more readable in the list so that I can identify files quickly without opening each document.

**Acceptance Criteria**
- In the document list, long filenames use the available horizontal space before truncation.
- When a filename is truncated, hover and keyboard focus reveal a tooltip with the full filename and key metadata shown in the row.
- Tooltip behavior is accessible: focus-triggered, dismissible with keyboard, and available on desktop and touch alternatives (for example, tap/long-press fallback).
- The list remains usable on mobile widths without overlapping status/actions.

**Scope Clarification**
- Already partially covered by US-04 (list visibility and metadata), but this story adds readability and accessibility refinements.
- This story does not introduce search/filtering/sorting.

**Authoritative References**
- UX: Document list behavior and responsive interaction principles: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)
- UX: Accessibility and interaction consistency: [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md)

**Test Expectations**
- Long filenames are easier to scan due to increased visible text before truncation.
- Tooltip content matches source metadata and is accessible via keyboard focus.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-24 — Support global drag-and-drop PDF upload across relevant screens

**User Story**
As a user, I want to drag and drop a PDF from multiple relevant screens so that I can upload documents without navigating back to a specific dropzone.

**Acceptance Criteria**
- I can drop supported PDFs from any approved upload-capable surface (including list view, document review screen, and relevant empty states).
- Drag-over/drop feedback is visually consistent across those surfaces.
- Upload validation and error messaging are consistent with existing upload behavior.
- Keyboard and non-drag alternatives remain available and equivalent.

**Scope Clarification**
- Already partially covered by US-21 (upload UX), but this story expands drag-and-drop coverage beyond existing dropzones.
- This story does not add support for new file types.

**Authoritative References**
- Tech: Existing upload contract and validation behavior: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- UX: Upload interaction consistency and fallbacks: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Drag-and-drop succeeds from each approved screen and follows the same success/failure feedback contract.
- Non-drag upload path remains fully functional.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-25 — Upload a folder of PDFs (bulk)

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
- Tech: Upload validation and failure behavior: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.2
- UX: Bulk upload feedback and fallback behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Supported environments can upload a folder of PDFs end-to-end.
- Unsupported environments fall back to multi-file selection without blocking upload.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-26 — Add keyboard shortcuts and help modal

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
- UX: Keyboard accessibility and modal behavior: [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md)
- UX: Project interaction patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Frequent actions can be executed through shortcuts outside typing contexts.
- Shortcut help modal is discoverable and keyboard-operable.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-27 — Add in-app help wiki and entry point

**User Story**
As a user, I want an in-app help wiki with a globally accessible entry point so that I can quickly understand key statuses, reprocess behavior, limits, and basic usage.

**Acceptance Criteria**
- A persistent Help entry point is available from main navigation or other globally discoverable UI.
- The entry point links to a help wiki (webpage or in-app section) with structured, navigable content.
- Help content includes minimum guidance for statuses, reprocess, known limits, and how to use the workflow.
- Help content is readable on desktop and mobile and is accessible by keyboard and screen readers.
- Help content avoids implementation/internal jargon and aligns with brand voice.

**Scope Clarification**
- This story delivers the help wiki content and a global entry point to access it.
- Contextual help icons throughout the UI linking to specific wiki sections are delivered separately in US-55.

**Authoritative References**
- Product/UX language and workflow semantics: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)
- Brand and copy tone: [`docs/shared/01-product/brand-guidelines.md`](../../../shared/01-product/brand-guidelines.md)

**Test Expectations**
- Users can open help from within the app and find the required minimum topics.
- Help content remains accessible and responsive.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-28 — Delete uploaded document from list (soft-delete/archive)

**User Story**
As a user, I want to remove an uploaded document from my active list so that I can keep my workspace clean.

**Acceptance Criteria**
- Each eligible document includes a delete/remove action from the list/detail context.
- The delete flow requires explicit user confirmation before completing.
- Deleting a document removes it from the default active list without breaking historical auditability expectations.
- If soft-delete/archive semantics are used, the behavior is explicit in UI copy and reversible behavior (if available) is clearly communicated.

**Scope Clarification**
- Recommended default is soft-delete/archive semantics; irreversible hard-delete behavior requires explicit policy confirmation before implementation.
- This story does not redefine audit/governance contracts.

**Authoritative References**
- Tech: Existing document listing/status contracts: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix B3/B3.1
- UX: Destructive action confirmation and recoverability patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Delete confirmation prevents accidental deletion.
- Deleted/archived documents follow defined visibility semantics consistently.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-29 — Improve toast queue behavior

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
- UX: Notification feedback and accessibility patterns: [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md)
- UX: Project-wide interaction consistency: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Rapid successive events preserve per-toast duration behavior and queue ordering.
- Toast visibility limit and eviction order remain stable across screen sizes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-30 — Change application UI language (multilingual UI)

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
- UX: Product language and interaction patterns: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)
- Tech: Existing document-language processing boundaries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix E + Appendix B3/B3.1

**Test Expectations**
- UI text changes according to selected language while processing behavior remains unchanged.
- Language preference persists according to the selected persistence strategy.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-31 — Externalize configuration and expose settings in UI

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
- Tech: Runtime contracts and operational constraints: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md)
- UX: Settings readability and information architecture: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)

**Test Expectations**
- Effective externalized configuration values are rendered consistently in the read-only settings page.
- Out-of-scope edit/reload behavior is explicitly communicated to users.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-33 — PDF Viewer Zoom

**Status**: Implemented (2026-02-13)

**User Story**
As a veterinarian reviewer, I want to zoom in/out the PDF viewer so I can read small text without losing context.

**Acceptance Criteria**
- Zoom controls (`+`, `-`, and `reset`) are visible in the PDF viewer toolbar.
- Zoom level persists while navigating pages within the same document.
- Zoom enforces reasonable limits (50%–200%).
- Zoom does not affect extracted text tab behavior or structured data layout.

**Scope Clarification**
- This story only covers in-viewer zoom controls and in-document persistence.
- Out of scope: pan/hand tool, multi-page thumbnails, and fit-to-width vs fit-to-page refinements.

**Authoritative References**
- UX: Review workflow and side-by-side behavior: [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md)
- Tech: Existing review/document surface boundaries: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md)

**Test Expectations**
- Users can change zoom with toolbar controls and reset to default.
- Zoom persists across page navigation for the active document and resets when changing document.
- Extracted text tab and structured data rendering remain unaffected by zoom changes.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).

---

## US-47 — Prevent losing unsaved field edits (dirty state + confirm discard)

**Status:** Planned

**User Story**
As a veterinarian, I want the field edit dialog to prevent losing unsaved changes so that I don't accidentally discard my work when pressing Escape or navigating away.

_Detailed acceptance criteria pending definition._

---

## US-48 — Reset field(s) to original detected value

**Status:** Planned

**User Story**
As a veterinarian, I want to reset a field to its originally detected value, or reset all fields of a document at once, so that I can undo my corrections without reprocessing.

_Detailed acceptance criteria pending definition._

---

## US-49 — Treat save of originally suggested value as unmodified

**Status:** Planned

**User Story**
As a veterinarian, I want saving a field with the originally suggested value to count as unmodified so that modification tracking is accurate.

_Detailed acceptance criteria pending definition._

---

## US-59 — Refresh visible confidence after edits on reopened document

**Status:** Planned

**User Story**
As a veterinarian, I want that when I reopen a reviewed document, modify fields, and mark it as reviewed again, the confidence displayed on all open documents reflects the updated corrections, so that the confidence signal is coherent with the current state of the data.

_Detailed acceptance criteria pending definition._

---

## US-50 — Navigate to and highlight field evidence in document viewer

**Status:** Planned

**User Story**
As a veterinarian, I want to click on a structured field and have the document viewer navigate to and highlight the exact location where the text was identified so that I can verify the extraction in context. When a field has been manually edited, the UI should indicate that evidence may no longer match.

_Detailed acceptance criteria pending definition._

---

## US-51 — Text search in PDF viewer

**Status:** Planned

**User Story**
As a veterinarian, I want to search for text in the PDF viewer so that I can quickly find specific content in the document.

_Detailed acceptance criteria pending definition._

---

## US-52 — Improve visit detection heuristics

**Status:** Planned

**User Story**
As a developer, I want to improve visit detection heuristics so that more clinical episodes are correctly identified.

_Detailed acceptance criteria pending definition._

---

## US-53 — Improve general extraction heuristics

**Status:** Planned

**User Story**
As a developer, I want to improve general extraction heuristics so that field detection accuracy increases.

_Detailed acceptance criteria pending definition._

---

## US-54 — Patient history summary field (antecedentes)

**Status:** Planned

**User Story**
As a veterinarian, I want a patient history summary field (antecedentes) so that I can see vaccination history, deworming, and prior surgeries at a glance.

_Detailed acceptance criteria pending definition._

---

## US-55 — Contextual help icons with wiki links throughout UI

**Status:** Planned

**User Story**
As a veterinarian, I want contextual help icons throughout the UI with tooltips and links to the help wiki so that I can get guidance where I need it.

_Detailed acceptance criteria pending definition._

---

## US-56 — Externalize UI texts to editable files

**Status:** Planned

**User Story**
As a content editor/translator, I want UI texts externalized to editable files so that copy can be corrected and translated without code changes.

_Detailed acceptance criteria pending definition._

---

## US-57 — Research field standardization (ISO, international recommendations)

**Status:** Planned

**User Story**
As a developer, I want to research which structured fields can adopt standards (ISO, international recommendations) so that data quality and interoperability improve.

_Detailed acceptance criteria pending definition._

---

## US-58 — Define production DB reset policy for reviewed documents

**Status:** Planned

**User Story**
As an operator, I want a defined policy for what happens to reviewed documents if the database is reset in production so that data governance is clear.

_Detailed acceptance criteria pending definition._

---

## US-42 — Provide evaluator-friendly installation & execution (Docker-first)

**Status**: Implemented (2026-02-19)

**User Story**
As an evaluator,
I want to install and run the full application locally with minimal setup (Docker-first),
so that I can validate MVP behavior quickly and reliably.

**Scope Clarification**
- Delivery and operability only (packaging + instructions).
- Must not change product behavior, API semantics, confidence model semantics, or UX behavior beyond what is required to run the system.

**Acceptance Criteria**
1. One-command run (preferred target)
- Running `docker compose up --build` (or equivalent documented command) starts the system in a usable local configuration:
  - backend API
  - frontend web app
  - required local persistence/storage with deterministic defaults
- After startup, the app is usable from a browser at documented URLs/ports.
2. Clear evaluator run instructions
- README (or a doc linked from README) includes:
  - prerequisites (Docker / Docker Compose)
  - exact commands to run the app
  - URLs/ports for frontend and backend
  - how to run automated tests (backend + frontend)
  - minimal manual smoke test steps (e.g., upload -> preview -> structured view -> edit; and any other MVP flows implemented, such as mark reviewed if available)
  - known limitations / assumptions and expected behavior
3. Config hygiene
- Provide `.env.example` (or documented defaults) requiring no secrets.
- The app runs without external services.
4. Optional QoL (non-blocking)
- Convenience wrappers (e.g., `make run`, `make test`) if feasible.

**Out of Scope**
- No new product capabilities.
- No changes to confidence computation/propagation semantics or UX beyond what is required to run.

**Fallback (only if needed)**
- If full FE+BE Dockerization is not feasible, allow:
  - backend via Docker + documented local run for frontend,
  - but the primary target remains full Docker Compose.

**Authoritative References**
- Exercise deliverables requirement at a high level for evaluator installation and execution readiness.
- Engineering playbook expectations for documented runbook quality, when applicable.

**Test Expectations**
- Evaluator can run the documented commands and access the frontend/backend at documented URLs/ports.
- Automated test commands (backend + frontend) and minimal smoke test steps are executable from provided instructions.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Delivery/run instructions are complete enough for evaluator execution without hidden setup steps.

---

## US-61 — Extract patient date of birth accurately

**Status:** Implemented (2026-03-05)

**Plan:** [COMPLETED_2026-03-05_GOLDEN-LOOP-DOB.md](plans/completed/COMPLETED_2026-03-05_GOLDEN-LOOP-DOB.md)

**User Story**
As a veterinarian, I want the system to extract the patient's date of birth from each medical record so that I can verify the animal's age without reading the full document.

_Acceptance criteria defined in the linked plan._

---

## US-62 — Extract patient microchip number accurately

**Status:** Implemented (2026-03-04)

**Plan:** [COMPLETED_2026-03-04_GOLDEN-LOOP-MICROCHIP.md](plans/completed/COMPLETED_2026-03-04_GOLDEN-LOOP-MICROCHIP.md)

**User Story**
As a veterinarian, I want the system to extract the patient's microchip number correctly so that I can confirm the animal's identity without searching through the document manually.

_Acceptance criteria defined in the linked plan._

---

## US-63 — Extract owner address without confusing it with the clinic address

**Status:** Active

**Plan:** [PLAN_2026-03-06_GOLDEN-LOOP-OWNER-ADDRESS.md](plans/PLAN_2026-03-06_GOLDEN-LOOP-OWNER-ADDRESS.md)

**User Story**
As a veterinarian, I want the system to extract the pet owner's address and distinguish it from the clinic address so that correspondence and records reference the correct location.

_Acceptance criteria defined in the linked plan._

---

## US-64 — Detect all visits in the document even when dates are not in explicit fields

**Status:** Implemented (2026-03-06)

**Plan:** [COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md](plans/completed/COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md)

**User Story**
As a veterinarian, I want the system to detect every clinical visit present in a medical record — even when visit dates are embedded in prose rather than in structured fields — so that no visit is silently omitted from the extracted data.

_Acceptance criteria defined in the linked plan._

---

## US-65 — View clinical data assigned to each specific visit

**Status:** Implemented (2026-03-07)

**Plan:** [COMPLETED_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md](plans/completed/COMPLETED_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md)

**User Story**
As a veterinarian, I want each extracted clinical field (diagnosis, treatment, weight, etc.) to be assigned to the visit it belongs to so that I can review the history of a patient visit by visit.

_Acceptance criteria defined in the linked plan._

---

## US-66 — Diagnose visit-to-data assignment problems (conditional)

**Status:** Planned (conditional)

**Plan:** [PLAN_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md](plans/PLAN_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md)

**User Story**
As a developer, I want observability endpoints or logs that show how the system assigned each data field to a visit so that I can diagnose and fix incorrect visit scoping without guesswork.

_Acceptance criteria defined in the linked plan._

---

## US-67 — Auditable, navigable, and consistent project documentation

**Status:** Active

**Plan:** [PLAN_2026-02-28_DOCS-IMPROVEMENT.md](plans/PLAN_2026-02-28_DOCS-IMPROVEMENT.md)

**User Story**
As a contributor (developer or evaluator), I want the project documentation to be complete, well-structured, and free of contradictions so that I can understand, audit, and extend the project with confidence.

_Acceptance criteria defined in the linked plan._

---

## US-68 — Identify the source worktree of each branch at a glance

**Status:** Implemented (2026-03-06)

**Plan:** [COMPLETED_2026-03-06_WORKTREE-PREFIXED-BRANCH-NAMING.md](plans/completed/COMPLETED_2026-03-06_WORKTREE-PREFIXED-BRANCH-NAMING.md)

**User Story**
As a developer, I want every branch name to include its originating worktree as a prefix so that I can immediately tell where a branch was created and avoid cross-worktree confusion.

_Acceptance criteria defined in the linked plan._

---

## US-69 — Extract pet name accurately

**Status:** Implemented (2026-03-02)

**Plan:** [COMPLETED_2026-03-02_GOLDEN-LOOP-PET-NAME.md](plans/completed/COMPLETED_2026-03-02_GOLDEN-LOOP-PET-NAME.md)

**User Story**
As a veterinarian, I want the system to extract the patient's (pet's) name correctly from each document so that I can identify the animal at a glance.

_Acceptance criteria defined in the linked plan._

---

## US-70 — Extract clinic name accurately

**Status:** Implemented (2026-03-03)

**Plan:** [COMPLETED_2026-03-03_GOLDEN-LOOP-CLINIC-NAME.md](plans/completed/COMPLETED_2026-03-03_GOLDEN-LOOP-CLINIC-NAME.md)

**User Story**
As a veterinarian, I want the system to extract the clinic's name correctly so that I know which clinic issued the medical record.

_Acceptance criteria defined in the linked plan._

---

## US-71 — Extract clinic address accurately

**Status:** Implemented (2026-03-04)

**Plan:** [COMPLETED_2026-03-04_GOLDEN-LOOP-CLINIC-ADDRESS.md](plans/completed/COMPLETED_2026-03-04_GOLDEN-LOOP-CLINIC-ADDRESS.md)

**User Story**
As a veterinarian, I want the system to extract the clinic's address correctly so that I can locate the originating clinic without re-reading the document.

_Acceptance criteria defined in the linked plan._

---

## US-72 — Complete clinic address from name (and vice versa) on demand

**Status:** Implemented (2026-03-04)

**Plan:** [COMPLETED_2026-03-04_CLINIC-ENRICHMENT-BIDIRECTIONAL.md](plans/completed/COMPLETED_2026-03-04_CLINIC-ENRICHMENT-BIDIRECTIONAL.md)

**User Story**
As a veterinarian, I want the system to fill in a clinic's missing address when the name is known (and vice versa) from previously seen records so that partial clinic data is completed automatically.

_Acceptance criteria defined in the linked plan._

---

## US-73 — Modular architecture and maintainable code

**Status:** Implemented

**Plans:**
- [COMPLETED_2026-02-24_ITER-1-2.md](plans/completed/COMPLETED_2026-02-24_ITER-1-2.md)
- [COMPLETED_2026-02-25_ITER-3.md](plans/completed/COMPLETED_2026-02-25_ITER-3.md)
- [COMPLETED_2026-02-25_ITER-4.md](plans/completed/COMPLETED_2026-02-25_ITER-4.md)
- [COMPLETED_2026-02-26_ITER-7.md](plans/completed/COMPLETED_2026-02-26_ITER-7.md)
- [COMPLETED_2026-02-26_ITER-8.md](plans/completed/COMPLETED_2026-02-26_ITER-8.md)
- [COMPLETED_2026-02-28_DECOMPOSE-APP-WORKSPACE.md](plans/completed/COMPLETED_2026-02-28_DECOMPOSE-APP-WORKSPACE.md)
- [COMPLETED_2026-02-28_DECOMPOSE-PDF-VIEWER.md](plans/completed/COMPLETED_2026-02-28_DECOMPOSE-PDF-VIEWER.md)

**User Story**
As a developer, I want the codebase to follow a modular architecture with clear separation of concerns so that I can understand, test, and extend each component independently.

_Acceptance criteria covered across the linked plans._

---

## US-74 — Automated test and E2E coverage in CI

**Status:** Implemented

**Plans:**
- [COMPLETED_2026-02-25_ITER-5.md](plans/completed/COMPLETED_2026-02-25_ITER-5.md)
- [COMPLETED_2026-02-25_ITER-6.md](plans/completed/COMPLETED_2026-02-25_ITER-6.md)
- [COMPLETED_2026-02-27_ITER-9-E2E.md](plans/completed/COMPLETED_2026-02-27_ITER-9-E2E.md)
- [COMPLETED_2026-02-27_ITER-12-FINAL.md](plans/completed/COMPLETED_2026-02-27_ITER-12-FINAL.md)
- [COMPLETED_2026-02-26_INSTALL-PLAYWRIGHT.md](plans/completed/COMPLETED_2026-02-26_INSTALL-PLAYWRIGHT.md)

**User Story**
As a developer, I want comprehensive automated tests (unit + E2E) running in CI so that regressions are caught before code is merged.

_Acceptance criteria covered across the linked plans._

---

## US-75 — Production security, performance, and resilience

**Status:** Implemented

**Plans:**
- [COMPLETED_2026-02-25_ITER-5.md](plans/completed/COMPLETED_2026-02-25_ITER-5.md)
- [COMPLETED_2026-02-25_ITER-6.md](plans/completed/COMPLETED_2026-02-25_ITER-6.md)
- [COMPLETED_2026-02-27_ITER-10-HARDENING.md](plans/completed/COMPLETED_2026-02-27_ITER-10-HARDENING.md)
- [COMPLETED_2026-02-27_ITER-11-FULLSTACK-HARDENING.md](plans/completed/COMPLETED_2026-02-27_ITER-11-FULLSTACK-HARDENING.md)

**User Story**
As a user, I want the application to be secure, performant, and resilient under normal operating conditions so that my data is protected and the system remains responsive.

_Acceptance criteria covered across the linked plans._

---

## US-76 — Functional L1/L2/L3 local validation pipeline on Windows

**Status:** Implemented

**Plans:**
- [COMPLETED_2026-03-03_L1-L2-L3-RULES-ALIGNMENT.md](plans/completed/COMPLETED_2026-03-03_L1-L2-L3-RULES-ALIGNMENT.md)
- [COMPLETED_2026-03-04_FIX-PREFLIGHT-L3-POWERSHELL.md](plans/completed/COMPLETED_2026-03-04_FIX-PREFLIGHT-L3-POWERSHELL.md)

**User Story**
As a developer on Windows, I want a local L1/L2/L3 validation pipeline that catches lint, type, test, and build errors before I push so that CI failures are minimized and feedback is immediate.

_Acceptance criteria covered across the linked plans._

---

## US-77 — Canonical documentation as source of truth with automatic derivation

**Status:** Implemented

**Plans:**
- [COMPLETED_2026-03-05_CANONICAL-DOC-RESTRUCTURE.md](plans/completed/COMPLETED_2026-03-05_CANONICAL-DOC-RESTRUCTURE.md)
- [COMPLETED_2026-03-03_SCRIPTS-REORG-V2.md](plans/completed/COMPLETED_2026-03-03_SCRIPTS-REORG-V2.md)
- [COMPLETED_2026-03-05_PLAN-MODE-ROUTING-FIX.md](plans/completed/COMPLETED_2026-03-05_PLAN-MODE-ROUTING-FIX.md)
- [COMPLETED_2026-03-05_RENUMBER-ROUTER-MINIFILES.md](plans/completed/COMPLETED_2026-03-05_RENUMBER-ROUTER-MINIFILES.md)

**User Story**
As a contributor, I want a single canonical copy of each document that auto-generates derived files (router mini-files, scripts index, etc.) so that documentation stays consistent and never drifts.

_Acceptance criteria covered across the linked plans._

---

## US-78 — Enhanced processing history UI for evaluator observability

**Status:** Planned

**Plan:** [PLAN_2026-03-07_PROCESSING-HISTORY-UI.md](plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md)

**User Story**
As an evaluator, I want to see a clear, informative processing history with state badges, durations, and per-run raw text access so that I can verify the system preserves all processing runs and artifacts end-to-end.

**Acceptance Criteria**

- Each processing run displays a visual state badge (success / failure / timeout / running / queued).
- The most recent run is visually distinguished with a "latest" label.
- Each run card shows total run duration (from `started_at` to `completed_at`).
- I can view the raw text artifact for any historical run, not just the latest.
- Runs are displayed in reverse-chronological order (newest first).
- Existing E2E tests pass without regression.

**Scope Clarification**

- This story is **frontend-only**; no backend or API changes required.
- All data is already served by existing endpoints (`GET /documents/{id}/processing-history`, `GET /runs/{run_id}/artifacts/raw-text`).
- This story extends the existing processing history rendering (US-11) with evaluator-oriented observability enhancements.
- The component is extracted from the current inline rendering in `PdfViewerPanel.tsx` "Technical" tab into a dedicated `ProcessingHistorySection` component.
- Out of scope: interpretation diff/comparison between runs; new tabs or panels; changes to the raw text main tab behavior; performance metrics/trends dashboard; changes to processing logic.

**Dependencies**

- US-11 — View document processing history (✅ Implemented).
- US-42 — Evaluator-friendly installation & execution (✅ Implemented).

**Authoritative References**

- Tech: Processing history endpoint contract: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../02-tech/technical-design.md) Appendix B3.1.
- Tech: Run artifacts endpoint: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../02-tech/technical-design.md) Appendix B3.2.
- Execution plan: [`docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md`](plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md).

**Test Expectations**

- State badges render correctly for each run state.
- Per-run raw text retrieval works for historical runs.
- No regressions in existing E2E tests.

**Definition of Done (DoD)**

- Acceptance criteria satisfied.
- Unit + integration tests per [docs/projects/veterinary-medical-records/02-tech/technical-design.md](../02-tech/technical-design.md) Appendix B7.
- When the story includes user-facing UI, interaction, accessibility, or copy changes, consult only the relevant sections of [docs/shared/01-product/ux-guidelines.md](../../shared/01-product/ux-guidelines.md) and [docs/projects/veterinary-medical-records/01-product/ux-design.md](../01-product/ux-design.md).
- When the story introduces or updates user-visible copy/branding, consult only the relevant sections of [docs/shared/01-product/brand-guidelines.md](../../../shared/01-product/brand-guidelines.md).
