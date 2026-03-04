from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from backend.app.application.documents._shared import (
    _MEDICAL_RECORD_CANONICAL_FIELD_SLOTS,
    _MEDICAL_RECORD_CANONICAL_SECTIONS,
    _REVIEW_SCHEMA_CONTRACT_CANONICAL,
    _VISIT_GROUP_METADATA_KEY_SET,
    _VISIT_GROUP_METADATA_KEYS,
    _VISIT_SCOPED_KEY_SET,
    _contains_any_date_token,
    _extract_evidence_snippet,
    _extract_visit_date_candidates_from_text,
    _normalize_visit_date_candidate,
)
from backend.app.application.documents.calibration import (
    _apply_reviewed_document_calibration,
    _revert_reviewed_document_calibration,
)
from backend.app.application.documents.upload_service import _default_now_iso
from backend.app.application.field_normalizers import normalize_microchip_digits_only
from backend.app.domain.models import ReviewStatus
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage


@dataclass(frozen=True, slots=True)
class LatestCompletedRunReview:
    run_id: str
    state: str
    completed_at: str | None
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class ActiveInterpretationReview:
    interpretation_id: str
    version_number: int
    data: dict[str, object]


@dataclass(frozen=True, slots=True)
class RawTextArtifactAvailability:
    run_id: str
    available: bool


@dataclass(frozen=True, slots=True)
class DocumentReview:
    document_id: str
    latest_completed_run: LatestCompletedRunReview
    active_interpretation: ActiveInterpretationReview
    raw_text_artifact: RawTextArtifactAvailability
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


@dataclass(frozen=True, slots=True)
class DocumentReviewLookupResult:
    review: DocumentReview | None
    unavailable_reason: str | None


def get_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    storage: FileStorage,
) -> DocumentReviewLookupResult | None:
    document = repository.get(document_id)
    if document is None:
        return None

    latest_completed_run = repository.get_latest_completed_run(document_id)
    if latest_completed_run is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="NO_COMPLETED_RUN",
        )

    interpretation_payload = repository.get_latest_artifact_payload(
        run_id=latest_completed_run.run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if interpretation_payload is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="INTERPRETATION_MISSING",
        )

    interpretation_id = str(interpretation_payload.get("interpretation_id", ""))
    version_number_raw = interpretation_payload.get("version_number", 1)
    version_number = version_number_raw if isinstance(version_number_raw, int) else 1

    structured_data = interpretation_payload.get("data")
    if not isinstance(structured_data, dict):
        structured_data = {}
    structured_data = _normalize_review_interpretation_data(structured_data)

    return DocumentReviewLookupResult(
        review=DocumentReview(
            document_id=document_id,
            latest_completed_run=LatestCompletedRunReview(
                run_id=latest_completed_run.run_id,
                state=latest_completed_run.state.value,
                completed_at=latest_completed_run.completed_at,
                failure_type=latest_completed_run.failure_type,
            ),
            active_interpretation=ActiveInterpretationReview(
                interpretation_id=interpretation_id,
                version_number=version_number,
                data=structured_data,
            ),
            raw_text_artifact=RawTextArtifactAvailability(
                run_id=latest_completed_run.run_id,
                available=storage.exists_raw_text(
                    document_id=latest_completed_run.document_id,
                    run_id=latest_completed_run.run_id,
                ),
            ),
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        ),
        unavailable_reason=None,
    )


def _normalize_review_interpretation_data(data: dict[str, object]) -> dict[str, object]:
    normalized_data = dict(data)
    changed = False

    raw_fields = normalized_data.get("fields")
    if isinstance(raw_fields, list):
        normalized_fields: list[object] = []
        for item in raw_fields:
            if not isinstance(item, dict):
                normalized_fields.append(item)
                continue
            from backend.app.application.documents.edit_service import (
                _sanitize_confidence_breakdown,
            )

            normalized_field = _sanitize_confidence_breakdown(item)
            normalized_fields.append(normalized_field)
            if normalized_field != item:
                changed = True
        if changed:
            normalized_data["fields"] = normalized_fields

    global_schema = normalized_data.get("global_schema")
    if not isinstance(global_schema, dict):
        base_data = normalized_data if changed else data
        return _project_review_payload_to_canonical(dict(base_data))

    raw_microchip = global_schema.get("microchip_id")
    normalized_microchip = normalize_microchip_digits_only(raw_microchip)
    if normalized_microchip == raw_microchip:
        base_data = normalized_data if changed else data
        return _project_review_payload_to_canonical(dict(base_data))

    normalized_global_schema = dict(global_schema)
    normalized_global_schema["microchip_id"] = normalized_microchip
    normalized_data["global_schema"] = normalized_global_schema
    changed = True

    fields_changed = _upsert_microchip_field_from_global_schema(
        normalized_data=normalized_data,
        normalized_microchip=normalized_microchip,
    )
    changed = changed or fields_changed

    if changed:
        return _project_review_payload_to_canonical(normalized_data)

    return _project_review_payload_to_canonical(dict(data))


def _upsert_microchip_field_from_global_schema(
    *,
    normalized_data: dict[str, object],
    normalized_microchip: str | None,
) -> bool:
    if not normalized_microchip:
        return False

    raw_fields = normalized_data.get("fields")
    fields: list[object]
    if isinstance(raw_fields, list):
        fields = list(raw_fields)
    else:
        fields = []

    microchip_field_index: int | None = None
    for index, item in enumerate(fields):
        if isinstance(item, dict) and item.get("key") == "microchip_id":
            microchip_field_index = index
            break

    if microchip_field_index is None:
        fields.append(
            {
                "field_id": "backfill-microchip-id",
                "key": "microchip_id",
                "value": normalized_microchip,
                "value_type": "string",
                "scope": "document",
                "section": "patient",
                "classification": "medical_record",
                "domain": "clinical",
                "is_critical": True,
                "origin": "machine",
                "evidence": {"page": 1, "snippet": normalized_microchip},
            }
        )
        normalized_data["fields"] = fields
        return True

    existing_field = fields[microchip_field_index]
    if not isinstance(existing_field, dict):
        return False

    existing_value = existing_field.get("value")
    existing_compact = str(existing_value).strip() if isinstance(existing_value, str) else ""
    if existing_compact == normalized_microchip:
        return False

    patched_field = dict(existing_field)
    patched_field["value"] = normalized_microchip
    patched_field["value_type"] = "string"
    patched_field.setdefault("scope", "document")
    patched_field.setdefault("section", "patient")
    patched_field.setdefault("classification", "medical_record")
    patched_field.setdefault("domain", "clinical")
    patched_field.setdefault("is_critical", True)
    patched_field.setdefault("origin", "machine")
    patched_field.setdefault("evidence", {"page": 1, "snippet": normalized_microchip})
    fields[microchip_field_index] = patched_field
    normalized_data["fields"] = fields
    return True


def _project_review_payload_to_canonical(data: dict[str, object]) -> dict[str, object]:
    medical_record_view = data.get("medical_record_view")
    projected = dict(data)

    default_medical_record_view = {
        "version": "mvp-1",
        "sections": list(_MEDICAL_RECORD_CANONICAL_SECTIONS),
        "field_slots": [dict(slot) for slot in _MEDICAL_RECORD_CANONICAL_FIELD_SLOTS],
    }
    if not isinstance(medical_record_view, dict):
        projected["medical_record_view"] = default_medical_record_view
    else:
        normalized_medical_record_view = dict(medical_record_view)
        if not isinstance(normalized_medical_record_view.get("version"), str):
            normalized_medical_record_view["version"] = default_medical_record_view["version"]
        if not isinstance(normalized_medical_record_view.get("sections"), list):
            normalized_medical_record_view["sections"] = default_medical_record_view["sections"]
        if not isinstance(normalized_medical_record_view.get("field_slots"), list):
            normalized_medical_record_view["field_slots"] = default_medical_record_view[
                "field_slots"
            ]
        projected["medical_record_view"] = normalized_medical_record_view

    projected["schema_contract"] = _REVIEW_SCHEMA_CONTRACT_CANONICAL
    projected.pop("schema_version", None)

    if not isinstance(projected.get("visits"), list):
        projected["visits"] = []
    if not isinstance(projected.get("other_fields"), list):
        projected["other_fields"] = []

    return _normalize_canonical_review_scoping(projected)


def _normalize_canonical_review_scoping(data: dict[str, object]) -> dict[str, object]:
    raw_fields = data.get("fields")
    if not isinstance(raw_fields, list):
        return data

    projected = dict(data)
    fields_to_keep: list[object] = []
    visit_scoped_fields: list[dict[str, object]] = []
    visit_group_metadata: dict[str, list[object]] = {}
    detected_visit_dates: list[str] = []
    seen_detected_visit_dates: set[str] = set()

    for item in raw_fields:
        if not isinstance(item, dict):
            fields_to_keep.append(item)
            continue

        key_raw = item.get("key")
        key = key_raw if isinstance(key_raw, str) else ""
        if key in _VISIT_GROUP_METADATA_KEY_SET:
            values = visit_group_metadata.setdefault(key, [])
            values.append(item.get("value"))
            if key == "visit_date":
                normalized_visit_date = _normalize_visit_date_candidate(item.get("value"))
                if (
                    normalized_visit_date is not None
                    and normalized_visit_date not in seen_detected_visit_dates
                ):
                    seen_detected_visit_dates.add(normalized_visit_date)
                    detected_visit_dates.append(normalized_visit_date)
            continue

        if key in _VISIT_SCOPED_KEY_SET:
            visit_field = dict(item)
            visit_field["scope"] = "visit"
            visit_field["section"] = "visits"
            visit_scoped_fields.append(visit_field)
            evidence_snippet = _extract_evidence_snippet(visit_field)
            for normalized_visit_date in _extract_visit_date_candidates_from_text(
                text=evidence_snippet
            ):
                if normalized_visit_date in seen_detected_visit_dates:
                    continue
                seen_detected_visit_dates.add(normalized_visit_date)
                detected_visit_dates.append(normalized_visit_date)
            continue

        fields_to_keep.append(item)

    if not visit_scoped_fields and not visit_group_metadata:
        return projected

    raw_visits = projected.get("visits")
    visits: list[dict[str, object]] = []
    if isinstance(raw_visits, list):
        for visit in raw_visits:
            if isinstance(visit, dict):
                visits.append(dict(visit))

    unassigned_visit: dict[str, object] | None = None
    assigned_visits: list[dict[str, object]] = []
    visit_by_date: dict[str, dict[str, object]] = {}
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
            if normalized_visit_date not in seen_detected_visit_dates:
                seen_detected_visit_dates.add(normalized_visit_date)
                detected_visit_dates.append(normalized_visit_date)

        assigned_visits.append(visit)

    for index, visit_date in enumerate(detected_visit_dates, start=1):
        if visit_date in visit_by_date:
            continue
        generated_visit = {
            "visit_id": f"visit-{index:03d}",
            "visit_date": visit_date,
            "admission_date": None,
            "discharge_date": None,
            "reason_for_visit": None,
            "fields": [],
        }
        assigned_visits.append(generated_visit)
        visit_by_date[visit_date] = generated_visit

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

    for visit_field in visit_scoped_fields:
        evidence_snippet = _extract_evidence_snippet(visit_field)
        evidence_visit_dates = _extract_visit_date_candidates_from_text(text=evidence_snippet)
        target_visit: dict[str, object] | None = None
        for candidate_visit_date in evidence_visit_dates:
            target_visit = visit_by_date.get(candidate_visit_date)
            if target_visit is not None:
                break
        has_ambiguous_date_token = _contains_any_date_token(text=evidence_snippet)
        if target_visit is None and len(visit_by_date) == 1 and not has_ambiguous_date_token:
            target_visit = next(iter(visit_by_date.values()))

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

    assigned_visits.sort(
        key=lambda visit: (
            str(visit.get("visit_date") or "9999-12-31"),
            str(visit.get("visit_id") or ""),
        )
    )

    normalized_visits: list[dict[str, object]] = list(assigned_visits)
    if unassigned_visit is not None:
        normalized_visits.append(unassigned_visit)

    projected["fields"] = fields_to_keep
    projected["visits"] = normalized_visits
    return projected


@dataclass(frozen=True, slots=True)
class ReviewToggleResult:
    document_id: str
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


def mark_document_reviewed(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
    reviewed_by: str | None = None,
) -> ReviewToggleResult | None:
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.REVIEWED:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reviewed_at = now_provider()
    latest_completed_run = repository.get_latest_completed_run(document_id)
    reviewed_run_id = latest_completed_run.run_id if latest_completed_run is not None else None
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.REVIEWED.value,
        updated_at=reviewed_at,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        reviewed_run_id=reviewed_run_id,
    )
    if updated is None:
        return None

    _apply_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=reviewed_run_id,
        repository=repository,
        created_at=reviewed_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )


def reopen_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
) -> ReviewToggleResult | None:
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.IN_REVIEW:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reopened_at = now_provider()
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.IN_REVIEW.value,
        updated_at=reopened_at,
        reviewed_at=None,
        reviewed_by=None,
        reviewed_run_id=None,
    )
    if updated is None:
        return None

    _revert_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=document.reviewed_run_id,
        repository=repository,
        created_at=reopened_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )
