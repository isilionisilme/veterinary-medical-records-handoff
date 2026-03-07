from __future__ import annotations

import re
from datetime import datetime

NUMERIC_TYPES = (int, float)
_REVIEW_SCHEMA_CONTRACT_CANONICAL = "visit-grouped-canonical"

_MEDICAL_RECORD_CANONICAL_SECTIONS: tuple[str, ...] = (
    "clinic",
    "patient",
    "owner",
    "visits",
    "notes",
    "other",
    "report_info",
)

_MEDICAL_RECORD_CANONICAL_FIELD_SLOTS: tuple[dict[str, object], ...] = (
    {
        "concept_id": "clinic.name",
        "section": "clinic",
        "scope": "document",
        "canonical_key": "clinic_name",
        "label_key": "clinic_name",
    },
    {
        "concept_id": "clinic.address",
        "section": "clinic",
        "scope": "document",
        "canonical_key": "clinic_address",
        "label_key": "clinic_address",
    },
    {
        "concept_id": "clinic.vet_name",
        "section": "clinic",
        "scope": "document",
        "canonical_key": "vet_name",
        "label_key": "vet_name",
    },
    {
        "concept_id": "clinic.nhc",
        "section": "clinic",
        "scope": "document",
        "canonical_key": "nhc",
        "aliases": ["medical_record_number"],
        "label_key": "nhc",
    },
    {
        "concept_id": "patient.pet_name",
        "section": "patient",
        "scope": "document",
        "canonical_key": "pet_name",
        "label_key": "pet_name",
    },
    {
        "concept_id": "patient.species",
        "section": "patient",
        "scope": "document",
        "canonical_key": "species",
        "label_key": "species",
    },
    {
        "concept_id": "patient.breed",
        "section": "patient",
        "scope": "document",
        "canonical_key": "breed",
        "label_key": "breed",
    },
    {
        "concept_id": "patient.sex",
        "section": "patient",
        "scope": "document",
        "canonical_key": "sex",
        "label_key": "sex",
    },
    {
        "concept_id": "patient.age",
        "section": "patient",
        "scope": "document",
        "canonical_key": "age",
        "label_key": "age",
    },
    {
        "concept_id": "patient.dob",
        "section": "patient",
        "scope": "document",
        "canonical_key": "dob",
        "label_key": "dob",
    },
    {
        "concept_id": "patient.microchip_id",
        "section": "patient",
        "scope": "document",
        "canonical_key": "microchip_id",
        "label_key": "microchip_id",
    },
    {
        "concept_id": "patient.weight",
        "section": "patient",
        "scope": "document",
        "canonical_key": "weight",
        "label_key": "weight",
    },
    {
        "concept_id": "patient.reproductive_status",
        "section": "patient",
        "scope": "document",
        "canonical_key": "reproductive_status",
        "aliases": ["repro_status"],
        "label_key": "reproductive_status",
    },
    {
        "concept_id": "owner.name",
        "section": "owner",
        "scope": "document",
        "canonical_key": "owner_name",
        "label_key": "owner_name",
    },
    {
        "concept_id": "owner.address",
        "section": "owner",
        "scope": "document",
        "canonical_key": "owner_address",
        "aliases": ["owner_id"],
        "label_key": "owner_address",
    },
    {
        "concept_id": "notes.main",
        "section": "notes",
        "scope": "document",
        "canonical_key": "notes",
        "label_key": "notes",
    },
    {
        "concept_id": "report.language",
        "section": "report_info",
        "scope": "document",
        "canonical_key": "language",
        "label_key": "language",
    },
)

_VISIT_GROUP_METADATA_KEYS: tuple[str, ...] = (
    "visit_date",
    "admission_date",
    "discharge_date",
    "reason_for_visit",
)

_VISIT_SCOPED_KEYS: tuple[str, ...] = (
    "observations",
    "actions",
    "symptoms",
    "diagnosis",
    "procedure",
    "medication",
    "treatment_plan",
    "allergies",
    "vaccinations",
    "lab_result",
    "imaging",
    "weight",
)

_VISIT_GROUP_METADATA_KEY_SET = set(_VISIT_GROUP_METADATA_KEYS)
_VISIT_SCOPED_KEY_SET = set(_VISIT_SCOPED_KEYS)
_VISIT_DATE_TOKEN_PATTERN = re.compile(
    r"(?P<iso>\b\d{4}[-\/.]\d{1,2}[-\/.]\d{1,2}\b)|"
    r"(?P<dmy>\b\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}\b)",
    re.IGNORECASE,
)
_VISIT_CONTEXT_PATTERN = re.compile(
    r"\b(visita|consulta|control|revisi[oó]n|seguimiento|ingreso|alta)\b",
    re.IGNORECASE,
)
_VISIT_LABEL_CONTEXT_PATTERN = re.compile(
    r"\b(fecha\s+de\s+(visita|consulta|cita|atenci[oó]n|exploraci[oó]n|control))\b",
    re.IGNORECASE,
)
_VISIT_CLINICAL_CONTEXT_PATTERN = re.compile(
    r"\b(revisar|reevaluar|tratamiento|medicaci[oó]n|exploraci[oó]n|seguimiento)\b",
    re.IGNORECASE,
)
_VISIT_TIMELINE_LINE_PATTERN = re.compile(
    (
        r"^\s*[-*•]?\s*\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}"
        r"\s*[-–—]\s*\d{1,2}:\d{2}(?::\d{2})?"
        r"(?:\s*[-–—]\s*.*)?$"
    ),
    re.IGNORECASE,
)
_VISIT_DAY_LINE_PATTERN = re.compile(
    r"\bd[ií]a\s+\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}\b",
    re.IGNORECASE,
)
_NEXT_VISIT_BOUNDARY_PATTERN = re.compile(
    r"(?:\s*)?visita\s+(?:consulta\s+general|administrativa)\s+del\s+d[ií]a",
    re.IGNORECASE,
)
_NON_VISIT_DATE_CONTEXT_PATTERN = re.compile(
    (
        r"\b("
        r"nacimiento|dob|microchip|chip|factura|invoice|emisi[oó]n|"
        r"documento|dni|nif|pasaporte|id\b|identificaci[oó]n|"
        r"lote|referencia|presupuesto|an[aá]lisis|laboratorio|orina|"
        r"coprol[oó]gico|documentos?\s+pdf"
        r")\b"
    ),
    re.IGNORECASE,
)


def _normalize_visit_date_candidate(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    raw_value = value.strip()
    if not raw_value:
        return None

    candidates = [raw_value]
    for match in _VISIT_DATE_TOKEN_PATTERN.finditer(raw_value):
        token = match.group(0)
        if token:
            candidates.append(token)

    seen_tokens: set[str] = set()
    for candidate in candidates:
        token = candidate.strip()
        if not token:
            continue
        token_key = token.casefold()
        if token_key in seen_tokens:
            continue
        seen_tokens.add(token_key)

        normalized_token = token.replace("/", "-").replace(".", "-")
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y"):
            try:
                parsed = datetime.strptime(normalized_token, fmt)
            except ValueError:
                continue
            if fmt == "%d-%m-%y" and (parsed.year < 2000 or parsed.year > 2100):
                continue
            if parsed.year < 1900 or parsed.year > 2100:
                continue
            return parsed.date().isoformat()

    return None


def _extract_visit_date_candidates_from_text(*, text: object) -> list[str]:
    if not isinstance(text, str):
        return []

    snippet = text.strip()
    if not snippet:
        return []

    has_visit_context = _VISIT_CONTEXT_PATTERN.search(snippet) is not None
    has_non_visit_context = _NON_VISIT_DATE_CONTEXT_PATTERN.search(snippet) is not None
    if not has_visit_context or has_non_visit_context:
        return []

    dates: list[str] = []
    seen_dates: set[str] = set()
    for match in _VISIT_DATE_TOKEN_PATTERN.finditer(snippet):
        normalized_date = _normalize_visit_date_candidate(match.group(0))
        if normalized_date is None or normalized_date in seen_dates:
            continue
        seen_dates.add(normalized_date)
        dates.append(normalized_date)
    return dates


def _detect_visit_dates_from_raw_text(*, raw_text: object) -> list[str]:
    return [
        normalized_date
        for normalized_date, _ in _locate_visit_date_occurrences_from_raw_text(raw_text=raw_text)
    ]


def _locate_visit_date_occurrences_from_raw_text(*, raw_text: object) -> list[tuple[str, int]]:
    if not isinstance(raw_text, str):
        return []

    if not raw_text.strip():
        return []

    date_occurrences: list[tuple[str, int]] = []
    line_records: list[tuple[str, int]] = []
    cursor = 0
    for raw_line in raw_text.splitlines(keepends=True):
        line = raw_line.strip()
        line_records.append((line, cursor))
        cursor += len(raw_line)

    for index, (line, line_offset) in enumerate(line_records):
        if not line:
            continue

        previous_non_empty = ""
        for previous, _ in reversed(line_records[:index]):
            candidate = previous.strip()
            if candidate:
                previous_non_empty = candidate
                break

        has_non_visit_context = _NON_VISIT_DATE_CONTEXT_PATTERN.search(line) is not None
        is_timeline_line = _VISIT_TIMELINE_LINE_PATTERN.search(line) is not None
        has_visit_context = (
            _VISIT_CONTEXT_PATTERN.search(line) is not None
            or _VISIT_LABEL_CONTEXT_PATTERN.search(line) is not None
            or _VISIT_CLINICAL_CONTEXT_PATTERN.search(line) is not None
            or is_timeline_line
            or (
                _VISIT_DAY_LINE_PATTERN.search(line) is not None
                and _VISIT_CONTEXT_PATTERN.search(previous_non_empty) is not None
            )
        )

        if has_non_visit_context and not is_timeline_line:
            continue
        if not has_visit_context:
            continue

        for token_match in _VISIT_DATE_TOKEN_PATTERN.finditer(line):
            normalized_date = _normalize_visit_date_candidate(token_match.group(0))
            if normalized_date is None:
                continue
            date_occurrences.append((normalized_date, line_offset + token_match.start()))

    return date_occurrences


def _locate_visit_boundary_offsets_from_raw_text(*, raw_text: object) -> list[int]:
    if not isinstance(raw_text, str):
        return []

    if not raw_text.strip():
        return []

    return [match.start() for match in _NEXT_VISIT_BOUNDARY_PATTERN.finditer(raw_text)]


def _contains_any_date_token(*, text: object) -> bool:
    if not isinstance(text, str):
        return False
    return _VISIT_DATE_TOKEN_PATTERN.search(text) is not None


def _extract_evidence_snippet(field: dict[str, object]) -> str | None:
    evidence = field.get("evidence")
    if not isinstance(evidence, dict):
        return None
    snippet = evidence.get("snippet")
    return snippet if isinstance(snippet, str) else None
