"""Candidate mining: text -> structured candidate extraction for interpretation."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping

from backend.app.application.field_normalizers import SPECIES_TOKEN_TO_CANONICAL
from backend.app.application.global_schema import GLOBAL_SCHEMA_KEYS, REPEATABLE_KEYS

from .constants import (
    _ADDRESS_LIKE_PATTERN,
    _MICROCHIP_DIGITS_PATTERN,
    _VET_OR_CLINIC_CONTEXT_PATTERN,
    _WHITESPACE_PATTERN,
    COVERAGE_CONFIDENCE_FALLBACK,
    COVERAGE_CONFIDENCE_LABEL,
    DATE_TARGET_KEYS,
)
from .date_parsing import (
    _normalize_person_fragment,
    _split_owner_before_address_tokens,
    extract_clinical_record_candidates,
    extract_date_candidates_with_classification,
    extract_labeled_person_candidates,
    extract_microchip_keyword_candidates,
    extract_ocr_microchip_candidates,
    extract_owner_nombre_candidates,
    extract_regex_labeled_candidates,
    extract_timeline_document_date_candidates,
    extract_unanchored_document_date_candidates,
)

# Guard pattern for unlabeled pet_name heuristic — rejects lines that look
# like addresses, phone numbers, license plates, or numeric IDs.
_PET_NAME_GUARD_RE = re.compile(
    r"\d{3,}|^[A-Z]{2,3}\d|calle|avda|portal|telf|tel[eé]f|c/|direc",
    re.IGNORECASE,
)
_PET_NAME_BIRTHLINE_RE = re.compile(
    r"^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\-\s]{1,40}?)\s*[-–—]\s*"
    r"(?:nacimiento|nac\.?|dob|birth(?:\s*date)?)\b",
    re.IGNORECASE,
)
_CLINIC_CONTEXT_LINE_RE = re.compile(
    r"(?i)\b(?:en\s+el|en\s+la)\s+"
    r"(centr[o0]|cl[ií]nica|hospital(?:\s+veterinari[oa])?)\s+"
    r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9][^\n,;]{2,100})"
)
_CLINIC_STANDALONE_LINE_RE = re.compile(
    r"(?i)^\s*(hv|h\.?\s*v\.?|hospital(?:\s+veterinari[oa])?|"
    r"centro(?:\s+veterinari[oa])?|cl[ií]nica(?:\s+veterinari[oa])?)\s+"
    r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9][^\n,;:]{2,100})\s*$"
)
_CLINIC_HEADER_ADDRESS_CONTEXT_RE = re.compile(
    r"(?i)\b(?:avda?\.?|avenida|calle|c/|portal|piso|puerta|codigo\s+postal|cp\b)\b"
)
_CLINIC_HEADER_SECTION_CONTEXT_RE = re.compile(
    r"(?i)\b(?:datos\s+de\s+la\s+mascota|datos\s+del\s+cliente|especie|raza|n[º°o]\s*chip)\b"
)
_CLINIC_HEADER_GENERIC_BLACKLIST = {
    "HISTORIAL",
    "INFORME",
    "FICHA",
}


def _mine_interpretation_candidates(raw_text: str) -> dict[str, list[dict[str, object]]]:
    compact_text = _WHITESPACE_PATTERN.sub(" ", raw_text).strip()
    candidates: dict[str, list[dict[str, object]]] = defaultdict(list)
    seen_values: dict[str, set[str]] = defaultdict(set)

    def add_candidate(
        *,
        key: str,
        value: str,
        confidence: float,
        snippet: str,
        page: int | None = 1,
        anchor: str | None = None,
        anchor_priority: int = 0,
        target_reason: str | None = None,
    ) -> None:
        cleaned_value = value.strip(" .,:;\t\r\n")
        if not cleaned_value:
            return
        if key == "microchip_id":
            digit_match = _MICROCHIP_DIGITS_PATTERN.search(cleaned_value)
            if digit_match is None:
                return
            cleaned_value = digit_match.group(1)
        if key == "owner_name":
            cleaned_value = _split_owner_before_address_tokens(cleaned_value)
            normalized_person = _normalize_person_fragment(cleaned_value)
            if normalized_person is None:
                return
            cleaned_value = normalized_person
            if _VET_OR_CLINIC_CONTEXT_PATTERN.search(snippet) is not None:
                return
        if key == "vet_name":
            normalized_person = _normalize_person_fragment(cleaned_value)
            if normalized_person is None:
                return
            if _ADDRESS_LIKE_PATTERN.search(normalized_person):
                return
            cleaned_value = normalized_person
        if key == "clinic_name":
            snippet_folded = snippet.casefold()
            if "dirección" in snippet_folded or "direccion" in snippet_folded:
                return
            if "domicilio" in snippet_folded:
                return
            compact_clinic = cleaned_value.casefold()
            if _ADDRESS_LIKE_PATTERN.search(compact_clinic) and re.search(r"\d", compact_clinic):
                return

        normalized_key = cleaned_value.casefold()
        if normalized_key in seen_values[key]:
            return
        seen_values[key].add(normalized_key)

        effective_confidence = (
            COVERAGE_CONFIDENCE_LABEL
            if confidence >= COVERAGE_CONFIDENCE_LABEL
            else COVERAGE_CONFIDENCE_FALLBACK
        )
        candidates[key].append(
            {
                "value": cleaned_value,
                "confidence": round(min(max(effective_confidence, 0.0), 1.0), 2),
                "anchor": anchor,
                "anchor_priority": anchor_priority,
                "target_reason": target_reason,
                "evidence": {
                    "page": page,
                    "snippet": snippet.strip()[:220],
                },
            }
        )

    def add_basic_payloads(payloads: list[dict[str, object]]) -> None:
        for payload in payloads:
            add_candidate(
                key=str(payload["key"]),
                value=str(payload["value"]),
                confidence=float(payload["confidence"]),
                snippet=str(payload["snippet"]),
            )

    for payloads in (
        extract_labeled_person_candidates(raw_text, confidence=COVERAGE_CONFIDENCE_LABEL),
        extract_owner_nombre_candidates(raw_text, confidence=COVERAGE_CONFIDENCE_LABEL),
        extract_regex_labeled_candidates(raw_text),
        extract_microchip_keyword_candidates(raw_text, confidence=COVERAGE_CONFIDENCE_LABEL),
        extract_clinical_record_candidates(raw_text, confidence=COVERAGE_CONFIDENCE_LABEL),
        extract_ocr_microchip_candidates(raw_text, confidence=COVERAGE_CONFIDENCE_FALLBACK),
        extract_unanchored_document_date_candidates(
            raw_text,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
        ),
    ):
        add_basic_payloads(payloads)

    for date_candidate in extract_date_candidates_with_classification(raw_text):
        add_candidate(
            key=str(date_candidate["target_key"]),
            value=str(date_candidate["value"]),
            confidence=float(date_candidate["confidence"]),
            snippet=str(date_candidate["snippet"]),
            page=1,
            anchor=(str(date_candidate["anchor"]) if date_candidate.get("anchor") else None),
            anchor_priority=int(date_candidate["anchor_priority"]),
            target_reason=str(date_candidate["target_reason"]),
        )

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    species_keywords = SPECIES_TOKEN_TO_CANONICAL
    breed_keywords = (
        "labrador",
        "retriever",
        "bulldog",
        "pastor",
        "yorkshire",
        "mestiz",
        "beagle",
        "caniche",
    )
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
    # Case-insensitive set for the relaxed (title-case) pet_name heuristic.
    _pet_name_stop_lower = stopwords_upper | {
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
    _pet_name_stop_lower = {s.casefold() for s in _pet_name_stop_lower}

    if lines:
        clinic_header = lines[0]
        clinic_header_folded = clinic_header.casefold()
        has_numeric = re.search(r"\d", clinic_header) is not None
        header_looks_institutional = (
            clinic_header.isupper()
            and 3 <= len(clinic_header) <= 60
            and ":" not in clinic_header
            and not has_numeric
            and "-" not in clinic_header
            and clinic_header not in _CLINIC_HEADER_GENERIC_BLACKLIST
            and clinic_header_folded not in _pet_name_stop_lower
        )
        if header_looks_institutional:
            context_lines = lines[1:8]
            context_compact = " ".join(context_lines)
            has_address_context = (
                _CLINIC_HEADER_ADDRESS_CONTEXT_RE.search(context_compact) is not None
                or re.search(r"\b\d{5}\b", context_compact) is not None
            )
            has_section_context = (
                _CLINIC_HEADER_SECTION_CONTEXT_RE.search(context_compact) is not None
            )
            if has_address_context and has_section_context:
                add_candidate(
                    key="clinic_name",
                    value=clinic_header,
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet="\n".join(lines[:4]),
                )

    for line in lines:
        if ":" in line:
            header, value = line.split(":", 1)
        elif "-" in line:
            header, value = line.split("-", 1)
        else:
            header, value = "", ""

        lower_header = header.casefold()
        if value:
            if any(token in lower_header for token in ("diagn", "impresi")):
                add_candidate(
                    key="diagnosis",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(token in lower_header for token in ("trat", "medic", "prescrip", "receta")):
                add_candidate(
                    key="medication",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
                add_candidate(key="treatment_plan", value=value, confidence=0.7, snippet=line)
            if any(token in lower_header for token in ("proced", "interv", "cirug", "quir")):
                add_candidate(
                    key="procedure",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(token in lower_header for token in ("sintom", "symptom")):
                add_candidate(
                    key="symptoms",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(token in lower_header for token in ("vacun", "vaccin")):
                add_candidate(
                    key="vaccinations",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(token in lower_header for token in ("laboratorio", "analit", "lab")):
                add_candidate(
                    key="lab_result",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(
                token in lower_header for token in ("radiograf", "ecograf", "imagen", "tac", "rm")
            ):
                add_candidate(
                    key="imaging",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )
            if any(token in lower_header for token in ("linea", "concepto", "item")):
                add_candidate(
                    key="line_item",
                    value=value,
                    confidence=COVERAGE_CONFIDENCE_LABEL,
                    snippet=line,
                )

        lower_line = line.casefold()
        if any(token in lower_line for token in ("macho", "hembra", "male", "female")):
            if "macho" in lower_line or "male" in lower_line:
                add_candidate(
                    key="sex",
                    value="macho",
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet=line,
                )
            if "hembra" in lower_line or "female" in lower_line:
                add_candidate(
                    key="sex",
                    value="hembra",
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet=line,
                )

        if any(token in lower_line for token in ("diagn", "impresi")) and ":" not in line:
            add_candidate(key="diagnosis", value=line, confidence=0.64, snippet=line)
        if any(
            token in lower_line
            for token in (
                "amoxic",
                "clavul",
                "predni",
                "omepra",
                "antibiot",
                "mg",
                "cada",
            )
        ):
            add_candidate(
                key="medication",
                value=line,
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )
        if any(
            token in lower_line
            for token in ("cirug", "proced", "sut", "cura", "ecograf", "radiograf")
        ):
            add_candidate(
                key="procedure",
                value=line,
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )

    for payload in extract_timeline_document_date_candidates(
        lines,
        confidence=COVERAGE_CONFIDENCE_FALLBACK,
    ):
        add_candidate(
            key=str(payload["key"]),
            value=str(payload["value"]),
            confidence=float(payload["confidence"]),
            snippet=str(payload["snippet"]),
            target_reason=str(payload["target_reason"]),
        )

    for index, line in enumerate(lines):
        lower_line = line.casefold()
        normalized_single = _WHITESPACE_PATTERN.sub(" ", lower_line).strip()

        clinic_context_match = _CLINIC_CONTEXT_LINE_RE.search(line)
        if clinic_context_match is not None:
            institution_token = clinic_context_match.group(1)
            institution_name = clinic_context_match.group(2).strip(" .,:;\t\r\n")
            canonical_institution = (
                "Centro" if institution_token.casefold() == "centr0" else institution_token
            )
            clinic_candidate = f"{canonical_institution} {institution_name}".strip()
            add_candidate(
                key="clinic_name",
                value=clinic_candidate,
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )

        clinic_standalone_match = _CLINIC_STANDALONE_LINE_RE.match(line)
        if clinic_standalone_match is not None:
            institution_token = clinic_standalone_match.group(1).strip()
            institution_name = clinic_standalone_match.group(2).strip(" .,:;\t\r\n")
            lowered_name = institution_name.casefold()
            if not lowered_name.startswith("de "):
                canonical_institution = institution_token
                if re.fullmatch(r"(?i)h\.?\s*v\.?", institution_token):
                    canonical_institution = "HV"
                clinic_candidate = f"{canonical_institution} {institution_name}".strip()
                add_candidate(
                    key="clinic_name",
                    value=clinic_candidate,
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet=line,
                )

        birthline_match = _PET_NAME_BIRTHLINE_RE.match(line)
        if birthline_match:
            candidate_name = _WHITESPACE_PATTERN.sub(" ", birthline_match.group(1)).strip()
            token_count = len(candidate_name.split())
            if (
                1 <= token_count <= 3
                and candidate_name.casefold() not in _pet_name_stop_lower
                and not _PET_NAME_GUARD_RE.search(candidate_name)
            ):
                nearby = " ".join(lines[index : min(len(lines), index + 4)]).casefold()
                if any(
                    token in nearby
                    for token in (
                        "canino",
                        "felino",
                        "raza",
                        "chip",
                        "especie",
                        "nacimiento",
                        "nac",
                    )
                ):
                    add_candidate(
                        key="pet_name",
                        value=candidate_name,
                        confidence=COVERAGE_CONFIDENCE_FALLBACK,
                        snippet=line,
                    )

        if normalized_single in species_keywords:
            add_candidate(
                key="species",
                value=species_keywords[normalized_single],
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )

        if any(keyword in lower_line for keyword in breed_keywords) and len(line) <= 80:
            add_candidate(
                key="breed",
                value=line,
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )

        if normalized_single in {"m", "macho", "male", "h", "hembra", "female"}:
            window = " ".join(lines[max(0, index - 1) : min(len(lines), index + 2)]).casefold()
            if "sexo" in window:
                sex_value = "macho" if normalized_single in {"m", "macho", "male"} else "hembra"
                add_candidate(
                    key="sex",
                    value=sex_value,
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet=" ".join(lines[max(0, index - 1) : min(len(lines), index + 2)]),
                )

        # ── pet_name unlabeled heuristic ──────────────────────────────
        # Accept lines that look like a standalone pet name (title-case or
        # uppercase, 1-3 tokens, near species/chip/breed context).  Guard
        # against addresses, phones, license numbers, section headers,
        # and labeled fields (lines with ':' or '-' separators).
        word_count = len(line.split())
        is_name_like = (
            2 < len(line) <= 40
            and 1 <= word_count <= 3
            and line not in stopwords_upper
            and line.casefold() not in _pet_name_stop_lower
            and (line.isupper() or line.istitle())
            and ":" not in line
            and not _PET_NAME_GUARD_RE.search(line)
        )
        if is_name_like:
            nearby = " ".join(lines[index : min(len(lines), index + 4)]).casefold()
            if any(token in nearby for token in ("canino", "felino", "raza", "chip", "especie")):
                add_candidate(
                    key="pet_name",
                    value=line.title(),
                    confidence=COVERAGE_CONFIDENCE_FALLBACK,
                    snippet=line,
                )

    if (
        compact_text
        and "language" not in candidates
        and any(
            token in compact_text.casefold() for token in ("paciente", "diagnost", "tratamiento")
        )
    ):
        add_candidate(
            key="language",
            value="es",
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet="Heuristic language inference based on Spanish clinical tokens",
            page=None,
        )

    return dict(candidates)


def _map_candidates_to_global_schema(
    candidate_bundle: Mapping[str, list[dict[str, object]]],
) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    mapped: dict[str, object] = {}
    evidence_map: dict[str, list[dict[str, object]]] = {}

    for key in GLOBAL_SCHEMA_KEYS:
        key_candidates = sorted(
            candidate_bundle.get(key, []),
            key=lambda item: _candidate_sort_key(item, key),
            reverse=True,
        )

        if key in REPEATABLE_KEYS:
            selected = key_candidates[:3]
            mapped[key] = [
                str(item.get("value", "")).strip()
                for item in selected
                if str(item.get("value", "")).strip()
            ]
            evidence_map[key] = selected
            continue

        if key_candidates:
            top = key_candidates[0]
            mapped[key] = str(top.get("value", "")).strip() or None
            evidence_map[key] = [top]
        else:
            mapped[key] = None
            evidence_map[key] = []

    return mapped, evidence_map


def _candidate_sort_key(item: dict[str, object], key: str) -> tuple[float, float]:
    confidence = float(item.get("confidence", 0.0))
    if key in DATE_TARGET_KEYS:
        return float(item.get("anchor_priority", 0)), confidence

    if key == "microchip_id":
        raw_value = str(item.get("value", "")).strip()
        if _MICROCHIP_DIGITS_PATTERN.fullmatch(raw_value):
            return 2.0, confidence
        if _MICROCHIP_DIGITS_PATTERN.search(raw_value):
            return 1.0, confidence
        return 0.0, confidence

    if key == "pet_name":
        raw_value = str(item.get("value", "")).strip()
        # Prefer candidates that look like real names: alphabetic, 2-40 chars,
        # no digits, no field-label patterns.  This gives labeled matches with
        # clean values an edge over noisy heuristic guesses without changing
        # the global confidence clamp.
        is_clean = bool(
            raw_value
            and not re.search(r"\d", raw_value)
            and not re.search(r"(?i)^(?:especie|raza|sexo|chip|fecha)", raw_value)
            and 2 <= len(raw_value) <= 40
        )
        return (1.0 if is_clean else 0.0), confidence

    if key == "clinic_name":
        raw_value = str(item.get("value", "")).strip()
        lower_value = raw_value.casefold()
        has_hv_abbrev = bool(re.search(r"\bh\.?\s*v\.?\b", lower_value))
        has_clinic_token = bool(
            re.search(
                r"\b(?:cl[ií]nic|veterinari|hospital|centro|vet|h\.?\s*v\.?)\b",
                lower_value,
            )
        )
        looks_address_like = bool(_ADDRESS_LIKE_PATTERN.search(lower_value)) and bool(
            re.search(r"\d", lower_value)
        )
        if has_hv_abbrev and not looks_address_like:
            return 3.0, confidence
        if has_clinic_token and not looks_address_like:
            return 2.0, confidence
        if has_clinic_token:
            return 1.0, confidence
        return 0.0, confidence

    return 0.0, confidence
