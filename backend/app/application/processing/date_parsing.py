"""Raw-text parsing helpers used by candidate mining."""

from __future__ import annotations

import re

from .constants import (
    _ADDRESS_LIKE_PATTERN,
    _CLINICAL_RECORD_GUARD_PATTERN,
    _DATE_CANDIDATE_PATTERN,
    _DATE_TARGET_ANCHORS,
    _DATE_TARGET_PRIORITY,
    _LABELED_PATTERNS,
    _LICENSE_ONLY_PATTERN,
    _MICROCHIP_DIGITS_PATTERN,
    _MICROCHIP_KEYWORD_WINDOW_PATTERN,
    _MICROCHIP_OCR_PREFIX_WINDOW_PATTERN,
    _NAME_TOKEN_PATTERN,
    _OWNER_CLIENT_HEADER_LINE_PATTERN,
    _OWNER_CLIENT_TABULAR_LABEL_LINE_PATTERN,
    _OWNER_CONTEXT_PATTERN,
    _OWNER_HEADER_LOOKBACK_LINES,
    _OWNER_INLINE_CONTEXT_WINDOW_LINES,
    _OWNER_LABEL_LINE_PATTERN,
    _OWNER_NOMBRE_LINE_PATTERN,
    _OWNER_PATIENT_LABEL_PATTERN,
    _OWNER_TABULAR_FORWARD_SCAN_LINES,
    _PHONE_LIKE_PATTERN,
    _VET_LABEL_LINE_PATTERN,
    _VET_OR_CLINIC_CONTEXT_PATTERN,
    _WHITESPACE_PATTERN,
    COVERAGE_CONFIDENCE_FALLBACK,
    COVERAGE_CONFIDENCE_LABEL,
)


def _extract_microchip_digits(window: str) -> str | None:
    direct_match = _MICROCHIP_DIGITS_PATTERN.search(window)
    if direct_match is not None:
        return direct_match.group(1)

    compact_digits = re.sub(r"\D", "", window)
    if 9 <= len(compact_digits) <= 15:
        return compact_digits
    return None


def _split_owner_before_address_tokens(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return ""

    address_markers = {
        "calle",
        "av",
        "av.",
        "avenida",
        "cp",
        "codigo",
        "postal",
        "no",
        "no.",
        "nº",
        "n°",
        "num",
        "num.",
        "número",
        "plaza",
        "pte",
        "pte.",
        "portal",
        "piso",
        "puerta",
    }
    for index, token in enumerate(tokens):
        normalized_token = token.casefold().strip(".,:;()[]{}")
        if (
            normalized_token == "codigo"
            and index + 1 < len(tokens)
            and tokens[index + 1].casefold().strip(".,:;()[]{}") == "postal"
        ):
            return " ".join(tokens[:index]).strip()
        if normalized_token.startswith("c/") or normalized_token in address_markers:
            return " ".join(tokens[:index]).strip()
    return text


def _normalize_person_fragment(fragment: str) -> str | None:
    value = _WHITESPACE_PATTERN.sub(" ", fragment).strip(" .,:;\t\r\n")
    if not value:
        return None
    if "@" in value or _PHONE_LIKE_PATTERN.search(value):
        return None
    if _LICENSE_ONLY_PATTERN.match(value):
        return None
    if _ADDRESS_LIKE_PATTERN.search(value):
        return None

    tokens = value.split()
    if not 2 <= len(tokens) <= 5:
        return None
    letter_tokens = [token for token in tokens if _NAME_TOKEN_PATTERN.match(token)]
    if len(letter_tokens) < max(2, int(len(tokens) * 0.6)):
        return None
    return " ".join(tokens)


def extract_labeled_person_candidates(raw_text: str, confidence: float) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    payloads.extend(
        _extract_labeled_person_candidates_by_pattern(
            raw_text=raw_text,
            key="vet_name",
            pattern=_VET_LABEL_LINE_PATTERN,
            confidence=confidence,
            owner_mode=False,
        )
    )
    payloads.extend(
        _extract_labeled_person_candidates_by_pattern(
            raw_text=raw_text,
            key="owner_name",
            pattern=_OWNER_LABEL_LINE_PATTERN,
            confidence=confidence,
            owner_mode=True,
        )
    )
    return payloads


def _extract_labeled_person_candidates_by_pattern(
    *,
    raw_text: str,
    key: str,
    pattern: re.Pattern[str],
    confidence: float,
    owner_mode: bool = False,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    raw_lines = raw_text.splitlines()

    for index, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match is None:
            continue

        candidate_source = match.group(1).strip() if isinstance(match.group(1), str) else ""
        if not candidate_source and ":" in line:
            for next_index in range(index + 1, min(index + 4, len(raw_lines))):
                next_line = raw_lines[next_index].strip()
                if next_line:
                    candidate_source = next_line
                    break

        if not candidate_source:
            continue
        if owner_mode:
            candidate_source = _split_owner_before_address_tokens(candidate_source)

        normalized = _normalize_person_fragment(candidate_source)
        if normalized is None:
            continue

        lower_line = line.casefold()
        if key == "vet_name" and _ADDRESS_LIKE_PATTERN.search(lower_line):
            continue
        if key == "owner_name" and _VET_OR_CLINIC_CONTEXT_PATTERN.search(lower_line):
            continue

        payloads.append(
            {"key": key, "value": normalized, "confidence": confidence, "snippet": line}
        )
    return payloads


def extract_owner_nombre_candidates(raw_text: str, confidence: float) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    raw_lines = raw_text.splitlines()

    for index, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue
        match = _OWNER_NOMBRE_LINE_PATTERN.match(line)
        if match is None:
            continue

        window_start = max(0, index - _OWNER_INLINE_CONTEXT_WINDOW_LINES)
        window_end = min(len(raw_lines), index + _OWNER_INLINE_CONTEXT_WINDOW_LINES + 1)
        context_window = " ".join(raw_lines[window_start:window_end])
        pre_context_window = " ".join(raw_lines[window_start:index])
        has_owner_context = _OWNER_CONTEXT_PATTERN.search(context_window) is not None

        previous_non_empty_line = ""
        for back_index in range(index - 1, -1, -1):
            previous_line = raw_lines[back_index].strip()
            if previous_line:
                previous_non_empty_line = previous_line
                break

        has_client_header_context = bool(
            previous_non_empty_line
            and _OWNER_CLIENT_HEADER_LINE_PATTERN.match(previous_non_empty_line)
        )
        if not has_owner_context and not has_client_header_context:
            lookback_start = max(0, index - _OWNER_HEADER_LOOKBACK_LINES)
            has_client_header_context = any(
                _OWNER_CLIENT_HEADER_LINE_PATTERN.match(raw_lines[lookback_index].strip())
                for lookback_index in range(lookback_start, index)
            )
        if not has_owner_context and not has_client_header_context:
            continue
        if _VET_OR_CLINIC_CONTEXT_PATTERN.search(context_window) is not None:
            continue
        if not has_owner_context and _OWNER_PATIENT_LABEL_PATTERN.search(pre_context_window):
            continue

        candidate_source = match.group(1).strip() if isinstance(match.group(1), str) else ""
        if not candidate_source:
            for next_index in range(
                index + 1,
                min(index + _OWNER_TABULAR_FORWARD_SCAN_LINES + 1, len(raw_lines)),
            ):
                next_line = raw_lines[next_index].strip()
                if not next_line:
                    continue
                if _OWNER_CLIENT_TABULAR_LABEL_LINE_PATTERN.match(next_line):
                    continue

                inline_candidate = _split_owner_before_address_tokens(next_line)
                inline_normalized = _normalize_person_fragment(inline_candidate)
                if inline_normalized is None:
                    continue
                candidate_source = inline_normalized
                break

        candidate_source = _split_owner_before_address_tokens(candidate_source)
        normalized = _normalize_person_fragment(candidate_source)
        if normalized is None:
            continue

        payloads.append(
            {"key": "owner_name", "value": normalized, "confidence": confidence, "snippet": line}
        )

    return payloads


def extract_regex_labeled_candidates(raw_text: str) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for key, pattern, confidence in _LABELED_PATTERNS:
        for match in re.finditer(pattern, raw_text, flags=re.IGNORECASE):
            payloads.append(
                {
                    "key": key,
                    "value": match.group(1),
                    "confidence": confidence,
                    "snippet": match.group(0),
                }
            )
    return payloads


def extract_microchip_keyword_candidates(
    raw_text: str,
    confidence: float,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for match in _MICROCHIP_KEYWORD_WINDOW_PATTERN.finditer(raw_text):
        window = match.group(1) if isinstance(match.group(1), str) else ""
        digits = _extract_microchip_digits(window)
        if digits is None:
            continue
        payloads.append(
            {
                "key": "microchip_id",
                "value": digits,
                "confidence": confidence,
                "snippet": match.group(0),
            }
        )
    return payloads


def extract_clinical_record_candidates(raw_text: str, confidence: float) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for match in re.finditer(
        (
            r"(?is)(?:nhc|n[ºo°]?\s*(?:historial|historia\s*cl[ií]nica)|"
            r"historial\s*cl[ií]nico)\s*[:\-]?\s*([^\n]{1,60})"
        ),
        raw_text,
    ):
        raw_value = str(match.group(1)).strip()
        if not raw_value or _CLINICAL_RECORD_GUARD_PATTERN.search(raw_value):
            continue
        payloads.append(
            {
                "key": "clinical_record_number",
                "value": raw_value,
                "confidence": confidence,
                "snippet": match.group(0),
            }
        )
    return payloads


def extract_ocr_microchip_candidates(raw_text: str, confidence: float) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for match in _MICROCHIP_OCR_PREFIX_WINDOW_PATTERN.finditer(raw_text):
        window = match.group(1) if isinstance(match.group(1), str) else ""
        digits = _extract_microchip_digits(window)
        if digits is None:
            continue
        payloads.append(
            {
                "key": "microchip_id",
                "value": digits,
                "confidence": confidence,
                "snippet": match.group(0),
            }
        )
    return payloads


def extract_microchip_adjacent_line_candidates(
    raw_text: str,
    confidence: float,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    raw_lines = raw_text.splitlines()
    chip_label_re = re.compile(
        r"(?i)\b(?:microchip|micr0chip|chip|transponder|identificaci[oó]n\s+electr[oó]nica|"
        r"n[º°o]?\s*chip)\b"
    )

    max_label_distance = 8

    for index, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue

        digits = _extract_microchip_digits(line)
        if digits is None:
            continue

        window_start = max(0, index - max_label_distance)
        window_end = min(len(raw_lines), index + max_label_distance + 1)
        has_label_in_window = any(
            chip_label_re.search(raw_lines[candidate_index].strip())
            for candidate_index in range(window_start, window_end)
            if candidate_index != index
        )
        if not has_label_in_window:
            continue

        snippet_start = window_start
        snippet_end = window_end
        snippet = "\n".join(raw_lines[snippet_start:snippet_end])
        payloads.append(
            {
                "key": "microchip_id",
                "value": digits,
                "confidence": confidence,
                "snippet": snippet,
            }
        )

    return payloads


def extract_unanchored_document_date_candidates(
    raw_text: str,
    confidence: float,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for match in re.finditer(r"\b([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4})\b", raw_text):
        snippet = raw_text[max(0, match.start() - 36) : min(len(raw_text), match.end() + 36)]
        payloads.append(
            {
                "key": "document_date",
                "value": match.group(1),
                "confidence": confidence,
                "snippet": snippet,
            }
        )
    return payloads


def extract_unlabeled_header_dob_candidates(
    raw_text: str,
    confidence: float,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    non_empty_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not non_empty_lines:
        return payloads

    header_window = non_empty_lines[:20]
    date_line_re = re.compile(r"^([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2})$")
    chip_context_re = re.compile(
        r"(?i)\b(?:microchip|micr0chip|chip|transponder|identificaci[oó]n\s+electr[oó]nica|n[º°o]?\s*chip)\b"
    )

    for index, line in enumerate(header_window):
        date_match = date_line_re.match(line)
        if date_match is None:
            continue

        context_lines = header_window[index : min(index + 9, len(header_window))]
        context_text = "\n".join(context_lines)
        has_chip_context = bool(chip_context_re.search(context_text))
        has_chip_digits = bool(_MICROCHIP_DIGITS_PATTERN.search(context_text))
        if not has_chip_context and not has_chip_digits:
            continue

        payloads.append(
            {
                "key": "dob",
                "value": date_match.group(1),
                "confidence": confidence,
                "snippet": context_text,
                "target_reason": "header_date_near_chip",
            }
        )
        break

    return payloads


def extract_timeline_document_date_candidates(
    lines: list[str],
    confidence: float,
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for line in lines:
        timeline_match = re.match(r"^-\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})\s*-", line)
        if timeline_match:
            payloads.append(
                {
                    "key": "document_date",
                    "value": timeline_match.group(1),
                    "confidence": confidence,
                    "snippet": line,
                    "target_reason": "timeline_unanchored",
                }
            )
    return payloads


def extract_date_candidates_with_classification(raw_text: str) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    lower_text = raw_text.casefold()

    for match in _DATE_CANDIDATE_PATTERN.finditer(raw_text):
        value = match.group(1)
        start = max(0, match.start() - 70)
        end = min(len(raw_text), match.end() + 70)
        snippet = _WHITESPACE_PATTERN.sub(" ", raw_text[start:end]).strip()
        context = lower_text[start:end]

        chosen_key = "document_date"
        chosen_anchor = "fallback"
        chosen_priority = 1
        chosen_reason = "fallback_document_date"

        for key, anchors in _DATE_TARGET_ANCHORS.items():
            matched_anchor = next((anchor for anchor in anchors if anchor in context), None)
            if matched_anchor is None:
                continue
            priority = _DATE_TARGET_PRIORITY.get(key, 1)
            if priority > chosen_priority:
                chosen_key = key
                chosen_anchor = matched_anchor
                chosen_priority = priority
                chosen_reason = f"anchor:{matched_anchor}"

        confidence = (
            COVERAGE_CONFIDENCE_LABEL if chosen_priority > 1 else COVERAGE_CONFIDENCE_FALLBACK
        )
        candidates.append(
            {
                "target_key": chosen_key,
                "value": value,
                "confidence": confidence,
                "snippet": snippet,
                "anchor": chosen_anchor,
                "anchor_priority": chosen_priority,
                "target_reason": chosen_reason,
            }
        )

    return candidates
