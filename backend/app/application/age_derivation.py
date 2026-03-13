"""Helpers for deriving age from normalized birth and reference dates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime

from backend.app.application.field_normalizers import _normalize_date_value

_DATE_FORMAT = "%d/%m/%Y"


@dataclass(frozen=True, slots=True)
class AgePresentation:
    years: int
    display_value: str


def calculate_age_in_years(dob: str, reference_date: str) -> int | None:
    """Return full years elapsed between dob and reference_date."""

    dob_value = _parse_normalized_date(dob)
    reference_value = _parse_normalized_date(reference_date)
    if dob_value is None or reference_value is None:
        return None

    if dob_value > reference_value:
        return None

    years = reference_value.year - dob_value.year
    birthday_not_reached = (reference_value.month, reference_value.day) < (
        dob_value.month,
        dob_value.day,
    )
    if birthday_not_reached:
        years -= 1
    return years


def calculate_age_presentation(
    dob: str,
    reference_date: str,
) -> AgePresentation | None:
    """Return a canonical-years value plus a user-facing display string."""

    dob_value = _parse_normalized_date(dob)
    reference_value = _parse_normalized_date(reference_date)
    if dob_value is None or reference_value is None:
        return None

    if dob_value > reference_value:
        return None

    years = calculate_age_in_years(dob, reference_date)
    if years is None:
        return None

    total_months = (reference_value.year - dob_value.year) * 12 + (
        reference_value.month - dob_value.month
    )
    if reference_value.day < dob_value.day:
        total_months -= 1

    if total_months < 0:
        return None

    if total_months < 12:
        return AgePresentation(
            years=years,
            display_value=_format_age_label(total_months, "mes"),
        )

    return AgePresentation(years=years, display_value=_format_age_label(years, "año"))


def resolve_reference_date(
    visits: list[dict],
    document_date: str | None,
) -> str | None:
    """Pick the latest valid non-future visit date, then document date, then today."""

    latest_visit_date = _latest_valid_visit_date(visits)
    if latest_visit_date is not None:
        return latest_visit_date.strftime(_DATE_FORMAT)

    valid_document_date = _parse_non_future_date(document_date)
    if valid_document_date is not None:
        return valid_document_date.strftime(_DATE_FORMAT)

    return date.today().strftime(_DATE_FORMAT)


def _latest_valid_visit_date(visits: Sequence[object]) -> date | None:
    latest: date | None = None
    for visit in visits:
        if not isinstance(visit, Mapping):
            continue

        visit_date = _parse_non_future_date(visit.get("visit_date"))
        if visit_date is None:
            continue

        if latest is None or visit_date > latest:
            latest = visit_date

    return latest


def _parse_non_future_date(value: object) -> date | None:
    parsed = _parse_normalized_date(value)
    if parsed is None:
        return None
    if parsed > date.today():
        return None
    return parsed


def _parse_normalized_date(value: object) -> date | None:
    normalized_value = _normalize_date_value(value)
    if not normalized_value:
        return None

    try:
        return datetime.strptime(normalized_value, _DATE_FORMAT).date()
    except ValueError:
        return None


def _format_age_label(value: int, singular_unit: str) -> str:
    plural_unit = "meses" if singular_unit == "mes" else "años"
    unit = singular_unit if value == 1 else plural_unit
    return f"{value} {unit}"
