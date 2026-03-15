"""Types and small helpers for visit scoping orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from backend.app.application.documents._shared import (
    _extract_evidence_snippet,
    _extract_visit_date_candidates_from_text,
    _normalize_visit_date_candidate,
)


@dataclass(frozen=True)
class VisitRoster:
    """Bundled visit collections produced by _build_visit_roster()."""

    assigned_visits: list[dict[str, object]]
    visit_by_date: dict[str, dict[str, object]]
    visit_occurrences_by_date: dict[str, list[dict[str, object]]]
    unassigned_visit: dict[str, object] | None


class RawTextContext(NamedTuple):
    """Raw-text analysis results for the orchestrator."""

    detected_visit_dates: list[str]
    date_occurrences: list[tuple[str, int]]
    offsets_by_date: dict[str, list[int]]
    boundary_offsets: list[int]


class FieldClassificationResult(NamedTuple):
    """Result of classifying raw fields into scopes."""

    fields_to_keep: list[object]
    visit_scoped_fields: list[dict[str, object]]
    visit_group_metadata: dict[str, list[object]]
    detected_visit_dates: list[str]
    seen_detected_visit_dates: set[str]


def extract_detected_visit_dates(
    item: dict[str, object],
    *,
    snippet_date_cache: dict[str, list[str]],
) -> list[str]:
    """Return normalized visit dates referenced by a field evidence snippet."""
    evidence_snippet = _extract_evidence_snippet(item)
    cached = snippet_date_cache.get(evidence_snippet)
    if cached is not None:
        return cached
    dates = list(_extract_visit_date_candidates_from_text(text=evidence_snippet))
    snippet_date_cache[evidence_snippet] = dates
    return dates


def should_scope_weight_as_visit(
    item: dict[str, object],
    *,
    snippet_date_cache: dict[str, list[str]],
) -> bool:
    """Return True when a weight field clearly belongs to a visit."""
    field_scope = item.get("scope")
    field_section = item.get("section")
    is_explicit_visit_scoped = (
        isinstance(field_scope, str) and field_scope.strip().casefold() == "visit"
    ) or (isinstance(field_section, str) and field_section.strip().casefold() == "visits")
    if is_explicit_visit_scoped:
        return True

    return bool(extract_detected_visit_dates(item, snippet_date_cache=snippet_date_cache))


def process_visit_date_metadata(
    value: object,
    *,
    seen_dates: set[str],
    detected_dates: list[str],
) -> None:
    """Record a visit_date metadata value if it normalizes to a new date."""
    normalized = _normalize_visit_date_candidate(value)
    if normalized is not None and normalized not in seen_dates:
        seen_dates.add(normalized)
        detected_dates.append(normalized)


def record_new_visit_dates(
    dates: list[str],
    *,
    seen: set[str],
    detected: list[str],
) -> None:
    """Append dates not already seen to the detected list."""
    for dt in dates:
        if dt not in seen:
            seen.add(dt)
            detected.append(dt)
