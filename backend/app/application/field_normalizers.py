"""Deterministic canonical normalization for Global Schema fields."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import datetime

from backend.app.application.extraction_constants import (
    MICROCHIP_MAX_DIGITS,
    MICROCHIP_MIN_DIGITS,
    WEIGHT_MAX_KG,
    WEIGHT_MIN_KG,
)
from backend.app.application.species_breed_normalizers import (
    CANONICAL_SPECIES as CANONICAL_SPECIES,
)
from backend.app.application.species_breed_normalizers import (
    SPECIES_TOKEN_TO_CANONICAL as SPECIES_TOKEN_TO_CANONICAL,
)
from backend.app.application.species_breed_normalizers import (
    _normalize_species_and_breed_pair,
    _normalize_species_value,
)

_WHITESPACE_PATTERN = re.compile(r"\s+")
_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2})\b"
)
_MICROCHIP_DIGITS_PATTERN = re.compile(r"(?<!\d)(\d{9,15})(?!\d)")

_WEIGHT_PATTERN = re.compile(
    r"(?P<number>\d+(?:[.,]\d+)?)\s*(?P<unit>kg|kgs|g|gr)?\b",
    re.IGNORECASE,
)

# pet_name normalization helpers
_PET_NAME_TRAILING_NOISE = re.compile(
    r"\s*[-–—]\s*(?:nacimiento|nac\.?|dob|birth|f\.?\s*nac).*$",
    re.IGNORECASE,
)
_PET_NAME_NUMERIC_ONLY = re.compile(r"^\d+$")
_PET_NAME_LOOKS_LIKE_LABEL = re.compile(
    r"(?i)^(?:especie|raza|sexo|peso|edad|chip|fecha|breed|species|sex|age|weight)"
    r"\s*[:\-|]",
)
_CLINIC_NAME_LEADING_LABEL = re.compile(
    r"(?i)^(?:cl[ií]nica|centro\s+veterinari[oa]|hospital\s+veterinari[oa])\s*[:\-|]\s*"
)
_CLINIC_NAME_ADDRESS_LIKE = re.compile(
    r"(?i)\b(?:c/|calle|av\.?|avenida|cp\b|portal|piso|puerta|direcci[oó]n|domicilio)\b"
)
_CLINIC_ADDRESS_LEADING_LABEL = re.compile(
    r"(?i)^(?:direcci[oó]n(?:\s+de\s+la\s+cl[ií]nica)?|"
    r"domicilio(?:\s+de\s+la\s+cl[ií]nica)?|dir\.?)\s*[:\-]\s*"
)
_CLINIC_ADDRESS_ABBREVIATIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bc/\s*"), "Calle "),
    (re.compile(r"(?i)\bavda\.?(?=\s|$)"), "Avenida"),
    (re.compile(r"(?i)\bpza\.?(?=\s|$)"), "Plaza"),
    (re.compile(r"(?i)\bctra\.?(?=\s|$)"), "Carretera"),
    (re.compile(r"(?i)\bn[º°o]\.?(?=\s|\d)"), "Número"),
)
_OWNER_ADDRESS_LEADING_LABEL = re.compile(
    r"(?i)^(?:direcci[oó]n|domicilio|dir\.?)"
    r"(?:\s+(?:(?:de(?:l)?)\s+)?(?:propietari[oa]|titular))?\s*[:\-]?\s*"
)
_OWNER_ADDRESS_ABBREVIATIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bc/\s*"), "Calle "),
    (re.compile(r"(?i)\bavda\.?(?=\s|$)"), "Avenida"),
    (re.compile(r"(?i)\bav\.?(?=\s|$)"), "Avenida"),
    (re.compile(r"(?i)\bpza\.?(?=\s|$)"), "Plaza"),
    (re.compile(r"(?i)\bcp\b"), "C.P."),
)
_OWNER_ADDRESS_ADDRESS_TOKEN = re.compile(
    r"(?i)\b("
    r"calle|avenida|plaza|carretera|camino|paseo|barrio|urbanizaci[oó]n|"
    r"c\.?p\.?|codigo\s+postal|portal|piso|puerta|bloque|escalera|"
    r"km|kil[oó]metro|n[º°o]?|num(?:ero)?|c/"
    r")\b"
)
_OWNER_ADDRESS_RESIDUAL_LABEL = re.compile(
    r"(?i)\b(?:propietari[oa]|titular|cliente|nombre|tel[eé]fono|telefono|email|dni|nif)\b"
)


def normalize_canonical_fields(
    values: Mapping[str, object],
    evidence_map: Mapping[str, list[dict[str, object]]] | None = None,
    *,
    visits: Sequence[object] | None = None,
    derive_age: bool = False,
) -> dict[str, object]:
    """Normalize selected canonical fields without changing semantics."""

    normalized = dict(values)

    normalized["pet_name"] = _normalize_pet_name_value(normalized.get("pet_name"))
    normalized["clinic_name"] = _normalize_clinic_name_value(normalized.get("clinic_name"))
    normalized["clinic_address"] = _normalize_clinic_address_value(normalized.get("clinic_address"))
    normalized["owner_address"] = _normalize_owner_address_value(normalized.get("owner_address"))
    normalized["species"] = _normalize_species_value(normalized.get("species"))
    normalized["breed"] = _normalize_scalar_with_labels(normalized.get("breed"), ("raza", "breed"))
    normalized = _normalize_species_and_breed_pair(normalized, evidence_map)

    normalized["sex"] = _normalize_sex_value(normalized.get("sex"))
    normalized["microchip_id"] = _normalize_microchip_id(
        value=normalized.get("microchip_id"),
        evidence=(evidence_map.get("microchip_id") if evidence_map else None),
    )
    normalized["dob"] = _normalize_date_value(normalized.get("dob"))
    normalized["visit_date"] = _normalize_date_value(normalized.get("visit_date"))
    normalized["document_date"] = _normalize_date_value(normalized.get("document_date"))
    normalized["admission_date"] = _normalize_date_value(normalized.get("admission_date"))
    normalized["discharge_date"] = _normalize_date_value(normalized.get("discharge_date"))

    if derive_age:
        normalized = _derive_age_from_dob(normalized, visits=visits)

    return normalized


def _derive_age_from_dob(
    values: dict[str, object],
    *,
    visits: Sequence[object] | None,
) -> dict[str, object]:
    from backend.app.application.age_derivation import (
        calculate_age_in_years,
        resolve_reference_date,
    )

    normalized = dict(values)

    if _has_non_empty_value(normalized.get("age")):
        normalized.pop("age_origin", None)
        return normalized

    dob_value = normalized.get("dob")
    if not isinstance(dob_value, str) or not dob_value.strip():
        normalized.pop("age_origin", None)
        return normalized

    reference_date = resolve_reference_date(
        [visit for visit in visits or () if isinstance(visit, Mapping)],
        normalized.get("document_date")
        if isinstance(normalized.get("document_date"), str)
        else None,
    )
    if not isinstance(reference_date, str):
        normalized.pop("age_origin", None)
        return normalized

    derived_age = calculate_age_in_years(dob_value, reference_date)
    if derived_age is None:
        normalized.pop("age_origin", None)
        return normalized

    normalized["age"] = str(derived_age)
    normalized["age_origin"] = "derived"
    return normalized


def _has_non_empty_value(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return value not in (None, "")


def normalize_microchip_digits_only(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    match = _MICROCHIP_DIGITS_PATTERN.search(cleaned)
    if match is not None:
        return match.group(1)

    compact_digits = re.sub(r"\D", "", cleaned)
    if MICROCHIP_MIN_DIGITS <= len(compact_digits) <= MICROCHIP_MAX_DIGITS:
        return compact_digits
    return None


def _normalize_whitespace(value: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", value).strip()


def _normalize_pet_name_value(value: object) -> str | None:
    """Normalize a raw pet_name candidate.

    Steps:
    1. Strip trailing date/birth fragments (e.g. "ALYA - Nacimiento: 05/07/2018" → "ALYA").
    2. Reject purely numeric values ("12345" → None).
    3. Reject values that look like a field label ("Especie: Canina" → None).
    4. Title-case the result for presentation consistency.
    """
    if not isinstance(value, str):
        return None

    cleaned = _normalize_whitespace(value)
    if not cleaned:
        return None

    # Strip trailing birth-date / date-of-birth fragments
    cleaned = _PET_NAME_TRAILING_NOISE.sub("", cleaned).strip(" -:;,.")

    # Strip stray label echoes (e.g. "Paciente:" prefix leaking)
    cleaned = re.sub(
        r"(?i)^(?:paciente|nombre(?:\s+del\s+(?:paciente|animal))?|patient|animal|mascota)\s*[:\-|]\s*",
        "",
        cleaned,
    ).strip()

    cleaned = _normalize_whitespace(cleaned)
    if not cleaned:
        return None

    # Reject numeric-only
    if _PET_NAME_NUMERIC_ONLY.match(cleaned):
        return None

    # Reject values that look like another field's label: value
    if _PET_NAME_LOOKS_LIKE_LABEL.match(cleaned):
        return None

    # Title-case for consistency (ALYA → Alya, luna → Luna)
    return cleaned.title()


def _normalize_scalar_with_labels(value: object, labels: tuple[str, ...]) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = _normalize_whitespace(value)
    if not cleaned:
        return None

    for label in labels:
        cleaned = re.sub(
            rf"(?i)\b{re.escape(label)}\b\s*[:\-]?\s*",
            "",
            cleaned,
        )

    cleaned = _normalize_whitespace(cleaned.strip(" -:;,."))
    return cleaned or None


def _normalize_clinic_name_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = _normalize_whitespace(value)
    if not cleaned:
        return None

    cleaned = _CLINIC_NAME_LEADING_LABEL.sub("", cleaned).strip(" -:;,.")
    cleaned = _normalize_whitespace(cleaned)
    if not cleaned:
        return None

    lower_cleaned = cleaned.casefold()
    if _CLINIC_NAME_ADDRESS_LIKE.search(lower_cleaned) and re.search(r"\d", lower_cleaned):
        return None

    return cleaned


def _normalize_clinic_address_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = value.replace("\n", " ")
    cleaned = _normalize_whitespace(cleaned)
    if not cleaned:
        return None

    cleaned = _CLINIC_ADDRESS_LEADING_LABEL.sub("", cleaned).strip(" -:;,.")
    if not cleaned:
        return None

    for pattern, replacement in _CLINIC_ADDRESS_ABBREVIATIONS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = _normalize_whitespace(cleaned).strip(" ,;.")
    if not cleaned:
        return None

    return cleaned


def _normalize_owner_address_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    # Keep at most two meaningful lines; extra breaks are flattened.
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if not lines:
        return None
    if len(lines) > 2:
        compact = " ".join(lines)
    else:
        compact = " ".join(lines)

    cleaned = _normalize_whitespace(compact)
    if not cleaned:
        return None

    cleaned = _OWNER_ADDRESS_LEADING_LABEL.sub("", cleaned).strip(" -:;,.")
    if not cleaned:
        return None

    for pattern, replacement in _OWNER_ADDRESS_ABBREVIATIONS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = _normalize_whitespace(cleaned).strip(" ,;.")
    if not cleaned:
        return None

    lower_cleaned = cleaned.casefold()
    has_digits = bool(re.search(r"\d", lower_cleaned))
    has_address_token = bool(_OWNER_ADDRESS_ADDRESS_TOKEN.search(lower_cleaned))
    if not has_digits or not has_address_token:
        return None

    if _OWNER_ADDRESS_RESIDUAL_LABEL.search(lower_cleaned) and ":" in lower_cleaned:
        return None

    return cleaned


def _normalize_sex_value(value: object) -> str | None:
    cleaned = _normalize_scalar_with_labels(value, ("sexo", "sex"))
    if not cleaned:
        return None

    match = re.search(r"(?i)\b(hembra|macho|female|male)\b", cleaned)
    if not match:
        return None
    token = match.group(1).casefold()
    if token in {"female", "hembra"}:
        return "hembra"
    return "macho"


def _normalize_microchip_id(
    *,
    value: object,
    evidence: list[dict[str, object]] | None,
) -> str | None:
    labels = (
        "microchip",
        "micr0chip",
        "chip",
        "transponder",
        "identificación electrónica",
        "identificacion electronica",
        "nº chip",
        "n.o chip",
        "n° chip",
        "id",
    )
    cleaned = _normalize_scalar_with_labels(value, labels)

    if not cleaned and evidence:
        first_evidence = evidence[0]
        raw_evidence = first_evidence.get("evidence") if isinstance(first_evidence, dict) else None
        snippet = raw_evidence.get("snippet") if isinstance(raw_evidence, dict) else None
        if isinstance(snippet, str):
            match = re.search(
                (
                    r"(?i)(?:microchip|micr0chip|chip|transponder|"
                    r"identificaci[oó]n\s+electr[oó]nica)\s*"
                    r"(?:n[ºo]\.?|nro\.?|id)?\s*[:\-]?\s*([^\n;]{3,80})"
                ),
                _normalize_whitespace(snippet),
            )
            if match:
                cleaned = _normalize_scalar_with_labels(match.group(1), labels)

    if not cleaned:
        return None

    compact = _normalize_whitespace(cleaned.strip(" -:;,."))
    compact = re.sub(r"[^A-Za-z0-9./_\- ]+", " ", compact)
    compact = _normalize_whitespace(compact)
    if not compact:
        return None

    trailing_label_tokens = {
        "paciente",
        "propietario",
        "propietaria",
        "tutor",
        "especie",
        "raza",
        "sexo",
        "edad",
        "fecha",
    }
    parts = compact.split(" ")
    while parts and parts[-1].casefold() in trailing_label_tokens:
        parts.pop()

    normalized = _normalize_whitespace(" ".join(parts))
    if not normalized:
        return None
    return normalize_microchip_digits_only(normalized)


def _normalize_date_value(value: object) -> str | None:
    cleaned = _normalize_scalar_with_labels(value, ("fecha", "date", "visita", "consulta"))
    if not cleaned:
        return None

    match = _DATE_PATTERN.search(cleaned)
    if not match:
        return None

    raw = match.group(1).replace("-", "/").replace(".", "/")
    parts = raw.split("/")
    if len(parts) != 3:
        return None

    if len(parts[0]) == 4:
        year, month, day = parts
        normalized = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        try:
            parsed = datetime.strptime(normalized, "%d/%m/%Y")
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return None

    day, month, year = parts
    normalized = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    if len(year) == 4:
        try:
            parsed = datetime.strptime(normalized, "%d/%m/%Y")
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return None

    if len(year) == 2:
        try:
            parsed = datetime.strptime(normalized, "%d/%m/%y")
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return None

    return None


def _normalize_weight(value: object) -> str:
    """Normalize weight to canonical ``X.Y kg`` format within [0.5, 120] kg."""
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()
    if not cleaned:
        return ""

    match = _WEIGHT_PATTERN.search(cleaned)
    if match is None:
        return ""

    number_str = match.group("number").replace(",", ".")
    try:
        number = float(number_str)
    except ValueError:
        return ""

    unit = (match.group("unit") or "").lower()
    if unit in ("g", "gr"):
        number = number / 1000.0

    if number <= 0 or number < WEIGHT_MIN_KG or number > WEIGHT_MAX_KG:
        return ""

    if number == int(number):
        return f"{int(number)} kg"
    return f"{number:g} kg"
