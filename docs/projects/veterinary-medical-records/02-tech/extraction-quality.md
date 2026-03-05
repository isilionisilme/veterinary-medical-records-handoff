# Extraction Quality

> **Canonical source of truth.**
> This document is the single authoritative reference for extraction quality rules, guardrails, and observability policies in this project.
>
> **Governance:**
> - This file is a canonical document maintained by humans.
> - Router files under `docs/agent_router/` are derived outputs generated from this canonical source.
> - Flow is **canonical → router only**. Router files MUST NOT be edited directly.
> - Any direct edit to a router file may be overwritten during the next regeneration cycle.

---

## Purpose

This document defines the operational rules for extraction quality: the strategy for improving field extraction, per-field guardrails and acceptance criteria, observability infrastructure, and risk management policies.

It consolidates stable operational rules from the extraction tracking system. Transient run logs and per-iteration reports are NOT included here; they remain in the extraction-tracking run artifacts.

---

## 1. Extraction Quality Strategy

### Operating Loop

1. **Observability:** Persist per-run snapshots and triage logs.
2. **Triage:** Rank issues with `/debug/extraction-runs/{documentId}/summary?limit=N` (default `N=20`).
3. **Minimal fix:** Apply the smallest safe change (candidate generation, selection, validator, normalizer).
4. **Verify:** Compare before/after with logs + summary (`limit=20` for trend, `limit=1` for latest run impact).
5. **Document:** Update iteration log + field guardrails.

### Decision Rules

- Prefer **rejecting garbage** over filling wrong values.
- Prioritize highest ROI first (frequency × business impact).
- Prioritize reject-prone fields where `top1` is semantically correct (normalization/selection issue).
- Defer "missing with no top1 candidate" until candidate visibility/generation exists.
- Keep fixes minimal; avoid broad refactors and prompt overhauls early.

### Field Done Criteria

A field is considered improved when:
- Rejected/missing counts decrease in summary trends.
- Latest run (`limit=1`) confirms the improvement.
- Accepted values are correct and evidenced in triage logs/snapshots.
- Guardrails/tests are updated for the touched behavior.

### Default Maintenance Policy

For every extraction-fix run:
1. Add/append an entry in the iteration log.
2. Update touched sections in field guardrails.
3. Update observability docs if observability behavior changed.
4. Add/update ADR only if decision logic changes.

---

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

## 3. Observability

### What We Capture

Per-run extraction snapshot with per-field status:
- `missing` / `rejected` / `accepted`

Per-field candidate evidence:
- `topCandidates` (max 3)
- confidence
- reason (for rejected)
- suspicious accepted flags (triage)

### Storage

- Path: `.local/extraction_runs/<documentId>.json`
- Behavior: ring buffer of latest 20 runs per document.

### Backend Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /debug/extraction-runs` | Persist one run snapshot |
| `GET /debug/extraction-runs/{documentId}` | Return persisted runs for one document |
| `GET /debug/extraction-runs/{documentId}/summary?limit=...` | Aggregate recent runs (default window: 20) |

Optional `run_id` parameter for run-pinned summary filtering.

### Summary Outputs

- Most missing fields
- Most rejected fields
- For missing/rejected: top1 sample + average confidence
- Suspicious accepted counts
- Missing split: with candidates / without candidates

### Practical Interpretation Rule

- `limit=20` includes historical behavior — useful for **trends**.
- `limit=1` isolates the latest run — correct check to confirm a **new fix**.

### Snapshot Ownership

Snapshots are **backend-canonical**. The backend auto-persists snapshots at completed-run boundary. Frontend does NOT write snapshots.

---

## 4. Risk Matrix (Golden Fields)

| Field | Primary risk | Typical trigger pattern | Active guardrail |
|-------|-------------|------------------------|------------------|
| `microchip_id` | Generic long numeric IDs captured as chip | `No:` / `Nro:` invoice/reference near 9–15 digits | Accept only chip-context or explicit OCR chip-like prefixes + digits-only 9–15 |
| `owner_name` | Patient/vet names promoted as owner | `Datos del Cliente` blocks with ambiguous `Nombre:` | Require explicit owner context or strict header fallback; reject patient/vet/clinic context |
| `weight` | Dosage/zero values accepted as weight | Treatment lines, `0` values, out-of-range values | Enforce range [0.5,120], reject `0`, prefer label-based weight context |
| `vet_name` | Clinic/address promoted as veterinarian | Clinic headings and address-rich lines | Person-like normalization + reject clinic/address context |
| `visit_date` | Birthdate mapped as visit date | Multiple dates in same document | Reject birthdate context, require visit/consult anchors |
| `discharge_date` | Timeline dates misclassified as discharge | Unlabeled date-only lines | Strict discharge-label context only |
| `vaccinations` | Narrative/admin text captured as vaccine list | Date-heavy or free narrative blocks | Strict label-only extraction + concise list guardrails |
| `symptoms` | Treatment instructions promoted as symptoms | Dosage/administration paragraphs | Strict symptom-label context + reject treatment/noise language |

### Reviewer Checklist

- Confirm each changed field iteration references this matrix and its field file.
- For any new heuristic, add one positive and one negative test case.
- Require `How to test` commands and PR/commit anchors before approval.

---

## 5. Confidence Policy

- Current confidence policy: fixed `0.66` for golden-loop promotion and conservative field heuristics.
- Label-driven extraction: `0.66`.
- Fallback extraction: `0.50`.
- No high-confidence claims in the current phase.

### Promotion Rules

Promote goal fields from candidates to structured interpretation only when:
- Canonical value is missing.
- Candidate top1 exists.
- Confidence meets the threshold.
- Never overwrite existing canonical values.

---

## 6. Golden Fields — Current Status

| Field | Status | Completed? |
|-------|--------|:---:|
| `microchip_id` | Active (digits-only 9–15, OCR hardened) | ✅ |
| `owner_name` | Active (tabular + conservative fallback) | ✅ |
| `weight` | Active (range [0.5,120], reject 0) | ✅ |
| `vet_name` | Active (person normalization, clinic rejection) | ✅ |
| `visit_date` | Active (date normalization, birthdate rejection) | ✅ |
| `dob` | Active (date normalization + birth-date anchors + observability flags) | ✅ |
| `discharge_date` | Active (label-only context) | ✅ |
| `vaccinations` | Active (strict label-only) | ✅ |
| `symptoms` | Active (label-only, treatment noise rejection) | ✅ |

### Pending Fields (No Guardrails Yet)

- `owner_id` — DNI/NIE extraction pending
- `reason_for_visit` — anchor coverage pending
- `clinical_record_number` — MVP coverage pass pending
- `coat_color`, `hair_length`, `repro_status`, `owner_address` — MVP schema fields pending coverage pass
