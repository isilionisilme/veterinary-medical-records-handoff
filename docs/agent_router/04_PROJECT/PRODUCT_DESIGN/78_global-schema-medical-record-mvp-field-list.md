# Global Schema (Medical Record MVP Canonical Field List)

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

Canonical source note:
- Historical appendix references are reference-only and non-normative for Medical Record MVP rendering.

## Medical Record MVP panel semantics (US-44)

- The `Extracted Data / Informe` panel is a **clinical Medical Record view**.
- The panel renders a **contract-defined Medical Record field-set and taxonomy** (document-level, visit-level, and explicit other/unmapped bucket).
- In `canonical contract`, required document-level panel fields (including missing-value slots) are defined by the Technical contract template (`medical_record_view.field_slots[]`, Appendix D9).
- Non-clinical claim concepts are out of scope for this panel.
- Labels/copy and empty-states for this panel are defined in [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](ux-design.md).
