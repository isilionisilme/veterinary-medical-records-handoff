"""Field building, confidence scoring, and review history for interpretation artifacts."""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping
from dataclasses import dataclass
from uuid import uuid4

from backend.app.application.confidence_calibration import (
    compute_review_history_adjustment,
    normalize_mapping_id,
)
from backend.app.application.global_schema import (
    CRITICAL_KEYS,
    GLOBAL_SCHEMA_KEYS,
    REPEATABLE_KEYS,
    VALUE_TYPE_BY_KEY,
)
from backend.app.ports.document_repository import DocumentRepository

from .constants import _WHITESPACE_PATTERN, NUMERIC_TYPES

logger = logging.getLogger(__name__)


def _find_line_number_for_snippet(raw_text: str, snippet: str) -> int | None:
    lines = raw_text.splitlines()
    compact_snippet = _WHITESPACE_PATTERN.sub(" ", snippet).strip().casefold()
    if not compact_snippet:
        return None

    for index, line in enumerate(lines, start=1):
        compact_line = _WHITESPACE_PATTERN.sub(" ", line).strip().casefold()
        if not compact_line:
            continue
        if compact_snippet in compact_line or compact_line in compact_snippet:
            return index

    return None


def _build_structured_fields_from_global_schema(
    *,
    normalized_values: Mapping[str, object],
    evidence_map: Mapping[str, list[dict[str, object]]],
    candidate_bundle: Mapping[str, list[dict[str, object]]],
    context_key: str,
    context_key_aliases: tuple[str, ...],
    policy_version: str,
    repository: DocumentRepository | None,
) -> list[dict[str, object]]:
    fields: list[dict[str, object]] = []
    candidate_suggestions_by_key = {
        key: _build_field_candidate_suggestions(key=key, candidate_bundle=candidate_bundle)
        for key in GLOBAL_SCHEMA_KEYS
    }

    for key in GLOBAL_SCHEMA_KEYS:
        value = normalized_values.get(key)
        key_evidence = evidence_map.get(key, [])
        candidate_suggestions = candidate_suggestions_by_key.get(key)

        if key in REPEATABLE_KEYS:
            if not isinstance(value, list):
                continue
            for index, item in enumerate(value):
                if not isinstance(item, str) or not item:
                    continue
                candidate = key_evidence[index] if index < len(key_evidence) else None
                evidence = candidate.get("evidence") if isinstance(candidate, dict) else None
                confidence = (
                    float(candidate.get("confidence", 0.65))
                    if isinstance(candidate, dict)
                    else 0.65
                )
                mapping_id = _derive_mapping_id(key=key, candidate=candidate)
                fields.append(
                    _build_structured_field(
                        FieldBuildContext(
                            key=key,
                            value=item,
                            confidence=confidence,
                            snippet=(
                                evidence.get("snippet") if isinstance(evidence, dict) else item
                            ),
                            value_type=VALUE_TYPE_BY_KEY.get(key, "string"),
                            page=(evidence.get("page") if isinstance(evidence, dict) else None),
                            mapping_id=mapping_id,
                            context_key=context_key,
                            context_key_aliases=context_key_aliases,
                            policy_version=policy_version,
                            repository=repository,
                            candidate_suggestions=candidate_suggestions,
                        )
                    )
                )
            continue

        if not isinstance(value, str) or not value:
            continue
        candidate = key_evidence[0] if key_evidence else None
        evidence = candidate.get("evidence") if isinstance(candidate, dict) else None
        confidence = (
            float(candidate.get("confidence", 0.65)) if isinstance(candidate, dict) else 0.65
        )
        mapping_id = _derive_mapping_id(key=key, candidate=candidate)
        fields.append(
            _build_structured_field(
                FieldBuildContext(
                    key=key,
                    value=value,
                    confidence=confidence,
                    snippet=(evidence.get("snippet") if isinstance(evidence, dict) else value),
                    value_type=VALUE_TYPE_BY_KEY.get(key, "string"),
                    page=(evidence.get("page") if isinstance(evidence, dict) else None),
                    mapping_id=mapping_id,
                    context_key=context_key,
                    context_key_aliases=context_key_aliases,
                    policy_version=policy_version,
                    repository=repository,
                    candidate_suggestions=candidate_suggestions,
                )
            )
        )

    return fields


def _build_field_candidate_suggestions(
    *, key: str, candidate_bundle: Mapping[str, list[dict[str, object]]]
) -> list[dict[str, object]]:
    ranked_candidates = sorted(
        candidate_bundle.get(key, []),
        key=_candidate_suggestion_sort_key,
    )

    suggestions: list[dict[str, object]] = []
    seen_values: set[str] = set()

    for candidate in ranked_candidates:
        value = str(candidate.get("value", "")).strip()
        if not value:
            continue
        normalized_value = value.casefold()
        if normalized_value in seen_values:
            continue
        seen_values.add(normalized_value)

        confidence = _sanitize_field_candidate_confidence(candidate.get("confidence"))
        suggestion: dict[str, object] = {
            "value": value,
            "confidence": confidence,
        }

        raw_evidence = candidate.get("evidence")
        if isinstance(raw_evidence, dict):
            evidence_payload: dict[str, object] = {}
            page = raw_evidence.get("page")
            if isinstance(page, int):
                evidence_payload["page"] = page
            snippet = raw_evidence.get("snippet")
            if isinstance(snippet, str) and snippet.strip():
                evidence_payload["snippet"] = snippet.strip()
            if evidence_payload:
                suggestion["evidence"] = evidence_payload

        suggestions.append(suggestion)
        if len(suggestions) >= 5:
            break

    return suggestions


def _candidate_suggestion_sort_key(item: dict[str, object]) -> tuple[float, str, str, int]:
    raw_evidence = item.get("evidence")
    evidence_snippet = ""
    evidence_page = 0
    if isinstance(raw_evidence, dict):
        snippet = raw_evidence.get("snippet")
        if isinstance(snippet, str):
            evidence_snippet = snippet.strip().casefold()
        page = raw_evidence.get("page")
        if isinstance(page, int):
            evidence_page = page

    return (
        -_sanitize_field_candidate_confidence(item.get("confidence")),
        str(item.get("value", "")).strip().casefold(),
        evidence_snippet,
        evidence_page,
    )


@dataclass(frozen=True, slots=True)
class FieldBuildContext:
    key: str
    value: str
    confidence: float
    snippet: str
    value_type: str
    page: int | None
    mapping_id: str | None
    context_key: str
    context_key_aliases: tuple[str, ...]
    policy_version: str
    repository: DocumentRepository | None
    candidate_suggestions: list[dict[str, object]] | None


def _build_structured_field(ctx: FieldBuildContext) -> dict[str, object]:
    normalized_snippet = ctx.snippet.strip()
    if len(normalized_snippet) > 180:
        normalized_snippet = normalized_snippet[:177].rstrip() + "..."
    field_candidate_confidence = _sanitize_field_candidate_confidence(ctx.confidence)
    text_extraction_reliability = _sanitize_text_extraction_reliability(None)
    field_review_history_adjustment = _resolve_review_history_adjustment(
        repository=ctx.repository,
        context_key=ctx.context_key,
        context_key_aliases=ctx.context_key_aliases,
        field_key=ctx.key,
        mapping_id=ctx.mapping_id,
        policy_version=ctx.policy_version,
    )
    field_mapping_confidence = _compose_field_mapping_confidence(
        candidate_confidence=field_candidate_confidence,
        review_history_adjustment=field_review_history_adjustment,
    )
    payload: dict[str, object] = {
        "field_id": str(uuid4()),
        "key": ctx.key,
        "value": ctx.value,
        "value_type": ctx.value_type,
        "field_candidate_confidence": field_candidate_confidence,
        "field_mapping_confidence": field_mapping_confidence,
        "text_extraction_reliability": text_extraction_reliability,
        "field_review_history_adjustment": field_review_history_adjustment,
        "context_key": ctx.context_key,
        "mapping_id": ctx.mapping_id,
        "policy_version": ctx.policy_version,
        "is_critical": ctx.key in CRITICAL_KEYS,
        "origin": "machine",
        "evidence": {
            "page": ctx.page,
            "snippet": normalized_snippet,
        },
    }
    if ctx.candidate_suggestions:
        payload["candidate_suggestions"] = ctx.candidate_suggestions
    return payload


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


def _sanitize_field_candidate_confidence(value: object) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, NUMERIC_TYPES):
        numeric = float(value)
        if math.isfinite(numeric):
            return min(max(numeric, 0.0), 1.0)
    return 0.0


def _derive_mapping_id(*, key: str, candidate: dict[str, object] | None) -> str | None:
    if not isinstance(candidate, dict):
        return None

    explicit = normalize_mapping_id(candidate.get("mapping_id"))
    if explicit is not None:
        return explicit

    anchor = candidate.get("anchor")
    if isinstance(anchor, str) and anchor.strip():
        return f"anchor::{anchor.strip().lower()}"

    reason = candidate.get("target_reason")
    if isinstance(reason, str) and reason.startswith("fallback"):
        return f"fallback::{key}"
    return None


def _resolve_review_history_adjustment(
    *,
    repository: DocumentRepository | None,
    context_key: str,
    context_key_aliases: tuple[str, ...],
    field_key: str,
    mapping_id: str | None,
    policy_version: str,
) -> float:
    _ = context_key_aliases
    if repository is None:
        return 0.0

    counts = repository.get_calibration_counts(
        context_key=context_key,
        field_key=field_key,
        mapping_id=mapping_id,
        policy_version=policy_version,
    )
    if counts is None:
        return 0.0

    accept_count, edit_count = counts
    return _sanitize_field_review_history_adjustment(
        compute_review_history_adjustment(
            accept_count=accept_count,
            edit_count=edit_count,
        )
    )


def _compose_field_mapping_confidence(
    *, candidate_confidence: float, review_history_adjustment: float
) -> float:
    composed = candidate_confidence + (review_history_adjustment / 100.0)
    return min(max(composed, 0.0), 1.0)


def _normalize_candidate_text(text: str) -> str:
    normalized = _WHITESPACE_PATTERN.sub(" ", text).strip()
    return normalized
