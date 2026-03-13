"""Triage classification and observability logging helpers."""

from __future__ import annotations

import logging
import re
import unicodedata
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from backend.app.application.extraction_constants import (
    CLINIC_ADDRESS_MIN_LENGTH,
    CLINIC_NAME_MIN_LENGTH,
    DAYS_PER_YEAR,
    MAX_PET_AGE_YEARS,
    MAX_VALUE_LENGTH,
    MICROCHIP_MAX_DIGITS,
    MICROCHIP_MIN_DIGITS,
    OWNER_ADDRESS_MAX_LENGTH,
    PET_NAME_MIN_LENGTH,
    PHONE_DIGIT_COUNT,
    WEIGHT_MAX_KG,
    WEIGHT_MIN_KG,
)
from backend.app.application.field_normalizers import CANONICAL_SPECIES

from .snapshot import (
    _as_text,
    _extract_top_candidates,
    _format_top_candidate_for_log,
)

logger = logging.getLogger(__name__)
_uvicorn_logger = logging.getLogger("uvicorn.error")
_ADDRESS_TOKEN_RE = re.compile(
    r"(?i)\b(?:c/|calle|av\.?|avenida|plaza|paseo|camino|carretera|ctra\.?|"
    r"portal|piso|puerta|cp\b|c\.p\.|codigo\s+postal|n[º°o]?)\b"
)
_GOAL_FIELDS = (
    "pet_name",
    "clinic_name",
    "clinic_address",
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


def _validate_microchip(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    compact_digits = re.sub(r"\D", "", value)
    if any(char.isalpha() for char in value):
        flags.append("microchip_contains_letters")
    if len(value.split()) > 1:
        flags.append("microchip_multiple_words")
    if not (MICROCHIP_MIN_DIGITS <= len(value) <= MICROCHIP_MAX_DIGITS):
        flags.append("microchip_length_out_of_range")
    if not value.isdigit():
        flags.append("microchip_non_digit_characters")
    if re.search(r"(?i)\b(?:tel(?:[eé]fono)?|movil|m[oó]vil)\b", value):
        flags.append("microchip_phone_context")
    if re.search(r"(?i)\b(?:nif|dni|nie|pasaporte|documento)\b", value):
        flags.append("microchip_document_id_context")
    if len(compact_digits) == PHONE_DIGIT_COUNT and compact_digits.startswith(("6", "7", "8", "9")):
        flags.append("microchip_phone_like_digits")
    return flags


def _validate_weight(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    letter_tokens = re.findall(r"[A-Za-z]+", value)
    if [token for token in letter_tokens if token.lower() not in {"kg", "kgs"}]:
        flags.append("weight_contains_non_kg_letters")
    numeric_value = _extract_first_number(value)
    if numeric_value is None:
        flags.append("weight_missing_numeric_value")
    elif numeric_value < WEIGHT_MIN_KG or numeric_value > WEIGHT_MAX_KG:
        flags.append("weight_out_of_range")
    return flags


def _validate_species(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    if _normalize_text(value) not in CANONICAL_SPECIES:
        return ["species_outside_allowed_set"]
    return []


def _validate_sex(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    if _normalize_text(value) not in {"macho", "hembra"}:
        return ["sex_outside_allowed_set"]
    return []


def _validate_pet_name(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    if value.isdigit():
        flags.append("pet_name_numeric_only")
    if len(value) <= PET_NAME_MIN_LENGTH:
        flags.append("pet_name_too_short")
    if re.search(r"\b(?:especie|raza|sexo|chip|fecha|peso)\b", value, re.IGNORECASE):
        flags.append("pet_name_contains_field_label")
    if re.search(r"\d{2}[/\-.]\d{2}[/\-.]\d{2,4}", value):
        flags.append("pet_name_contains_embedded_date")
    _stop = {"nombre", "datos", "cliente", "historial", "visita"}
    if _normalize_text(value) in _stop:
        flags.append("pet_name_is_stopword")
    return flags


def _validate_clinic_name(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    compact = _normalize_text(value)
    if value.isdigit():
        flags.append("clinic_name_numeric_only")
    if len(value.strip()) <= CLINIC_NAME_MIN_LENGTH:
        flags.append("clinic_name_too_short")
    if re.search(
        r"(?i)\b(?:c/|calle|av\.?|avenida|cp\b|portal|piso|puerta|direcci[oó]n|domicilio)\b",
        value,
    ) and re.search(r"\d", value):
        flags.append("clinic_name_address_like")
    if not re.search(r"\b(?:clinica|veterinari|hospital|centro|vet)\b", compact):
        flags.append("clinic_name_missing_institution_token")
    return flags


def _validate_clinic_address(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    compact = _normalize_text(value)
    if value.isdigit():
        flags.append("clinic_address_numeric_only")
    if len(value.strip()) < CLINIC_ADDRESS_MIN_LENGTH:
        flags.append("clinic_address_too_short")
    if re.search(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", value):
        flags.append("clinic_address_contains_email")
    if re.search(r"(?i)\b(?:tel(?:[eé]fono)?|movil|m[oó]vil)\b", value):
        flags.append("clinic_address_contains_phone_token")
    if re.search(rf"\b\d{{{PHONE_DIGIT_COUNT},}}\b", value):
        flags.append("clinic_address_contains_phone_number")
    has_po_box = bool(
        re.search(r"(?i)\b(?:po\s*box|apartado\s+postal|apdo\.?\s*postal)\b", compact)
    )
    has_street_token = bool(
        re.search(
            r"(?i)\b(?:c/|calle|av\.?|avenida|plaza|paseo|camino|carretera|ctra\.?|portal|puerta)\b",
            value,
        )
    )
    if has_po_box and not has_street_token:
        flags.append("clinic_address_po_box_without_street")
    return flags


def _validate_owner_address(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    compact = _normalize_text(value)
    if len(value.strip()) < CLINIC_ADDRESS_MIN_LENGTH:
        flags.append("owner_address_too_short")
    if len(value.strip()) > OWNER_ADDRESS_MAX_LENGTH:
        flags.append("owner_address_too_long")
    has_address_token = bool(_ADDRESS_TOKEN_RE.search(compact))
    has_digits = bool(re.search(r"\d", value))
    if not has_address_token or not has_digits:
        flags.append("owner_address_no_address_tokens")
    if all_fields:
        clinic_address_payload = all_fields.get("clinic_address")
        if (
            isinstance(clinic_address_payload, dict)
            and clinic_address_payload.get("status") == "accepted"
        ):
            clinic_address_value = _as_text(clinic_address_payload.get("valueNormalized"))
            if clinic_address_value and _normalize_text(clinic_address_value) == compact:
                flags.append("owner_address_matches_clinic_address")
    return flags


def _validate_dob(value: str, all_fields: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    try:
        dob_date = datetime.strptime(value, "%d/%m/%Y").date()
        today = date.today()
        if dob_date > today:
            flags.append("dob_future_date")
        age_years = (today - dob_date).days / DAYS_PER_YEAR
        if age_years > MAX_PET_AGE_YEARS:
            flags.append("dob_implausibly_old")
        if all_fields:
            visit_date_payload = all_fields.get("visit_date")
            if (
                isinstance(visit_date_payload, dict)
                and visit_date_payload.get("status") == "accepted"
            ):
                visit_date_value = _as_text(visit_date_payload.get("valueNormalized"))
                if visit_date_value and visit_date_value == value:
                    flags.append("dob_matches_visit_date")
    except (ValueError, AttributeError):
        pass
    return flags


_FIELD_VALIDATORS: dict[str, Callable[[str, dict[str, Any] | None], list[str]]] = {
    "microchip_id": _validate_microchip,
    "weight": _validate_weight,
    "species": _validate_species,
    "sex": _validate_sex,
    "pet_name": _validate_pet_name,
    "clinic_name": _validate_clinic_name,
    "clinic_address": _validate_clinic_address,
    "owner_address": _validate_owner_address,
    "dob": _validate_dob,
}


def _suspicious_accepted_flags(
    field_key: str, value: str | None, all_fields: dict[str, Any] | None = None
) -> list[str]:
    if not value:
        return []
    normalized_value = value.strip()
    if not normalized_value:
        return []
    flags: list[str] = []
    if len(normalized_value) > MAX_VALUE_LENGTH:
        flags.append("value_too_long")
    validator = _FIELD_VALIDATORS.get(field_key.strip().lower())
    if validator is not None:
        flags.extend(validator(normalized_value, all_fields))
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
            flags = _suspicious_accepted_flags(field_key, value_for_triage, fields)
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
