# Track Plan T1 (AUDIT-01-T1): Backend Code Quality

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.
>
> **Master plan:** [AUDIT-01 Master](PLAN_2026-03-12_AUDIT-01-CODEBASE-QUALITY-MASTER.md)

**Branch:** improvement/audit-01-t1-backend-quality
**Worktree:** D:/Git/worktrees/1
**Execution Mode:** Autonomous
**Model Assignment:** GPT-5.4 (A1), Claude Opus 4.6 (A2)
**PR:** Pending (PR created on explicit user request)
**Related item ID:** `AUDIT-01-T1`
**Prerequisite:** None (independent track)

**Implementation Report:** [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T1-BACKEND-QUALITY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T1-BACKEND-QUALITY.md)

---

## TL;DR

Extract ~20 magic numbers scattered across triage, normalizers, and quality scoring into a shared constants module, then refactor `_suspicious_accepted_flags` (CC=32, 134 LOC) into a dispatch-table architecture with CC ≤ 10 per function.

---

## Context

### Problem 1: Magic Numbers (A1)

The audit found ~20 hardcoded numeric literals duplicated between `triage.py` and `field_normalizers.py`, with additional thresholds in `extraction_quality.py`. When a threshold changes, multiple files must be updated in sync — a DRY violation and maintenance hazard.

**Current duplication examples:**

| Constant | `triage.py` | `field_normalizers.py` |
|----------|-------------|----------------------|
| Microchip min length | Line 78: `9` | Line 181: `9` |
| Microchip max length | Line 78: `15` | Line 181: `15` |
| Weight min kg | Line 95: `0.2` | Line 19: `0.5` (⚠️ inconsistent!) |
| Weight max kg | Line 95: `120` | Line 20: `120.0` |

### Problem 2: Cyclomatic Complexity (A2)

`_suspicious_accepted_flags` at `triage.py:62` has CC=32 (CI limit: 30), 134 LOC, and 5-6 levels of nesting. It uses a long `if/elif` chain dispatching on `field_key` values to apply field-specific validation rules.

---

## Scope Boundary

- **In scope:** A1 (constants extraction), A2 (triage refactor)
- **Out of scope:** Changing business logic thresholds, modifying test assertions, refactoring `extraction_quality.py` scoring algorithm, touching any file not listed in Relevant Files

---

## Design Decisions

### DD-1: New `extraction_constants.py` module
**Location:** `backend/app/application/extraction_observability/extraction_constants.py`
**Rationale:** Co-located with `triage.py` (primary consumer). Constants grouped by domain (weight, microchip, name, address, age).

### DD-2: Dispatch-table pattern for triage refactor
**Rationale:** Replace `if/elif` chain with a `dict[str, Callable]` mapping `field_key` → validator function. Each validator is a small pure function with CC ≤ 5. The dispatcher itself becomes CC ≤ 3.

### DD-3: Reconcile weight threshold inconsistency
**Current state:** `triage.py` uses `0.2` kg minimum, `field_normalizers.py` uses `0.5` kg.
**Decision:** Use `0.5` kg (the normalizer value) as the canonical constant. `triage.py` was using a looser bound; aligning to `0.5` is stricter but more correct (a 200g animal weight is not meaningful in veterinary context).

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~250 | 400 | ✅ |
| Code files changed | 5 | 15 | ✅ |
| Scope classification | code + tests | — | ✅ |
| Semantic risk | MEDIUM (refactor with behavior preservation) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — Internal refactor with no API or user-facing changes.

---

## Steps

### Phase 1 — A1: Extract Constants

**AGENTE: GPT-5.4**

#### Step 1: Create `extraction_constants.py`

Create `backend/app/application/extraction_observability/extraction_constants.py` with all magic numbers:

```python
"""Shared numeric constants for extraction observability and field normalization."""

# Microchip ID
MICROCHIP_MIN_DIGITS: int = 9
MICROCHIP_MAX_DIGITS: int = 15

# Weight (kg)
WEIGHT_MIN_KG: float = 0.5
WEIGHT_MAX_KG: float = 120.0

# Value length bounds
MAX_VALUE_LENGTH: int = 80
PET_NAME_MIN_LENGTH: int = 1
CLINIC_NAME_MIN_LENGTH: int = 2
CLINIC_ADDRESS_MIN_LENGTH: int = 10
OWNER_ADDRESS_MAX_LENGTH: int = 120

# Age
MAX_PET_AGE_YEARS: int = 40
DAYS_PER_YEAR: float = 365.25

# Phone-like pattern
PHONE_DIGIT_COUNT: int = 9
```

#### Step 2: Update `triage.py` imports

**AGENTE: GPT-5.4**

Replace all magic number literals in `_suspicious_accepted_flags` (lines 62–195) with imports from `extraction_constants`.

#### Step 3: Update `field_normalizers.py` imports

**AGENTE: GPT-5.4**

Replace `_WEIGHT_MIN_KG = 0.5`, `_WEIGHT_MAX_KG = 120.0` (lines 19–20), and microchip bounds (line 181) with imports from `extraction_constants`.

#### Step 4: Validate Phase 1

**AGENTE: GPT-5.4**

- `ruff check backend/app/application/extraction_observability/`
- `ruff check backend/app/application/field_normalizers.py`
- `python -m pytest backend/tests/ -x --tb=short -q` — all 709+ tests pass

### Phase 2 — A2: Refactor `_suspicious_accepted_flags`

**AGENTE: Claude Opus 4.6**

#### Step 5: Create field validators

In `triage.py`, below imports, create individual validator functions:

```python
def _validate_microchip(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    """Check microchip ID for suspicious patterns. Returns list of flag reasons."""
    ...

def _validate_weight(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    ...

def _validate_pet_name(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    ...

# etc. for each field_key case
```

Each function:
- Takes `(value: str, all_fields: dict[str, Any] | None)` → `list[str]`
- Contains the logic from one `elif` branch
- Uses constants from `extraction_constants`
- Has CC ≤ 5

#### Step 6: Create dispatch table

**AGENTE: Claude Opus 4.6**

```python
_FIELD_VALIDATORS: dict[str, Callable[[str, dict[str, Any] | None], list[str]]] = {
    "microchip_number": _validate_microchip,
    "patient_weight_kg": _validate_weight,
    "pet_name": _validate_pet_name,
    "clinic_name": _validate_clinic_name,
    "clinic_address": _validate_clinic_address,
    "owner_address": _validate_owner_address,
    "date_of_birth": _validate_date_of_birth,
    # ... all field_key values
}
```

#### Step 7: Simplify `_suspicious_accepted_flags`

**AGENTE: Claude Opus 4.6**

Replace the body with:

```python
def _suspicious_accepted_flags(
    field_key: str, value: str | None, all_fields: dict[str, Any] | None = None
) -> list[str]:
    if not value:
        return []
    normalized_value = value.strip()
    if not normalized_value:
        return []
    if len(normalized_value) > MAX_VALUE_LENGTH:
        return [f"value_too_long:{len(normalized_value)}"]

    validator = _FIELD_VALIDATORS.get(field_key)
    if validator is None:
        return []
    return validator(normalized_value, all_fields)
```

Target: CC ≤ 5 for the dispatcher, CC ≤ 5 per validator.

#### Step 8: Validate Phase 2

**AGENTE: Claude Opus 4.6**

- `radon cc -s backend/app/application/extraction_observability/triage.py` — no function > CC 10
- `ruff check backend/app/application/extraction_observability/triage.py`
- `python -m pytest backend/tests/ -x --tb=short -q` — all 709+ tests pass
- `python -m pytest backend/tests/ -x --tb=short -q -k triage` — triage-specific tests pass

### Phase 3 — Final Validation

**AGENTE: Claude Opus 4.6**

#### Step 9: Full test suite

- `python -m pytest backend/tests/ --tb=short -q` — 709+ passed
- `ruff check backend/` — 0 errors
- `ruff format --check backend/` — 0 diffs
- `radon cc -n C backend/app/` — 0 functions with CC > 10

---

## Execution Status

### Phase 0 — Preflight

- [x] P0-A 🔄 — Create branch `improvement/audit-01-t1-backend-quality` from latest `main`. Verify clean worktree. — ✅ `no-commit (branch preflight)` **AGENTE: GPT-5.4**

### Phase 1 — A1: Extract Constants

- [x] P1-A 🔄 — Create `extraction_constants.py` with all constants. — ✅ `73dad6f3` **AGENTE: GPT-5.4**
- [x] P1-B 🔄 — Update `triage.py` to import from constants module. — ✅ `73dad6f3` **AGENTE: GPT-5.4**
- [x] P1-C 🔄 — Update `field_normalizers.py` to import from constants module. — ✅ `73dad6f3` **AGENTE: GPT-5.4**
- [x] P1-D 🔄 — Run tests, verify all 709+ pass. — ✅ `no-commit (L2 pass)` **AGENTE: GPT-5.4**
- [x] P1-E 🚧 — Checkpoint: present diff for user review. — ✅ `no-commit (reviewed in chat)` **AGENTE: GPT-5.4**

### Phase 2 — A2: Refactor Triage

- [x] P2-A 🔄 — Create individual validator functions. — ✅ `no-commit (local refactor applied)` **AGENTE: Claude Opus 4.6**
- [x] P2-B 🔄 — Create dispatch table. — ✅ `no-commit (local refactor applied)` **AGENTE: Claude Opus 4.6**
- [x] P2-C 🔄 — Simplify `_suspicious_accepted_flags` to use dispatch table. — ✅ `no-commit (CC 32→5 local validation)` **AGENTE: Claude Opus 4.6**
- [x] P2-D 🔄 — Verify CC ≤ 10 with radon. — ✅ `no-commit (radon local pass)` **AGENTE: Claude Opus 4.6**
- [x] P2-E 🔄 — Run full test suite. — ✅ `no-commit (709 passed, 2 xfailed)` **AGENTE: Claude Opus 4.6**
- [x] P2-F 🚧 — Checkpoint: present diff for user review. — ✅ `no-commit (reviewed in chat)` **AGENTE: Claude Opus 4.6**

### Phase 3 — Final

- [ ] P3-A 🔄 — Full validation (tests + lint + radon). **AGENTE: Claude Opus 4.6**
- [ ] P3-B 🚧 — Present commit proposal to user. **AGENTE: Claude Opus 4.6**

---

## Relevant Files

| File | Action |
|------|--------|
| `backend/app/application/extraction_observability/triage.py` | REFACTOR (A1 + A2) |
| `backend/app/application/field_normalizers.py` | MODIFY (A1 — import constants) |
| `backend/app/application/extraction_quality.py` | MODIFY (A1 — import constants) |
| `backend/app/application/extraction_observability/extraction_constants.py` | CREATE (A1) |
| `backend/tests/` | VERIFY (no changes, all must pass) |

---

## Acceptance Criteria

- [ ] No magic number literals in `triage.py`, `field_normalizers.py`, or `extraction_quality.py` that have equivalents in `extraction_constants.py`
- [ ] `_suspicious_accepted_flags` CC ≤ 10 (radon verified)
- [ ] All individual validator functions CC ≤ 5
- [ ] 709+ tests pass, ≥91% coverage
- [ ] `ruff check` + `ruff format` clean
- [ ] Weight threshold inconsistency resolved (unified to 0.5 kg)
