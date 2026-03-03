"""Triage classification and observability logging helpers."""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

from backend.app.application.field_normalizers import CANONICAL_SPECIES

from .snapshot import (
    _as_text,
    _extract_top_candidates,
    _format_top_candidate_for_log,
)

logger = logging.getLogger(__name__)
_uvicorn_logger = logging.getLogger("uvicorn.error")
_GOAL_FIELDS = (
    "pet_name",
    "clinic_name",
    "microchip_id",
    "owner_name",
    "weight",
    "document_date",
    "visit_date",
    "discharge_date",
    "vet_name",
)


def _emit_info(message: str) -> None:
    if _uvicorn_logger.handlers:
        _uvicorn_logger.info(message)
        return
    logger.info(message)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_diacritics = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_diacritics.strip().lower()


def _extract_first_number(value: str) -> float | None:
    match = re.search(r"-?\d+(?:[\.,]\d+)?", value)
    if match is None:
        return None
    try:
        return float(match.group(0).replace(",", "."))
    except ValueError:
        return None


def _suspicious_accepted_flags(field_key: str, value: str | None) -> list[str]:
    if not value:
        return []
    flags: list[str] = []
    normalized_value = value.strip()
    normalized_key = field_key.strip().lower()
    if len(normalized_value) > 80:
        flags.append("value_too_long")
    if normalized_key == "microchip_id":
        if any(char.isalpha() for char in normalized_value):
            flags.append("microchip_contains_letters")
        if len(normalized_value.split()) > 1:
            flags.append("microchip_multiple_words")
        if len(normalized_value) < 9 or len(normalized_value) > 15:
            flags.append("microchip_length_out_of_range")
        if not normalized_value.isdigit():
            flags.append("microchip_non_digit_characters")
    if normalized_key == "weight":
        letter_tokens = re.findall(r"[A-Za-z]+", normalized_value)
        if [token for token in letter_tokens if token.lower() not in {"kg", "kgs"}]:
            flags.append("weight_contains_non_kg_letters")
        numeric_value = _extract_first_number(normalized_value)
        if numeric_value is None:
            flags.append("weight_missing_numeric_value")
        elif numeric_value < 0.2 or numeric_value > 120:
            flags.append("weight_out_of_range")
    if normalized_key == "species" and _normalize_text(normalized_value) not in CANONICAL_SPECIES:
        flags.append("species_outside_allowed_set")
    if normalized_key == "sex" and _normalize_text(normalized_value) not in {"macho", "hembra"}:
        flags.append("sex_outside_allowed_set")
    if normalized_key == "pet_name":
        if normalized_value.isdigit():
            flags.append("pet_name_numeric_only")
        if len(normalized_value) <= 1:
            flags.append("pet_name_too_short")
        if re.search(r"\b(?:especie|raza|sexo|chip|fecha|peso)\b", normalized_value, re.IGNORECASE):
            flags.append("pet_name_contains_field_label")
        if re.search(r"\d{2}[/\-.]\d{2}[/\-.]\d{2,4}", normalized_value):
            flags.append("pet_name_contains_embedded_date")
        # Stopword-only names (e.g. "Nombre", "Datos")
        _stop = {"nombre", "datos", "cliente", "historial", "visita"}
        if _normalize_text(normalized_value) in _stop:
            flags.append("pet_name_is_stopword")
    if normalized_key == "clinic_name":
        compact = _normalize_text(normalized_value)
        if normalized_value.isdigit():
            flags.append("clinic_name_numeric_only")
        if len(normalized_value.strip()) <= 2:
            flags.append("clinic_name_too_short")
        if re.search(
            r"(?i)\b(?:c/|calle|av\.?|avenida|cp\b|portal|piso|puerta|direcci[oó]n|domicilio)\b",
            normalized_value,
        ) and re.search(r"\d", normalized_value):
            flags.append("clinic_name_address_like")
        if not re.search(r"\b(?:clinica|veterinari|hospital|centro|vet)\b", compact):
            flags.append("clinic_name_missing_institution_token")
    return flags


def build_extraction_triage(snapshot: dict[str, Any]) -> dict[str, Any]:
    fields = snapshot.get("fields") if isinstance(snapshot.get("fields"), dict) else {}
    counts = snapshot.get("counts") if isinstance(snapshot.get("counts"), dict) else {}
    missing: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    suspicious_accepted: list[dict[str, Any]] = []

    for field_key in sorted(fields.keys()):
        raw_payload = fields.get(field_key)
        if not isinstance(raw_payload, dict):
            continue
        status = str(raw_payload.get("status", "")).strip().lower()
        value_normalized = _as_text(raw_payload.get("valueNormalized"))
        value_raw = _as_text(raw_payload.get("valueRaw"))
        raw_candidate = _as_text(raw_payload.get("rawCandidate"))
        source_hint = _as_text(raw_payload.get("sourceHint"))
        top_candidates = _extract_top_candidates(raw_payload)
        top1 = top_candidates[0] if top_candidates else None
        top1_value = _as_text(top1.get("value")) if isinstance(top1, dict) else None
        value_for_triage = value_normalized or value_raw or raw_candidate or top1_value

        if status == "missing":
            missing.append(
                {
                    "field": field_key,
                    "value": None,
                    "reason": "missing",
                    "flags": [],
                    "rawCandidate": raw_candidate,
                    "sourceHint": source_hint,
                    "topCandidates": top_candidates,
                }
            )
            continue
        if status == "rejected":
            rejected.append(
                {
                    "field": field_key,
                    "value": value_for_triage,
                    "reason": _as_text(raw_payload.get("reason")) or "rejected",
                    "flags": [],
                    "rawCandidate": raw_candidate,
                    "sourceHint": source_hint,
                    "topCandidates": top_candidates,
                }
            )
            continue
        if status == "accepted":
            flags = _suspicious_accepted_flags(field_key, value_for_triage)
            if flags:
                suspicious_accepted.append(
                    {
                        "field": field_key,
                        "value": value_for_triage,
                        "reason": None,
                        "flags": flags,
                        "rawCandidate": raw_candidate,
                        "sourceHint": source_hint,
                        "topCandidates": top_candidates,
                    }
                )

    return {
        "documentId": _as_text(snapshot.get("documentId")) or "",
        "runId": _as_text(snapshot.get("runId")) or "",
        "createdAt": _as_text(snapshot.get("createdAt")) or "",
        "summary": {
            "accepted": int(counts.get("accepted", 0) or 0),
            "missing": int(counts.get("missing", 0) or 0),
            "rejected": int(counts.get("rejected", 0) or 0),
            "low": int(counts.get("low", 0) or 0),
            "mid": int(counts.get("mid", 0) or 0),
            "high": int(counts.get("high", 0) or 0),
        },
        "missing": missing,
        "rejected": rejected,
        "suspiciousAccepted": suspicious_accepted,
    }


def _goal_field_state(raw_payload: dict[str, Any] | None) -> dict[str, str]:
    payload = raw_payload if isinstance(raw_payload, dict) else {}
    status = str(payload.get("status", "missing")).strip().lower() or "missing"
    top_candidates = _extract_top_candidates(payload)
    top1 = top_candidates[0] if top_candidates else None
    return {"status": status, "top1": _format_top_candidate_for_log(top1)}


def _log_goal_fields_report(
    *, document_id: str, current: dict[str, Any], previous: dict[str, Any] | None
) -> None:
    current_fields = current.get("fields") if isinstance(current.get("fields"), dict) else {}
    previous_fields = (
        previous.get("fields")
        if isinstance(previous, dict) and isinstance(previous.get("fields"), dict)
        else {}
    )
    lines = [
        f"[extraction-observability] document={document_id} run={current.get('runId')} goal_fields"
    ]
    for field in _GOAL_FIELDS:
        state = _goal_field_state(current_fields.get(field))
        lines.append(f"- {field}: status={state['status']} {state['top1']}")
    lines.append("GOAL_FIELDS_DIFF:")
    if not previous_fields:
        lines.append("- none (first snapshot)")
    else:
        has_diff = False
        for field in _GOAL_FIELDS:
            current_state = _goal_field_state(current_fields.get(field))
            previous_state = _goal_field_state(previous_fields.get(field))
            if current_state == previous_state:
                continue
            has_diff = True
            lines.append(
                f"- {field}: "
                f"status={previous_state['status']} {previous_state['top1']} "
                f"-> status={current_state['status']} {current_state['top1']}"
            )
        if not has_diff:
            lines.append("- none")
    _emit_info("\n".join(lines))


def _log_triage_report(document_id: str, triage: dict[str, Any]) -> None:
    summary = triage.get("summary") if isinstance(triage.get("summary"), dict) else {}
    missing = triage.get("missing") if isinstance(triage.get("missing"), list) else []
    rejected = triage.get("rejected") if isinstance(triage.get("rejected"), list) else []
    suspicious = (
        triage.get("suspiciousAccepted")
        if isinstance(triage.get("suspiciousAccepted"), list)
        else []
    )

    lines: list[str] = [
        "[extraction-observability] "
        f"document={document_id} run={triage.get('runId')} triage "
        f"accepted={int(summary.get('accepted', 0) or 0)} "
        f"missing={int(summary.get('missing', 0) or 0)} "
        f"rejected={int(summary.get('rejected', 0) or 0)} "
        f"low={int(summary.get('low', 0) or 0)} "
        f"mid={int(summary.get('mid', 0) or 0)} "
        f"high={int(summary.get('high', 0) or 0)}",
        "MISSING:",
        "REJECTED:",
    ]

    if not missing:
        lines.insert(len(lines) - 1, "- none")
    else:
        missing_lines: list[str] = []
        for item in missing:
            if not isinstance(item, dict):
                continue
            field = item.get("field")
            candidates = (
                item.get("topCandidates") if isinstance(item.get("topCandidates"), list) else []
            )
            top1 = candidates[0] if candidates else None
            missing_lines.append(f"- {field}: {_format_top_candidate_for_log(top1)}")
        lines[len(lines) - 1 : len(lines) - 1] = missing_lines

    if not rejected:
        lines.append("- none")
    else:
        for item in rejected:
            if not isinstance(item, dict):
                continue
            field = item.get("field")
            reason = item.get("reason")
            raw_candidate = _as_text(item.get("rawCandidate"))
            candidates = (
                item.get("topCandidates") if isinstance(item.get("topCandidates"), list) else []
            )
            top1 = candidates[0] if candidates else None
            line = f"- {field}: reason={reason} {_format_top_candidate_for_log(top1)}"
            if raw_candidate:
                line += f" rawCandidate={raw_candidate!r}"
            lines.append(line)

    lines.append("SUSPICIOUS_ACCEPTED:")
    if not suspicious:
        lines.append("- none")
    else:
        for item in suspicious:
            if not isinstance(item, dict):
                continue
            field = item.get("field")
            value = _as_text(item.get("value"))
            flags = item.get("flags") if isinstance(item.get("flags"), list) else []
            raw_candidate = _as_text(item.get("rawCandidate"))
            flags_label = ",".join(str(flag) for flag in flags) if flags else "unknown"
            line = f"- {field}: flags=[{flags_label}]"
            if value:
                line += f" value={value!r}"
            if raw_candidate:
                line += f" rawCandidate={raw_candidate!r}"
            lines.append(line)

    _emit_info("\n".join(lines))
