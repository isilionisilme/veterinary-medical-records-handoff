# Product Design — Executive Summary

> One-page overview of what the system does, for whom, and why it matters.
> For more detail, see [Product Design](product-design).

---

## Problem

Veterinary clinics process unstructured medical documents — invoices, lab reports, referral letters — under
time pressure. Today, the veterinarian reads each document, mentally extracts the relevant information, and
decides what matters. This is repetitive, error-prone, and impossible to scale.

## Proposed Solution

An **AI-assisted document interpretation** system that presents the veterinarian with a structured medical
record derived from the original document, together with confidence signals that guide where to focus
attention. The veterinarian reviews, corrects if needed, and marks the document as reviewed. The system
learns passively from those corrections — no explicit feedback, no extra steps.

## Target user

The **veterinarian** (primary user) reviews uploaded medical records, inspects structured data, corrects
errors, and makes final clinical decisions. A future **reviewer** role governs system-level meaning without
participating in individual document workflows. Out of scope for MVP: pet owners, external clinics,
administrative staff.

## Product principles

| Principle | What it means |
|-----------|---------------|
| **Assistance before automation** | The system assists interpretation but never replaces medical judgment. Automation only where evidence of stability exists. |
| **Visibility over magic** | Uncertainty is explicit, never hidden. All changes remain observable and auditable. |
| **Zero-friction correction** | Corrections apply instantly, no approval workflows. The system's learning needs never slow clinical work. |
| **Controlled learning** | Structural changes are proposed, not auto-applied. Safety over speed, clarity over automation depth. |

## MVP workflow

1. **Upload** — veterinarian uploads a PDF; system shows processing state.
2. **Review** — original document, extracted text, and structured record shown together.
3. **Confidence** — each field carries a qualitative confidence signal guiding where to look first.
4. **Correct** — instant local edits; no system approval needed.
5. **Complete** — "Mark as reviewed" closes the review; corrections become learning signals silently.

## Key differentiators

- **Confidence-first design** — confidence guides attention, never blocks or imposes decisions.
- **Human-in-the-loop by default** — automation expands only where sustained evidence supports it.
- **Progressive learning loop** — every review cycle makes the system more accurate; veterinarian work is the system's primary input.
- **Safety boundaries** — changes affecting money, coverage, or medical interpretation can never self-promote; they always require human governance.

## Deployment path

| Stage | Description |
|-------|-------------|
| Shadow mode | System runs in parallel, observes, extracts, scores — no user-facing impact. |
| Passive learning | Captures human corrections as structured evidence without interfering. |
| Assisted suggestions | Surfaces advisory suggestions; veterinarians accept or correct. |
| Progressive automation | Fields with sustained high confidence promoted to automatic under guardrails. |

Each stage transition is a deliberate organizational decision, not an automatic threshold.

## Success criteria

- **Faster reviews** — less time per document.
- **Fewer repetitive actions** — the system handles what it can.
- **Higher confidence in outputs** — veterinarians trust more and check less over time.
- **Clear path to automation** — every review cycle makes the system better.

## Scope boundaries

| Topic | Where to find it |
|-------|-----------------|
| Product design | [Product Design](product-design) |
| Extended appendices (schema, panel semantics) | [Product Design Extended](product-design-full) |
| UX interaction contract | [UX Design](ux-design) |
| Visual design system | [Design System](Design-System) |
| Architecture & API contracts | [Technical Design](technical-design) |
| Implementation scope & sequencing | [Implementation Plan](implementation-plan) |
