# Product Design — Document Interpretation & Layout Evolution

## Note for readers

This repository includes a minimal summary of the product approach for technical context only.

The complete product design — including problem framing, user experience, rationale, and business considerations — is maintained as a single source of truth in the following document:

https://docs.google.com/document/d/1eUCXDTYX3Vw_EJ_nfiJKlRghMO7mZOfitVpMrM5kjFc

Readers interested in the full product and user experience design should refer to that document.

---

## High-level product approach

The product approach focuses on improving the interpretation of unstructured veterinary medical documents in a **safe, incremental, and non-disruptive way**.

Instead of attempting full automation, the system:

- assists veterinarians during document review,
- makes uncertainty and confidence explicit,
- and passively captures corrections as signals for gradual improvement.

The key principle is to convert **inevitable human review work into cumulative system learning**, without changing how veterinarians work or introducing operational risk.

This high-level approach informs the technical and implementation decisions described elsewhere in the repository.


## 1. Core Product Strategy

The system is designed to enable **incremental, human-in-the-loop automation**
without disrupting existing veterinary workflows.

The product assumes that:
- deterministic checks can eventually be automated safely,
- interpretative reasoning must remain **assistive**, never authoritative,
- high-stakes or irreversible decisions always require **explicit human action**.

The long-term goal is to convert **inevitable human corrections**
into **cumulative system improvement**, without asking users to:
- change how they work,
- provide explicit feedback,
- or take responsibility for system behavior.

This strategy deliberately prioritizes:
- safety over speed,
- clarity over automation depth,
- evolvability over premature optimization.

---

## 2. Human-in-the-Loop Philosophy (Product-Level)

Human involvement is not a fallback mechanism; it is a **first-class design choice**.

Product-level rules:
- The system may suggest, highlight, and assist.
- The system must never silently decide or override.
- All meaningful changes remain observable and auditable.
- Human judgment always has the final word.

Automation is introduced **incrementally**, and only where its behavior is
well understood, explainable, and reversible.

---

## 2.1 Confidence Principles (Product-Level)

Confidence is a **signal about interpretation stability**, not a decision or a truth claim.

Product guarantees:
- Confidence guides attention and prioritization; it never blocks decisions or actions.
- Confidence reflects consistency over time/context for similar interpretations.
- Confidence may decrease faster than it increases when new contradictory evidence appears.
- Detailed semantics for confidence in mapping context are defined in
  **Confidence Semantics (Stability, not Truth)** below.

---

## 3. Structural Signals & Pending Review

Some human actions carry **system-level meaning** beyond a single document.

These actions generate **structural signals**.

### 3.1 Definition

A structural signal represents a **repeated, semantically similar correction**
observed across multiple documents under comparable conditions.

Structural signals:
- are accumulated over time,
- are evaluated in aggregate,
- never trigger automatic system changes.

They exist to support **deliberate, informed human governance**.

---

### 3.2 Pending Review State

Structural signals may enter a `pending_review` state when they indicate a
potential need for system-level intervention.

Rules:
- `pending_review` is an **internal system state**.
- It never blocks or alters veterinary workflows.
- It never affects previously processed documents.
- It never triggers implicit reprocessing.

Pending review exists solely to surface **candidates for human review**.

---

### 3.3 Scope of Impact

Any decision derived from structural signals:
- applies **prospectively only**,
- never modifies past interpretations,
- never silently alters system behavior.

The system must remain explainable at all times.

---

## 4. Critical Concepts

Some concepts are inherently **high-risk or high-impact** if misinterpreted.

These are referred to as **critical concepts**.

Examples include (non-exhaustive):
- patient or pet identity,
- species,
- visit or invoice dates,
- monetary amounts.

---

### 4.1 Semantics

Critical concepts:
- are defined explicitly by product policy,
- are not inferred dynamically by the system,
- may evolve only through deliberate human review.

The classification of a concept as “critical” is:
- intentional,
- explicit,
- conservative by design.

---

### 4.2 Interaction with Structural Signals

Edits affecting critical concepts:
- always apply **locally and immediately**,
- generate **high-priority structural signals**,
- never block document review or completion.

No additional friction is introduced for operational users.

---

### 4.3 Governance Boundary

Critical concepts introduce a stricter governance threshold:

- No automatic promotion to system-wide behavior.
- Explicit human review is required before any global effect.
- Decisions affect **future interpretations only**.

Criticality is a governance concern, not a workflow constraint.

---

### 4.4 Critical / Non-Reversible Changes Policy

Some system-level changes are treated as **critical/non-reversible** because they can
reshape future interpretation semantics and are costly to safely undo.

Critical/non-reversible changes include (non-exhaustive):
- schema-level key add/remove/rename decisions,
- key remapping that changes canonical meaning,
- changes affecting the definition/classification of critical concepts.

Product guarantees:
- Veterinarian workflow remains local to single-document resolution and never carries governance burden.
- Reviewer governance handles cross-document/system-level policy decisions explicitly and prospectively.
- Stricter handling applies only to governance decisions, never as added friction for veterinarians.

---

## Conceptual Model: Local Schema, Global Schema, and Mapping

This conceptual model defines how interpretation data is understood at product level.
It does not prescribe storage tables or transport contracts.

- **Local Schema (per document/run):**
  the structured interpretation for one case/run, with evidence + confidence, editable without friction.
- **Global Schema (canonical):**
  the standardized field set the system recognizes and presents consistently across documents;
  it evolves safely and prospectively.
- **Field:**
  semantic unit that can exist locally and/or globally.
- **Mapping:**
  "this local field/value maps to this global key in this context";
  context can include document type, language, clinic, and similar operational conditions.

### Confidence Semantics (Stability, not Truth)

- `candidate_confidence` is an extractor diagnostic for a local candidate in one run; it indicates extraction certainty, not cross-document stability.
- `field_mapping_confidence` is assigned to a mapping in context; it is a proxy for operational stability, not medical truth.
- Confidence guides attention and defaults over time, but must never block veterinary workflow.
- Safety asymmetry applies: `field_mapping_confidence` decreases fast on contradiction, increases slowly on repeated consistency, and remains reversible.

### Context (Deterministic)

- Purpose: deterministic aggregation key for correction/review signals and `field_mapping_confidence` propagation.
- Context fields: `doc_family`/`document_type`, `language`, `country`, `layout_fingerprint`, `extractor_version`, `schema_contract`.
- Context is computed per document/run and persisted alongside review/correction signals; it is deterministic system metadata, not LLM-defined.
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

- `field_mapping_confidence` propagates continuously as new reviewed documents arrive, using smoothing to avoid abrupt oscillations from isolated events.
- Product policy actions (for example default suggestion promotion/demotion or review prioritization) are triggered only when thresholds are met with hysteresis and minimum volume.
- Policy actions adjust default ranking/selection behavior and do not add/remove Global Schema keys.
- `candidate_confidence` can influence extraction diagnostics, but governance and policy actions use `field_mapping_confidence` in context.
- By default, we do not require explicit per-field confirmation: implicit review is used as a weak positive signal when a veterinarian marks the document as reviewed and a field remains unchanged.
- Global Schema keys/order do not change automatically during this propagation; only `field_mapping_confidence` and policy state may change.

#### Future Improvements

- Random audit sampling to periodically validate high-confidence mappings and detect drift.
- Explicit per-field confirmation as a strong positive signal (stronger than implicit unchanged-on-complete signals).
- Veterinarian-proposed fields from **Other extracted fields** as high-priority reviewer proposals; naming reconciliation across synonyms/aliases is tracked as future complexity.

### Governance and Safeguards (pending_review, critical, non-reversible)

- `pending_review` means "captured as a structural signal", not blocked workflow.
- Global schema changes are prospective only and never silently rewrite history.
- Any change that can affect money, coverage, or medical/legal interpretation must not auto-promote.
- `CRITICAL_KEYS` remains authoritative and closed.

## Visit grouping (MVP)

- **Visita** means one care episode identified primarily by `visit_date`, with optional `admission_date`, `discharge_date`, and `reason_for_visit`.
- Clinical concepts are **visit-scoped**. In `canonical contract`, they are grouped under `visits[].fields[]` as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D9.
- The UI must not infer or heuristic-group visits. Grouping comes from the structured payload (`visits[]`).
- MVP excludes cross-document deduplication, merge/reconciliation, and longitudinal visit tracking.
- Review completion remains **document-level**: `Mark as reviewed` applies to the full document, including all its visits.

## Global Schema (Canonical Field List — Medical Record MVP)

Canonical source location:
- This section in `docs/projects/veterinary-medical-records/01-product/product-design.md` is the canonical product source for the Global Schema Medical Record MVP field list.
- The historical appendix in this document is reference-only and non-normative.

Purpose: define the canonical contract-aligned field universe for the Medical Record panel.

Document-level sections (top-level fields):

A) Centro Veterinario
- `clinic_name` (string)
- `clinic_address` (string)
- `vet_name` (string)
- `nhc` (string; canonical NHC concept)

B) Paciente
- `pet_name` (string)
- `species` (string)
- `breed` (string)
- `sex` (string)
- `age` (string)
- `dob` (date)
- `microchip_id` (string)
- `weight` (string)
- `reproductive_status` (string)

C) Propietario
- `owner_name` (string)
- `owner_address` (string; real address concept)

D) Notas internas
- `notes` (string)

E) Información del informe
- `language` (string)

Visit-level fields:
- Visit-level clinical data is canonical in `canonical contract` under `visits[]` and `visits[].fields[]` (see Appendix D9 in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md)).
- Visit fields are not part of the document-level top-level list above.

Panel boundary (Medical Record MVP):
- Non-clinical claim concepts are not part of this canonical panel field-set by definition.
- Classification and taxonomy boundaries are defined by contract metadata in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md), not by frontend denylists.

Product compatibility rule:
- `age` and `dob` may coexist; any derived display behavior is defined by UX and does not imply new extraction requirements.

### CRITICAL_KEYS (Authoritative, closed set)

Historical continuity note: Appendix D7.4 keeps the same closed CRITICAL_KEYS set defined in the historical Global Schema.
For Medical Record canonical contract critical/taxonomy semantics, the normative authority is [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) Appendix D9.

## Medical Record MVP panel semantics (US-44)

- The `Extracted Data / Informe` panel is a **clinical Medical Record view**.
- The panel renders a **contract-defined Medical Record field-set and taxonomy** (document-level, visit-level, and explicit other/unmapped bucket).
- In `canonical contract`, required document-level panel fields (including missing-value slots) are defined by the Technical contract template (`medical_record_view.field_slots[]`, Appendix D9).
- Non-clinical claim concepts are out of scope for this panel and must not be rendered here.
- Panel section order is fixed: `Centro Veterinario` -> `Paciente` -> `Propietario` -> `Visitas` -> `Notas internas` -> `Otros campos detectados` -> `Información del informe`.
- Labels/copy and empty-states for this panel are defined in [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md).
- `owner_id` is not part of Medical Record panel semantics; owner address is represented by `owner_address`.
- NHC is part of `Centro Veterinario` panel semantics and must render with label `NHC` and tooltip `Número de historial clínico`.
- Product compatibility for age and birth date: both `age` and `dob` may coexist; any derived display behavior is UX-defined and does not imply new extraction requirements.

### Authority / cross-doc

- [`docs/projects/veterinary-medical-records/01-product/product-design.md`](product-design.md) defines panel meaning and scope (clinical Medical Record view).
- [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md) defines layout, labels, and empty states.
- [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](technical-design.md) defines canonical payload contracts (`schema_contract` visit-grouped), field taxonomy, and explicit `other/unmapped` contract bucket.

## Appendix: Historical Global Schema Reference (Non-normative)

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
- `diagnosis`, `symptoms`, `procedure`, `medication`, `treatment_plan`, `allergies`, `vaccinations`, `lab_result`, `imaging`
- `notes`, `language`


## 5. Separation of Responsibilities (Product-Level)

The product enforces a strict separation of responsibility:

- **Veterinarians**
  - Resolve individual documents.
  - Correct and validate information locally.
  - Never manage system behavior or learning.

- **Reviewers**
  - Oversee system-level meaning and evolution.
  - Review aggregated patterns and signals.
  - Never participate in operational document workflows.

This separation is:
- intentional,
- asymmetric,
- non-negotiable.

No user is responsible for both document resolution
and system governance within the same workflow.

---

## 6. Learning & Governance

This project is designed to keep veterinary workflows operational and safe while enabling deliberate, auditable system-level evolution over time.

Any change that affects global behavior or schema meaning should be introduced via explicit governance and corresponding product, UX, and technical design updates.

---

## 7. Final Product Rule

This document defines **what the system means and why**.

It does not define UI layout or interaction patterns, architectural or implementation details, or API/persistence contracts.

If a decision cannot be justified using:
- this document,
- UX Design,
- or Technical Design,

**STOP and clarify before proceeding.**
