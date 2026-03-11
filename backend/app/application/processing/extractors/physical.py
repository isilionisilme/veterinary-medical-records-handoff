"""Physical and pet-identity candidate extraction helpers."""

from __future__ import annotations

from ..constants import _DATE_CANDIDATE_PATTERN, COVERAGE_CONFIDENCE_FALLBACK
from ..field_patterns import (
    _PET_NAME_BIRTHLINE_RE,
    _PET_NAME_GUARD_RE,
    _VISIT_TIMELINE_CONTEXT_RE,
    _WEIGHT_STANDALONE_LINE_RE,
)
from .common import CandidateCollector, MiningContext

_BREED_KEYWORDS = (
    "labrador",
    "retriever",
    "bulldog",
    "pastor",
    "yorkshire",
    "mestiz",
    "beagle",
    "caniche",
)
_STOPWORDS_UPPER = {
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
_PET_NAME_STOP_LOWER = {
    s.casefold()
    for s in _STOPWORDS_UPPER
    | {
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
}


def extract_physical_candidates(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for index, line in enumerate(context.lines):
        lower_line = line.casefold()
        normalized_single = lower_line.strip()
        _extract_inline_sex_candidate(line, lower_line, collector)
        _extract_pet_name_birthline(context, collector, index, line)
        _extract_species_candidate(context, collector, line, normalized_single)
        _extract_breed_candidate(line, lower_line, collector)
        _extract_short_sex_candidate(context, collector, index, normalized_single)
        _extract_weight_candidate(context, collector, index, line)
        _extract_unlabeled_pet_name(context, collector, index, line)


def _extract_inline_sex_candidate(
    line: str, lower_line: str, collector: CandidateCollector
) -> None:
    if any(token in lower_line for token in ("macho", "hembra", "male", "female")):
        if "macho" in lower_line or "male" in lower_line:
            collector.add_candidate(
                key="sex",
                value="macho",
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )
        if "hembra" in lower_line or "female" in lower_line:
            collector.add_candidate(
                key="sex",
                value="hembra",
                confidence=COVERAGE_CONFIDENCE_FALLBACK,
                snippet=line,
            )


def _extract_pet_name_birthline(
    context: MiningContext, collector: CandidateCollector, index: int, line: str
) -> None:
    birthline_match = _PET_NAME_BIRTHLINE_RE.match(line)
    if not birthline_match:
        return
    candidate_name = " ".join(birthline_match.group(1).split())
    token_count = len(candidate_name.split())
    if not (1 <= token_count <= 3):
        return
    if candidate_name.casefold() in _PET_NAME_STOP_LOWER or _PET_NAME_GUARD_RE.search(
        candidate_name
    ):
        return
    nearby = " ".join(context.lines[index : min(len(context.lines), index + 4)]).casefold()
    if any(
        token in nearby
        for token in ("canino", "felino", "raza", "chip", "especie", "nacimiento", "nac")
    ):
        collector.add_candidate(
            key="pet_name",
            value=candidate_name,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=line,
        )


def _extract_species_candidate(
    context: MiningContext,
    collector: CandidateCollector,
    line: str,
    normalized_single: str,
) -> None:
    if normalized_single in context.species_keywords:
        collector.add_candidate(
            key="species",
            value=context.species_keywords[normalized_single],
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=line,
        )


def _extract_breed_candidate(
    line: str,
    lower_line: str,
    collector: CandidateCollector,
) -> None:
    if any(keyword in lower_line for keyword in _BREED_KEYWORDS) and len(line) <= 80:
        collector.add_candidate(
            key="breed", value=line, confidence=COVERAGE_CONFIDENCE_FALLBACK, snippet=line
        )


def _extract_short_sex_candidate(
    context: MiningContext,
    collector: CandidateCollector,
    index: int,
    normalized_single: str,
) -> None:
    if normalized_single not in {"m", "macho", "male", "h", "hembra", "female"}:
        return
    window = " ".join(
        context.lines[max(0, index - 1) : min(len(context.lines), index + 2)]
    ).casefold()
    if "sexo" in window:
        sex_value = "macho" if normalized_single in {"m", "macho", "male"} else "hembra"
        collector.add_candidate(
            key="sex",
            value=sex_value,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=" ".join(context.lines[max(0, index - 1) : min(len(context.lines), index + 2)]),
        )


def _extract_weight_candidate(
    context: MiningContext, collector: CandidateCollector, index: int, line: str
) -> None:
    standalone_weight_match = _WEIGHT_STANDALONE_LINE_RE.match(line)
    if standalone_weight_match is None:
        return
    value_raw = standalone_weight_match.group(1)
    unit_raw = standalone_weight_match.group(2).lower()
    unit = "kg" if unit_raw in {"kg", "kgs"} else unit_raw
    context_lines = context.lines[max(0, index - 3) : min(len(context.lines), index + 2)]
    context_text = " ".join(context_lines)
    has_date_context = _DATE_CANDIDATE_PATTERN.search(context_text) is not None
    has_visit_context = _VISIT_TIMELINE_CONTEXT_RE.search(context_text) is not None
    if has_date_context or has_visit_context or len(context.lines) <= 5:
        collector.add_candidate(
            key="weight",
            value=f"{value_raw} {unit}".strip(),
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet="\n".join(context_lines),
        )


def _extract_unlabeled_pet_name(
    context: MiningContext, collector: CandidateCollector, index: int, line: str
) -> None:
    word_count = len(line.split())
    is_name_like = (
        2 < len(line) <= 40
        and 1 <= word_count <= 3
        and line not in _STOPWORDS_UPPER
        and line.casefold() not in _PET_NAME_STOP_LOWER
        and (line.isupper() or line.istitle())
        and ":" not in line
        and not _PET_NAME_GUARD_RE.search(line)
    )
    if not is_name_like:
        return
    nearby = " ".join(context.lines[index : min(len(context.lines), index + 4)]).casefold()
    if any(token in nearby for token in ("canino", "felino", "raza", "chip", "especie")):
        collector.add_candidate(
            key="pet_name",
            value=line.title(),
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=line,
        )
