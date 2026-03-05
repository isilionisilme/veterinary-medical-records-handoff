<!-- AUTO-GENERATED from canonical source: extraction-quality.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

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
