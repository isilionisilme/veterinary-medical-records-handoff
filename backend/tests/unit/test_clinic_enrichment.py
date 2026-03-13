from __future__ import annotations

from backend.app.application import field_normalizers

KNOWN_NAME = "CENTRO COSTA AZAHAR"
KNOWN_ADDRESS = "Rosa Molas 6, Bajo, 12003 Castelló"


def test_no_auto_enrichment_address_from_name() -> None:
    """Auto-enrichment was removed. clinic_address stays empty even if
    clinic_name matches a catalog entry. Users trigger lookup explicitly."""
    evidence_map: dict[str, list[dict[str, object]]] = {}

    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_name": KNOWN_NAME, "clinic_address": None},
        evidence_map=evidence_map,
    )

    assert normalized["clinic_address"] is None
    assert "clinic_address" not in evidence_map


def test_no_auto_enrichment_name_from_address() -> None:
    """Reverse enrichment (address→name) is also not automatic."""
    evidence_map: dict[str, list[dict[str, object]]] = {}

    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_name": None, "clinic_address": KNOWN_ADDRESS},
        evidence_map=evidence_map,
    )

    # clinic_name stays None — address normalization applies but no auto-enrichment
    assert normalized["clinic_name"] is None
    assert "clinic_name" not in evidence_map


def test_no_enrichment_zero_matches() -> None:
    evidence_map: dict[str, list[dict[str, object]]] = {}

    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_name": "CLINICA INEXISTENTE", "clinic_address": None},
        evidence_map=evidence_map,
    )

    assert normalized["clinic_name"] == "CLINICA INEXISTENTE"
    assert normalized["clinic_address"] is None
    assert "clinic_address" not in evidence_map


def test_no_overwrite_existing_ocr_value() -> None:
    evidence_map: dict[str, list[dict[str, object]]] = {}
    raw_name = "CLINICA OCR ORIGINAL"
    raw_address = "Calle OCR 99, 12002 Castellón"

    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_name": raw_name, "clinic_address": raw_address},
        evidence_map=evidence_map,
    )

    assert normalized["clinic_name"] == raw_name
    assert normalized["clinic_address"] == raw_address
    assert "clinic_name" not in evidence_map
    assert "clinic_address" not in evidence_map


def test_docA_no_auto_enrichment() -> None:
    """docA scenario: clinic_name extracted, clinic_address empty.
    After removing auto-enrichment, address stays empty."""
    evidence_map: dict[str, list[dict[str, object]]] = {}

    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_name": "CENTRO COSTA AZAHAR", "clinic_address": None},
        evidence_map=evidence_map,
    )

    assert normalized["clinic_address"] is None
    assert "clinic_address" not in evidence_map
