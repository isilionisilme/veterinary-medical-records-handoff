"""Global Schema constants and normalization helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

_SCHEMA_CONTRACT_PATH = (
    Path(__file__).resolve().parents[3] / "shared" / "global_schema_contract.json"
)


def _load_schema_contract() -> dict[str, object]:
    try:
        raw_text = _SCHEMA_CONTRACT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Global Schema contract file not found: {_SCHEMA_CONTRACT_PATH}"
        ) from exc

    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Global Schema contract JSON is invalid: {_SCHEMA_CONTRACT_PATH}"
        ) from exc

    if not isinstance(raw, dict):
        raise RuntimeError("Global Schema contract must be a JSON object")

    fields = raw.get("fields")
    if not isinstance(fields, list) or not fields:
        raise RuntimeError("Global Schema contract must define a non-empty fields list")

    required_keys = {
        "key",
        "label",
        "section",
        "value_type",
        "repeatable",
        "critical",
        "optional",
    }
    seen_keys: set[str] = set()
    for index, field in enumerate(fields):
        if not isinstance(field, dict):
            raise RuntimeError(f"Global Schema field at index {index} must be an object")

        missing_keys = sorted(required_keys.difference(field.keys()))
        if missing_keys:
            missing_keys_text = ", ".join(missing_keys)
            raise RuntimeError(
                f"Global Schema field at index {index} is missing keys: {missing_keys_text}"
            )

        field_key = str(field.get("key", "")).strip()
        if not field_key:
            raise RuntimeError(f"Global Schema field at index {index} must define a non-empty key")
        if field_key in seen_keys:
            raise RuntimeError(f"Global Schema contains duplicate key: {field_key}")
        seen_keys.add(field_key)

        value_type = field.get("value_type")
        if not isinstance(value_type, str) or not value_type.strip():
            raise RuntimeError(
                f"Global Schema field '{field_key}' must define a non-empty string value_type"
            )

        for flag in ("repeatable", "critical", "optional"):
            if not isinstance(field.get(flag), bool):
                raise RuntimeError(
                    f"Global Schema field '{field_key}' must define boolean flag '{flag}'"
                )

    return raw


def _validate_contract_metadata(raw_contract: Mapping[str, object]) -> tuple[str, str] | None:
    contract_name = raw_contract.get("contract_name")
    contract_revision = raw_contract.get("contract_revision")
    if contract_name is None and contract_revision is None:
        return None
    if not isinstance(contract_name, str) or not contract_name.strip():
        raise RuntimeError(
            "Global Schema contract metadata 'contract_name' must be a non-empty string"
        )
    if not isinstance(contract_revision, str) or not contract_revision.strip():
        raise RuntimeError(
            "Global Schema contract metadata 'contract_revision' must be a non-empty string"
        )
    return (contract_name.strip(), contract_revision.strip())


_SCHEMA_CONTRACT = _load_schema_contract()
_CONTRACT_METADATA = _validate_contract_metadata(_SCHEMA_CONTRACT)
_FIELD_DEFINITIONS = list(_SCHEMA_CONTRACT["fields"])

CONTRACT_NAME: str | None = _CONTRACT_METADATA[0] if _CONTRACT_METADATA is not None else None
CONTRACT_REVISION: str | None = _CONTRACT_METADATA[1] if _CONTRACT_METADATA is not None else None

GLOBAL_SCHEMA_KEYS: tuple[str, ...] = tuple(
    str(field["key"]).strip() for field in _FIELD_DEFINITIONS
)

REPEATABLE_KEYS: frozenset[str] = frozenset(
    str(field["key"]).strip() for field in _FIELD_DEFINITIONS if bool(field.get("repeatable"))
)

CRITICAL_KEYS: frozenset[str] = frozenset(
    str(field["key"]).strip() for field in _FIELD_DEFINITIONS if bool(field.get("critical"))
)

VALUE_TYPE_BY_KEY: dict[str, str] = {
    str(field["key"]).strip(): str(field.get("value_type", "string"))
    for field in _FIELD_DEFINITIONS
}


def empty_global_schema_payload() -> dict[str, object]:
    """Return a full schema-shaped payload with empty values."""

    payload: dict[str, object] = {}
    for key in GLOBAL_SCHEMA_KEYS:
        payload[key] = [] if key in REPEATABLE_KEYS else None
    return payload


def normalize_global_schema(payload: Mapping[str, object] | None) -> dict[str, object]:
    """Normalize arbitrary payload into a full Global Schema shape."""

    normalized = empty_global_schema_payload()
    if payload is None:
        return normalized

    for key in GLOBAL_SCHEMA_KEYS:
        raw_value = payload.get(key)
        if key in REPEATABLE_KEYS:
            if isinstance(raw_value, list):
                normalized[key] = [str(item).strip() for item in raw_value if str(item).strip()]
            elif raw_value is None:
                normalized[key] = []
            else:
                text = str(raw_value).strip()
                normalized[key] = [text] if text else []
            continue

        if raw_value is None:
            normalized[key] = None
            continue

        text_value = str(raw_value).strip()
        normalized[key] = text_value if text_value else None

    visit_date = normalized.get("visit_date")
    if normalized.get("document_date") is None and isinstance(visit_date, str) and visit_date:
        normalized["document_date"] = visit_date

    return normalized


def validate_global_schema_shape(payload: Mapping[str, object]) -> list[str]:
    """Return human-readable validation errors for schema payload shape."""

    errors: list[str] = []
    missing_keys = [key for key in GLOBAL_SCHEMA_KEYS if key not in payload]
    if missing_keys:
        errors.append(f"Missing keys: {', '.join(missing_keys)}")

    for key in REPEATABLE_KEYS:
        value = payload.get(key)
        if not isinstance(value, list):
            errors.append(f"Repeatable key '{key}' must be a list")

    return errors
