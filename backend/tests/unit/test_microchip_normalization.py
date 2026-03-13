"""Unit tests for microchip normalization helpers."""

from __future__ import annotations

from backend.app.application.field_normalizers import (
    _normalize_microchip_id,
    normalize_microchip_digits_only,
)
from backend.app.application.processing.candidate_mining import _candidate_sort_key


def test_normalize_microchip_digits_only_keeps_valid_digits() -> None:
    assert normalize_microchip_digits_only("941000024967769") == "941000024967769"


def test_normalize_microchip_digits_only_extracts_from_labelled_text() -> None:
    assert normalize_microchip_digits_only("Microchip: 941000024967769") == "941000024967769"


def test_normalize_microchip_digits_only_rejects_empty() -> None:
    assert normalize_microchip_digits_only("") is None


def test_normalize_microchip_digits_only_rejects_none() -> None:
    assert normalize_microchip_digits_only(None) is None


def test_normalize_microchip_digits_only_rejects_without_9_15_digits() -> None:
    assert normalize_microchip_digits_only("NIF 12345678Z") is None


def test_normalize_microchip_id_with_clean_value() -> None:
    assert _normalize_microchip_id(value="941000024967769", evidence=None) == "941000024967769"


def test_normalize_microchip_id_strips_label_and_suffix() -> None:
    value = "Microchip: 941000024967769 (ISO 11784)"
    assert _normalize_microchip_id(value=value, evidence=None) == "941000024967769"


def test_normalize_microchip_id_handles_spaces_and_dashes() -> None:
    value = "Chip: 941 0000-2496 7769"
    assert _normalize_microchip_id(value=value, evidence=None) == "941000024967769"


def test_normalize_microchip_id_uses_evidence_when_value_missing() -> None:
    evidence = [
        {
            "evidence": {
                "snippet": "Identificación electrónica: 900123456789012",
            }
        }
    ]
    assert _normalize_microchip_id(value=None, evidence=evidence) == "900123456789012"


def test_normalize_microchip_id_rejects_invalid_length() -> None:
    assert _normalize_microchip_id(value="Microchip: 12345678", evidence=None) is None


def test_microchip_sort_prefers_chip_context_over_phone_context() -> None:
    chip_context = {
        "value": "941000024967769",
        "confidence": 0.5,
        "evidence": {"snippet": "Microchip: 941000024967769"},
    }
    phone_context = {
        "value": "941000024967769",
        "confidence": 0.5,
        "evidence": {"snippet": "Teléfono: 941000024"},
    }
    assert _candidate_sort_key(chip_context, "microchip_id") > _candidate_sort_key(
        phone_context,
        "microchip_id",
    )


def test_microchip_sort_prefers_fullmatch_over_partial_digits() -> None:
    fullmatch = {
        "value": "941000024967769",
        "confidence": 0.5,
        "evidence": {"snippet": "Microchip: 941000024967769"},
    }
    partial = {
        "value": "ID 941000024967769 ISO 11784",
        "confidence": 0.5,
        "evidence": {"snippet": "ID 941000024967769 ISO 11784"},
    }
    assert _candidate_sort_key(fullmatch, "microchip_id") > _candidate_sort_key(
        partial,
        "microchip_id",
    )
