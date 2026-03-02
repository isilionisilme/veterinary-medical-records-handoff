# D9. Structured Interpretation Schema (Visit-grouped Canonical) (Normative)

The canonical visit-grouped contract defines deterministic visit grouping for multi-visit documents.

- Multi-visit PDFs exist; UI must not heuristic-group.
- The canonical contract enables deterministic grouping by introducing `visits[]`.
- Canon note for Medical Record panel: `canonical contract` is canonical for this surface.

## D9.1 Top-Level Object: StructuredInterpretation (Canonical Visit-grouped) (JSON)

```json
{
  "schema_contract": "visit-grouped-canonical",
  "document_id": "uuid",
  "processing_run_id": "uuid",
  "created_at": "2026-02-05T12:34:56Z",
  "medical_record_view": {
    "version": "mvp-1",
    "sections": [
      "clinic",
      "patient",
      "owner",
      "visits",
      "notes",
      "other",
      "report_info"
    ],
    "field_slots": []
  },
  "fields": [],
  "visits": [],
  "other_fields": []
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| schema_contract | string | ✓ | Always `"visit-grouped-canonical"` |
| document_id | uuid | ✓ | Convenience for debugging |
| processing_run_id | uuid | ✓ | Links to a specific processing attempt |
| created_at | ISO 8601 string | ✓ | Snapshot creation time |
| medical_record_view | `MedicalRecordViewTemplate` | ✓ | Deterministic panel template for Medical Record MVP rendering (US-44); contract uses stable section ids (not localized labels). |
| fields | array of `StructuredField` | ✓ | Non-visit-scoped fields only |
| visits | array of `VisitGroup` | ✓ | Deterministic grouping container for visit-scoped data |
| other_fields | array of `StructuredField` | ✓ | Explicit unmapped/other bucket for deterministic rendering; FE MUST render “Otros campos detectados” only from this bucket. |

## D9.1.a Medical Record View Template / Field Slots (Normative, US-44)

`medical_record_view` defines deterministic render intent for the Medical Record MVP panel without frontend heuristics.

`field_slots[]` minimum shape:
- `concept_id` (stable concept identifier, string)
- `section` (stable section id, string: `clinic|patient|owner|visits|notes|other|report_info`)
- `scope` (`"document" | "visit"`)
- `canonical_key` (canonical payload key, string)
- `aliases` (optional string array)
- `label_key` (optional label token/string)

Minimum MVP document-level slots (required when interpretation is in ready state):
- `clinic_name`, `clinic_address`, `vet_name`, `nhc`
- `pet_name`, `species`, `breed`, `sex`, `age`, `dob`, `microchip_id`, `weight`, `reproductive_status`
- `owner_name`, `owner_address`
- `notes`, `language`

Localization boundary:
- Contract carries stable section ids and canonical keys.
- Human-readable section labels (for example `Centro Veterinario`, `Notas internas`) are defined by UX, not by contract payload strings.

Normative rendering rules:
1. Frontend MUST render all `scope = "document"` slots from `medical_record_view.field_slots[]`.
2. If no resolved value exists for a required document slot in ready state, frontend MUST render placeholder `—`.
3. Frontend MUST NOT infer section membership or required fields from key presence.
4. Alias resolution to canonical concept (for example `medical_record_number` -> `nhc`) MUST be resolved by producer/contract metadata before rendering; frontend MUST NOT guess.
5. In `ready` state, frontend placeholder rendering MUST be driven by `medical_record_view.field_slots[]` as source of truth, including slots without resolved entries in top-level `fields[]`.

## D9.2 VisitGroup (Normative)

```json
{
  "visit_id": "uuid",
  "visit_date": "2026-02-05",
  "admission_date": "2026-02-05",
  "discharge_date": "2026-02-07",
  "reason_for_visit": "Vomiting",
  "fields": []
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| visit_id | uuid | ✓ | Stable identifier for the visit group within this interpretation version |
| visit_date | ISO 8601 date string | ✓ (nullable) | Critical concept; may be `null` if unknown |
| admission_date | ISO 8601 date string | ✗ | Optional |
| discharge_date | ISO 8601 date string | ✗ | Optional |
| reason_for_visit | string | ✗ | Optional |
| fields | array of `StructuredField` | ✓ | Visit-scoped structured fields (clinical); `StructuredField` is unchanged from D5 |

## D9.3 Scoping Rules (Normative)

For `canonical contract`:
1. Top-level `fields[]` MUST contain only non-visit-scoped keys (clinic/patient/owner/notes metadata and any future non-visit keys).
2. Visit-scoped concepts MUST appear inside exactly one `visits[].fields[]` entry set, not in top-level `fields[]`.
3. “Otros campos detectados” MUST be contract-driven through explicit `other_fields[]`; FE MUST NOT reclassify and MUST NOT source this section from `fields[]` or `visits[]`.
4. Medical Record panel membership is contract metadata (`scope`, `section`, `domain`, `classification`) and not UI inference.

Visit-scoped keys (MUST be inside `visits[].fields[]`):
- `symptoms`
- `diagnosis`
- `procedure`
- `medication`
- `treatment_plan`
- `allergies`
- `vaccinations`
- `lab_result`
- `imaging`

Visit metadata keys are represented as `VisitGroup` properties:
- `visit_date`
- `admission_date`
- `discharge_date`
- `reason_for_visit`

Document-level Medical Record keys (MUST be represented by `medical_record_view.field_slots[]`; resolved values are emitted in top-level `fields[]` with `scope = "document"`, `classification = "medical_record"`):
- Clinic section (`section = "clinic"`): `clinic_name`, `clinic_address`, `vet_name`, `nhc`.
- Patient section (`section = "patient"`): `pet_name`, `species`, `breed`, `sex`, `age`, `dob`, `microchip_id`, `weight`, `reproductive_status`.
- Owner section (`section = "owner"`): `owner_name`, `owner_address`.
- Notes section (`section = "notes"`): `notes`.

Section-id normalization (normative):
- Producers/contract adapters MUST map `section = "review_notes"` to stable `section = "notes"` before consumer rendering.
- Producers/contract adapters MUST map `section = "visit"` to stable `section = "visits"` before consumer rendering.
- Frontend consumers MUST NOT infer or heuristically remap section ids.
- Report info section (`section = "report_info"`): `language`.

Reproductive status concept (normative):
- Canonical key is `reproductive_status`.
- `repro_status` aliases MUST be mapped to canonical `reproductive_status` in contract metadata.

Owner address concept (normative):
- `owner_address` is the explicit owner address concept for Medical Record taxonomy.
- `owner_id` is an identifier concept and MUST NOT be interpreted as address in Medical Record taxonomy.

NHC (normative):
- Preferred key is `nhc` (Número de historial clínico), document-level, clinic section.
- `medical_record_number` aliases MUST map to `nhc`.
- Deterministic taxonomy rule: producers MUST map both key variants to the same Medical Record concept (`NHC`) in contract metadata; frontend consumers MUST NOT infer this mapping heuristically.

Age and DOB (normative compatibility):
- `age` and `dob` are both valid patient fields.
- Backend may emit either or both; the contract does not require deriving one from the other in frontend consumers.

Medical Record boundary (contract taxonomy):
- Medical Record panel rendering MUST rely on contract classification (`classification = "medical_record"` and domain/section metadata), not frontend denylists.
- Non-clinical claim concepts are excluded from Medical Record taxonomy by classification/domain.

Medical Record panel eligibility taxonomy (normative summary):
- `Centro Veterinario`: `clinic_name`, `clinic_address`, `vet_name`, `nhc`.
- `Paciente`: `pet_name`, `species`, `breed`, `sex`, `age`, `dob`, `microchip_id`, `weight`, `reproductive_status`.
- `Propietario`: `owner_name`, `owner_address` (`owner_id` excluded).
- `Visitas`: visit metadata + visit-scoped fields in `visits[].fields[]`.
- `Notas internas`: `notes`.
- `Información del informe`: `language`.
- `Otros campos detectados`: explicit contract bucket only (`other_fields[]`), never UI-side classification.

Date normalization (canonical contract target):
- Canonical date representation for `visit_date`, `admission_date`, and `discharge_date` is ISO 8601 date string (`YYYY-MM-DD`).
- Transitional note: non-ISO inputs (for example `dd/mm/yyyy`) may exist upstream; producers should normalize to canonical ISO in payload output.

## D9.4 Determinism and Unassigned Rule (Normative)

If an extracted clinical field cannot be deterministically linked to a specific visit, it MUST be placed under a synthetic `VisitGroup` with:
- `visit_id = "unassigned"`
- `visit_date = null`
- `admission_date = null`
- `discharge_date = null`
- `reason_for_visit = null`

Contract clarification:
- `visit_id = "unassigned"` is an explicit contract value (not a frontend heuristic or fallback label).
- A payload where all visit-scoped concepts are contained in a single synthetic `unassigned` group is valid for `canonical contract`.

This rule prevents UI-side heuristic grouping and keeps all visit-scoped items contained in `visits[]`.

Sufficient evidence boundary for assigned VisitGroup creation (US-45, deterministic):
- Producer MAY create an assigned `VisitGroup` (`visit_id != "unassigned"`) only when a date token is normalizable to ISO (`YYYY-MM-DD`) and the same evidence includes visit context (`visita|consulta|control|revisión|seguimiento|ingreso|alta`) without non-visit context.
- Non-visit/administrative contexts (for example DOB/nacimiento, microchip/chip, invoice/factura, report/informe/emisión/documento date references) MUST NOT create assigned VisitGroups.
- If a field evidence snippet contains ambiguous date tokens without sufficient visit context, that field MUST remain in `unassigned`.

## D9.5 Contract Note (Normative)

- Frontend may branch rendering by `schema_contract` in general integrations, but this document defines contract shape only (UX owns layout).

## D9.6 Authoritative Contract Boundary for Medical Record Rendering

- This appendix is the technical source of truth for payload taxonomy and deterministic buckets (`fields[]`, `visits[]`, `other_fields[]`, and classification metadata).
- Frontend consumers MUST render Medical Record structure from contract metadata only; they MUST NOT infer grouping/classification heuristically.
- UX labels/copy are defined in [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../UX_DESIGN/00_entry.md); this appendix defines contract semantics only.

---
