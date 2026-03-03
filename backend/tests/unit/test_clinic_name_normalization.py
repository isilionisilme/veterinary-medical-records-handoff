"""Unit tests for clinic_name normalization and ranking."""

from __future__ import annotations

from backend.app.application.extraction_observability.triage import _suspicious_accepted_flags
from backend.app.application.field_normalizers import _normalize_clinic_name_value
from backend.app.application.processing.candidate_mining import _candidate_sort_key


def test_normalize_clinic_name_keeps_clean_value() -> None:
    assert _normalize_clinic_name_value("Hospital Vet Costa") == "Hospital Vet Costa"


def test_normalize_clinic_name_strips_leading_label() -> None:
    assert _normalize_clinic_name_value("Clínica: VetSalud Madrid") == "VetSalud Madrid"


def test_normalize_clinic_name_rejects_address_like_value() -> None:
    assert _normalize_clinic_name_value("Av. Norte 99") is None


def test_clinic_name_sort_prefers_institution_like_over_plain_address() -> None:
    clinic_candidate = {"value": "Hospital Vet Costa", "confidence": 0.66}
    address_candidate = {"value": "Av. Norte 99", "confidence": 0.66}

    assert _candidate_sort_key(clinic_candidate, "clinic_name") > _candidate_sort_key(
        address_candidate,
        "clinic_name",
    )


def test_clinic_name_sort_prefers_hv_abbrev_over_centro() -> None:
    hv_candidate = {"value": "HV COSTA AZAHAR", "confidence": 0.5}
    centro_candidate = {"value": "CENTRO COSTA AZAHAR", "confidence": 0.66}

    assert _candidate_sort_key(hv_candidate, "clinic_name") > _candidate_sort_key(
        centro_candidate,
        "clinic_name",
    )


def test_clinic_name_triage_flags_address_like_value() -> None:
    flags = _suspicious_accepted_flags("clinic_name", "Av. Norte 99")
    assert "clinic_name_address_like" in flags


def test_clinic_name_triage_flags_missing_institution_token() -> None:
    flags = _suspicious_accepted_flags("clinic_name", "Nombre Demo")
    assert "clinic_name_missing_institution_token" in flags


def test_clinic_name_triage_clean_value_no_flags() -> None:
    flags = _suspicious_accepted_flags("clinic_name", "Hospital Veterinario Costa")
    assert flags == []
