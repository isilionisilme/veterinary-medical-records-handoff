"""Unit tests for dob (date of birth) normalization and date value handling."""

from __future__ import annotations

import pytest

from backend.app.application.field_normalizers import (
    _normalize_date_value,
    normalize_canonical_fields,
)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        # Valid formats DD/MM/YYYY
        ("15/03/2018", "15/03/2018"),
        ("01/01/2020", "01/01/2020"),
        ("31/12/2019", "31/12/2019"),
        # Valid formats with zero-padding normalization
        ("5/1/20", "05/01/2020"),
        ("1/11/2021", "01/11/2021"),
        # Valid ISO format YYYY-MM-DD → DD/MM/YYYY
        ("2018-03-15", "15/03/2018"),
        ("2020-01-01", "01/01/2020"),
        # Valid format with dash separator DD-MM-YYYY → DD/MM/YYYY
        ("15-03-2018", "15/03/2018"),
        ("30-04-2016", "30/04/2016"),
        # Valid format with dot separator DD.MM.YYYY → DD/MM/YYYY
        ("15.03.2018", "15/03/2018"),
        ("01.11.2021", "01/11/2021"),
        # Valid format with 2-digit year (assumed 20xx)
        ("15/03/18", "15/03/2018"),
        ("01/01/21", "01/01/2021"),
        # Valid format with short year (single digit or xx format)
        ("30/04/16", "30/04/2016"),
        # Edge case: label residuals should be stripped
        ("Fecha nac: 15/03/2018", "15/03/2018"),
        ("DOB: 01/11/2021", "01/11/2021"),
        ("F. Nac - 30/04/2016", "30/04/2016"),
        # Edge case: whitespace and extra characters
        ("  15/03/2018  ", "15/03/2018"),
        ("15/03/2018 (estimado)", "15/03/2018"),
    ],
)
def test_normalize_date_value_valid_formats(raw_value: str, expected: str) -> None:
    """Test that _normalize_date_value correctly normalizes valid date formats."""
    assert _normalize_date_value(raw_value) == expected


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        "",
        "   ",
        "invalid",
        "99/99/9999",
        "32/01/2020",  # invalid day
        "15/13/2020",  # invalid month
        "00/01/2020",  # day cannot be 0
        "15/00/2020",  # month cannot be 0
        "2020-13-01",  # invalid month in ISO
        "2020-01-32",  # invalid day in ISO
        "not a date",
        "123456",  # digits but not date format
        "15-03",  # incomplete date
        "2020",  # year only
    ],
)
def test_normalize_date_value_invalid_inputs(invalid_value: str | None) -> None:
    """Test that _normalize_date_value returns None for invalid inputs."""
    assert _normalize_date_value(invalid_value) is None


def test_normalize_date_value_with_none() -> None:
    """Test that _normalize_date_value handles None gracefully."""
    assert _normalize_date_value(None) is None


def test_normalize_date_value_empty_string() -> None:
    """Test that _normalize_date_value handles empty string."""
    assert _normalize_date_value("") is None


def test_normalize_canonical_fields_includes_dob() -> None:
    """Test that normalize_canonical_fields processes dob field."""
    raw_fields = {"dob": "15/03/2018"}
    normalized = normalize_canonical_fields(raw_fields)
    assert normalized["dob"] == "15/03/2018"


def test_normalize_canonical_fields_normalizes_dob_with_short_year() -> None:
    """Test that dob normalization applies to short year formats."""
    raw_fields = {"dob": "5/1/20"}
    normalized = normalize_canonical_fields(raw_fields)
    assert normalized["dob"] == "05/01/2020"


def test_normalize_canonical_fields_handles_missing_dob() -> None:
    """Test that normalize_canonical_fields handles missing dob field."""
    raw_fields = {"pet_name": "Luna"}
    normalized = normalize_canonical_fields(raw_fields)
    assert "dob" in normalized
    assert normalized["dob"] is None


def test_normalize_canonical_fields_handles_null_dob() -> None:
    """Test that normalize_canonical_fields handles null dob value."""
    raw_fields = {"dob": None}
    normalized = normalize_canonical_fields(raw_fields)
    assert normalized["dob"] is None


def test_normalize_canonical_fields_strips_dob_labels() -> None:
    """Test that dob normalization strips common label prefixes."""
    raw_fields = {"dob": "Fecha nac: 15/03/2018"}
    normalized = normalize_canonical_fields(raw_fields)
    assert normalized["dob"] == "15/03/2018"


def test_normalize_date_value_calendar_validation() -> None:
    """Test that _normalize_date_value validates calendar dates (e.g., Feb 30 is invalid)."""
    assert _normalize_date_value("30/02/2020") is None  # Feb 30 doesn't exist
    assert _normalize_date_value("31/04/2020") is None  # April has 30 days
    assert _normalize_date_value("29/02/2020") == "29/02/2020"  # leap year valid
    assert _normalize_date_value("29/02/2021") is None  # non-leap year invalid


def test_normalize_date_value_two_digit_year_99_maps_to_1999() -> None:
    """Test that %y pivot is respected for two-digit year 99."""
    assert _normalize_date_value("31/12/99") == "31/12/1999"


def test_normalize_canonical_fields_two_digit_year_applies_to_all_date_fields() -> None:
    """Test that two-digit year parsing behaves consistently across date fields."""
    raw_fields = {
        "dob": "31/12/99",
        "visit_date": "01/01/00",
        "document_date": "15/03/18",
        "admission_date": "05/04/21",
        "discharge_date": "06/04/21",
    }
    normalized = normalize_canonical_fields(raw_fields)
    assert normalized["dob"] == "31/12/1999"
    assert normalized["visit_date"] == "01/01/2000"
    assert normalized["document_date"] == "15/03/2018"
    assert normalized["admission_date"] == "05/04/2021"
    assert normalized["discharge_date"] == "06/04/2021"


def test_normalize_canonical_fields_derives_age_from_latest_visit_when_enabled() -> None:
    raw_fields = {
        "dob": "15/03/2018",
        "age": "",
        "document_date": "01/02/2026",
    }

    normalized = normalize_canonical_fields(
        raw_fields,
        visits=[
            {"visit_date": "01/02/2026"},
            {"visit_date": "14/03/2026"},
        ],
        derive_age=True,
    )

    assert normalized["age"] == "7"
    assert normalized["age_origin"] == "derived"


def test_normalize_canonical_fields_does_not_overwrite_existing_age_when_enabled() -> None:
    raw_fields = {
        "dob": "15/03/2018",
        "age": "99",
        "document_date": "01/02/2026",
    }

    normalized = normalize_canonical_fields(
        raw_fields,
        visits=[{"visit_date": "14/03/2026"}],
        derive_age=True,
    )

    assert normalized["age"] == "99"
    assert "age_origin" not in normalized


def test_normalize_canonical_fields_keeps_age_empty_when_dob_is_invalid() -> None:
    normalized = normalize_canonical_fields(
        {"dob": "31/02/2018", "age": "", "document_date": "14/03/2026"},
        visits=[{"visit_date": "14/03/2026"}],
        derive_age=True,
    )

    assert normalized["age"] == ""
    assert "age_origin" not in normalized


def test_normalize_canonical_fields_keeps_age_empty_when_dob_is_in_future() -> None:
    normalized = normalize_canonical_fields(
        {"dob": "15/03/2027", "age": "", "document_date": "14/03/2026"},
        visits=[{"visit_date": "14/03/2026"}],
        derive_age=True,
    )

    assert normalized["age"] == ""
    assert "age_origin" not in normalized
