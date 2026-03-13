from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.application.processing_runner import _build_interpretation_artifact

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "interpretation"


@pytest.mark.parametrize(
    ("fixture_name", "field_key", "expected"),
    [
        ("species_breed_case.txt", "species", "canino"),
        ("species_breed_case.txt", "breed", "YORKSHIRE TERRIER"),
        ("sex_case.txt", "sex", "hembra"),
        ("microchip_suffix_case.txt", "microchip_id", "00023035139"),
        ("visit_date_anchor_case.txt", "visit_date", "07/03/2024"),
    ],
)
def test_interpretation_fixture_regressions(
    fixture_name: str,
    field_key: str,
    expected: str,
) -> None:
    raw_text = (FIXTURES_DIR / fixture_name).read_text(encoding="utf-8")

    payload = _build_interpretation_artifact(
        document_id="doc-fixture",
        run_id="run-fixture",
        raw_text=raw_text,
    )

    global_schema = payload["data"]["global_schema"]
    assert global_schema[field_key] == expected


def test_species_token_is_not_kept_inside_breed() -> None:
    raw_text = (FIXTURES_DIR / "species_breed_case.txt").read_text(encoding="utf-8")

    payload = _build_interpretation_artifact(
        document_id="doc-breed-clean",
        run_id="run-breed-clean",
        raw_text=raw_text,
    )

    breed = payload["data"]["global_schema"]["breed"]
    assert isinstance(breed, str)
    assert "canina" not in breed.casefold()
    assert "canino" not in breed.casefold()


def test_visit_date_fixture_exposes_anchor_based_selection_reason() -> None:
    raw_text = (FIXTURES_DIR / "visit_date_anchor_case.txt").read_text(encoding="utf-8")

    payload = _build_interpretation_artifact(
        document_id="doc-visit-anchor",
        run_id="run-visit-anchor",
        raw_text=raw_text,
    )

    date_selection = payload["data"]["summary"]["date_selection"]
    visit_selection = date_selection["visit_date"]
    assert isinstance(visit_selection, dict)
    assert visit_selection["anchor_priority"] >= 4
    assert isinstance(visit_selection["target_reason"], str)
    assert visit_selection["target_reason"].startswith("anchor:")


def test_unanchored_dates_default_to_document_date_not_visit_date() -> None:
    raw_text = """
    Paciente: Luna
    Fecha: 14/03/2024
    """

    payload = _build_interpretation_artifact(
        document_id="doc-unanchored-date",
        run_id="run-unanchored-date",
        raw_text=raw_text,
    )

    global_schema = payload["data"]["global_schema"]
    assert global_schema["visit_date"] is None
    date_selection = payload["data"]["summary"]["date_selection"]
    document_selection = date_selection["document_date"]
    assert isinstance(document_selection, dict)
    assert document_selection["anchor"] is None
    assert document_selection["anchor_priority"] == 0
    assert document_selection["target_reason"] is None


def test_alphanumeric_microchip_value_without_digits_is_dropped() -> None:
    raw_text = """
    Paciente: Toby
    Microchip: NHC 2.c AB-77
    """

    payload = _build_interpretation_artifact(
        document_id="doc-microchip-alphanumeric",
        run_id="run-microchip-alphanumeric",
        raw_text=raw_text,
    )

    assert payload["data"]["global_schema"]["microchip_id"] is None


def test_invalid_calendar_date_is_dropped() -> None:
    raw_text = """
    Paciente: Nala
    Fecha de visita: 39/19/2024
    """

    payload = _build_interpretation_artifact(
        document_id="doc-invalid-date",
        run_id="run-invalid-date",
        raw_text=raw_text,
    )

    assert payload["data"]["global_schema"]["visit_date"] is None


def test_unanchored_timeline_date_does_not_set_visit_date() -> None:
    raw_text = """
    Paciente: Kira
    - 14/03/2024 - Factura emitida
    """

    payload = _build_interpretation_artifact(
        document_id="doc-timeline-unanchored",
        run_id="run-timeline-unanchored",
        raw_text=raw_text,
    )

    global_schema = payload["data"]["global_schema"]
    assert global_schema["visit_date"] is None
    date_selection = payload["data"]["summary"]["date_selection"]
    document_selection = date_selection["document_date"]
    assert isinstance(document_selection, dict)
    assert document_selection["anchor"] is None
    assert document_selection["anchor_priority"] == 0
    assert document_selection["target_reason"] is None
