"""Snapshot builders and shared snapshot parsing helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from backend.app.application.global_schema import GLOBAL_SCHEMA_KEYS, REPEATABLE_KEYS

SNAPSHOT_SCHEMA_VERSION_CANONICAL = "canonical"
SNAPSHOT_CONFIDENCE_MID_MIN = 0.6
SNAPSHOT_CONFIDENCE_HIGH_MIN = 0.8


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric < 0:
        return 0.0
    if numeric > 1:
        return 1.0
    return numeric


def _confidence_to_band(confidence: float | None) -> str | None:
    if confidence is None:
        return None
    if confidence >= SNAPSHOT_CONFIDENCE_HIGH_MIN:
        return "high"
    if confidence >= SNAPSHOT_CONFIDENCE_MID_MIN:
        return "mid"
    return "low"


def _source_hint_from_evidence(raw_field: dict[str, Any]) -> str | None:
    evidence = raw_field.get("evidence") if isinstance(raw_field, dict) else None
    if not isinstance(evidence, dict):
        return None
    parts: list[str] = []
    page = evidence.get("page")
    if isinstance(page, int):
        parts.append(f"page:{page}")
    snippet = _as_text(evidence.get("snippet"))
    if snippet:
        parts.append(f"snippet:{snippet}")
    return " | ".join(parts) if parts else None


def _collect_top_candidates(raw_fields: list[Any]) -> dict[str, list[dict[str, Any]]]:
    top_candidates_by_field: dict[str, list[dict[str, Any]]] = defaultdict(list)
    dedup_values_by_field: dict[str, set[str]] = defaultdict(set)
    for raw_field in raw_fields:
        if not isinstance(raw_field, dict):
            continue
        field_key = _as_text(raw_field.get("key"))
        if not field_key or field_key not in GLOBAL_SCHEMA_KEYS:
            continue
        candidate_value = _as_text(raw_field.get("value"))
        if not candidate_value:
            continue
        candidate_key = candidate_value.casefold()
        if candidate_key in dedup_values_by_field[field_key]:
            continue
        dedup_values_by_field[field_key].add(candidate_key)
        top_candidates_by_field[field_key].append(
            {
                "value": candidate_value,
                "confidence": _coerce_confidence(raw_field.get("confidence")),
                "sourceHint": _source_hint_from_evidence(raw_field),
            }
        )

    for field_key, candidates in top_candidates_by_field.items():
        candidates.sort(key=lambda item: float(item.get("confidence") or 0.0), reverse=True)
        top_candidates_by_field[field_key] = candidates[:3]

    return dict(top_candidates_by_field)


def _build_snapshot_fields(
    global_schema: dict[str, Any],
    top_candidates_by_field: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    fields: dict[str, dict[str, Any]] = {}
    for field_key in GLOBAL_SCHEMA_KEYS:
        top_candidates = top_candidates_by_field.get(field_key, [])
        top1 = top_candidates[0] if top_candidates else None
        raw_value = global_schema.get(field_key)
        if field_key in REPEATABLE_KEYS:
            normalized_value = (
                next((str(item).strip() for item in raw_value if str(item).strip()), None)
                if isinstance(raw_value, list)
                else None
            )
        else:
            normalized_value = _as_text(raw_value)

        if normalized_value:
            confidence = (
                _coerce_confidence(top1.get("confidence")) if isinstance(top1, dict) else None
            )
            fields[field_key] = {
                "status": "accepted",
                "confidence": _confidence_to_band(confidence),
                "valueNormalized": normalized_value,
                "valueRaw": _as_text(top1.get("value"))
                if isinstance(top1, dict)
                else normalized_value,
                "rawCandidate": _as_text(top1.get("value")) if isinstance(top1, dict) else None,
                "sourceHint": _as_text(top1.get("sourceHint")) if isinstance(top1, dict) else None,
                "topCandidates": top_candidates,
            }
            continue

        fields[field_key] = {
            "status": "missing",
            "confidence": None,
            "topCandidates": top_candidates,
        }

    return fields


def build_extraction_snapshot_from_interpretation(
    *,
    document_id: str,
    run_id: str,
    created_at: str,
    interpretation_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not document_id.strip() or not run_id.strip() or not created_at.strip():
        return None
    data = interpretation_payload.get("data") if isinstance(interpretation_payload, dict) else None
    if not isinstance(data, dict):
        return None

    global_schema_raw = data.get("global_schema")
    global_schema = global_schema_raw if isinstance(global_schema_raw, dict) else {}
    raw_fields = data.get("fields") if isinstance(data.get("fields"), list) else []

    top_candidates_by_field = _collect_top_candidates(raw_fields)
    fields = _build_snapshot_fields(global_schema, top_candidates_by_field)

    field_values = list(fields.values())
    return {
        "runId": run_id,
        "documentId": document_id,
        "createdAt": created_at,
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION_CANONICAL,
        "fields": fields,
        "counts": {
            "totalFields": len(GLOBAL_SCHEMA_KEYS),
            "accepted": sum(1 for item in field_values if item.get("status") == "accepted"),
            "rejected": sum(1 for item in field_values if item.get("status") == "rejected"),
            "missing": sum(1 for item in field_values if item.get("status") == "missing"),
            "low": sum(1 for item in field_values if item.get("confidence") == "low"),
            "mid": sum(1 for item in field_values if item.get("confidence") == "mid"),
            "high": sum(1 for item in field_values if item.get("confidence") == "high"),
        },
    }


def _extract_top_candidates(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_candidates = raw_payload.get("topCandidates")
    candidates: list[dict[str, Any]] = []
    if isinstance(raw_candidates, list):
        for item in raw_candidates[:3]:
            if not isinstance(item, dict):
                continue
            value = _as_text(item.get("value"))
            if not value:
                continue
            candidates.append(
                {
                    "value": value,
                    "confidence": _coerce_confidence(item.get("confidence")),
                    "sourceHint": _as_text(item.get("sourceHint")),
                }
            )
    if candidates:
        return candidates
    fallback_value = (
        _as_text(raw_payload.get("rawCandidate"))
        or _as_text(raw_payload.get("valueRaw"))
        or _as_text(raw_payload.get("valueNormalized"))
    )
    return (
        [{"value": fallback_value, "confidence": None, "sourceHint": None}]
        if fallback_value
        else []
    )


def _preview(value: str | None, *, limit: int = 80) -> str | None:
    if not value:
        return None
    return value if len(value) <= limit else f"{value[: limit - 1].rstrip()}…"


def _format_top_candidate_for_log(item: dict[str, Any] | None) -> str:
    if not isinstance(item, dict):
        return "top1=<none>"
    value = _preview(_as_text(item.get("value")))
    if not value:
        return "top1=<none>"
    confidence = _coerce_confidence(item.get("confidence"))
    return (
        f"top1={value!r} (conf={confidence:.2f})"
        if confidence is not None
        else f"top1={value!r} (conf=n/a)"
    )


def _truncate_text(value: str | None, *, limit: int = 80) -> str | None:
    if value is None:
        return None
    compact = value.strip()
    if not compact:
        return None
    return compact if len(compact) <= limit else f"{compact[: limit - 1].rstrip()}…"
