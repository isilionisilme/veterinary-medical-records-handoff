"""Segment text parsing: clause normalization and observation/action classification.

Extracted from review_service.py (ARCH-01) to isolate the regex-heavy clause
classification logic into a focused module.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Compiled regex patterns for clause classification
# ---------------------------------------------------------------------------

_VISIT_REASON_LABEL_PREFIX_RE = re.compile(
    r"^(?:visita|consulta|control|revisi[oó]n|seguimiento|ingreso|alta)\b",
    re.IGNORECASE,
)
_SUMMARY_CLAUSE_PREFIX_RE = re.compile(
    r"^(?:visita|consulta|control|revisi[oó]n|seguimiento|ingreso)\b",
    re.IGNORECASE,
)
_DATE_TOKEN_RE = re.compile(
    r"^(?:\d{4}[-\/.]\d{1,2}[-\/.]\d{1,2}|\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4})\b"
)
_CLAUSE_SPLIT_RE = re.compile(r";|\.(?=\s|$)")
_ACTION_VERB_RE = re.compile(
    r"\b("
    r"se\s+recomienda|se\s+prescribe|se\s+administra|se\s+aplica|"
    r"se\s+indica|se\s+pauta|se\s+realiza|"
    r"recomendar|recomiendo|recomendamos|prescribir|administrar|aplicar|iniciar|continuar|"
    r"mantener|mezclar|cambiar|esterilizar|castrar|lavados?|"
    r"damos|pongo|ponemos|vacunar|vacunamos|se\s+vacuna|vacunaci[oó]n|"
    r"vamos\s+a\s+(?:hacer|pasar|repetir|valorar|tratar|controlar|cambiar)|"
    r"cogemos\s+cita|poner\s+cita|repetiremos|volveremos\s+a\s+tratar|"
    r"controlamos|podemos\s+esterilizar|le\s+comentamos|"
    r"curas?\b|observar|acudir\s+de\s+urgencias|contactamos|llamo|"
    r"recalcamos|preguntar|preguntamos|desparasitar|heptavalente|novibac|"
    r"hospitalizad[oa]|hospitalizar|dieta\b|"
    r"coger\s+muestra|conservar\s+en\s+fr[ií]o|plan\s+cachorro|"
    r"mando|mandamos|enviar\s+por\s+mail|mandar\s+por\s+mail|por\s+mail|"
    r"volvemos\s+a\s+revisar|traer\s+fotos|castraremos|repetir\s+test"
    r")\b",
    re.IGNORECASE,
)
_THERAPEUTIC_ACTION_RE = re.compile(
    r"\b("
    r"pongo\s+vacuna|ponemos\s+vacuna|se\s+vacuna|vacunamos|vacunaci[oó]n|"
    r"damos|administrar|administra(?:mos)?|aplicar|aplica(?:mos)?|"
    r"comprimid[oa]s?|c[aá]psul[ae]s?|"
    r"gotas?|sobre(?:s)?|ml|mg|cada\s+\d+\s*(?:h|horas?|d[ií]as?)|"
    r"durante\s+\d+\s*(?:d[ií]as?|semanas?|meses?)|"
    r"revisi[oó]n|seguimiento|control|lata\s+i/d|"
    r"mantener|mezclar|insistir|cambiar|esterilizar|castrar"
    r")\b",
    re.IGNORECASE,
)
_DIAGNOSTIC_CONTEXT_RE = re.compile(
    r"\b("
    r"test|anal[ií]tica|coprol[oó]gic[oa]|perfil\s+heces|"
    r"ecograf[ií]a|radiograf[ií]a|rx|biopsia|colonoscopia|"
    r"saco\s+sangre|extra(?:er|emos?)\s+sangre|muestra(?:s)?\s+de\s+heces|"
    r"resultado(?:s)?|negativ[oa]s?|positiv[oa]s?|descarta(?:mos|r)?"
    r")\b",
    re.IGNORECASE,
)
_INLINE_ACTION_SPLIT_RE = re.compile(
    r"\s+(?=(?:"
    r"pongo\s+vacuna|ponemos\s+vacuna|se\s+recomienda|se\s+prescribe|"
    r"se\s+administra|se\s+aplica|se\s+indica|se\s+pauta|damos|"
    r"tratamie?nto\s*:|tto\s*:|"
    r"vamos\s+a\s+(?:hacer|pasar|repetir|valorar|tratar|controlar|cambiar)|"
    r"cogemos\s+cita|poner\s+cita|seguimiento|recomiendo|recomendamos|"
    r"mezcla\s+progresiva|observar|curas?\s+con|"
    r"por\s+lo\s+que\s+(?:mando|mandamos)"
    r")\b)",
    re.IGNORECASE,
)
_TREATMENT_LABEL_RE = re.compile(
    r"^\s*(?:tratamie?nto|tto)\b(?:\s*[:\-])?",
    re.IGNORECASE,
)
_IMPERATIVE_DAR_RE = re.compile(r"^\s*dar\s+\d", re.IGNORECASE)
_IMPERATIVE_SEGUIR_RE = re.compile(r"^\s*[-*•]?\s*seguir\s+con\b", re.IGNORECASE)
_ANAMNESIS_INTENT_RE = re.compile(r"\b(?:anamnesis|acude\s+para)\b", re.IGNORECASE)
_PERFORMED_ACTION_RE = re.compile(
    r"\b(?:pongo|ponemos|damos|se\s+administra|se\s+aplica|se\s+pauta|se\s+prescribe)\b",
    re.IGNORECASE,
)
_DOSAGE_INSTRUCTION_RE = re.compile(
    r"\b(?:\d+(?:[.,]\d+)?\s*(?:ml|mg)|"
    r"\d+\s*(?:/\s*\d+)?\s*comprimid[oa]s?|"
    r"(?:comprimid[oa]s?|c[aá]psul[ae]s?|gotas?|sobres?)\b)"
    r".{0,40}\b(?:cada|durante)\b",
    re.IGNORECASE,
)
_PLAN_RECOMMENDATION_RE = re.compile(
    r"^(?:importante\s+ofrecer|es\s+importante\s+que|"
    r"en\s+\d+\s*(?:d[ií]as?|semanas?|mes(?:es)?)\s+deber[ií]a|"
    r"si\s+se\s+mantiene|si\s+evoluciona|si\s+no\s+hay\s+mejor[ií]a|"
    r"introduciremos|revisaremos|ser[aá]\s+necesario\s+realizar|"
    r"(?:y\s+)?si\s+no\s+haremos|tenemos\s+que\s+descartar|si\s+empeora)\b",
    re.IGNORECASE,
)
_OBSERVATION_HEADER_RE = re.compile(
    r"^(?:exploraci[oó]n|exploracion|anamnesis)\b",
    re.IGNORECASE,
)
_TRAILING_STUB_RE = re.compile(r"\b(?:les|le|se)\s*$", re.IGNORECASE)
_ACTION_CONTINUATION_RE = re.compile(
    r"^(?:el\s+test\s+de|la\s+anal[ií]tica|el\s+coprol[oó]gico|"
    r"mezclado\s+con|pienso\s+digestivo|limpiezas?|lata\s+i/d)\b|^en\s+casa$",
    re.IGNORECASE,
)
_LEADING_DAY_DATETIME_RE = re.compile(
    r"^d[ií]a\s+\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*",
    re.IGNORECASE,
)
_ADMIN_ACTION_CONTINUATION_RE = re.compile(
    r"^(?:recordatorios?|vacuna|f|pr[oó]xima|f\.?\s*pr[oó]xima|aplicada|s[ií])$",
    re.IGNORECASE,
)
_OBSERVATION_FINDING_RE = re.compile(
    r"\b(?:no\s+parecen?\s+hongos|inflamaci[oó]n|alopecia|mordisco)\b",
    re.IGNORECASE,
)
_HOME_STATUS_OBSERVATION_RE = re.compile(
    r"^(?:en\s+casa\s+comentan|en\s+casa\b.*\best[aá]\s+bien\b)",
    re.IGNORECASE,
)
_ADMIN_ACTION_RE = re.compile(
    r"\b(?:recordatorios?\s+vacunaciones|vacunaci[oó]n\s+\w+)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Clause normalization
# ---------------------------------------------------------------------------


def normalize_segment_clause(*, raw_clause: str) -> str:
    """Normalize a single raw clause from a visit segment."""
    clause = raw_clause.strip()
    if not clause:
        return ""

    clause = clause.lstrip("-*• \t")
    clause = re.sub(r"^[^\wáéíóúüñÁÉÍÓÚÜÑ]+", "", clause)
    clause = _LEADING_DAY_DATETIME_RE.sub("", clause).strip()
    clause = _SUMMARY_CLAUSE_PREFIX_RE.sub("", clause, count=1).strip()

    while True:
        compact = clause.lstrip(" :,-\t")
        date_match = _DATE_TOKEN_RE.match(compact)
        if date_match is None:
            clause = compact
            break
        clause = compact[date_match.end() :].strip()

    normalized = " ".join(clause.strip(" :,-\t").split())
    normalized = _TRAILING_STUB_RE.sub("", normalized).strip()
    return normalized


def extract_reason_for_visit_from_segment(*, segment_text: str) -> str | None:
    """Extract the first meaningful clinical reason from a visit segment."""
    for raw_line in segment_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        line = line.lstrip("-*• \t")
        line = _VISIT_REASON_LABEL_PREFIX_RE.sub("", line, count=1).strip()

        while True:
            compact = line.lstrip(" :,-\t")
            date_match = _DATE_TOKEN_RE.match(compact)
            if date_match is None:
                line = compact
                break
            line = compact[date_match.end() :].strip()

        if not line:
            continue

        line = line.lstrip(":,- \t")
        if not line:
            continue

        for separator in (".", ";"):
            if separator in line:
                line = line.split(separator, 1)[0].strip()
                break

        normalized = " ".join(line.split()).strip()
        if normalized:
            return normalized

    return None


# ---------------------------------------------------------------------------
# Clause classification helpers
# ---------------------------------------------------------------------------


def _classify_as_observation(
    *, normalized_clause: str, raw_clause: str, actions: list[str]
) -> bool | None:
    """Return True if observation, False if action, None if undecided."""
    has_anamnesis_intent = _ANAMNESIS_INTENT_RE.search(normalized_clause) is not None
    has_performed_action = _PERFORMED_ACTION_RE.search(normalized_clause) is not None

    if has_anamnesis_intent and not has_performed_action:
        return True

    has_treatment_label = _TREATMENT_LABEL_RE.search(raw_clause) is not None
    has_dosage_instruction = _DOSAGE_INSTRUCTION_RE.search(normalized_clause) is not None

    if _OBSERVATION_HEADER_RE.search(normalized_clause) is not None and not has_treatment_label:
        return True

    if (
        _OBSERVATION_FINDING_RE.search(normalized_clause) is not None
        and not has_treatment_label
        and not has_dosage_instruction
    ):
        return True

    if _HOME_STATUS_OBSERVATION_RE.search(normalized_clause) is not None:
        return True

    if _ADMIN_ACTION_RE.search(normalized_clause) is not None:
        return False

    if _ADMIN_ACTION_CONTINUATION_RE.search(normalized_clause) is not None and actions:
        return False

    if _ACTION_CONTINUATION_RE.search(normalized_clause) is not None and actions:
        return False

    is_therapeutic_action = _THERAPEUTIC_ACTION_RE.search(normalized_clause) is not None
    has_imperative_dar = _IMPERATIVE_DAR_RE.search(raw_clause) is not None
    has_imperative_seguir = _IMPERATIVE_SEGUIR_RE.search(raw_clause) is not None
    has_plan_recommendation = _PLAN_RECOMMENDATION_RE.search(normalized_clause) is not None

    if (
        has_treatment_label
        or has_imperative_dar
        or has_imperative_seguir
        or has_dosage_instruction
        or has_plan_recommendation
        or is_therapeutic_action
    ):
        return False

    is_diagnostic_context = _DIAGNOSTIC_CONTEXT_RE.search(normalized_clause) is not None
    is_generic_action = _ACTION_VERB_RE.search(normalized_clause) is not None

    if (
        is_diagnostic_context
        and not has_treatment_label
        and not has_imperative_dar
        and not has_imperative_seguir
        and not is_therapeutic_action
        and not is_generic_action
    ):
        return True

    if is_generic_action:
        return False

    # Default: observation
    return None


# ---------------------------------------------------------------------------
# Main segment parser
# ---------------------------------------------------------------------------


def split_segment_into_observations_actions(*, segment_text: str) -> tuple[str | None, str | None]:
    """Split a visit segment into observation and action summaries."""
    observations: list[str] = []
    actions: list[str] = []
    seen_observations: set[str] = set()
    seen_actions: set[str] = set()

    for raw_line in segment_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        raw_clauses = [line]
        if "." in line or ";" in line:
            split_clauses = [part for part in _CLAUSE_SPLIT_RE.split(line) if part.strip()]
            if split_clauses:
                raw_clauses = split_clauses

        expanded_clauses: list[str] = []
        for raw_clause in raw_clauses:
            inline_split = [
                part for part in _INLINE_ACTION_SPLIT_RE.split(raw_clause) if part.strip()
            ]
            if inline_split:
                expanded_clauses.extend(inline_split)
            else:
                expanded_clauses.append(raw_clause)

        for raw_clause in expanded_clauses:
            normalized_clause = normalize_segment_clause(raw_clause=raw_clause)
            if not normalized_clause:
                continue

            key = normalized_clause.casefold()

            classification = _classify_as_observation(
                normalized_clause=normalized_clause,
                raw_clause=raw_clause,
                actions=actions,
            )

            if classification is True or classification is None:
                # True = explicitly observation, None = default to observation
                if key not in seen_observations:
                    seen_observations.add(key)
                    observations.append(normalized_clause)
            else:
                if key not in seen_actions:
                    seen_actions.add(key)
                    actions.append(normalized_clause)

    observation_value = " ".join(observations).strip() or None
    action_value = " ".join(actions).strip() or None
    return observation_value, action_value
