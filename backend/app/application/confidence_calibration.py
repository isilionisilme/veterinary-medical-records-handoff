"""Deterministic confidence calibration helpers (MVP)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from backend.app.config import confidence_policy_version

CONTEXT_VERSION = "v1"
CONTEXT_KEY_PREFIX = "ctx_v1:"
DEFAULT_DOCUMENT_TYPE = "veterinary_record"
DEFAULT_LANGUAGE = "unknown"
CALIBRATION_MIN_VOLUME = 3
CALIBRATION_MAX_ABS_ADJUSTMENT_PP = 15.0
CALIBRATION_SIGNAL_EDITED = "edited"
CALIBRATION_SIGNAL_ACCEPTED_UNCHANGED = "accepted_unchanged"


def resolve_calibration_policy_version() -> str:
    return confidence_policy_version()


def _normalize_document_type(value: str | None) -> str:
    normalized_document_type = (value or DEFAULT_DOCUMENT_TYPE).strip().lower()
    if not normalized_document_type:
        normalized_document_type = DEFAULT_DOCUMENT_TYPE
    return normalized_document_type


def _normalize_language(value: str | None) -> str:
    normalized_language = (value or DEFAULT_LANGUAGE).strip().lower()
    if not normalized_language:
        normalized_language = DEFAULT_LANGUAGE
    return normalized_language


def _build_context_key_with_payload(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"{CONTEXT_KEY_PREFIX}{digest}"


def build_context_key(*, document_type: str | None, language: str | None) -> str:
    normalized_document_type = _normalize_document_type(document_type)
    normalized_language = _normalize_language(language)

    payload = {
        "context_version": CONTEXT_VERSION,
        "document_type": normalized_document_type,
        "language": normalized_language,
    }
    return _build_context_key_with_payload(payload)


def build_context_key_from_interpretation_data(data: Mapping[str, object]) -> str:
    document_type_raw = data.get("document_type")
    document_type = document_type_raw if isinstance(document_type_raw, str) else None

    language: str | None = None
    global_schema = data.get("global_schema")
    if isinstance(global_schema, Mapping):
        language_raw = global_schema.get("language")
        if isinstance(language_raw, str):
            language = language_raw

    if language is None:
        raw_fields = data.get("fields")
        if isinstance(raw_fields, list):
            for field in raw_fields:
                if not isinstance(field, Mapping):
                    continue
                if field.get("key") != "language":
                    continue
                value = field.get("value")
                if isinstance(value, str):
                    language = value
                    break

    return build_context_key(
        document_type=document_type,
        language=language,
    )


def normalize_mapping_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def is_empty_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False


def compute_review_history_adjustment(
    *,
    accept_count: int,
    edit_count: int,
    min_volume: int = CALIBRATION_MIN_VOLUME,
    max_abs_adjustment_pp: float = CALIBRATION_MAX_ABS_ADJUSTMENT_PP,
) -> float:
    accepts = max(0, int(accept_count))
    edits = max(0, int(edit_count))
    volume = accepts + edits
    if volume < min_volume:
        return 0.0

    posterior = (accepts + 1.0) / (volume + 2.0)
    centered = (posterior - 0.5) * 2.0
    bounded = min(max(centered, -1.0), 1.0)
    adjustment = bounded * max_abs_adjustment_pp
    return round(adjustment, 1)
