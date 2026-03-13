"""Visit population: populating visit records with data from text segments.

Extracted from review_service.py (ARCH-01) to isolate segment-to-visit
field population logic.
"""

from __future__ import annotations

from backend.app.application.documents.segment_parser import (
    extract_reason_for_visit_from_segment,
    split_segment_into_observations_actions,
)
from backend.app.application.processing.candidate_mining import (
    _mine_interpretation_candidates,
)


def _append_visit_segment_summary_field(
    *,
    visit_fields: list[object],
    visit_id: str,
    key: str,
    value: str,
) -> None:
    visit_fields.append(
        {
            "field_id": f"derived-{key}-{visit_id}",
            "key": key,
            "value": value,
            "value_type": "string",
            "scope": "visit",
            "section": "visits",
            "classification": "medical_record",
            "origin": "derived",
            "evidence": {"snippet": value},
        }
    )


def populate_visit_observations_actions_from_segments(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
) -> None:
    for visit in assigned_visits:
        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        visit_fields = visit.get("fields")
        if not isinstance(visit_fields, list):
            visit_fields = []
            visit["fields"] = visit_fields

        existing_keys = {
            field.get("key")
            for field in visit_fields
            if isinstance(field, dict) and isinstance(field.get("key"), str)
        }

        observation_value, action_value = split_segment_into_observations_actions(
            segment_text=segment_text
        )
        if "observations" not in existing_keys and isinstance(observation_value, str):
            _append_visit_segment_summary_field(
                visit_fields=visit_fields,
                visit_id=visit_id,
                key="observations",
                value=observation_value,
            )

        if "actions" not in existing_keys and isinstance(action_value, str):
            _append_visit_segment_summary_field(
                visit_fields=visit_fields,
                visit_id=visit_id,
                key="actions",
                value=action_value,
            )


def populate_missing_reason_for_visit_from_segments(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
) -> None:
    for visit in assigned_visits:
        reason_for_visit = visit.get("reason_for_visit")
        if isinstance(reason_for_visit, str) and reason_for_visit.strip():
            continue
        if reason_for_visit is not None and not isinstance(reason_for_visit, str):
            continue

        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        extracted_reason = extract_reason_for_visit_from_segment(segment_text=segment_text)
        if extracted_reason is not None:
            visit["reason_for_visit"] = extracted_reason


def populate_visit_scoped_fields_from_segment_candidates(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
    candidate_keys: tuple[str, ...],
) -> None:
    for visit in assigned_visits:
        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        visit_fields = visit.get("fields")
        if not isinstance(visit_fields, list):
            visit_fields = []
            visit["fields"] = visit_fields

        existing_keys = {
            field.get("key")
            for field in visit_fields
            if isinstance(field, dict) and isinstance(field.get("key"), str)
        }

        mined_candidates = _mine_interpretation_candidates(segment_text)
        for candidate_key in candidate_keys:
            if candidate_key in existing_keys:
                continue

            key_candidates = mined_candidates.get(candidate_key)
            if not isinstance(key_candidates, list) or not key_candidates:
                continue

            selected_candidate = key_candidates[0]
            if candidate_key == "weight":
                weighted_candidates = [c for c in key_candidates if isinstance(c, dict)]
                if weighted_candidates:
                    selected_candidate = max(
                        weighted_candidates,
                        key=lambda candidate: (
                            float(candidate.get("evidence", {}).get("offset"))
                            if isinstance(candidate.get("evidence"), dict)
                            and isinstance(candidate.get("evidence", {}).get("offset"), int | float)
                            else -1.0
                        ),
                    )

            if not isinstance(selected_candidate, dict):
                continue

            candidate_value = selected_candidate.get("value")
            if not isinstance(candidate_value, str) or not candidate_value.strip():
                continue

            evidence = selected_candidate.get("evidence")
            visit_fields.append(
                {
                    "field_id": f"derived-{candidate_key}-{visit_id}",
                    "key": candidate_key,
                    "value": candidate_value,
                    "value_type": "string",
                    "scope": "visit",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "derived",
                    "evidence": evidence if isinstance(evidence, dict) else None,
                }
            )
            existing_keys.add(candidate_key)


# ---------------------------------------------------------------------------
# Phase helpers for the main scoping orchestrator
# ---------------------------------------------------------------------------
