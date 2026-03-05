<!-- AUTO-GENERATED from canonical source: extraction-quality.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 2. Field Guardrails Catalog

### microchip_id

| Aspect | Rule |
|--------|------|
| **Business meaning** | Unique pet microchip identifier |
| **Accept** | 9–15 digits. Candidate starts with 9–15 digits and trailing text can be trimmed. |
| **Reject** | Owner/address-like text, alphanumeric non-digit IDs, anything outside 9–15 digit range. |
| **Common failures** | Owner/address text selected as top1 candidate; legacy runs showing historical rejects. |
| **Examples** | Good: `Microchip: 00023035139 NHC` → `00023035139`. Bad: `BEATRIZ ABARCA C/ ORTEGA` → rejected. |
| **Implementation** | `backend/app/application/processing_runner.py` (candidate mining, sort key). `frontend/src/extraction/fieldValidators.ts`. |
| **Tests** | `backend/tests/unit/test_interpretation_schema.py`, `test_interpretation_canonical_fixtures.py`, `frontend/src/extraction/fieldValidators.test.ts`. |

### weight

| Aspect | Rule |
|--------|------|
| **Business meaning** | Patient weight |
| **Accept** | Numeric, range 0.5–120, unit optional (`kg/kgs`), comma decimals supported. Normalizes to `X kg`. |
| **Reject** | `0` treated as missing. Out-of-range or non-numeric values. |
| **Examples** | Good: `7,2kg` → `7.2 kg`. Bad: `0` → missing/rejected. |
| **Implementation** | `frontend/src/extraction/fieldValidators.ts`. |
| **Tests** | `frontend/src/extraction/fieldValidators.test.ts`. |

### Date Fields (visit_date, discharge_date, document_date)

| Aspect | Rule |
|--------|------|
| **Business meaning** | Clinical visit date / discharge date / document date |
| **Accept** | `DD/MM/YYYY`, `D/M/YY`, `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`. Two-digit year: `00–69 → 2000–2069`, `70–99 → 1970–1999`. |
| **Reject** | Invalid calendar dates, non-date strings. |
| **Special rules** | `visit_date`: reject birthdate context, require visit/consult anchors. `discharge_date`: strict discharge-label context only. |
| **Implementation** | `frontend/src/extraction/fieldValidators.ts`, `backend/app/application/processing_runner.py`. |
| **Tests** | `frontend/src/extraction/fieldValidators.test.ts`, `backend/tests/unit/test_interpretation_canonical_fixtures.py`. |

### dob

| Aspect | Rule |
|--------|------|
| **Business meaning** | Patient date of birth |
| **Accept** | Valid calendar date in DD/MM/YYYY, D/M/YY, YYYY-MM-DD. Plausible age (0–40 years). |
| **Reject** | Future dates, implausibly old (> 40 years), non-date strings. |
| **Common failures** | `visit_date` promoted as `dob`, unlabeled date captured as `dob`. |
| **Implementation** | `backend/app/application/field_normalizers.py`, `backend/app/application/processing/constants.py` (`DATE_TARGET_KEYS` + anchors). |
| **Tests** | `backend/tests/benchmarks/test_dob_extraction_accuracy.py`, `backend/tests/unit/test_dob_normalization.py`, `backend/tests/unit/test_golden_extraction_regression.py`. |

### vet_name

| Aspect | Rule |
|--------|------|
| **Business meaning** | Veterinarian name |
| **Status** | Tuning focus: header-block capture (`Veterinario/a`, `Dr./Dra.`), disambiguation from clinic labels. |
| **Guardrails** | Person-like normalization + reject clinic/address context. |

### owner_name

| Aspect | Rule |
|--------|------|
| **Business meaning** | Owner/tutor name |
| **Guardrails** | Require explicit owner context or strict header fallback; reject patient-labeled and vet/clinic context. |
| **Tuning focus** | Person-like token extraction, address-token rejection. |

### owner_id

| Aspect | Rule |
|--------|------|
| **Business meaning** | Owner identifier (DNI/NIE-like) |
| **Tuning focus** | Explicit DNI/NIE candidate extraction and schema mapping checks. |

### symptoms

| Aspect | Rule |
|--------|------|
| **Business meaning** | Clinical symptoms |
| **Guardrails** | Strict symptom-label context + reject treatment/noise language. |
| **Tuning focus** | Section/header-driven candidate mining. |

### vaccinations

| Aspect | Rule |
|--------|------|
| **Business meaning** | Vaccination records |
| **Guardrails** | Strict label-only extraction + concise list guardrails. |
| **Tuning focus** | Timeline/list pattern candidate extraction. |

### reason_for_visit

| Aspect | Rule |
|--------|------|
| **Business meaning** | Reason for consultation |
| **Tuning focus** | Robust anchor coverage (`motivo`, `consulta`, `reason for visit`). |

---
