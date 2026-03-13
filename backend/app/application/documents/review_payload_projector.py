"""Canonical review payload projection."""

from __future__ import annotations

from backend.app.application.documents._shared import (
    _MEDICAL_RECORD_CANONICAL_FIELD_SLOTS,
    _MEDICAL_RECORD_CANONICAL_SECTIONS,
    _REVIEW_SCHEMA_CONTRACT_CANONICAL,
)
from backend.app.application.documents.age_normalizer import _normalize_age_from_review_projection
from backend.app.application.documents.edit_service import _sanitize_confidence_breakdown
from backend.app.application.documents.visit_scoping import normalize_canonical_review_scoping
from backend.app.application.field_normalizers import normalize_microchip_digits_only


def _normalize_review_interpretation_data(
    data: dict[str, object], *, raw_text: str | None = None
) -> dict[str, object]:
    normalized_data = dict(data)
    changed = False

    raw_fields = normalized_data.get("fields")
    if isinstance(raw_fields, list):
        normalized_fields: list[object] = []
        for item in raw_fields:
            if not isinstance(item, dict):
                normalized_fields.append(item)
                continue
            normalized_field = _sanitize_confidence_breakdown(item)
            normalized_fields.append(normalized_field)
            if normalized_field != item:
                changed = True
        if changed:
            normalized_data["fields"] = normalized_fields

    global_schema = normalized_data.get("global_schema")
    if not isinstance(global_schema, dict):
        base_data = normalized_data if changed else data
        projected = _project_review_payload_to_canonical(dict(base_data), raw_text=raw_text)
        return _normalize_age_from_review_projection(projected)

    raw_microchip = global_schema.get("microchip_id")
    normalized_microchip = normalize_microchip_digits_only(raw_microchip)
    if normalized_microchip == raw_microchip:
        fields_changed = _upsert_microchip_field_from_global_schema(
            normalized_data=normalized_data,
            normalized_microchip=normalized_microchip,
        )
        changed = changed or fields_changed
        base_data = normalized_data if changed else data
        projected = _project_review_payload_to_canonical(dict(base_data), raw_text=raw_text)
        return _normalize_age_from_review_projection(projected)

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
        projected = _project_review_payload_to_canonical(normalized_data, raw_text=raw_text)
    else:
        projected = _project_review_payload_to_canonical(dict(data), raw_text=raw_text)

    return _normalize_age_from_review_projection(projected)


def _has_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _project_review_payload_to_canonical(
    data: dict[str, object], *, raw_text: str | None = None
) -> dict[str, object]:
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

    return normalize_canonical_review_scoping(projected, raw_text=raw_text)


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
