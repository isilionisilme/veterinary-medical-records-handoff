"""Processing subsystem modules extracted from processing_runner."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import uuid4

from backend.app.application.confidence_calibration import (
    build_context_key,
    resolve_calibration_policy_version,
)
from backend.app.application.field_normalizers import normalize_canonical_fields
from backend.app.application.global_schema import (
    GLOBAL_SCHEMA_KEYS,
    normalize_global_schema,
    validate_global_schema_shape,
)
from backend.app.config import (
    confidence_band_cutoffs_or_none,
    confidence_policy_explicit_config_diagnostics,
    confidence_policy_version_or_none,
)
from backend.app.ports.document_repository import DocumentRepository
from backend.app.settings import should_include_interpretation_candidates

from .candidate_mining import (
    _candidate_sort_key,
    _map_candidates_to_global_schema,
    _mine_interpretation_candidates,
)
from .confidence_scoring import (
    _build_structured_fields_from_global_schema,
    _find_line_number_for_snippet,
)
from .constants import (
    _WHITESPACE_PATTERN,
    MVP_COVERAGE_DEBUG_KEYS,
    REVIEW_SCHEMA_CONTRACT,
)

logger = logging.getLogger(__name__)


def _default_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _build_interpretation_artifact(
    *,
    document_id: str,
    run_id: str,
    raw_text: str,
    repository: DocumentRepository | None = None,
) -> dict[str, object]:
    compact_text = _WHITESPACE_PATTERN.sub(" ", raw_text).strip()
    warning_codes: list[str] = []
    candidate_bundle: dict[str, list[dict[str, object]]] = {}
    canonical_evidence: dict[str, list[dict[str, object]]] = {}

    if compact_text:
        candidate_bundle = _mine_interpretation_candidates(raw_text)
        canonical_values, canonical_evidence = _map_candidates_to_global_schema(candidate_bundle)
        canonical_values = normalize_canonical_fields(
            canonical_values,
            canonical_evidence,
        )
        normalized_values = normalize_global_schema(canonical_values)
        validation_errors = validate_global_schema_shape(normalized_values)
        if validation_errors:
            from .orchestrator import InterpretationBuildError

            raise InterpretationBuildError(
                error_code="INTERPRETATION_VALIDATION_FAILED",
                details={"errors": validation_errors},
            )

        calibration_context_key = build_context_key(
            document_type="veterinary_record",
            language=normalized_values.get("language")
            if isinstance(normalized_values.get("language"), str)
            else None,
        )
        context_key_aliases: tuple[str, ...] = ()
        calibration_policy_version = resolve_calibration_policy_version()
        fields = _build_structured_fields_from_global_schema(
            normalized_values=normalized_values,
            evidence_map=canonical_evidence,
            candidate_bundle=candidate_bundle,
            context_key=calibration_context_key,
            context_key_aliases=context_key_aliases,
            policy_version=calibration_policy_version,
            repository=repository,
        )
    else:
        normalized_values = normalize_global_schema(None)
        fields = []
        warning_codes.append("EMPTY_RAW_TEXT")
        calibration_context_key = build_context_key(
            document_type="veterinary_record",
            language=None,
        )
        context_key_aliases = ()

    populated_keys = [
        key
        for key in GLOBAL_SCHEMA_KEYS
        if (
            isinstance(normalized_values.get(key), list) and len(normalized_values.get(key, [])) > 0
        )
        or (isinstance(normalized_values.get(key), str) and bool(normalized_values.get(key)))
    ]
    now_iso = _default_now_iso()
    policy_version = confidence_policy_version_or_none()
    band_cutoffs = confidence_band_cutoffs_or_none()
    mvp_coverage_debug = _build_mvp_coverage_debug_summary(
        raw_text=raw_text,
        normalized_values=normalized_values,
        candidate_bundle=candidate_bundle,
        evidence_map=canonical_evidence,
    )
    data: dict[str, object] = {
        "document_id": document_id,
        "processing_run_id": run_id,
        "created_at": now_iso,
        "schema_contract": REVIEW_SCHEMA_CONTRACT,
        "fields": fields,
        "global_schema": normalized_values,
        "summary": {
            "total_keys": len(GLOBAL_SCHEMA_KEYS),
            "populated_keys": len(populated_keys),
            "keys_present": populated_keys,
            "warning_codes": warning_codes,
            "date_selection": _build_date_selection_debug(canonical_evidence),
            "mvp_coverage_debug": mvp_coverage_debug,
        },
        "context_key": calibration_context_key,
    }
    if policy_version is not None and band_cutoffs is not None:
        low_max, mid_max = band_cutoffs
        data["confidence_policy"] = {
            "policy_version": policy_version,
            "band_cutoffs": {
                "low_max": round(low_max, 4),
                "mid_max": round(mid_max, 4),
            },
        }
        logger.info(
            "confidence_policy included in interpretation payload policy_version=%s",
            policy_version,
        )
    else:
        _, reason, missing_keys, invalid_keys = confidence_policy_explicit_config_diagnostics()
        logger.warning(
            "confidence_policy omitted from interpretation payload "
            "reason=%s missing_keys=%s invalid_keys=%s",
            reason,
            missing_keys,
            invalid_keys,
        )
    logger.info(
        "MVP coverage debug run_id=%s document_id=%s fields=%s",
        run_id,
        document_id,
        mvp_coverage_debug,
    )
    if _should_include_interpretation_candidates():
        data["candidate_bundle"] = candidate_bundle

    return {
        "interpretation_id": str(uuid4()),
        "version_number": 1,
        "data": data,
    }


def _should_include_interpretation_candidates() -> bool:
    return should_include_interpretation_candidates()


def _build_date_selection_debug(
    evidence_map: Mapping[str, list[dict[str, object]]],
) -> dict[str, dict[str, object] | None]:
    payload: dict[str, dict[str, object] | None] = {}
    for key in ("visit_date", "document_date", "admission_date", "discharge_date"):
        candidates = evidence_map.get(key, [])
        if not candidates:
            payload[key] = None
            continue
        top = candidates[0]
        payload[key] = {
            "anchor": top.get("anchor"),
            "anchor_priority": top.get("anchor_priority", 0),
            "target_reason": top.get("target_reason"),
        }
    return payload


def _build_mvp_coverage_debug_summary(
    *,
    raw_text: str,
    normalized_values: Mapping[str, object],
    candidate_bundle: Mapping[str, list[dict[str, object]]],
    evidence_map: Mapping[str, list[dict[str, object]]],
) -> dict[str, dict[str, object] | None]:
    summary: dict[str, dict[str, object] | None] = {}
    for key in MVP_COVERAGE_DEBUG_KEYS:
        raw_value = normalized_values.get(key)
        accepted = (isinstance(raw_value, str) and bool(raw_value.strip())) or (
            isinstance(raw_value, list) and len(raw_value) > 0
        )

        key_candidates = sorted(
            candidate_bundle.get(key, []),
            key=lambda item: _candidate_sort_key(item, key),
            reverse=True,
        )
        top1 = key_candidates[0] if key_candidates else None
        top1_value = str(top1.get("value", "")).strip() if isinstance(top1, dict) else None
        top1_conf = float(top1.get("confidence", 0.0)) if isinstance(top1, dict) else None

        line_number: int | None = None
        if accepted:
            key_evidence = evidence_map.get(key, [])
            top_evidence = key_evidence[0] if key_evidence else None
            evidence_payload = (
                top_evidence.get("evidence") if isinstance(top_evidence, dict) else None
            )
            snippet = (
                evidence_payload.get("snippet") if isinstance(evidence_payload, dict) else None
            )
            if isinstance(snippet, str) and snippet.strip():
                line_number = _find_line_number_for_snippet(raw_text, snippet)

        summary[key] = {
            "status": "accepted" if accepted else "missing",
            "top1": top1_value,
            "confidence": round(top1_conf, 2) if isinstance(top1_conf, float) else None,
            "line_number": line_number,
        }

    return summary
