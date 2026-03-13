from __future__ import annotations

from backend.app.application.processing import field_patterns


def test_pet_name_guard_blocks_address_like_tokens() -> None:
    assert field_patterns._PET_NAME_GUARD_RE.search("C/ Mayor 10") is not None
    assert field_patterns._PET_NAME_GUARD_RE.search("Luna") is None


def test_pet_name_birthline_extracts_name_prefix() -> None:
    match = field_patterns._PET_NAME_BIRTHLINE_RE.search("Luna - nacimiento: 12/01/2020")

    assert match is not None
    assert match.group(1) == "Luna"


def test_clinic_standalone_line_pattern_captures_clinic_name() -> None:
    match = field_patterns._CLINIC_STANDALONE_LINE_RE.search(
        "Hospital Veterinario Central Valencia"
    )

    assert match is not None
    assert match.group(2) == "Central Valencia"


def test_owner_name_like_line_pattern_accepts_person_name_and_rejects_numeric_noise() -> None:
    assert field_patterns._OWNER_NAME_LIKE_LINE_RE.search("Juan Perez Gomez") is not None
    assert field_patterns._OWNER_NAME_LIKE_LINE_RE.search("Juan 123") is None


def test_weight_guard_patterns_detect_dosage_and_lab_context() -> None:
    assert field_patterns._WEIGHT_DOSAGE_GUARD_RE.search("amoxicilina 2 mg/kg") is not None
    assert field_patterns._WEIGHT_LAB_GUARD_RE.search("glucosa 92 mg/dL") is not None


def test_weight_explicit_context_pattern_detects_weight_label() -> None:
    assert field_patterns._WEIGHT_EXPLICIT_CONTEXT_RE.search("Peso corporal: 12 kg") is not None
