"""Location-focused candidate extraction helpers."""

from __future__ import annotations

import re

from ..constants import (
    _ADDRESS_LIKE_PATTERN,
    _WHITESPACE_PATTERN,
    COVERAGE_CONFIDENCE_FALLBACK,
    COVERAGE_CONFIDENCE_LABEL,
)
from ..field_patterns import (
    _AMBIGUOUS_ADDRESS_LABEL_LINE_RE,
    _CLINIC_ADDRESS_CONTEXT_RE,
    _CLINIC_ADDRESS_LABEL_LINE_RE,
    _CLINIC_ADDRESS_START_RE,
    _CLINIC_CONTEXT_LINE_RE,
    _CLINIC_HEADER_ADDRESS_CONTEXT_RE,
    _CLINIC_HEADER_GENERIC_BLACKLIST,
    _CLINIC_HEADER_SECTION_CONTEXT_RE,
    _CLINIC_OR_HOSPITAL_CONTEXT_RE,
    _CLINIC_STANDALONE_LINE_RE,
    _HEADER_BLOCK_SCAN_WINDOW,
    _OWNER_ADDRESS_CONTEXT_RE,
    _OWNER_ADDRESS_LABEL_LINE_RE,
    _OWNER_BLOCK_IDENTIFICATION_CONTEXT_RE,
    _OWNER_CONTEXT_RE,
    _OWNER_HEADER_RE,
    _OWNER_LOCALITY_LINE_RE,
    _OWNER_LOCALITY_SECTION_BLACKLIST,
    _OWNER_NAME_LIKE_LINE_RE,
    _POSTAL_HINT_RE,
    _SIMPLE_FIELD_LABEL_RE,
)
from .common import CandidateCollector, MiningContext


def extract_location_candidates(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    _extract_clinic_header_candidate(context, collector)
    _extract_three_line_clinic_address(context, collector)
    _extract_owner_address_block(context, collector)
    _extract_owner_header_inline_address(context, collector)
    _extract_labeled_address_lines(context, collector)
    _extract_inline_clinic_address(context, collector)
    _extract_clinic_name_contexts(context, collector)


def _extract_clinic_header_candidate(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    if not context.lines:
        return
    clinic_header = context.lines[0]
    clinic_header_folded = clinic_header.casefold()
    header_looks_institutional = (
        clinic_header.isupper()
        and 3 <= len(clinic_header) <= 60
        and ":" not in clinic_header
        and "-" not in clinic_header
        and re.search(r"\d", clinic_header) is None
        and clinic_header not in _CLINIC_HEADER_GENERIC_BLACKLIST
        and clinic_header_folded not in _pet_name_stopwords()
    )
    if not header_looks_institutional:
        return
    context_compact = " ".join(context.lines[1:8])
    has_address_context = (
        _CLINIC_HEADER_ADDRESS_CONTEXT_RE.search(context_compact) is not None
        or re.search(r"\b\d{5}\b", context_compact) is not None
    )
    has_section_context = _CLINIC_HEADER_SECTION_CONTEXT_RE.search(context_compact) is not None
    if has_address_context and has_section_context:
        collector.add_candidate(
            key="clinic_name",
            value=clinic_header,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet="\n".join(context.lines[:4]),
        )


def _extract_three_line_clinic_address(
    context: MiningContext, collector: CandidateCollector
) -> None:
    max_header_scan = min(len(context.lines) - 2, _HEADER_BLOCK_SCAN_WINDOW)
    for index in range(max_header_scan):
        first_line = context.lines[index]
        second_line = context.lines[index + 1]
        third_line = context.lines[index + 2]
        if _CLINIC_ADDRESS_START_RE.search(first_line) is None:
            continue
        if any(
            _SIMPLE_FIELD_LABEL_RE.match(line) is not None for line in (first_line, second_line)
        ):
            continue
        if _POSTAL_HINT_RE.search(third_line) is None:
            continue
        if any(
            _CLINIC_HEADER_SECTION_CONTEXT_RE.search(line.casefold()) is not None
            for line in (second_line, third_line)
        ):
            continue
        if not (re.search(r"\d", first_line) or re.search(r"\d", second_line)):
            continue
        owner_block_context = " ".join(
            context.lines[max(0, index - 1) : min(len(context.lines), index + 4)]
        ).casefold()
        if _OWNER_CONTEXT_RE.search(owner_block_context) is not None:
            continue
        collector.add_candidate(
            key="clinic_address",
            value=" ".join(
                part.strip(" .,:;\t\r\n") for part in (first_line, second_line, third_line)
            ),
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet="\n".join(context.lines[index : min(len(context.lines), index + 4)]),
        )


def _extract_owner_address_block(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for index in range(len(context.lines) - 1):
        owner_line = context.lines[index]
        address_line = context.lines[index + 1]
        if _SIMPLE_FIELD_LABEL_RE.match(owner_line) or _SIMPLE_FIELD_LABEL_RE.match(address_line):
            continue
        if _OWNER_NAME_LIKE_LINE_RE.match(owner_line) is None:
            continue
        if (
            _ADDRESS_LIKE_PATTERN.search(address_line) is None
            or re.search(r"\d", address_line) is None
        ):
            continue
        context_text = " ".join(
            context.lines[max(0, index - 3) : min(len(context.lines), index + 4)]
        ).casefold()
        has_owner_context = _OWNER_ADDRESS_CONTEXT_RE.search(context_text) is not None
        has_identification_context = (
            _OWNER_BLOCK_IDENTIFICATION_CONTEXT_RE.search(context_text) is not None
        )
        has_clinic_context = _CLINIC_ADDRESS_CONTEXT_RE.search(context_text) is not None
        if (has_clinic_context and not has_owner_context) or (
            not has_owner_context and not has_identification_context
        ):
            continue
        candidate_value = _build_owner_address_candidate(context.lines, index)
        if candidate_value:
            collector.add_candidate(
                key="owner_address",
                value=candidate_value,
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet="\n".join(context.lines[index : min(len(context.lines), index + 3)]),
            )


def _extract_owner_header_inline_address(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for line in context.lines:
        if ":" in line:
            header, value = line.split(":", 1)
        elif "-" in line:
            header, value = line.split("-", 1)
        else:
            header, value = "", ""

        lower_header = header.casefold()
        if not value or _OWNER_HEADER_RE.search(lower_header) is None:
            continue

        owner_value = value.strip(" .,:;\t\r\n")
        address_start = _CLINIC_ADDRESS_START_RE.search(owner_value)
        if address_start is None:
            continue

        address_fragment = owner_value[address_start.start() :].strip(" .,:;\t\r\n")
        if address_fragment:
            collector.add_candidate(
                key="owner_address",
                value=address_fragment,
                confidence=COVERAGE_CONFIDENCE_LABEL,
                snippet=line,
            )


def _extract_labeled_address_lines(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for index, line in enumerate(context.lines):
        _extract_owner_labeled_address(context, collector, index, line)
        _extract_clinic_labeled_address(context, collector, index, line)


def _extract_inline_clinic_address(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for index, line in enumerate(context.lines):
        if _CLINIC_ADDRESS_START_RE.search(line) is None or re.search(r"\d", line) is None:
            continue
        previous_line = context.lines[index - 1] if index > 0 else ""
        owner_nearby = _OWNER_CONTEXT_RE.search(previous_line.casefold()) is not None
        clinic_context_nearby = (
            _CLINIC_OR_HOSPITAL_CONTEXT_RE.search(previous_line.casefold()) is not None
        )
        if clinic_context_nearby and not owner_nearby and ":" not in line:
            collector.add_candidate(
                key="clinic_address",
                value=line.strip(" .,:;\t\r\n"),
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet="\n".join(
                    context.lines[max(0, index - 1) : min(len(context.lines), index + 2)]
                ),
            )


def _extract_clinic_name_contexts(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for line in context.lines:
        _extract_clinic_context_line(line, collector)
        _extract_clinic_standalone_line(line, collector)


def _extract_owner_labeled_address(
    context: MiningContext,
    collector: CandidateCollector,
    index: int,
    line: str,
) -> None:
    match = _OWNER_ADDRESS_LABEL_LINE_RE.match(line)
    if match is None:
        return
    address_parts = _collect_address_parts(context.lines, index, match.group(1) or "")
    if address_parts:
        collector.add_candidate(
            key="owner_address",
            value=" ".join(address_parts),
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet="\n".join(context.lines[index : min(len(context.lines), index + 3)]),
        )


def _extract_clinic_labeled_address(
    context: MiningContext,
    collector: CandidateCollector,
    index: int,
    line: str,
) -> None:
    match = _CLINIC_ADDRESS_LABEL_LINE_RE.match(line)
    if match is None:
        return
    candidate_value = " ".join(_collect_address_parts(context.lines, index, match.group(2) or ""))
    if not candidate_value:
        return
    raw_label = match.group(1).strip().casefold()
    snippet_block = "\n".join(context.lines[index : min(len(context.lines), index + 3)])
    explicit_clinic_label = "clínica" in raw_label or "clinica" in raw_label
    is_ambiguous_generic_label = (
        not explicit_clinic_label and _AMBIGUOUS_ADDRESS_LABEL_LINE_RE.match(line) is not None
    )
    if explicit_clinic_label:
        collector.add_candidate(
            key="clinic_address",
            value=candidate_value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=snippet_block,
        )
        return
    context_decision = collector.classify_address_context(index)
    if context_decision == "owner" and is_ambiguous_generic_label:
        collector.add_candidate(
            key="owner_address",
            value=candidate_value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=snippet_block,
        )
        return
    if context_decision == "clinic" and is_ambiguous_generic_label:
        collector.add_candidate(
            key="clinic_address",
            value=candidate_value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=snippet_block,
        )
        return
    collector.add_candidate(
        key="clinic_address",
        value=candidate_value,
        confidence=COVERAGE_CONFIDENCE_FALLBACK,
        snippet=snippet_block,
    )


def _extract_clinic_context_line(
    line: str,
    collector: CandidateCollector,
) -> None:
    match = _CLINIC_CONTEXT_LINE_RE.search(line)
    if match is None:
        return
    institution_token = match.group(1)
    institution_name = match.group(2).strip(" .,:;\t\r\n")
    canonical_institution = (
        "Centro" if institution_token.casefold() == "centr0" else institution_token
    )
    collector.add_candidate(
        key="clinic_name",
        value=f"{canonical_institution} {institution_name}".strip(),
        confidence=COVERAGE_CONFIDENCE_FALLBACK,
        snippet=line,
    )


def _extract_clinic_standalone_line(
    line: str,
    collector: CandidateCollector,
) -> None:
    match = _CLINIC_STANDALONE_LINE_RE.match(line)
    if match is None:
        return
    institution_token = match.group(1).strip()
    institution_name = match.group(2).strip(" .,:;\t\r\n")
    if institution_name.casefold().startswith("de "):
        return
    canonical_institution = (
        "HV" if re.fullmatch(r"(?i)h\.?\s*v\.?", institution_token) else institution_token
    )
    collector.add_candidate(
        key="clinic_name",
        value=f"{canonical_institution} {institution_name}".strip(),
        confidence=COVERAGE_CONFIDENCE_FALLBACK,
        snippet=line,
    )


def _collect_address_parts(
    lines: list[str],
    index: int,
    inline_value: str,
) -> list[str]:
    address_parts: list[str] = []
    inline_clean = inline_value.strip(" .,:;\t\r\n")
    if inline_clean:
        address_parts.append(inline_clean)
    elif index + 1 < len(lines) and not _SIMPLE_FIELD_LABEL_RE.match(lines[index + 1]):
        address_parts.append(lines[index + 1].strip(" .,:;\t\r\n"))
    if (
        address_parts
        and index + 2 < len(lines)
        and not _SIMPLE_FIELD_LABEL_RE.match(lines[index + 2])
        and _POSTAL_HINT_RE.search(lines[index + 2]) is not None
    ):
        address_parts.append(lines[index + 2].strip(" .,:;\t\r\n"))
    return [part for part in address_parts if part]


def _build_owner_address_candidate(lines: list[str], index: int) -> str:
    address_parts = [lines[index + 1].strip(" .,:;\t\r\n")]
    tail_index = index + 2
    tail_limit = min(len(lines), index + 5)
    while tail_index < tail_limit:
        tail_line = lines[tail_index]
        if _SIMPLE_FIELD_LABEL_RE.match(tail_line) is not None:
            break
        tail_clean = tail_line.strip(" .,:;\t\r\n")
        if not tail_clean or re.match(r"^\s*-\s*\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}", tail_line):
            break
        if _OWNER_NAME_LIKE_LINE_RE.match(tail_clean) is not None:
            break
        locality_tail = tail_clean.casefold().strip(" .,:;\t\r\n")
        is_postal_like = _POSTAL_HINT_RE.search(tail_clean) is not None
        is_locality_like = _OWNER_LOCALITY_LINE_RE.fullmatch(tail_clean) is not None
        if locality_tail in _OWNER_LOCALITY_SECTION_BLACKLIST or not (
            is_postal_like or is_locality_like
        ):
            break
        address_parts.append(tail_clean)
        tail_index += 1
    return " ".join(part for part in address_parts if part)


def _pet_name_stopwords() -> set[str]:
    stopwords_upper = {
        "DATOS",
        "CLIENTE",
        "NOMBRE",
        "ESPECIE",
        "RAZA",
        "SEXO",
        "CHIP",
        "HISTORIAL",
        "VISITA",
    }
    extended = stopwords_upper | {
        "nº chip",
        "n° chip",
        "no chip",
        "nº historial",
        "fecha",
        "paciente",
        "propietario",
        "propietaria",
        "veterinario",
        "veterinaria",
        "diagnóstico",
        "diagnostico",
        "tratamiento",
        "medicación",
        "medicacion",
        "vacunación",
        "vacunacion",
    }
    return {_WHITESPACE_PATTERN.sub(" ", word).strip().casefold() for word in extended}
