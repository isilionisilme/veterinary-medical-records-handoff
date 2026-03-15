"""Visit scoping orchestration: field classification, visit roster, assignment."""

from __future__ import annotations

from backend.app.application.documents._shared import (
    _VISIT_GROUP_METADATA_KEY_SET,
    _VISIT_GROUP_METADATA_KEYS,
    _VISIT_SCOPED_KEY_SET,
    _contains_any_date_token,
    _detect_visit_dates_from_raw_text,
    _extract_evidence_snippet,
    _extract_visit_date_candidates_from_text,
    _locate_visit_boundary_offsets_from_raw_text,
    _locate_visit_date_occurrences_from_raw_text,
    _normalize_visit_date_candidate,
)
from backend.app.application.documents.visit_helpers import (
    build_visit_segment_text_by_visit_id,
    postprocess_weights,
    resolve_snippet_anchor_offset,
    resolve_visit_from_anchor,
)
from backend.app.application.documents.visit_population import (
    populate_missing_reason_for_visit_from_segments,
    populate_visit_observations_actions_from_segments,
    populate_visit_scoped_fields_from_segment_candidates,
)
from backend.app.application.documents.visit_scoping_helpers import (
    FieldClassificationResult,
    RawTextContext,
    VisitRoster,
    extract_detected_visit_dates,
    process_visit_date_metadata,
    record_new_visit_dates,
    should_scope_weight_as_visit,
)

_UNASSIGNED_VISIT_SORT_DATE = "9999-12-31"


def _classify_fields_into_scopes(
    raw_fields: list[object],
    *,
    raw_text_detected_visit_dates: list[str],
) -> FieldClassificationResult:
    """Phase 1: Split fields into document-scoped, visit-scoped, and metadata."""
    fields_to_keep: list[object] = []
    visit_scoped_fields: list[dict[str, object]] = []
    visit_group_metadata: dict[str, list[object]] = {}
    detected_visit_dates: list[str] = []
    seen_detected_visit_dates: set[str] = set()
    snippet_date_cache: dict[str, list[str]] = {}

    for item in raw_fields:
        if not isinstance(item, dict):
            fields_to_keep.append(item)
            continue

        key_raw = item.get("key")
        key = key_raw if isinstance(key_raw, str) else ""

        if key in _VISIT_GROUP_METADATA_KEY_SET:
            visit_group_metadata.setdefault(key, []).append(item.get("value"))
            if key == "visit_date":
                process_visit_date_metadata(
                    item.get("value"),
                    seen_dates=seen_detected_visit_dates,
                    detected_dates=detected_visit_dates,
                )
            continue

        if key not in _VISIT_SCOPED_KEY_SET:
            fields_to_keep.append(item)
            continue

        if key == "weight" and not should_scope_weight_as_visit(
            item, snippet_date_cache=snippet_date_cache
        ):
            fields_to_keep.append(item)
            continue

        visit_field = dict(item)
        visit_field["scope"] = "visit"
        visit_field["section"] = "visits"
        visit_scoped_fields.append(visit_field)
        record_new_visit_dates(
            extract_detected_visit_dates(visit_field, snippet_date_cache=snippet_date_cache),
            seen=seen_detected_visit_dates,
            detected=detected_visit_dates,
        )

    record_new_visit_dates(
        raw_text_detected_visit_dates,
        seen=seen_detected_visit_dates,
        detected=detected_visit_dates,
    )

    return FieldClassificationResult(
        fields_to_keep=fields_to_keep,
        visit_scoped_fields=visit_scoped_fields,
        visit_group_metadata=visit_group_metadata,
        detected_visit_dates=detected_visit_dates,
        seen_detected_visit_dates=seen_detected_visit_dates,
    )


def _parse_existing_visits(
    projected: dict[str, object],
    *,
    detected_visit_dates: list[str],
    seen_detected_visit_dates: set[str],
) -> tuple[
    list[dict[str, object]],
    dict[str, dict[str, object]],
    dict[str, list[dict[str, object]]],
    dict[str, object] | None,
]:
    raw_visits = projected.get("visits")
    visits: list[dict[str, object]] = [
        dict(v) for v in (raw_visits if isinstance(raw_visits, list) else []) if isinstance(v, dict)
    ]

    unassigned_visit: dict[str, object] | None = None
    assigned_visits: list[dict[str, object]] = []
    visit_by_date: dict[str, dict[str, object]] = {}
    visit_occurrences_by_date: dict[str, list[dict[str, object]]] = {}
    for visit in visits:
        visit_id = visit.get("visit_id")
        if isinstance(visit_id, str) and visit_id == "unassigned":
            unassigned_visit = visit
            continue

        existing_fields = visit.get("fields")
        if isinstance(existing_fields, list):
            visit["fields"] = list(existing_fields)
        else:
            visit["fields"] = []

        normalized_visit_date = _normalize_visit_date_candidate(visit.get("visit_date"))
        if normalized_visit_date is not None:
            visit["visit_date"] = normalized_visit_date
            visit_by_date.setdefault(normalized_visit_date, visit)
            visit_occurrences_by_date.setdefault(normalized_visit_date, []).append(visit)
            if normalized_visit_date not in seen_detected_visit_dates:
                seen_detected_visit_dates.add(normalized_visit_date)
                detected_visit_dates.append(normalized_visit_date)

        assigned_visits.append(visit)

    return assigned_visits, visit_by_date, visit_occurrences_by_date, unassigned_visit


def _generate_missing_visits(
    *,
    assigned_visits: list[dict[str, object]],
    visit_by_date: dict[str, dict[str, object]],
    visit_occurrences_by_date: dict[str, list[dict[str, object]]],
    detected_visit_dates: list[str],
    raw_text_detected_visit_dates: list[str],
) -> None:
    required_visit_sequence: list[str] = list(detected_visit_dates)
    raw_visit_occurrence_counts: dict[str, int] = {}
    for visit_date in raw_text_detected_visit_dates:
        raw_visit_occurrence_counts[visit_date] = raw_visit_occurrence_counts.get(visit_date, 0) + 1
    for visit_date, count in raw_visit_occurrence_counts.items():
        if count > 1:
            required_visit_sequence.extend([visit_date] * (count - 1))

    generated_visit_counter = len(assigned_visits) + 1
    seen_required_occurrences: dict[str, int] = {}
    for visit_date in required_visit_sequence:
        occurrence_index = seen_required_occurrences.get(visit_date, 0) + 1
        seen_required_occurrences[visit_date] = occurrence_index

        existing_occurrences = len(visit_occurrences_by_date.get(visit_date, []))
        if existing_occurrences >= occurrence_index:
            continue

        generated_visit = {
            "visit_id": f"visit-{generated_visit_counter:03d}",
            "visit_date": visit_date,
            "admission_date": None,
            "discharge_date": None,
            "reason_for_visit": None,
            "fields": [],
        }
        generated_visit_counter += 1
        assigned_visits.append(generated_visit)
        visit_by_date.setdefault(visit_date, generated_visit)
        visit_occurrences_by_date.setdefault(visit_date, []).append(generated_visit)


def _build_visit_roster(
    projected: dict[str, object],
    *,
    detected_visit_dates: list[str],
    seen_detected_visit_dates: set[str],
    raw_text_detected_visit_dates: list[str],
) -> VisitRoster:
    """Phase 2+3: Parse existing visits and generate missing ones."""
    assigned_visits, visit_by_date, visit_occurrences_by_date, unassigned_visit = (
        _parse_existing_visits(
            projected,
            detected_visit_dates=detected_visit_dates,
            seen_detected_visit_dates=seen_detected_visit_dates,
        )
    )
    _generate_missing_visits(
        assigned_visits=assigned_visits,
        visit_by_date=visit_by_date,
        visit_occurrences_by_date=visit_occurrences_by_date,
        detected_visit_dates=detected_visit_dates,
        raw_text_detected_visit_dates=raw_text_detected_visit_dates,
    )

    for visit in assigned_visits:
        for metadata_key in _VISIT_GROUP_METADATA_KEYS:
            if metadata_key not in visit:
                visit[metadata_key] = None

    if unassigned_visit is not None:
        existing_unassigned_fields = unassigned_visit.get("fields")
        if isinstance(existing_unassigned_fields, list):
            unassigned_visit["fields"] = list(existing_unassigned_fields)
        else:
            unassigned_visit["fields"] = []

    return VisitRoster(
        assigned_visits=assigned_visits,
        visit_by_date=visit_by_date,
        visit_occurrences_by_date=visit_occurrences_by_date,
        unassigned_visit=unassigned_visit,
    )


def _resolve_target_visit(
    visit_field: dict[str, object],
    *,
    roster: VisitRoster,
    raw_text: str | None,
    raw_text_offsets_by_date: dict[str, list[int]],
    visit_boundary_offsets: list[int],
) -> dict[str, object] | None:
    """Resolve target visit for a field via 4-strategy fallback chain."""
    evidence_snippet = _extract_evidence_snippet(visit_field)
    evidence_visit_dates = _extract_visit_date_candidates_from_text(text=evidence_snippet)
    has_ambiguous_date_token = _contains_any_date_token(text=evidence_snippet)
    evidence_anchor_offset = resolve_snippet_anchor_offset(
        raw_text=raw_text,
        snippet=evidence_snippet,
    )

    if evidence_visit_dates:
        target = resolve_visit_from_anchor(
            candidate_dates=evidence_visit_dates,
            anchor_offset=evidence_anchor_offset,
            visit_by_date=roster.visit_by_date,
            visit_occurrences_by_date=roster.visit_occurrences_by_date,
            raw_text_offsets_by_date=raw_text_offsets_by_date,
            visit_boundary_offsets=visit_boundary_offsets,
        )
        if target is not None:
            return target

    if (
        not has_ambiguous_date_token
        and evidence_anchor_offset is not None
        and len(roster.visit_by_date) > 1
    ):
        target = resolve_visit_from_anchor(
            candidate_dates=[],
            anchor_offset=evidence_anchor_offset,
            visit_by_date=roster.visit_by_date,
            visit_occurrences_by_date=roster.visit_occurrences_by_date,
            raw_text_offsets_by_date=raw_text_offsets_by_date,
            visit_boundary_offsets=visit_boundary_offsets,
        )
        if target is not None:
            return target

    if len(roster.visit_by_date) == 1 and not has_ambiguous_date_token:
        return next(iter(roster.visit_by_date.values()))

    return None


def _assign_fields_to_visits(
    *,
    visit_scoped_fields: list[dict[str, object]],
    raw_text: str | None,
    roster: VisitRoster,
    raw_text_offsets_by_date: dict[str, list[int]],
    visit_boundary_offsets: list[int],
) -> dict[str, object] | None:
    """Phase 4: Assign each visit-scoped field to a visit via evidence anchoring."""
    unassigned_visit = roster.unassigned_visit
    for visit_field in visit_scoped_fields:
        target_visit = _resolve_target_visit(
            visit_field,
            roster=roster,
            raw_text=raw_text,
            raw_text_offsets_by_date=raw_text_offsets_by_date,
            visit_boundary_offsets=visit_boundary_offsets,
        )

        if target_visit is None:
            if unassigned_visit is None:
                unassigned_visit = {
                    "visit_id": "unassigned",
                    "visit_date": None,
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [],
                }
            unassigned_fields = unassigned_visit.get("fields")
            if not isinstance(unassigned_fields, list):
                unassigned_fields = []
                unassigned_visit["fields"] = unassigned_fields
            unassigned_fields.append(visit_field)
            continue

        target_visit_fields = target_visit.get("fields")
        if not isinstance(target_visit_fields, list):
            target_visit_fields = []
            target_visit["fields"] = target_visit_fields
        target_visit_fields.append(visit_field)

    return unassigned_visit


def _distribute_visit_group_metadata(
    *,
    visit_group_metadata: dict[str, list[object]],
    visit_by_date: dict[str, dict[str, object]],
    unassigned_visit: dict[str, object] | None,
) -> None:
    """Phase 6: Distribute visit-group metadata to matching visits."""
    metadata_values_for_unassigned: dict[str, object] = {}
    for metadata_key in _VISIT_GROUP_METADATA_KEYS:
        values = visit_group_metadata.get(metadata_key, [])
        if metadata_key == "visit_date":
            for value in values:
                normalized_visit_date = _normalize_visit_date_candidate(value)
                if normalized_visit_date is None:
                    continue
                target_visit = visit_by_date.get(normalized_visit_date)
                if target_visit is None:
                    metadata_values_for_unassigned.setdefault(metadata_key, normalized_visit_date)
                    continue
                target_visit["visit_date"] = normalized_visit_date
            continue

        if values:
            metadata_values_for_unassigned.setdefault(metadata_key, values[0])

    if unassigned_visit is not None:
        for metadata_key in _VISIT_GROUP_METADATA_KEYS:
            if metadata_key in metadata_values_for_unassigned:
                unassigned_visit[metadata_key] = metadata_values_for_unassigned[metadata_key]
            elif metadata_key not in unassigned_visit:
                unassigned_visit[metadata_key] = None


def _finalize_visit_list(
    *,
    assigned_visits: list[dict[str, object]],
    unassigned_visit: dict[str, object] | None,
) -> list[dict[str, object]]:
    """Phase 8: Sort visits and append unassigned bucket if non-empty."""
    assigned_visits.sort(
        key=lambda visit: (
            str(visit.get("visit_date") or _UNASSIGNED_VISIT_SORT_DATE),
            str(visit.get("visit_id") or ""),
        )
    )

    normalized_visits: list[dict[str, object]] = list(assigned_visits)
    if unassigned_visit is not None:
        unassigned_fields = unassigned_visit.get("fields")
        has_unassigned_fields = isinstance(unassigned_fields, list) and any(
            isinstance(field, dict) for field in unassigned_fields
        )
        has_unassigned_metadata = any(
            unassigned_visit.get(metadata_key) not in (None, "")
            for metadata_key in _VISIT_GROUP_METADATA_KEYS
        )
        if has_unassigned_fields or has_unassigned_metadata:
            normalized_visits.append(unassigned_visit)
    return normalized_visits


def _prepare_raw_text_context(raw_text: str | None) -> RawTextContext:
    """Analyse raw text for visit dates, offsets, and boundaries."""
    detected_visit_dates = _detect_visit_dates_from_raw_text(raw_text=raw_text)
    date_occurrences = _locate_visit_date_occurrences_from_raw_text(raw_text=raw_text)
    offsets_by_date: dict[str, list[int]] = {}
    for norm_date, offset in date_occurrences:
        offsets_by_date.setdefault(norm_date, []).append(offset)
    boundary_offsets = _locate_visit_boundary_offsets_from_raw_text(raw_text=raw_text)
    return RawTextContext(
        detected_visit_dates=detected_visit_dates,
        date_occurrences=date_occurrences,
        offsets_by_date=offsets_by_date,
        boundary_offsets=boundary_offsets,
    )


def normalize_canonical_review_scoping(
    data: dict[str, object], *, raw_text: str | None = None
) -> dict[str, object]:
    """Assign fields to visits based on evidence anchoring and raw-text analysis."""
    raw_fields = data.get("fields")
    if not isinstance(raw_fields, list):
        return data

    projected = dict(data)
    rtx = _prepare_raw_text_context(raw_text)

    (
        fields_to_keep,
        visit_scoped_fields,
        visit_group_metadata,
        detected_visit_dates,
        seen_detected_visit_dates,
    ) = _classify_fields_into_scopes(
        raw_fields,
        raw_text_detected_visit_dates=rtx.detected_visit_dates,
    )

    if not visit_scoped_fields and not visit_group_metadata and not rtx.detected_visit_dates:
        return projected

    roster = _build_visit_roster(
        projected,
        detected_visit_dates=detected_visit_dates,
        seen_detected_visit_dates=seen_detected_visit_dates,
        raw_text_detected_visit_dates=rtx.detected_visit_dates,
    )

    unassigned_visit = _assign_fields_to_visits(
        visit_scoped_fields=visit_scoped_fields,
        raw_text=raw_text,
        roster=roster,
        raw_text_offsets_by_date=rtx.offsets_by_date,
        visit_boundary_offsets=rtx.boundary_offsets,
    )

    visit_segments_by_id = build_visit_segment_text_by_visit_id(
        raw_text=raw_text,
        visit_occurrences_by_date=roster.visit_occurrences_by_date,
        raw_text_date_occurrences=rtx.date_occurrences,
        visit_boundary_offsets=rtx.boundary_offsets,
    )
    populate_missing_reason_for_visit_from_segments(
        assigned_visits=roster.assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
    )
    populate_visit_scoped_fields_from_segment_candidates(
        assigned_visits=roster.assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
        candidate_keys=("diagnosis", "symptoms", "medication", "procedure", "weight"),
    )
    populate_visit_observations_actions_from_segments(
        assigned_visits=roster.assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
    )

    _distribute_visit_group_metadata(
        visit_group_metadata=visit_group_metadata,
        visit_by_date=roster.visit_by_date,
        unassigned_visit=unassigned_visit,
    )

    fields_to_keep = postprocess_weights(
        fields_to_keep=fields_to_keep,
        assigned_visits=roster.assigned_visits,
        unassigned_visit=unassigned_visit,
        raw_text=raw_text,
    )

    projected["fields"] = fields_to_keep
    projected["visits"] = _finalize_visit_list(
        assigned_visits=roster.assigned_visits,
        unassigned_visit=unassigned_visit,
    )
    return projected
