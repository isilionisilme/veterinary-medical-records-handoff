"""Regex patterns local to candidate mining heuristics."""

from __future__ import annotations

import re

from .constants import _OWNER_CONTEXT_PATTERN

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
_CLINIC_ADDRESS_LABEL_LINE_RE = re.compile(
    r"(?i)^\s*(?:(?:centro|cl[ií]nica|hospital)(?:\s+veterinari[oa])?\s*/\s*)?"
    r"(direcci[oó]n(?:\s+de\s+la\s+cl[ií]nica)?|"
    r"domicilio(?:\s+de\s+la\s+cl[ií]nica)?|dir\.?)\s*(?:[:\-]\s*(.*))?$"
)
_AMBIGUOUS_ADDRESS_LABEL_LINE_RE = re.compile(
    r"(?i)^\s*(?:direcci[oó]n|domicilio|dir\.?)\s*(?:[:\-]\s*(.*))?$"
)
_OWNER_ADDRESS_LABEL_LINE_RE = re.compile(
    r"(?i)^\s*(?:direcci[oó]n\s+del\s+(?:propietari[oa]|titular)|"
    r"domicilio\s+del\s+(?:propietari[oa]|titular)|"
    r"dir\.?\s*(?:propietari[oa]|titular))\s*(?:[:\-]\s*(.*))?$"
)
_CLINIC_ADDRESS_START_RE = re.compile(
    r"(?i)(?:^|\s)(?:c/\s*|calle\b|avda?\.?\b|avenida\b|plaza\b|"
    r"pza\.?\b|paseo\b|camino\b|carretera\b|ctra\.?\b)"
)
_CLINIC_OR_HOSPITAL_CONTEXT_RE = re.compile(
    r"(?i)\b(?:cl[ií]nica|centro|hospital|veterinari[oa]|vet)\b"
)
_OWNER_CONTEXT_RE = _OWNER_CONTEXT_PATTERN
_OWNER_ADDRESS_CONTEXT_RE = re.compile(
    r"(?i)\b(?:propietari[oa]|titular|dueñ(?:o|a)|owner|tutor|"
    r"datos\s+del\s+cliente|cliente)\b"
)
_OWNER_HEADER_RE = re.compile(r"(?i)\b(?:propietari[oa]|titular|dueñ(?:o|a)|owner|cliente|tutor)\b")
_OWNER_NAME_LIKE_LINE_RE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.-]*(?:\s+"
    r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.-]*){1,4}$"
)
_OWNER_LOCALITY_LINE_RE = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s'\.-]{1,40}$")
_OWNER_LOCALITY_SECTION_BLACKLIST = {
    "historial",
    "plan",
    "exploracion",
    "exploración",
    "tratamiento",
    "diagnostico",
    "diagnóstico",
}
_OWNER_BLOCK_IDENTIFICATION_CONTEXT_RE = re.compile(
    r"(?i)\b(?:n[º°o]\s*chip|chip|microchip|paciente|mascota|especie|raza|sexo)\b"
)
_CLINIC_ADDRESS_CONTEXT_RE = re.compile(
    r"(?i)\b(?:cl[ií]nica|hospital|centro\s+veterinario|"
    r"veterinari[oa]|vet\b|dr\.?|dra\.?|doctor(?:a)?)\b"
)
_POSTAL_HINT_RE = re.compile(r"(?i)\b(?:cp\b|c[oó]digo\s+postal|\d{5})\b")
_SIMPLE_FIELD_LABEL_RE = re.compile(r"^[^\n]{1,40}\s*[:\-]\s*")
_HEADER_BLOCK_SCAN_WINDOW = 8
_AMBIGUOUS_ADDRESS_CONTEXT_WINDOW_LINES = 5
_WEIGHT_EXPLICIT_CONTEXT_RE = re.compile(
    r"(?i)\b(?:peso(?:\s+corporal)?|weight|signos?\s+vitales|p\.(?!\s*ej\.?\b))\b"
)
_WEIGHT_DOSAGE_GUARD_RE = re.compile(r"(?i)\b(?:ml|mg)\s*/\s*kg\b")
_WEIGHT_LAB_GUARD_RE = re.compile(r"(?i)\b(?:mg\s*/\s*dL|mmol\s*/\s*L|U\s*/\s*L)\b")
_WEIGHT_PRICE_GUARD_RE = re.compile(r"(?i)(?:\$|\u20ac|\bEUR\b)")
_WEIGHT_MED_OR_LAB_CONTEXT_RE = re.compile(
    r"(?i)\b(?:dosis|tratamiento|medicaci[oó]n|prescripci[oó]n|amoxic|clavul|"
    r"predni|omepra|anal[ií]tica|laboratorio|hemograma|bioqu[ií]mica|glucosa|"
    r"urea|creatinina|mg\s*/\s*kg|ml\s*/\s*kg|mg\s*/\s*dL|mmol\s*/\s*L|U\s*/\s*L)\b"
)
_WEIGHT_STANDALONE_LINE_RE = re.compile(
    r"^\s*(?:peso|pv|p\.)?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(kg|kgs|g)\.?\s*$",
    re.IGNORECASE,
)
_VISIT_TIMELINE_CONTEXT_RE = re.compile(
    r"(?i)\b(?:visita|consulta|control|seguimiento|ingreso|alta)\b"
)
