# Product Design — Specification Detail

**Breadcrumbs:** [Home](Home) / [Projects](Sitemap) / veterinary-medical-records / 01-product / specs

<!-- START doctoc generated TOC please keep comment here to allow auto update -->

**Contents**

- [Product Design — Specification Detail](#product-design--specification-detail)
  - [Scope and relationship to Product Design](#scope-and-relationship-to-product-design)
  - [Conceptual Model — Specification Detail](#conceptual-model--specification-detail)
    - [Confidence Semantics (Stability, not Truth)](#confidence-semantics-stability-not-truth)
    - [Context (Deterministic)](#context-deterministic)
    - [Learnable Unit (`mapping_id`)](#learnable-unit-mapping_id)
    - [Signals \& Weighting (qualitative)](#signals--weighting-qualitative)
    - [Policy State (soft behavior)](#policy-state-soft-behavior)
    - [Confidence Propagation \& Calibration](#confidence-propagation--calibration)
      - [Future Improvements](#future-improvements)
    - [Governance and Safeguards (pending\_review, critical, non-reversible)](#governance-and-safeguards-pending_review-critical-non-reversible)
  - [Appendix A — Global Schema (Canonical Field List — Medical Record MVP)](#appendix-a--global-schema-canonical-field-list--medical-record-mvp)
  - [Appendix B — Medical Record MVP Panel Semantics (US-44)](#appendix-b--medical-record-mvp-panel-semantics-us-44)
  - [Appendix C — Historical Global Schema Reference (Non-normative)](#appendix-c--historical-global-schema-reference-non-normative)
  - [Final Product Rule](#final-product-rule)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Scope and relationship to Product Design

This document provides **specification-level technical detail** that extends the canonical
[Product Design](product-design) document.

For the complete product narrative — including problem framing, product goal, design premise, product principles,
veterinarian and reviewer experience, confidence as a product signal, the conceptual model (Local Schema, Global Schema,
Mapping, Context), learning and governance, deployment strategy, and observability — see
[product-design.md](product-design). For a one-page business-level overview, see
[Product Design — Executive Summary](product-design-executive).

The complete product design — including business considerations — is also maintained in:

<https://docs.google.com/document/d/1eUCXDTYX3Vw_EJ_nfiJKlRghMO7mZOfitVpMrM5kjFc>

**Authority boundaries:**

- Product meaning, strategy, governance → [product-design.md](product-design)
- Global Schema field list & panel semantics → Appendix A and Appendix B below
- UX layout, labels, and interaction patterns → [ux-design.md](ux-design)
- Architecture, persistence, and API contracts → [technical-design.md](technical-design)
- Implementation scope and sequencing → [implementation-plan.md](implementation-plan)

---

## Conceptual Model — Specification Detail

This section extends the [Conceptual Model](product-design#7-conceptual-model-from-document-interpretation-to-shared-meaning)
in product-design.md with specification-level precision for confidence mechanics, context definition, mapping
identification, signal weighting, and calibration rules.

For the high-level definitions of Field, Local Schema, Global Schema, Mapping, and Context, see
[product-design.md §7](product-design#7-conceptual-model-from-document-interpretation-to-shared-meaning).

For product-level rules on strategy, principles, human-in-the-loop philosophy, confidence principles, structural
signals, critical concepts, and non-reversible changes policy, see the corresponding sections in
[product-design.md](product-design).

### Confidence Semantics (Stability, not Truth)

- `candidate_confidence` is an extractor diagnostic for a local candidate in one run; it indicates extraction certainty,
  not cross-document stability.
- `field_mapping_confidence` is assigned to a mapping in context; it is a proxy for operational stability, not medical
  truth.
- Confidence guides attention and defaults over time, but must never block veterinary workflow.
- Safety asymmetry applies: `field_mapping_confidence` decreases fast on contradiction, increases slowly on repeated
  consistency, and remains reversible.

### Context (Deterministic)

- Purpose: deterministic aggregation key for correction/review signals and `field_mapping_confidence` propagation.
- Context fields: `doc_family`/`document_type`, `language`, `country`, `layout_fingerprint`, `extractor_version`,
  `schema_contract`.
- Context is computed per document/run and persisted alongside review/correction signals; it is deterministic system
  metadata, not LLM-defined.
- `veterinarian_id` is explicitly excluded from Context.
- `clinic_id` is not a first-class context key; use `layout_fingerprint` for layout-level grouping.
- Context semantics are deterministic and stable for the current MVP contract.

### Learnable Unit (`mapping_id`)

- The learnable unit is the pair (`field_key`, `mapping_id`).
- `mapping_id` is a stable identifier for the extraction/mapping strategy that produced a value.
- Representative stable forms include: `label_regex::<label>`, `anchor::<anchor_id>`, `fallback::<heuristic_name>`.

### Signals & Weighting (qualitative)

- Weak positive: veterinarian marks document reviewed and field remains unchanged.
- Negative: field value is edited/corrected.
- Negative (when applicable): value is reassigned/moved away from this field.
- Future strong positive: explicit per-field confirm.
- Confidence increases slowly, decreases quickly; requires minimum volume; and remains reversible.

### Policy State (soft behavior)

- `neutral`: no bias adjustment.
- `boosted`: preferred default suggestion/ranking in context.
- `demoted`/`suppressed`: reduced or hidden default suggestion priority.
- Policy state (not the metric itself) is what may enter `pending_review` where applicable.

### Confidence Propagation & Calibration

- `field_mapping_confidence` propagates continuously as new reviewed documents arrive, using smoothing to avoid abrupt
  oscillations from isolated events.
- Product policy actions (for example default suggestion promotion/demotion or review prioritization) are triggered only
  when thresholds are met with hysteresis and minimum volume.
- Policy actions adjust default ranking/selection behavior and do not add/remove Global Schema keys.
- `candidate_confidence` can influence extraction diagnostics, but governance and policy actions use
  `field_mapping_confidence` in context.
- By default, we do not require explicit per-field confirmation: implicit review is used as a weak positive signal when
  a veterinarian marks the document as reviewed and a field remains unchanged.
- Global Schema keys/order do not change automatically during this propagation; only `field_mapping_confidence` and
  policy state may change.

#### Future Improvements

- Random audit sampling to periodically validate high-confidence mappings and detect drift.
- Explicit per-field confirmation as a strong positive signal (stronger than implicit unchanged-on-complete signals).
- Veterinarian-proposed fields from **Other extracted fields** as high-priority reviewer proposals; naming
  reconciliation across synonyms/aliases is tracked as future complexity.

### Governance and Safeguards (pending_review, critical, non-reversible)

- `pending_review` means "captured as a structural signal", not blocked workflow.
- Global schema changes are prospective only and never silently rewrite history.
- Any change that can affect money, coverage, or medical/legal interpretation must not auto-promote.
- `CRITICAL_KEYS` remains authoritative and closed.

---

## Appendix A — Global Schema (Canonical Field List — Medical Record MVP)

Purpose: define the canonical contract-aligned field universe for the Medical Record panel.

### Document-level sections (top-level fields)

**A) Centro Veterinario**

- `clinic_name` (string)
- `clinic_address` (string)
- `vet_name` (string)
- `nhc` (string; canonical NHC concept)

**B) Paciente**

- `pet_name` (string)
- `species` (string)
- `breed` (string)
- `sex` (string)
- `age` (string)
- `dob` (date)
- `microchip_id` (string)
- `weight` (string)
- `reproductive_status` (string)

**C) Propietario**

- `owner_name` (string)
- `owner_address` (string; real address concept)

**D) Notas internas**

- `notes` (string)

**E) Información del informe**

- `language` (string)

### Visit-level fields

- Visit-level clinical data is canonical in `canonical contract` under `visits[]` and `visits[].fields[]` (see Appendix
  D9 in [technical-design.md](technical-design)).
- Visit fields are not part of the document-level top-level list above.

### Panel boundary (Medical Record MVP)

- Non-clinical claim concepts are not part of this canonical panel field-set by definition.
- Classification and taxonomy boundaries are defined by contract metadata in
  [technical-design.md](technical-design), not by frontend denylists.

### Product compatibility rule

- `age` and `dob` may coexist; any derived display behavior is defined by UX and does not imply new extraction
  requirements.

### CRITICAL_KEYS (Authoritative, closed set)

Historical continuity note: Appendix D7.4 keeps the same closed CRITICAL_KEYS set defined in the historical Global
Schema. For Medical Record canonical contract critical/taxonomy semantics, the normative authority is
[technical-design.md](technical-design) Appendix D9.

---

## Appendix B — Medical Record MVP Panel Semantics (US-44)

- The `Extracted Data / Informe` panel is a **clinical Medical Record view**.
- The panel renders a **contract-defined Medical Record field-set and taxonomy** (document-level, visit-level, and
  explicit other/unmapped bucket).
- In `canonical contract`, required document-level panel fields (including missing-value slots) are defined by the
  Technical contract template (`medical_record_view.field_slots[]`, Appendix D9).
- Non-clinical claim concepts are out of scope for this panel and must not be rendered here.
- Panel section order is fixed: `Centro Veterinario` → `Paciente` → `Propietario` → `Visitas` → `Notas internas` →
  `Otros campos detectados` → `Información del informe`.
- Labels/copy and empty-states for this panel are defined in [ux-design.md](ux-design).
- `owner_id` is not part of Medical Record panel semantics; owner address is represented by `owner_address`.
- NHC is part of `Centro Veterinario` panel semantics and must render with label `NHC` and tooltip
  `Número de historial clínico`.
- Product compatibility for age and birth date: both `age` and `dob` may coexist; any derived display behavior is
  UX-defined and does not imply new extraction requirements.

### Authority / cross-doc

- [product-design.md](product-design) defines panel meaning and scope (clinical Medical Record view).
- [ux-design.md](ux-design) defines layout, labels, and empty states.
- [technical-design.md](technical-design) defines canonical payload contracts (`schema_contract` visit-grouped),
  field taxonomy, and explicit `other/unmapped` contract bucket.

---

## Appendix C — Historical Global Schema Reference (Non-normative)

Status:

- Global Schema here is retained only for historical reference.
- It is not the canonical schema for the Medical Record MVP panel.
- For this panel, canonical behavior is defined by Global Schema + contract taxonomy.
- Additional non-clinical keys are outside this MVP panel scope.

Historical reference model:

A) Identificación del caso

- `claim_id`
- `clinic_name`
- `clinic_address`
- `vet_name`
- `document_date`

B) Paciente

- `pet_name`, `species`, `breed`, `sex`, `age`, `dob`, `microchip_id`, `weight`

C) Propietario

- `owner_name`, `owner_id`

D) Visita / episodio

- `visit_date`, `admission_date`, `discharge_date`, `reason_for_visit`

E) Clínico / revisión

- `diagnosis`, `symptoms`, `procedure`, `medication`, `treatment_plan`, `allergies`, `vaccinations`, `lab_result`,
  `imaging`
- `notes`, `language`

---

For separation of responsibilities and learning & governance, see
[product-design.md](product-design) §5b, §8.

---

## Final Product Rule

This document defines **what the system means and why**.

It does not define UI layout or interaction patterns, architectural or implementation details, or API/persistence
contracts.

If a decision cannot be justified using:

- this document,
- UX Design,
- or Technical Design,

**STOP and clarify before proceeding.**