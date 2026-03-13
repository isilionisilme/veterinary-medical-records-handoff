"""Shared constants for processing modules."""

from __future__ import annotations

import re

_NAME_TOKEN_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.-]*$")

PROCESSING_TICK_SECONDS = 0.5
PROCESSING_TIMEOUT_SECONDS = 120.0
MAX_RUNS_PER_TICK = 10
# Legacy compatibility exports (tests/import shims); runtime reads are centralized in settings.py.
PDF_EXTRACTOR_FORCE_ENV = "PDF_EXTRACTOR_FORCE"
INTERPRETATION_DEBUG_INCLUDE_CANDIDATES_ENV = "VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES"
COVERAGE_CONFIDENCE_LABEL = 0.66
COVERAGE_CONFIDENCE_FALLBACK = 0.50
COVERAGE_CONFIDENCE_ENRICHMENT = 0.40
MVP_COVERAGE_DEBUG_KEYS: tuple[str, ...] = (
    "microchip_id",
    "clinical_record_number",
    "pet_name",
    "species",
    "breed",
    "sex",
    "dob",
    "weight",
    "visit_date",
    "owner_name",
    "owner_address",
    "diagnosis",
    "procedure",
    "medication",
    "reason_for_visit",
    "symptoms",
    "treatment_plan",
    "clinic_address",
    "clinic_name",
    "coat_color",
    "hair_length",
    "repro_status",
)
DATE_TARGET_KEYS = frozenset(
    {"visit_date", "document_date", "admission_date", "discharge_date", "dob"}
)
_DATE_CANDIDATE_PATTERN = re.compile(
    r"\b(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2})\b"
)
_DATE_TARGET_ANCHORS: dict[str, tuple[str, ...]] = {
    "visit_date": (
        "visita",
        "consulta",
        "revision",
        "revisión",
        "control",
        "urgencia",
    ),
    "document_date": (
        "fecha documento",
        "documento",
        "informe",
        "historial",
        "fecha",
    ),
    "admission_date": ("admisión", "admision", "ingreso", "hospitaliza"),
    "discharge_date": ("alta", "egreso"),
    "dob": (
        "nacimiento",
        "nac.",
        "nac",
        "f. nac",
        "f/nto",
        "fnto",
        "dob",
        "birth",
        "fecha de nacimiento",
        "fecha nac",
    ),
}
_DATE_TARGET_PRIORITY: dict[str, int] = {
    "visit_date": 4,
    "admission_date": 3,
    "discharge_date": 3,
    "document_date": 2,
    "dob": 1,
}
_MICROCHIP_KEYWORD_WINDOW_PATTERN = re.compile(
    r"(?is)(?:microchip|micr0chip|chip|transponder|identificaci[oó]n\s+electr[oó]nica|"
    r"n[ºo°\uFFFD]\s*chip)\s*(?:n[ºo°\uFFFD]\.?|nro\.?|id)?\s*[:\-]?\s*([^\n]{0,90})"
)
_MICROCHIP_DIGITS_PATTERN = re.compile(r"(?<!\d)(\d{9,15})(?!\d)")
_MICROCHIP_OCR_PREFIX_WINDOW_PATTERN = re.compile(
    r"(?is)\bn(?:[º°\uFFFD]|ro)?\.?\s*[:\-]\s*([^\n]{0,60})"
)
_VET_LABEL_LINE_PATTERN = re.compile(
    r"(?i)^\s*(?:veterinari(?:o|a|o/a)|vet|dr\.?|dra\.?|dr/a|doctor|doctora)\b\s*[:\-]?\s*(.*)$"
)
_OWNER_LABEL_LINE_PATTERN = re.compile(
    r"(?i)^\s*(?:propietari(?:o|a)|titular|dueñ(?:o|a)|owner)\b\s*[:\-]?\s*(.*)$"
)
_OWNER_NOMBRE_LINE_PATTERN = re.compile(r"(?i)^\s*nombre\s*(?::|-)?\s*(.*)$")
_OWNER_CLIENT_HEADER_LINE_PATTERN = re.compile(r"(?i)^\s*datos\s+del\s+cliente\s*$")
_OWNER_CLIENT_TABULAR_LABEL_LINE_PATTERN = re.compile(
    r"(?i)^\s*(?:especie|raza|f/?nto|capa|n[º°o]?\s*chip)\s*$"
)
_OWNER_INLINE_CONTEXT_WINDOW_LINES = 2
_OWNER_HEADER_LOOKBACK_LINES = 8
_OWNER_TABULAR_FORWARD_SCAN_LINES = 8
_ADDRESS_SPLIT_PATTERN = re.compile(
    r"(?i)\b(?:c/|calle|av\.?|avenida|cp\b|n[º°o]\.?|num\.?|número|plaza|pte\.?|portal|piso|puerta)\b"
)
_ADDRESS_LIKE_PATTERN = re.compile(
    r"(?i)(?:\b(?:c/|calle|av\.?|avenida|cp\b|portal|piso|puerta)\b|\d+\s*(?:[,\-]|$))"
)
_PHONE_LIKE_PATTERN = re.compile(r"\+?\d[\d\s().-]{6,}")
_LICENSE_ONLY_PATTERN = re.compile(
    r"(?i)^\s*(?:col(?:egiad[oa])?\.?|n[º°o]?\s*col\.?|lic(?:encia)?\.?|cmp\.?|nif\b|dni\b)\s*[:\-]?\s*[A-Za-z0-9\-./\s]{3,}$"
)
_OWNER_CONTEXT_PATTERN = re.compile(
    r"(?i)\b(?:propietari(?:o|a)|titular|dueñ(?:o|a)|owner|tutor)\b"
)
_OWNER_PATIENT_LABEL_PATTERN = re.compile(r"(?i)\bpaciente\b\s*[:\-]")
_VET_OR_CLINIC_CONTEXT_PATTERN = re.compile(
    r"(?i)\b(?:veterinari[oa]|vet\b|doctor(?:a)?\b|dra\.?\b|dr\.?\b|cl[ií]nica|hospital|centro\s+veterinario)\b"
)
_CLINICAL_RECORD_GUARD_PATTERN = re.compile(r"(?i)\b(?:\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})\b")
NUMERIC_TYPES = (int, float)
REVIEW_SCHEMA_CONTRACT = "visit-grouped-canonical"
_WHITESPACE_PATTERN = re.compile(r"\s+")

_LABELED_PATTERNS: tuple[tuple[str, str, float], ...] = (
    (
        "pet_name",
        r"(?:paciente|nombre(?:\s+del\s+(?:paciente|animal))?|patient|animal|mascota|"
        r"nombre\s+mascota)\s*[:\-|][ \t]*(?:\n[ \t]*)?([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][^\n;|]{1,99})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "species",
        r"(?:especie\s*/\s*raza|raza\s*/\s*especie)\s*[:\-]\s*([^\n;]{2,120})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "breed",
        r"(?:especie\s*/\s*raza|raza\s*/\s*especie)\s*[:\-]\s*([^\n;]{2,120})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    ("species", r"(?:especie|species)\s*[:\-]\s*([^\n;]{2,80})", COVERAGE_CONFIDENCE_LABEL),
    ("breed", r"(?:raza|breed)\s*[:\-]\s*([^\n;]{2,80})", COVERAGE_CONFIDENCE_LABEL),
    ("sex", r"(?:sexo|sex)\s*[:\-]\s*([^\n;]{1,40})", COVERAGE_CONFIDENCE_LABEL),
    ("age", r"(?:edad|age)\s*[:\-]\s*([^\n;]{1,60})", COVERAGE_CONFIDENCE_LABEL),
    (
        "dob",
        r"(?:f\.\s*nac\.?|fcha\s+(?:de\s+)?nacimiento|f(?:echa)?\s*(?:de\s*)?(?:nacimiento|nac\.?|nac|nto)|f[\/\s]?nto|fnto|nacimiento|dob|birth\s*date|fecha\s*nac)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[0-9]{4}[\/\-.][0-9]{1,2}[\/\-.][0-9]{1,2})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "weight",
        r"(?:peso(?:\s+corporal)?|weight|peso\s*\(\s*kg\s*\)|p\.(?!\s*ej\.?\b))\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?\s*(?:kg|kgs|g)?)",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "weight",
        r"(?is)(?:signos?\s+vitales\s*[:\-]?\s*(?:\n\s*)?)(?:peso(?:\s+corporal)?|weight|p\.(?!\s*ej\.?\b))?\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?\s*(?:kg|kgs|g)\b)",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "weight",
        r"(?is)(?:datos\s+de\s+la\s+mascota|datos\s+del\s+paciente|paciente|mascota|especie|raza|sexo|n[º°o]?\s*chip)\b[^\n]{0,90}?([0-9]+(?:[\.,][0-9]+)?\s*(?:kg|kgs|g)\b)",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "microchip_id",
        r"(?:microchip|micr0chip|chip|transponder|identificaci[oó]n\s+electr[oó]nica)\s*(?:n[ºo°\uFFFD]\.?|nro\.?|id)?\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9./_\-]{1,30}(?:\s+[A-Za-z0-9][A-Za-z0-9./_\-]{0,20}){0,3})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "clinical_record_number",
        r"(?:nhc|n[ºo°]?\s*(?:historial|historia\s*cl[ií]nica)|historial\s*cl[ií]nico|n[uú]mero\s*de\s*historial)\s*[:\-]?\s*([A-Za-z0-9./_\-]{2,40})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "visit_date",
        r"(?:fecha\s+de\s+visita|visita|consulta|visit\s+date)\s*[:\-]\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "document_date",
        r"(?:fecha\s+documento|fecha|date)\s*[:\-]\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "clinic_name",
        (
            r"(?m)^\s*(?:cl[ií]nica|centro\s+veterinari[oa]|hospital\s+veterinari[oa]|"
            r"centr0\s+veterinari0)\s*[:\-|]\s*(?:\n\s*)?([^\n;]{3,120})"
        ),
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "clinic_address",
        r"(?:direcci[oó]n\s*(?:de\s*la\s*cl[ií]nica)?|domicilio\s*(?:de\s*la\s*cl[ií]nica)?)\s*[:\-]\s*([^\n;]{4,160})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "vet_name",
        r"(?:veterinari[oa]|dr\.?|dra\.?)\s*[:\-]\s*([^\n;]{3,120})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "owner_name",
        r"(?:propietari[oa]|tutor)\s*[:\-]\s*([^\n;]{3,120})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "owner_address",
        (
            r"(?:direcci[oó]n\s+del\s+(?:propietari[oa]|titular)|"
            r"domicilio\s+del\s+(?:propietari[oa]|titular)|"
            r"dir\.\s*(?:propietari[oa]|titular))\s*[:\-]\s*([^\n;]{4,160})"
        ),
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "coat_color",
        r"(?:capa|color\s*(?:del\s*(?:pelaje|pelo))?)\s*[:\-]\s*([^\n;]{2,100})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "hair_length",
        r"(?:pelo|longitud\s*del\s*pelo)\s*[:\-]\s*([^\n;]{2,100})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "repro_status",
        (
            r"(?:estado\s*reproductivo|repro(?:ductivo)?|esterilizad[oa]|"
            r"castrad[oa]|f[eé]rtil)\s*[:\-]\s*([^\n;]{2,80})"
        ),
        COVERAGE_CONFIDENCE_LABEL,
    ),
    (
        "reason_for_visit",
        r"(?:motivo(?:\s+de\s+consulta)?|reason\s+for\s+visit)\s*[:\-]\s*([^\n]{3,200})",
        COVERAGE_CONFIDENCE_LABEL,
    ),
)
