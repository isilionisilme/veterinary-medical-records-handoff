from __future__ import annotations

import math
from typing import Any
from uuid import uuid4

from backend.app.application.documents._shared import NUMERIC_TYPES
from backend.app.application.global_schema import REPEATABLE_KEYS, normalize_global_schema


def _normalize_string_for_noop(value: str) -> str:
    return " ".join(value.split())


def _normalize_value_for_noop(*, value: object, value_type: str) -> object:
    normalized_type = value_type.strip().lower()
    if normalized_type in {"string", "text", "date"}:
        if isinstance(value, str):
            return _normalize_string_for_noop(value)
        return value

    if normalized_type in {"integer", "int", "number", "float", "decimal"}:
        if isinstance(value, bool):
            return value
        if isinstance(value, NUMERIC_TYPES):
            numeric = float(value)
            if math.isfinite(numeric):
                return numeric
            return value
        if isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                return candidate
            try:
                numeric = float(candidate)
            except ValueError:
                return candidate
            if math.isfinite(numeric):
                return numeric
            return candidate
        return value

    if normalized_type in {"boolean", "bool"}:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            candidate = value.strip().lower()
            if candidate in {"true", "1"}:
                return True
            if candidate in {"false", "0"}:
                return False
            return candidate
        return value

    if isinstance(value, str):
        return value.strip()
    return value


def _is_noop_update(
    *,
    old_value: object,
    new_value: object,
    existing_value_type: str | None,
    incoming_value_type: str,
) -> bool:
    if existing_value_type is None:
        return False
    if existing_value_type != incoming_value_type:
        return False
    return _normalize_value_for_noop(value=old_value, value_type=incoming_value_type) == (
        _normalize_value_for_noop(value=new_value, value_type=incoming_value_type)
    )


def _sanitize_text_extraction_reliability(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        numeric = float(value)
        if math.isfinite(numeric) and 0.0 <= numeric <= 1.0:
            return numeric
    return None


def _sanitize_field_review_history_adjustment(value: object) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, int | float):
        numeric = float(value)
        if math.isfinite(numeric):
            return numeric
    return 0.0


def _sanitize_field_candidate_confidence(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, NUMERIC_TYPES):
        numeric = float(value)
        if math.isfinite(numeric):
            return min(max(numeric, 0.0), 1.0)
    return None


def _sanitize_field_mapping_confidence(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, NUMERIC_TYPES):
        numeric = float(value)
        if math.isfinite(numeric):
            return min(max(numeric, 0.0), 1.0)
    return None


def _compose_field_mapping_confidence(
    *, candidate_confidence: float, review_history_adjustment: float
) -> float:
    composed = candidate_confidence + (review_history_adjustment / 100.0)
    return min(max(composed, 0.0), 1.0)


def _resolve_human_edit_candidate_confidence(
    field: dict[str, object], *, neutral_candidate_confidence: float
) -> float:
    candidate_confidence = _sanitize_field_candidate_confidence(
        field.get("field_candidate_confidence")
    )
    if candidate_confidence is not None:
        return candidate_confidence

    mapping_confidence = _sanitize_field_mapping_confidence(field.get("field_mapping_confidence"))
    if mapping_confidence is not None:
        return mapping_confidence

    return neutral_candidate_confidence


def _sanitize_confidence_breakdown(field: dict[str, object]) -> dict[str, object]:
    sanitized = dict(field)
    sanitized.pop("confidence", None)
    sanitized["text_extraction_reliability"] = _sanitize_text_extraction_reliability(
        sanitized.get("text_extraction_reliability")
    )
    sanitized["field_review_history_adjustment"] = _sanitize_field_review_history_adjustment(
        sanitized.get("field_review_history_adjustment")
    )
    candidate_confidence = _sanitize_field_candidate_confidence(
        sanitized.get("field_candidate_confidence")
    )
    if candidate_confidence is None:
        mapping_confidence = _sanitize_field_mapping_confidence(
            sanitized.get("field_mapping_confidence")
        )
        candidate_confidence = mapping_confidence if mapping_confidence is not None else 0.0
    sanitized["field_candidate_confidence"] = candidate_confidence
    sanitized["field_mapping_confidence"] = _compose_field_mapping_confidence(
        candidate_confidence=candidate_confidence,
        review_history_adjustment=sanitized["field_review_history_adjustment"],
    )
    return sanitized


def _build_field_change_log(
    *,
    document_id: str,
    run_id: str,
    interpretation_id: str,
    base_version_number: int,
    new_version_number: int,
    field_id: str,
    field_key: str | None,
    value_type: str | None,
    old_value: object,
    new_value: object,
    change_type: str,
    created_at: str,
    occurred_at: str,
    context_key: str,
    mapping_id: str | None,
    policy_version: str,
) -> dict[str, object]:
    return {
        "event_type": "field_corrected",
        "source": "reviewer_edit",
        "document_id": document_id,
        "run_id": run_id,
        "change_id": str(uuid4()),
        "interpretation_id": interpretation_id,
        "base_version_number": base_version_number,
        "new_version_number": new_version_number,
        "field_id": field_id,
        "field_key": field_key,
        "field_path": f"fields.{field_id}.value",
        "value_type": value_type,
        "old_value": old_value,
        "new_value": new_value,
        "change_type": change_type,
        "created_at": created_at,
        "occurred_at": occurred_at,
        "context_key": context_key,
        "mapping_id": mapping_id,
        "policy_version": policy_version,
    }


def _build_global_schema_from_fields(fields: list[dict[str, object]]) -> dict[str, object]:
    schema_accumulator: dict[str, object] = {}
    for field in fields:
        key = str(field.get("key", "")).strip()
        if not key:
            continue
        value = field.get("value")
        if key in REPEATABLE_KEYS:
            if is_field_value_empty(value):
                continue
            bucket = schema_accumulator.get(key)
            if not isinstance(bucket, list):
                bucket = []
                schema_accumulator[key] = bucket
            bucket.append(value)
            continue

        if key not in schema_accumulator and not is_field_value_empty(value):
            schema_accumulator[key] = value

    return normalize_global_schema(schema_accumulator)


def is_field_value_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False
