---
title: "UX Design — Project Interaction Contract"
type: reference
status: active
audience: contributor
last-updated: 2026-03-02
---

# UX Design — Project Interaction Contract


**Breadcrumbs:** [Docs](../../../README.md) / [Projects](../../README.md) / veterinary-medical-records / 01-product

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [1. User Roles & UX Goals](#1-user-roles--ux-goals)
  - [1.1 Veterinarian — Document Review Under Time Pressure](#11-veterinarian--document-review-under-time-pressure)
  - [1.2 Reviewer — System-Level Oversight](#12-reviewer--system-level-oversight)
- [2. Confidence — UX Definition](#2-confidence--ux-definition)
- [3. Confidence Visibility](#3-confidence-visibility)
  - [3.1 Qualitative Signal (Primary)](#31-qualitative-signal-primary)
  - [3.2 Quantitative Signal (Secondary)](#32-quantitative-signal-secondary)
- [4. Veterinarian Review Flow](#4-veterinarian-review-flow)
  - [Step 1 — Document & Interpretation Together](#step-1--document--interpretation-together)
  - [Step 2 — Confidence-Guided Attention](#step-2--confidence-guided-attention)
  - [Step 3 — Immediate Local Correction](#step-3--immediate-local-correction)
  - [Step 4 — Mark document as reviewed (toggle)](#step-4--mark-document-as-reviewed-toggle)
- [4.1 Review-in-Context Contract](#41-review-in-context-contract)
- [Review UI Rendering Rules (Extracted Data / Informe — Medical Record MVP)](#review-ui-rendering-rules-extracted-data--informe--medical-record-mvp)
- [4.2 Confidence Propagation & Calibration (UX Contract)](#42-confidence-propagation--calibration-ux-contract)
- [4.3 Confidence Tooltip Breakdown (Veterinarian UI)](#43-confidence-tooltip-breakdown-veterinarian-ui)
  - [Future Improvements](#future-improvements)
- [5. Structural Effects — UX Consequences Only](#5-structural-effects--ux-consequences-only)
  - [Veterinarian UX Rules](#veterinarian-ux-rules)
  - [Reviewer UX Rules](#reviewer-ux-rules)
- [6. Sensitive Changes — UX Rules](#6-sensitive-changes--ux-rules)
- [7. Reviewer Interaction Model](#7-reviewer-interaction-model)
- [8. Separation of Responsibilities (Non-Negotiable)](#8-separation-of-responsibilities-non-negotiable)
- [9. Final UX Rule](#9-final-ux-rule)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

This document defines the **project-specific UX and interaction design contract**
for the Veterinary Medical Records Processing system.

It complements the global UX principles defined in [`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md).

All UI and interaction decisions for this project must comply with this document.
If a design choice conflicts with these rules, it must be reconsidered.

---

## 1. User Roles & UX Goals

### 1.1 Veterinarian — Document Review Under Time Pressure

**Context**  
Veterinarians review medical documents as part of their normal clinical
and operational work.

**UX Goals**
- Reduce cognitive load.
- Minimize context switching.
- Make uncertainty, confidence, and provenance explicit.
- Optimize for scanning, not reading.
- Every screen answers: *“What do I need to decide or fix now?”*

**Mental Model**
- “I am reviewing this document.”
- “I fix what is wrong and move on.”
- I am not managing schemas, learning, or system behavior.

---

### 1.2 Reviewer — System-Level Oversight

**Context**  
Reviewers operate at system level and are responsible for overseeing
global patterns and long-term consistency.

They do not resolve individual documents and do not participate
in operational review workflows.

**UX Goals**
- Make global impact explicit and inspectable.
- Support deliberate, high-stakes decisions.
- Prioritize safety, auditability, and coherence over speed.
- Focus attention on patterns, not individual actions.

**Mental Model**
- “I am reviewing system behavior over time.”
- “I decide what should change globally.”
- My decisions never affect past documents.

---

## 2. Confidence — UX Definition

Confidence is **not correctness**.

From a UX perspective, confidence means:

> “How stable a given interpretation appears across similar documents.”

UX rules:
- Confidence guides **attention**, not decisions.
- Confidence never blocks actions.
- Confidence never overrides human judgment.
- `candidate_confidence` and `field_mapping_confidence` are distinct and must not be conflated in UX copy.

---

## 3. Confidence Visibility

### 3.1 Qualitative Signal (Primary)

- Confidence must be visible at a glance.
- Use qualitative signals (e.g. emphasis, grouping, visual weight).
- Low-confidence elements should naturally attract attention first.

Exact thresholds and scoring models are product decisions, not UX logic.

---

### 3.2 Quantitative Signal (Secondary)

- Numeric confidence values may be visible via secondary affordances
  (tooltips, expandable details).
- Quantitative signals must never be required to complete work.
- Domain-intrinsic numbers (dates, amounts, quantities) remain fully usable.

---

## 4. Veterinarian Review Flow

### Step 1 — Document & Interpretation Together

The veterinarian reviews, in a single unified context:
- the original document,
- the structured interpretation,
- confidence indicators per field.

These elements must never be split into separate screens.

---

### Step 2 — Confidence-Guided Attention

- Low-confidence fields stand out visually.
- High-confidence fields recede into the background.

The UI guides *where to look first*, not *what to decide*.

---

### Step 3 — Immediate Local Correction

The veterinarian can:
- edit existing values,
- reassign information,
- create new fields when needed.

UX rules:
- Changes apply immediately to the current document.
- No explicit actions exist to submit feedback or “teach” the system.
- No explicit per-field confirmation is required in the current phase.
- A single explicit action may exist to mark the document as reviewed.

- If the veterinarian marks the document as reviewed and a field remains unchanged, that outcome is treated as a weak positive signal for mapping stability.
- This implicit signal must not introduce extra steps or friction in veterinarian flow.

From the veterinarian’s perspective:
> “I am done with this document.”

---

### Step 4 — Mark document as reviewed (toggle)

The veterinarian can explicitly toggle review state from document view.

UX rules:
- A single action button `Mark as reviewed` is available in document view.
- `Mark as reviewed` is the canonical user action that completes review for a document.
- When marked as reviewed, the document list shows a checkmark indicator and the status label `Reviewed`.
- The veterinarian can unmark/reopen the document, returning it to the review queue and restoring the non-reviewed list indicator/label state.
- Unmark/reopen does not delete extracted values, corrections, or prior edits.
- Implicit review signal fires when the veterinarian marks reviewed and a field remains unchanged.

---

## 4.1 Review-in-Context Contract

The review experience must remain usable and explainable even when evidence rendering is imperfect.

Normative behavior:
- Selecting a field must navigate the document viewer to the field evidence context (at minimum, page jump).
- `View evidence` must always present useful context (page + snippet), including when precise highlighting is unavailable.
- Highlighting should be treated as progressive enhancement (best effort only), and failure to highlight must not block review flow.
- Low confidence should guide attention and inspection priority.
- Low confidence must not block editing, marking reviewed, or any other veterinarian action.

---

## Review UI Rendering Rules (Extracted Data / Informe — Medical Record MVP)

Panel definition and scope:
- The panel represents a **Medical Record** (clinical summary).
- In Medical Record MVP, non-clinical concepts are excluded from this panel by contract taxonomy (`medical_record_view`, `scope`, `section`, `classification`, `other_fields[]`), not by UI heuristics or denylists.

Section structure and order (fixed):
1. **Centro Veterinario**
2. **Paciente**
3. **Propietario**
4. **Visitas** (from `visits[]`)
5. **Notas internas**
6. **Otros campos detectados**
7. **Información del informe** (bottom)

Layout note:
- Sections render as normal blocks (no tabs), preserving the current visual system without redesign.

Schema-aware rendering mode (deterministic):
- Medical Record MVP panel uses a single canonical structured contract (non-versioned).
- Render the fixed section order above, with **Visitas** sourced from `visits[]` (per [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md), Appendix D9).
- Required document-level placeholders (for example NHC when missing) are driven by `medical_record_view.field_slots[]` in Appendix D9, not by UI hardcoding.
- No heuristics grouping in UI; grouping comes from `visits[]` in the canonical contract.

Display labels (UI-only; internal keys unchanged):
- **Centro Veterinario**
  - `clinic_name` -> `Nombre`
  - `clinic_address` -> `Dirección`
  - `vet_name` renders when present
  - `NHC`: visible label is always `NHC`; tooltip: `Número de historial clínico`.
  - Backend key may be `nhc` or `medical_record_number`; visible UX label remains `NHC`.
  - NHC must be rendered as a visible field in this section even when missing; when absent in ready state, show placeholder `—`.
  - Deterministic mapping rule: the contract/taxonomy must map backend key variants (`nhc` or `medical_record_number`) to the single NHC concept before rendering; UI must not guess concept mapping.
- **Paciente**
  - `pet_name` -> `Nombre`
  - `dob` -> `Nacimiento`
  - `Estado reproductivo` renders when present/extracted
  - `Capa/Pelo` is not mapped in Medical Record MVP; if detected, it goes to `Otros campos detectados`.
- **Propietario**
  - `owner_name` -> `Nombre`
  - `owner_address` -> `Dirección`
  - `owner_id` is not shown in Medical Record MVP.

Key -> UI label -> Section (UI):

| Key | UI label | Section (UI) |
|---|---|---|
| clinic_name | Nombre | Centro Veterinario |
| clinic_address | Dirección | Centro Veterinario |
| vet_name | Veterinario/a | Centro Veterinario |
| nhc | NHC | Centro Veterinario |
| medical_record_number | NHC | Centro Veterinario |
| pet_name | Nombre | Paciente |
| dob | Nacimiento | Paciente |
| reproductive_status | Estado reproductivo | Paciente |
| owner_name | Nombre | Propietario |
| owner_address | Dirección | Propietario |
| visit_date | Fecha | Visitas |
| admission_date | Admisión | Visitas |
| discharge_date | Alta | Visitas |
| reason_for_visit | Motivo | Visitas |

Visit rendering rules for the canonical contract:
- UI does not infer visits and does not regroup items by date/content.
- Render one visual unit per `VisitGroup` from `visits[]` only (Appendix D9 is authoritative).
- Recommended in-visit rendering order (display-only):
  1. `Fecha` / `Motivo`
  2. `Síntomas`
  3. `Diagnóstico`
  4. `Procedimientos`
  5. `Medicación`
  6. `Plan de tratamiento`
- If `visit_date` is null, show `Sin fecha`.
- If synthetic/unassigned visit group is present (`visit_id = "unassigned"`), show fixed group label `Sin asignar`.

Missing vs loading (deterministic):
- While structured data is loading, show a clear loading state and do not show missing placeholders yet.
- Once the run is ready, any absent/non-extracted value must render an explicit placeholder.

Empty states (deterministic):
- If `visits = []`, render **Visitas** with empty state.
- If a visit exists but `fields[]` is empty, show `Sin campos detectados en esta visita.`
- If `Otros campos detectados` is empty, show `Sin otros campos detectados.`

Otros campos detectados:
- This section is a contract-driven bucket for explicit unmapped/other items only; no UI-side classification.
- If the contract does not expose an explicit unmapped bucket (for example `unmapped_fields[]` / `other_fields[]`), implementation is blocked until technical alignment is defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md).

Información del informe:
- This section is always rendered as the final block.
- It includes report metadata such as detected language when present in payload.

No governance terminology in veterinarian UX:
- The veterinarian UI copy must not expose terms such as `pending_review`, `governance`, or `reviewer`.

## 4.2 Confidence Propagation & Calibration (UX Contract)

- `candidate_confidence` is an extraction-time diagnostic signal for a local candidate.
- `field_mapping_confidence` is a context stability signal used over time for the same semantic mapping.
- `field_mapping_confidence` is the primary UX signal; `candidate_confidence` is diagnostic and should not be shown by default.
- Veterinarian-facing review UI shows only `field_mapping_confidence` by default.
- `field_mapping_confidence` propagates continuously with smoothing; UI state should remain stable and avoid abrupt visual churn.
- Product policy actions (for example default suggestion or demotion) occur only via thresholds + hysteresis + minimum volume; UX should reflect outcomes, not expose calibration mechanics.

## 4.3 Confidence Tooltip Breakdown (Veterinarian UI)

- The veterinarian UI must show `field_mapping_confidence` as the default confidence signal.
- Numeric confidence values are secondary and may appear only inside tooltip details.
- `candidate_confidence` and `field_mapping_confidence` must not be conflated in UI copy or semantics.

Tooltip structure (Spanish, standard copy):
- First line: `Confianza: 72% (Media)`
- Explanation sentence: `Indica qué tan fiable es el valor extraído automáticamente.`
- `Desglose:`
  - `Fiabilidad de la extracción de texto: 65%`
  - `Ajuste por histórico de revisiones: +7%`

Semantic rules:
- `Fiabilidad de la extracción de texto` is a per-document diagnostic component tied to extraction quality for the current run.
- `Ajuste por histórico de revisiones` is an aggregated cross-document, system-level adjustment and is not about this single document only.
- The displayed confidence remains a field-level result; no document-level confidence policy UI is shown.

Visual rule:
- Adjustment value color is green when `> 0`, red when `< 0`, and neutral/muted when `= 0`.

Edge cases:
- If there is no review history, show `Ajuste por histórico de revisiones: 0%`.
- If extraction reliability is unavailable, show `Fiabilidad de la extracción de texto: No disponible`.

The rule "No governance terminology in veterinarian UX" remains in force for confidence tooltip copy.

### Future Improvements

- Random audit sampling support for occasional spot checks.
- Explicit per-field confirmation as an optional strong positive signal, stronger than implicit unchanged-on-complete signals.
- Fields proposed by veterinarians from **Other extracted fields** become high-priority reviewer proposals; naming reconciliation is expected future complexity.

---

## 5. Structural Effects — UX Consequences Only

Some user actions may have **system-level consequences**.

From a UX standpoint:

### Veterinarian UX Rules
- These consequences are **not exposed** to veterinarians.
- No warnings, confirmations, or explanations are shown.
- No responsibility beyond the current document is implied.
- Workflows remain identical regardless of downstream effects.

### Reviewer UX Rules
- Reviewers may see aggregated effects of repeated actions.
- Signals are presented as patterns, never as individual blame.
- High-impact patterns are visually distinguishable.

---

## 6. Sensitive Changes — UX Rules

Some edits may be considered more sensitive at system level.

UX implications:
- Veterinarians can always edit fields without friction.
- No additional confirmations are introduced.
- Sensitive edits never block completion of review.

Any escalation, prioritization, or governance resulting from these edits
is **not defined by this document** and must not surface in the veterinarian UI.

---

## 7. Reviewer Interaction Model

Reviewers interact with **aggregated patterns**, not individual edits.

UX principles:
- Patterns emerge over time.
- Single actions have no standalone meaning.
- Review focuses on trends, stability, and risk.

Reviewer decisions:
- never block veterinary work,
- never affect past documents,
- apply prospectively only.

---

## 8. Separation of Responsibilities (Non-Negotiable)

- Veterinarians resolve documents.
- Reviewers oversee system-level meaning.
- The workflows are asymmetric and decoupled.

The veterinarian UI must not:
- surface reviewer decisions,
- preempt governance workflows,
- imply responsibility for system behavior.

---

## 9. Final UX Rule

This document defines **how the system feels and behaves to users**.

It does not define:
- product strategy,
- system semantics,
- governance rules,
- learning mechanisms.

If a UX decision cannot be resolved using this document and
[`docs/shared/01-product/ux-guidelines.md`](../../../shared/01-product/ux-guidelines.md), it must be escalated to Product Design.
