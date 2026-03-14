"""Clinical-text candidate extraction helpers."""

from __future__ import annotations

from ..constants import COVERAGE_CONFIDENCE_FALLBACK, COVERAGE_CONFIDENCE_LABEL
from .common import CandidateCollector, MiningContext


def extract_clinical_candidates(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    for line in context.lines:
        _extract_labeled_clinical_candidates(line, collector)
        _extract_unlabeled_clinical_candidates(line, collector)
    _extract_language_candidate(context, collector)


def _extract_labeled_clinical_candidates(
    line: str,
    collector: CandidateCollector,
) -> None:
    if ":" in line:
        header, value = line.split(":", 1)
    elif "-" in line:
        header, value = line.split("-", 1)
    else:
        header, value = "", ""
    if not value:
        return

    lower_header = header.casefold()
    if any(token in lower_header for token in ("diagn", "impresi")):
        collector.add_candidate(
            key="diagnosis",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("trat", "medic", "prescrip", "receta")):
        collector.add_candidate(
            key="medication",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
        collector.add_candidate(
            key="treatment_plan",
            value=value,
            confidence=0.7,
            snippet=line,
        )
    if any(token in lower_header for token in ("proced", "interv", "cirug", "quir")):
        collector.add_candidate(
            key="procedure",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("sintom", "symptom")):
        collector.add_candidate(
            key="symptoms",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("vacun", "vaccin")):
        collector.add_candidate(
            key="vaccinations",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("laboratorio", "analit", "lab")):
        collector.add_candidate(
            key="lab_result",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("radiograf", "ecograf", "imagen", "tac", "rm")):
        collector.add_candidate(
            key="imaging",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )
    if any(token in lower_header for token in ("linea", "concepto", "item")):
        collector.add_candidate(
            key="line_item",
            value=value,
            confidence=COVERAGE_CONFIDENCE_LABEL,
            snippet=line,
        )


def _extract_unlabeled_clinical_candidates(
    line: str,
    collector: CandidateCollector,
) -> None:
    lower_line = line.casefold()
    if any(token in lower_line for token in ("diagn", "impresi")) and ":" not in line:
        collector.add_candidate(
            key="diagnosis",
            value=line,
            confidence=0.64,
            snippet=line,
        )
    if any(
        token in lower_line
        for token in ("amoxic", "clavul", "predni", "omepra", "antibiot", "mg", "cada")
    ):
        collector.add_candidate(
            key="medication",
            value=line,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=line,
        )
    if any(
        token in lower_line for token in ("cirug", "proced", "sut", "cura", "ecograf", "radiograf")
    ):
        collector.add_candidate(
            key="procedure",
            value=line,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet=line,
        )


def _extract_language_candidate(
    context: MiningContext,
    collector: CandidateCollector,
) -> None:
    if not context.compact_text or "language" in collector.candidates:
        return
    if any(
        token in context.compact_text.casefold()
        for token in ("paciente", "diagnost", "tratamiento")
    ):
        collector.add_candidate(
            key="language",
            value="es",
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
            snippet="Heuristic language inference based on Spanish clinical tokens",
            page=None,
        )
