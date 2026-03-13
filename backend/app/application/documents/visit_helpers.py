"""Visit helpers: weight evidence, anchor resolution, segment text building.

Extracted from review_service.py (ARCH-01) to provide low-level utilities
for the visit scoping pipeline.
"""

from __future__ import annotations

import re

from backend.app.application.documents._shared import (
    _extract_evidence_snippet,
    _normalize_visit_date_candidate,
)
from backend.app.application.field_normalizers import _normalize_weight

# Raw-text weight extraction
# ---------------------------------------------------------------------------

_RAW_TIMELINE_HEADER_RE = re.compile(
    r"^\s*[-*•]?\s*(\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4})\s*[-–—]\s*\d{1,2}:\d{2}(?::\d{2})?",
    re.IGNORECASE,
)
_RAW_WEIGHT_TOKEN_RE = re.compile(
    r"(?i)\b(?:peso|pv|p\.)?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(kg|kgs|g)\b"
)


def _weight_evidence_offset(field: dict[str, object], *, default: float = -1.0) -> float:
    evidence = field.get("evidence")
    if isinstance(evidence, dict):
        offset = evidence.get("offset")
        if isinstance(offset, int | float):
            return float(offset)
    return default


def _weight_effective_visit_date(
    *, visit: dict[str, object], weight_field: dict[str, object]
) -> str | None:
    raw_visit_date = visit.get("visit_date")
    normalized_visit_date = _normalize_visit_date_candidate(raw_visit_date)
    if normalized_visit_date is not None:
        return normalized_visit_date

    evidence_snippet = _extract_evidence_snippet(weight_field)
    normalized_from_evidence = _normalize_visit_date_candidate(evidence_snippet)
    if normalized_from_evidence is not None:
        return normalized_from_evidence

    return None


def _extract_latest_visit_weight_from_raw_text(raw_text: str | None) -> dict[str, object] | None:
    if not isinstance(raw_text, str) or not raw_text.strip():
        return None

    current_visit_date: str | None = None
    candidates: list[tuple[str, int, str, str]] = []
    lines = raw_text.splitlines()

    for line_index, line in enumerate(lines):
        header_match = _RAW_TIMELINE_HEADER_RE.search(line)
        if header_match is not None:
            current_visit_date = _normalize_visit_date_candidate(header_match.group(1))

        token_match = _RAW_WEIGHT_TOKEN_RE.search(line)
        if token_match is None or current_visit_date is None:
            continue

        raw_number = token_match.group(1)
        raw_unit = token_match.group(2).lower()
        normalized_weight = _normalize_weight(f"{raw_number} {raw_unit}")
        if not normalized_weight:
            continue

        candidates.append((current_visit_date, line_index, normalized_weight, line.strip()))

    if not candidates:
        return None

    best_date, _, best_weight, best_snippet = max(candidates, key=lambda item: (item[0], item[1]))
    return {
        "date": best_date,
        "value": best_weight,
        "evidence": {"snippet": best_snippet},
    }


# ---------------------------------------------------------------------------
# Visit anchor resolution
# ---------------------------------------------------------------------------


def resolve_snippet_anchor_offset(*, raw_text: str | None, snippet: str | None) -> int | None:
    if not isinstance(raw_text, str) or not isinstance(snippet, str):
        return None

    compact_snippet = " ".join(snippet.split()).strip()
    if len(compact_snippet) < 8:
        return None

    raw_text_lower = raw_text.casefold()
    snippet_lower = compact_snippet.casefold()
    exact_offset = raw_text_lower.find(snippet_lower)
    if exact_offset >= 0:
        return exact_offset

    snippet_prefix = snippet_lower[: min(len(snippet_lower), 48)]
    if len(snippet_prefix) < 12:
        return None

    prefix_offset = raw_text_lower.find(snippet_prefix)
    if prefix_offset >= 0:
        return prefix_offset

    return None


def resolve_visit_from_anchor(
    *,
    candidate_dates: list[str],
    anchor_offset: int | None,
    visit_by_date: dict[str, dict[str, object]],
    visit_occurrences_by_date: dict[str, list[dict[str, object]]],
    raw_text_offsets_by_date: dict[str, list[int]],
    visit_boundary_offsets: list[int],
) -> dict[str, object] | None:
    if anchor_offset is None:
        for candidate_date in candidate_dates:
            target_visit = visit_by_date.get(candidate_date)
            if target_visit is not None:
                return target_visit
        return None

    def _find_nearest_target(
        *,
        lower_offset_inclusive: int | None,
        upper_offset_exclusive: int | None,
    ) -> tuple[int, str, int] | None:
        nearest: tuple[int, str, int] | None = None
        dates_to_check = (
            candidate_dates if candidate_dates else list(raw_text_offsets_by_date.keys())
        )
        for candidate_date in dates_to_check:
            offsets = raw_text_offsets_by_date.get(candidate_date, [])
            if not offsets:
                continue
            for occurrence_index, offset in enumerate(offsets):
                if lower_offset_inclusive is not None and offset < lower_offset_inclusive:
                    continue
                if upper_offset_exclusive is not None and offset >= upper_offset_exclusive:
                    continue
                distance = abs(offset - anchor_offset)
                if nearest is None or distance < nearest[0]:
                    nearest = (distance, candidate_date, occurrence_index)
        return nearest

    nearest_target: tuple[int, str, int] | None = None
    if visit_boundary_offsets:
        lower_offset: int | None = None
        upper_offset: int | None = None
        for boundary_offset in visit_boundary_offsets:
            if boundary_offset <= anchor_offset:
                lower_offset = boundary_offset
                continue
            upper_offset = boundary_offset
            break
        nearest_target = _find_nearest_target(
            lower_offset_inclusive=lower_offset,
            upper_offset_exclusive=upper_offset,
        )

    if nearest_target is None:
        nearest_target = _find_nearest_target(
            lower_offset_inclusive=None,
            upper_offset_exclusive=None,
        )

    if nearest_target is None:
        for candidate_date in candidate_dates:
            target_visit = visit_by_date.get(candidate_date)
            if target_visit is not None:
                return target_visit
        return None

    _, target_date, target_occurrence_index = nearest_target
    date_visits = visit_occurrences_by_date.get(target_date, [])
    if not date_visits:
        return visit_by_date.get(target_date)

    visit_index = min(target_occurrence_index, len(date_visits) - 1)
    return date_visits[visit_index]


# ---------------------------------------------------------------------------
# Segment bounds
# ---------------------------------------------------------------------------


def _find_line_start_offset(*, text: str, offset: int) -> int:
    safe_offset = max(0, min(offset, len(text)))
    previous_break = text.rfind("\n", 0, safe_offset)
    return 0 if previous_break < 0 else previous_break + 1


def _resolve_visit_segment_bounds(
    *,
    anchor_offset: int,
    raw_text: str,
    visit_boundary_offsets: list[int],
    ordered_anchor_offsets: list[int],
) -> tuple[int, int]:
    line_start = _find_line_start_offset(text=raw_text, offset=anchor_offset)

    start_offset = line_start
    for boundary_offset in visit_boundary_offsets:
        if boundary_offset > anchor_offset:
            break
        if boundary_offset >= line_start:
            start_offset = boundary_offset

    end_offset = len(raw_text)
    for boundary_offset in visit_boundary_offsets:
        if boundary_offset > anchor_offset:
            end_offset = min(end_offset, boundary_offset)
            break

    for candidate_anchor in ordered_anchor_offsets:
        if candidate_anchor <= anchor_offset:
            continue
        candidate_line_start = _find_line_start_offset(text=raw_text, offset=candidate_anchor)
        end_offset = min(end_offset, candidate_line_start)
        break

    if end_offset < start_offset:
        end_offset = start_offset
    return start_offset, end_offset


# ---------------------------------------------------------------------------
# Segment text building and population helpers
# ---------------------------------------------------------------------------


def build_visit_segment_text_by_visit_id(
    *,
    raw_text: str | None,
    visit_occurrences_by_date: dict[str, list[dict[str, object]]],
    raw_text_date_occurrences: list[tuple[str, int]],
    visit_boundary_offsets: list[int],
) -> dict[str, str]:
    if not isinstance(raw_text, str) or not raw_text.strip():
        return {}

    ordered_anchor_offsets = [offset for _, offset in raw_text_date_occurrences]
    consumed_occurrences: dict[str, int] = {}
    visit_segments: dict[str, str] = {}

    for visit_date, anchor_offset in raw_text_date_occurrences:
        date_visits = visit_occurrences_by_date.get(visit_date, [])
        if not date_visits:
            continue

        visit_index = consumed_occurrences.get(visit_date, 0)
        if visit_index >= len(date_visits):
            visit_index = len(date_visits) - 1
        consumed_occurrences[visit_date] = consumed_occurrences.get(visit_date, 0) + 1

        target_visit = date_visits[visit_index]
        visit_id = target_visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue
        if visit_id in visit_segments:
            continue

        start_offset, end_offset = _resolve_visit_segment_bounds(
            anchor_offset=anchor_offset,
            raw_text=raw_text,
            visit_boundary_offsets=visit_boundary_offsets,
            ordered_anchor_offsets=ordered_anchor_offsets,
        )
        segment_text = raw_text[start_offset:end_offset].strip()
        if segment_text:
            visit_segments[visit_id] = segment_text

    return visit_segments


# ---------------------------------------------------------------------------
# Weight post-processing (phase helper used by the orchestrator)
# ---------------------------------------------------------------------------


def postprocess_weights(
    *,
    fields_to_keep: list[object],
    assigned_visits: list[dict[str, object]],
    unassigned_visit: dict[str, object] | None,
    raw_text: str | None,
) -> list[object]:
    """Phase 7: Derive document-level weight from most-recent visit weight."""
    unassigned_weight_fields_for_derivation: list[dict[str, object]] = []
    if unassigned_visit is not None:
        raw_unassigned_fields = unassigned_visit.get("fields")
        if isinstance(raw_unassigned_fields, list):
            weight_fields_in_unassigned = [
                f for f in raw_unassigned_fields if isinstance(f, dict) and f.get("key") == "weight"
            ]
            if weight_fields_in_unassigned:
                for wf in weight_fields_in_unassigned:
                    restored = dict(wf)
                    restored["scope"] = "document"
                    restored["section"] = "patient"
                    raw_val = restored.get("value")
                    normalized_val = _normalize_weight(raw_val)
                    if normalized_val:
                        restored["value"] = normalized_val
                    fields_to_keep.append(restored)
                    unassigned_weight_fields_for_derivation.append(restored)
                unassigned_visit["fields"] = [
                    f
                    for f in raw_unassigned_fields
                    if not (isinstance(f, dict) and f.get("key") == "weight")
                ]

    visit_weights: list[tuple[str, float, int, int, dict[str, object]]] = []
    for visit_index, visit in enumerate(assigned_visits):
        vf = visit.get("fields")
        if not isinstance(vf, list):
            continue
        for field_index, field in enumerate(vf):
            if isinstance(field, dict) and field.get("key") == "weight":
                effective_visit_date = _weight_effective_visit_date(
                    visit=visit,
                    weight_field=field,
                )
                if effective_visit_date is None:
                    continue
                visit_weights.append(
                    (
                        effective_visit_date,
                        _weight_evidence_offset(field),
                        visit_index,
                        field_index,
                        field,
                    )
                )

    for unassigned_index, unassigned_weight in enumerate(unassigned_weight_fields_for_derivation):
        effective_date = _normalize_visit_date_candidate(
            _extract_evidence_snippet(unassigned_weight)
        )
        if effective_date is None:
            continue
        visit_weights.append(
            (
                effective_date,
                _weight_evidence_offset(unassigned_weight),
                len(assigned_visits),
                unassigned_index,
                unassigned_weight,
            )
        )

    latest_weight_from_raw = _extract_latest_visit_weight_from_raw_text(raw_text)
    if latest_weight_from_raw is not None:
        visit_weights.append(
            (
                str(latest_weight_from_raw["date"]),
                -1.0,
                len(assigned_visits) + 1,
                0,
                {
                    "value": latest_weight_from_raw["value"],
                    "value_type": "string",
                    "classification": "medical_record",
                    "evidence": latest_weight_from_raw["evidence"],
                },
            )
        )

    if visit_weights:
        visit_weights.sort(key=lambda entry: (entry[0], entry[1], entry[2], entry[3]))
        most_recent_weight = visit_weights[-1][4]
        fields_to_keep = [
            f for f in fields_to_keep if not (isinstance(f, dict) and f.get("key") == "weight")
        ]
        raw_derived_val = most_recent_weight.get("value")
        normalized_derived_val = _normalize_weight(raw_derived_val)
        fields_to_keep.append(
            {
                "field_id": "derived-weight-current",
                "key": "weight",
                "value": normalized_derived_val if normalized_derived_val else raw_derived_val,
                "value_type": most_recent_weight.get("value_type", "string"),
                "scope": "document",
                "section": "patient",
                "classification": most_recent_weight.get("classification", "medical_record"),
                "origin": "derived",
                "evidence": most_recent_weight.get("evidence"),
            }
        )

    return fields_to_keep
