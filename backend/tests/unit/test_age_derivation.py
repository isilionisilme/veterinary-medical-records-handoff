"""Unit tests for age derivation helpers."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest

from backend.app.application.age_derivation import (
    calculate_age_in_years,
    calculate_age_presentation,
    resolve_reference_date,
)


@pytest.mark.parametrize(
    ("dob", "reference_date", "expected"),
    [
        ("15/03/2018", "15/03/2026", 8),
        ("15/03/2018", "14/03/2026", 7),
        ("29/02/2020", "28/02/2021", 0),
        ("29/02/2020", "01/03/2021", 1),
    ],
)
def test_calculate_age_in_years_returns_complete_years(
    dob: str,
    reference_date: str,
    expected: int,
) -> None:
    assert calculate_age_in_years(dob, reference_date) == expected


@pytest.mark.parametrize(
    ("dob", "reference_date", "expected_years", "expected_display_value"),
    [
        ("15/03/2018", "15/03/2026", 8, "8 años"),
        ("15/03/2018", "14/03/2026", 7, "7 años"),
        ("29/02/2020", "28/02/2021", 0, "11 meses"),
        ("01/10/2025", "14/03/2026", 0, "5 meses"),
        ("01/03/2025", "01/03/2026", 1, "1 año"),
    ],
)
def test_calculate_age_presentation_returns_display_value(
    dob: str,
    reference_date: str,
    expected_years: int,
    expected_display_value: str,
) -> None:
    result = calculate_age_presentation(dob, reference_date)

    assert result is not None
    assert result.years == expected_years
    assert result.display_value == expected_display_value


@pytest.mark.parametrize(
    ("dob", "reference_date"),
    [
        (None, "15/03/2026"),
        ("", "15/03/2026"),
        ("invalid", "15/03/2026"),
        ("15/03/2018", None),
        ("15/03/2018", ""),
        ("15/03/2018", "invalid"),
        ("16/03/2026", "15/03/2026"),
    ],
)
def test_calculate_age_in_years_returns_none_for_invalid_inputs(
    dob: str | None,
    reference_date: str | None,
) -> None:
    assert calculate_age_in_years(dob, reference_date) is None


@pytest.mark.parametrize(
    ("dob", "reference_date"),
    [
        (None, "15/03/2026"),
        ("", "15/03/2026"),
        ("invalid", "15/03/2026"),
        ("15/03/2018", None),
        ("15/03/2018", ""),
        ("15/03/2018", "invalid"),
        ("16/03/2026", "15/03/2026"),
    ],
)
def test_calculate_age_presentation_returns_none_for_invalid_inputs(
    dob: str | None,
    reference_date: str | None,
) -> None:
    assert calculate_age_presentation(dob, reference_date) is None


def test_resolve_reference_date_prefers_latest_valid_visit_date() -> None:
    visits = [
        {"visit_date": "01/02/2024"},
        {"visit_date": "05/01/2025"},
        {"visit_date": "invalid"},
        {"visit_date": "31/12/2024"},
    ]

    with patch("backend.app.application.age_derivation.date") as mocked_date:
        mocked_date.today.return_value = date(2026, 3, 8)
        mocked_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert resolve_reference_date(visits, "15/03/2025") == "05/01/2025"


def test_resolve_reference_date_falls_back_to_document_date_when_visits_invalid() -> None:
    visits = [
        {"visit_date": "invalid"},
        {"visit_date": "09/03/2026"},
        {},
    ]

    with patch("backend.app.application.age_derivation.date") as mocked_date:
        mocked_date.today.return_value = date(2026, 3, 8)
        mocked_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert resolve_reference_date(visits, "15/03/2025") == "15/03/2025"


def test_resolve_reference_date_falls_back_to_today_when_no_valid_dates_exist() -> None:
    visits = [{"visit_date": "10/03/2026"}, {"visit_date": "invalid"}, "bad"]

    with patch("backend.app.application.age_derivation.date") as mocked_date:
        mocked_date.today.return_value = date(2026, 3, 8)
        mocked_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert resolve_reference_date(visits, "32/01/2025") == "08/03/2026"


def test_resolve_reference_date_ignores_future_document_date() -> None:
    with patch("backend.app.application.age_derivation.date") as mocked_date:
        mocked_date.today.return_value = date(2026, 3, 8)
        mocked_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert resolve_reference_date([], "09/03/2026") == "08/03/2026"
