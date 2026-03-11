from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass

from backend.app.application.documents import review_payload_projector
from backend.app.application.documents._shared import (
    _VISIT_GROUP_METADATA_KEY_SET,
    _VISIT_GROUP_METADATA_KEYS,
    _VISIT_SCOPED_KEY_SET,
    _contains_any_date_token,
    _detect_visit_dates_from_raw_text,
    _extract_evidence_snippet,
    _extract_visit_date_candidates_from_text,
    _locate_visit_boundary_offsets_from_raw_text,
    _locate_visit_date_occurrences_from_raw_text,
    _normalize_visit_date_candidate,
)
from backend.app.application.documents.calibration import (
    _apply_reviewed_document_calibration,
    _revert_reviewed_document_calibration,
)
from backend.app.application.documents.upload_service import _default_now_iso
from backend.app.application.field_normalizers import (
    _normalize_weight,
)
from backend.app.application.processing.candidate_mining import _mine_interpretation_candidates
from backend.app.domain.models import ReviewStatus
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

logger = logging.getLogger(__name__)

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
_RAW_TIMELINE_HEADER_RE = re.compile(
    r"^\s*[-*•]?\s*(\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4})\s*[-–—]\s*\d{1,2}:\d{2}(?::\d{2})?",
    re.IGNORECASE,
)
_RAW_WEIGHT_TOKEN_RE = re.compile(
    r"(?i)\b(?:peso|pv|p\.)?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(kg|kgs|g)\b"
)


def _weight_evidence_offset(field: dict[str, object], *, default: float = -1.0) -> float:
    evidence = field.get("evidence")
    if isinstance(evidence, dict):
        offset = evidence.get("offset")
        if isinstance(offset, int | float):
            return float(offset)
    return default


def _weight_effective_visit_date(
    *, visit: dict[str, object], weight_field: dict[str, object]
) -> str | None:
    raw_visit_date = visit.get("visit_date")
    normalized_visit_date = _normalize_visit_date_candidate(raw_visit_date)
    if normalized_visit_date is not None:
        return normalized_visit_date

    # Fallback: if visit_date comes in a non-normalizable shape, try date token
    # from the weight evidence snippet before discarding the candidate.
    evidence_snippet = _extract_evidence_snippet(weight_field)
    normalized_from_evidence = _normalize_visit_date_candidate(evidence_snippet)
    if normalized_from_evidence is not None:
        return normalized_from_evidence

    return None


def _extract_latest_visit_weight_from_raw_text(raw_text: str | None) -> dict[str, object] | None:
    if not isinstance(raw_text, str) or not raw_text.strip():
        return None

    current_visit_date: str | None = None
    candidates: list[tuple[str, int, str, str]] = []
    lines = raw_text.splitlines()

    for line_index, line in enumerate(lines):
        header_match = _RAW_TIMELINE_HEADER_RE.search(line)
        if header_match is not None:
            current_visit_date = _normalize_visit_date_candidate(header_match.group(1))

        token_match = _RAW_WEIGHT_TOKEN_RE.search(line)
        if token_match is None or current_visit_date is None:
            continue

        raw_number = token_match.group(1)
        raw_unit = token_match.group(2).lower()
        normalized_weight = _normalize_weight(f"{raw_number} {raw_unit}")
        if not normalized_weight:
            continue

        candidates.append((current_visit_date, line_index, normalized_weight, line.strip()))

    if not candidates:
        return None

    # Latest chronological visit date first, then latest line index for deterministic tie-break.
    best_date, _, best_weight, best_snippet = max(candidates, key=lambda item: (item[0], item[1]))
    return {
        "date": best_date,
        "value": best_weight,
        # Raw timeline extraction works on aggregated text; page may be unknown.
        "evidence": {"snippet": best_snippet},
    }


@dataclass(frozen=True, slots=True)
class LatestCompletedRunReview:
    run_id: str
    state: str
    completed_at: str | None
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class ActiveInterpretationReview:
    interpretation_id: str
    version_number: int
    data: dict[str, object]


@dataclass(frozen=True, slots=True)
class RawTextArtifactAvailability:
    run_id: str
    available: bool


@dataclass(frozen=True, slots=True)
class DocumentReview:
    document_id: str
    latest_completed_run: LatestCompletedRunReview
    active_interpretation: ActiveInterpretationReview
    raw_text_artifact: RawTextArtifactAvailability
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


@dataclass(frozen=True, slots=True)
class DocumentReviewLookupResult:
    review: DocumentReview | None
    unavailable_reason: str | None


def get_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    storage: FileStorage,
) -> DocumentReviewLookupResult | None:
    logger.info("get_document_review called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    latest_completed_run = repository.get_latest_completed_run(document_id)
    if latest_completed_run is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="NO_COMPLETED_RUN",
        )

    interpretation_payload = repository.get_latest_artifact_payload(
        run_id=latest_completed_run.run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if interpretation_payload is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="INTERPRETATION_MISSING",
        )

    interpretation_id = str(interpretation_payload.get("interpretation_id", ""))
    version_number_raw = interpretation_payload.get("version_number", 1)
    version_number = version_number_raw if isinstance(version_number_raw, int) else 1

    structured_data = interpretation_payload.get("data")
    if not isinstance(structured_data, dict):
        structured_data = {}

    raw_text: str | None = None
    raw_text_path = storage.resolve_raw_text(
        document_id=latest_completed_run.document_id,
        run_id=latest_completed_run.run_id,
    )
    if raw_text_path.exists():
        try:
            raw_text = raw_text_path.read_text(encoding="utf-8")
        except OSError:
            logger.warning("Failed to read raw_text file path=%s", raw_text_path)
            raw_text = None

    structured_data = review_payload_projector._normalize_review_interpretation_data(
        structured_data,
        raw_text=raw_text,
    )

    return DocumentReviewLookupResult(
        review=DocumentReview(
            document_id=document_id,
            latest_completed_run=LatestCompletedRunReview(
                run_id=latest_completed_run.run_id,
                state=latest_completed_run.state.value,
                completed_at=latest_completed_run.completed_at,
                failure_type=latest_completed_run.failure_type,
            ),
            active_interpretation=ActiveInterpretationReview(
                interpretation_id=interpretation_id,
                version_number=version_number,
                data=structured_data,
            ),
            raw_text_artifact=RawTextArtifactAvailability(
                run_id=latest_completed_run.run_id,
                available=storage.exists_raw_text(
                    document_id=latest_completed_run.document_id,
                    run_id=latest_completed_run.run_id,
                ),
            ),
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        ),
        unavailable_reason=None,
    )


def _resolve_snippet_anchor_offset(*, raw_text: str | None, snippet: str | None) -> int | None:
    if not isinstance(raw_text, str) or not isinstance(snippet, str):
        return None

    compact_snippet = " ".join(snippet.split()).strip()
    if len(compact_snippet) < 8:
        return None

    raw_text_lower = raw_text.casefold()
    snippet_lower = compact_snippet.casefold()
    exact_offset = raw_text_lower.find(snippet_lower)
    if exact_offset >= 0:
        return exact_offset

    # Fallback for OCR punctuation drift: anchor with snippet prefix.
    snippet_prefix = snippet_lower[: min(len(snippet_lower), 48)]
    if len(snippet_prefix) < 12:
        return None

    prefix_offset = raw_text_lower.find(snippet_prefix)
    if prefix_offset >= 0:
        return prefix_offset

    return None


def _resolve_visit_from_anchor(
    *,
    candidate_dates: list[str],
    anchor_offset: int | None,
    visit_by_date: dict[str, dict[str, object]],
    visit_occurrences_by_date: dict[str, list[dict[str, object]]],
    raw_text_offsets_by_date: dict[str, list[int]],
    visit_boundary_offsets: list[int],
) -> dict[str, object] | None:
    if anchor_offset is None:
        for candidate_date in candidate_dates:
            target_visit = visit_by_date.get(candidate_date)
            if target_visit is not None:
                return target_visit
        return None

    def _find_nearest_target(
        *,
        lower_offset_inclusive: int | None,
        upper_offset_exclusive: int | None,
    ) -> tuple[int, str, int] | None:
        nearest: tuple[int, str, int] | None = None
        dates_to_check = (
            candidate_dates if candidate_dates else list(raw_text_offsets_by_date.keys())
        )
        for candidate_date in dates_to_check:
            offsets = raw_text_offsets_by_date.get(candidate_date, [])
            if not offsets:
                continue
            for occurrence_index, offset in enumerate(offsets):
                if lower_offset_inclusive is not None and offset < lower_offset_inclusive:
                    continue
                if upper_offset_exclusive is not None and offset >= upper_offset_exclusive:
                    continue
                distance = abs(offset - anchor_offset)
                if nearest is None or distance < nearest[0]:
                    nearest = (distance, candidate_date, occurrence_index)
        return nearest

    nearest_target: tuple[int, str, int] | None = None
    if visit_boundary_offsets:
        lower_offset: int | None = None
        upper_offset: int | None = None
        for boundary_offset in visit_boundary_offsets:
            if boundary_offset <= anchor_offset:
                lower_offset = boundary_offset
                continue
            upper_offset = boundary_offset
            break
        nearest_target = _find_nearest_target(
            lower_offset_inclusive=lower_offset,
            upper_offset_exclusive=upper_offset,
        )

    if nearest_target is None:
        nearest_target = _find_nearest_target(
            lower_offset_inclusive=None,
            upper_offset_exclusive=None,
        )

    if nearest_target is None:
        for candidate_date in candidate_dates:
            target_visit = visit_by_date.get(candidate_date)
            if target_visit is not None:
                return target_visit
        return None

    _, target_date, target_occurrence_index = nearest_target
    date_visits = visit_occurrences_by_date.get(target_date, [])
    if not date_visits:
        return visit_by_date.get(target_date)

    visit_index = min(target_occurrence_index, len(date_visits) - 1)
    return date_visits[visit_index]


def _find_line_start_offset(*, text: str, offset: int) -> int:
    safe_offset = max(0, min(offset, len(text)))
    previous_break = text.rfind("\n", 0, safe_offset)
    return 0 if previous_break < 0 else previous_break + 1


def _resolve_visit_segment_bounds(
    *,
    anchor_offset: int,
    raw_text: str,
    visit_boundary_offsets: list[int],
    ordered_anchor_offsets: list[int],
) -> tuple[int, int]:
    line_start = _find_line_start_offset(text=raw_text, offset=anchor_offset)

    start_offset = line_start
    for boundary_offset in visit_boundary_offsets:
        if boundary_offset > anchor_offset:
            break
        if boundary_offset >= line_start:
            start_offset = boundary_offset

    end_offset = len(raw_text)
    for boundary_offset in visit_boundary_offsets:
        if boundary_offset > anchor_offset:
            end_offset = min(end_offset, boundary_offset)
            break

    for candidate_anchor in ordered_anchor_offsets:
        if candidate_anchor <= anchor_offset:
            continue
        candidate_line_start = _find_line_start_offset(text=raw_text, offset=candidate_anchor)
        end_offset = min(end_offset, candidate_line_start)
        break

    if end_offset < start_offset:
        end_offset = start_offset
    return start_offset, end_offset


def _extract_reason_for_visit_from_segment(*, segment_text: str) -> str | None:
    for raw_line in segment_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Normalize common prefixes so the first clause becomes clinical content.
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


def _normalize_segment_clause(*, raw_clause: str) -> str:
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


def _split_segment_into_observations_actions(*, segment_text: str) -> tuple[str | None, str | None]:
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
            normalized_clause = _normalize_segment_clause(raw_clause=raw_clause)
            if not normalized_clause:
                continue

            key = normalized_clause.casefold()
            is_therapeutic_action = _THERAPEUTIC_ACTION_RE.search(normalized_clause) is not None
            is_diagnostic_context = _DIAGNOSTIC_CONTEXT_RE.search(normalized_clause) is not None
            is_generic_action = _ACTION_VERB_RE.search(normalized_clause) is not None
            has_treatment_label = _TREATMENT_LABEL_RE.search(raw_clause) is not None
            has_imperative_dar = _IMPERATIVE_DAR_RE.search(raw_clause) is not None
            has_imperative_seguir = _IMPERATIVE_SEGUIR_RE.search(raw_clause) is not None
            has_anamnesis_intent = _ANAMNESIS_INTENT_RE.search(normalized_clause) is not None
            has_performed_action = _PERFORMED_ACTION_RE.search(normalized_clause) is not None
            has_dosage_instruction = _DOSAGE_INSTRUCTION_RE.search(normalized_clause) is not None
            has_plan_recommendation = _PLAN_RECOMMENDATION_RE.search(normalized_clause) is not None
            has_observation_header = _OBSERVATION_HEADER_RE.search(normalized_clause) is not None
            is_action_continuation = _ACTION_CONTINUATION_RE.search(normalized_clause) is not None
            has_observation_finding = _OBSERVATION_FINDING_RE.search(normalized_clause) is not None
            has_home_status_observation = (
                _HOME_STATUS_OBSERVATION_RE.search(normalized_clause) is not None
            )
            is_admin_action = _ADMIN_ACTION_RE.search(normalized_clause) is not None
            is_admin_action_continuation = (
                _ADMIN_ACTION_CONTINUATION_RE.search(normalized_clause) is not None
            )

            if has_anamnesis_intent and not has_performed_action:
                if key in seen_observations:
                    continue
                seen_observations.add(key)
                observations.append(normalized_clause)
                continue

            if has_observation_header and not has_treatment_label:
                if key in seen_observations:
                    continue
                seen_observations.add(key)
                observations.append(normalized_clause)
                continue

            if has_observation_finding and not has_treatment_label and not has_dosage_instruction:
                if key in seen_observations:
                    continue
                seen_observations.add(key)
                observations.append(normalized_clause)
                continue

            if has_home_status_observation:
                if key in seen_observations:
                    continue
                seen_observations.add(key)
                observations.append(normalized_clause)
                continue

            if is_admin_action:
                if key in seen_actions:
                    continue
                seen_actions.add(key)
                actions.append(normalized_clause)
                continue

            if is_admin_action_continuation and actions:
                if key in seen_actions:
                    continue
                seen_actions.add(key)
                actions.append(normalized_clause)
                continue

            if is_action_continuation and actions:
                if key in seen_actions:
                    continue
                seen_actions.add(key)
                actions.append(normalized_clause)
                continue

            if (
                has_treatment_label
                or has_imperative_dar
                or has_imperative_seguir
                or has_dosage_instruction
                or has_plan_recommendation
                or is_therapeutic_action
            ):
                if key in seen_actions:
                    continue
                seen_actions.add(key)
                actions.append(normalized_clause)
                continue

            if (
                is_diagnostic_context
                and not has_treatment_label
                and not has_imperative_dar
                and not has_imperative_seguir
                and not is_therapeutic_action
                and not is_generic_action
            ):
                if key in seen_observations:
                    continue
                seen_observations.add(key)
                observations.append(normalized_clause)
                continue

            if is_generic_action:
                if key in seen_actions:
                    continue
                seen_actions.add(key)
                actions.append(normalized_clause)
                continue

            if key in seen_observations:
                continue
            seen_observations.add(key)
            observations.append(normalized_clause)

    observation_value = " ".join(observations).strip() or None
    action_value = " ".join(actions).strip() or None
    return observation_value, action_value


def _append_visit_segment_summary_field(
    *,
    visit_fields: list[object],
    visit_id: str,
    key: str,
    value: str,
) -> None:
    visit_fields.append(
        {
            "field_id": f"derived-{key}-{visit_id}",
            "key": key,
            "value": value,
            "value_type": "string",
            "scope": "visit",
            "section": "visits",
            "classification": "medical_record",
            "origin": "derived",
            "evidence": {"snippet": value},
        }
    )


def _populate_visit_observations_actions_from_segments(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
) -> None:
    for visit in assigned_visits:
        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        visit_fields = visit.get("fields")
        if not isinstance(visit_fields, list):
            visit_fields = []
            visit["fields"] = visit_fields

        existing_keys = {
            field.get("key")
            for field in visit_fields
            if isinstance(field, dict) and isinstance(field.get("key"), str)
        }

        observation_value, action_value = _split_segment_into_observations_actions(
            segment_text=segment_text
        )
        if "observations" not in existing_keys and isinstance(observation_value, str):
            _append_visit_segment_summary_field(
                visit_fields=visit_fields,
                visit_id=visit_id,
                key="observations",
                value=observation_value,
            )

        if "actions" not in existing_keys and isinstance(action_value, str):
            _append_visit_segment_summary_field(
                visit_fields=visit_fields,
                visit_id=visit_id,
                key="actions",
                value=action_value,
            )


def _build_visit_segment_text_by_visit_id(
    *,
    raw_text: str | None,
    visit_occurrences_by_date: dict[str, list[dict[str, object]]],
    raw_text_date_occurrences: list[tuple[str, int]],
    visit_boundary_offsets: list[int],
) -> dict[str, str]:
    if not isinstance(raw_text, str) or not raw_text.strip():
        return {}

    ordered_anchor_offsets = [offset for _, offset in raw_text_date_occurrences]
    consumed_occurrences: dict[str, int] = {}
    visit_segments: dict[str, str] = {}

    for visit_date, anchor_offset in raw_text_date_occurrences:
        date_visits = visit_occurrences_by_date.get(visit_date, [])
        if not date_visits:
            continue

        visit_index = consumed_occurrences.get(visit_date, 0)
        if visit_index >= len(date_visits):
            visit_index = len(date_visits) - 1
        consumed_occurrences[visit_date] = consumed_occurrences.get(visit_date, 0) + 1

        target_visit = date_visits[visit_index]
        visit_id = target_visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue
        if visit_id in visit_segments:
            continue

        start_offset, end_offset = _resolve_visit_segment_bounds(
            anchor_offset=anchor_offset,
            raw_text=raw_text,
            visit_boundary_offsets=visit_boundary_offsets,
            ordered_anchor_offsets=ordered_anchor_offsets,
        )
        segment_text = raw_text[start_offset:end_offset].strip()
        if segment_text:
            visit_segments[visit_id] = segment_text

    return visit_segments


def _populate_missing_reason_for_visit_from_segments(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
) -> None:
    for visit in assigned_visits:
        reason_for_visit = visit.get("reason_for_visit")
        if isinstance(reason_for_visit, str) and reason_for_visit.strip():
            continue
        if reason_for_visit is not None and not isinstance(reason_for_visit, str):
            continue

        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        extracted_reason = _extract_reason_for_visit_from_segment(segment_text=segment_text)
        if extracted_reason is not None:
            visit["reason_for_visit"] = extracted_reason


def _populate_visit_scoped_fields_from_segment_candidates(
    *,
    assigned_visits: list[dict[str, object]],
    visit_segments_by_id: dict[str, str],
    candidate_keys: tuple[str, ...],
) -> None:
    for visit in assigned_visits:
        visit_id = visit.get("visit_id")
        if not isinstance(visit_id, str) or not visit_id:
            continue

        segment_text = visit_segments_by_id.get(visit_id)
        if not isinstance(segment_text, str) or not segment_text.strip():
            continue

        visit_fields = visit.get("fields")
        if not isinstance(visit_fields, list):
            visit_fields = []
            visit["fields"] = visit_fields

        existing_keys = {
            field.get("key")
            for field in visit_fields
            if isinstance(field, dict) and isinstance(field.get("key"), str)
        }

        mined_candidates = _mine_interpretation_candidates(segment_text)
        for candidate_key in candidate_keys:
            if candidate_key in existing_keys:
                continue

            key_candidates = mined_candidates.get(candidate_key)
            if not isinstance(key_candidates, list) or not key_candidates:
                continue

            selected_candidate = key_candidates[0]
            if candidate_key == "weight":
                weighted_candidates = [c for c in key_candidates if isinstance(c, dict)]
                if weighted_candidates:
                    selected_candidate = max(
                        weighted_candidates,
                        key=lambda candidate: (
                            float(candidate.get("evidence", {}).get("offset"))
                            if isinstance(candidate.get("evidence"), dict)
                            and isinstance(candidate.get("evidence", {}).get("offset"), int | float)
                            else -1.0
                        ),
                    )

            if not isinstance(selected_candidate, dict):
                continue

            candidate_value = selected_candidate.get("value")
            if not isinstance(candidate_value, str) or not candidate_value.strip():
                continue

            evidence = selected_candidate.get("evidence")
            visit_fields.append(
                {
                    "field_id": f"derived-{candidate_key}-{visit_id}",
                    "key": candidate_key,
                    "value": candidate_value,
                    "value_type": "string",
                    "scope": "visit",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "derived",
                    "evidence": evidence if isinstance(evidence, dict) else None,
                }
            )
            existing_keys.add(candidate_key)


def _normalize_canonical_review_scoping(
    data: dict[str, object], *, raw_text: str | None = None
) -> dict[str, object]:
    raw_fields = data.get("fields")
    if not isinstance(raw_fields, list):
        return data

    projected = dict(data)
    fields_to_keep: list[object] = []
    visit_scoped_fields: list[dict[str, object]] = []
    visit_group_metadata: dict[str, list[object]] = {}
    detected_visit_dates: list[str] = []
    seen_detected_visit_dates: set[str] = set()
    raw_text_detected_visit_dates = _detect_visit_dates_from_raw_text(raw_text=raw_text)
    raw_text_date_occurrences = _locate_visit_date_occurrences_from_raw_text(raw_text=raw_text)
    raw_text_offsets_by_date: dict[str, list[int]] = {}
    for normalized_date, offset in raw_text_date_occurrences:
        raw_text_offsets_by_date.setdefault(normalized_date, []).append(offset)
    visit_boundary_offsets = _locate_visit_boundary_offsets_from_raw_text(raw_text=raw_text)

    for item in raw_fields:
        if not isinstance(item, dict):
            fields_to_keep.append(item)
            continue

        key_raw = item.get("key")
        key = key_raw if isinstance(key_raw, str) else ""
        if key in _VISIT_GROUP_METADATA_KEY_SET:
            values = visit_group_metadata.setdefault(key, [])
            values.append(item.get("value"))
            if key == "visit_date":
                normalized_visit_date = _normalize_visit_date_candidate(item.get("value"))
                if (
                    normalized_visit_date is not None
                    and normalized_visit_date not in seen_detected_visit_dates
                ):
                    seen_detected_visit_dates.add(normalized_visit_date)
                    detected_visit_dates.append(normalized_visit_date)
            continue

        if key in _VISIT_SCOPED_KEY_SET:
            if key == "weight":
                field_scope = item.get("scope")
                field_section = item.get("section")
                is_explicit_visit_scoped = (
                    isinstance(field_scope, str) and field_scope.strip().casefold() == "visit"
                ) or (
                    isinstance(field_section, str) and field_section.strip().casefold() == "visits"
                )
                evidence_snippet = _extract_evidence_snippet(item)
                has_visit_date_evidence = bool(
                    _extract_visit_date_candidates_from_text(text=evidence_snippet)
                )
                if not is_explicit_visit_scoped and not has_visit_date_evidence:
                    # Keep header/global weight at document scope; do not force
                    # visit assignment only by key name.
                    fields_to_keep.append(item)
                    continue

            visit_field = dict(item)
            visit_field["scope"] = "visit"
            visit_field["section"] = "visits"
            visit_scoped_fields.append(visit_field)
            evidence_snippet = _extract_evidence_snippet(visit_field)
            for normalized_visit_date in _extract_visit_date_candidates_from_text(
                text=evidence_snippet
            ):
                if normalized_visit_date in seen_detected_visit_dates:
                    continue
                seen_detected_visit_dates.add(normalized_visit_date)
                detected_visit_dates.append(normalized_visit_date)
            continue

        fields_to_keep.append(item)

    for normalized_visit_date in raw_text_detected_visit_dates:
        if normalized_visit_date in seen_detected_visit_dates:
            continue
        seen_detected_visit_dates.add(normalized_visit_date)
        detected_visit_dates.append(normalized_visit_date)

    if not visit_scoped_fields and not visit_group_metadata and not raw_text_detected_visit_dates:
        return projected

    raw_visits = projected.get("visits")
    visits: list[dict[str, object]] = []
    if isinstance(raw_visits, list):
        for visit in raw_visits:
            if isinstance(visit, dict):
                visits.append(dict(visit))

    unassigned_visit: dict[str, object] | None = None
    assigned_visits: list[dict[str, object]] = []
    visit_by_date: dict[str, dict[str, object]] = {}
    visit_occurrences_by_date: dict[str, list[dict[str, object]]] = {}
    for visit in visits:
        visit_id = visit.get("visit_id")
        if isinstance(visit_id, str) and visit_id == "unassigned":
            unassigned_visit = visit
            continue

        existing_fields = visit.get("fields")
        if isinstance(existing_fields, list):
            visit["fields"] = list(existing_fields)
        else:
            visit["fields"] = []

        normalized_visit_date = _normalize_visit_date_candidate(visit.get("visit_date"))
        if normalized_visit_date is not None:
            visit["visit_date"] = normalized_visit_date
            visit_by_date.setdefault(normalized_visit_date, visit)
            visit_occurrences_by_date.setdefault(normalized_visit_date, []).append(visit)
            if normalized_visit_date not in seen_detected_visit_dates:
                seen_detected_visit_dates.add(normalized_visit_date)
                detected_visit_dates.append(normalized_visit_date)

        assigned_visits.append(visit)

    required_visit_sequence: list[str] = list(detected_visit_dates)
    raw_visit_occurrence_counts: dict[str, int] = {}
    for visit_date in raw_text_detected_visit_dates:
        raw_visit_occurrence_counts[visit_date] = raw_visit_occurrence_counts.get(visit_date, 0) + 1
    for visit_date, count in raw_visit_occurrence_counts.items():
        extra_occurrences = max(0, count - 1)
        if extra_occurrences > 0:
            required_visit_sequence.extend([visit_date] * extra_occurrences)

    generated_visit_counter = len(assigned_visits) + 1
    seen_required_occurrences: dict[str, int] = {}
    for visit_date in required_visit_sequence:
        occurrence_index = seen_required_occurrences.get(visit_date, 0) + 1
        seen_required_occurrences[visit_date] = occurrence_index

        existing_occurrences = len(visit_occurrences_by_date.get(visit_date, []))
        if existing_occurrences >= occurrence_index:
            continue

        generated_visit = {
            "visit_id": f"visit-{generated_visit_counter:03d}",
            "visit_date": visit_date,
            "admission_date": None,
            "discharge_date": None,
            "reason_for_visit": None,
            "fields": [],
        }
        generated_visit_counter += 1
        assigned_visits.append(generated_visit)
        visit_by_date.setdefault(visit_date, generated_visit)
        visit_occurrences_by_date.setdefault(visit_date, []).append(generated_visit)

    for visit in assigned_visits:
        for metadata_key in _VISIT_GROUP_METADATA_KEYS:
            if metadata_key not in visit:
                visit[metadata_key] = None

    if unassigned_visit is not None:
        existing_unassigned_fields = unassigned_visit.get("fields")
        if isinstance(existing_unassigned_fields, list):
            unassigned_visit["fields"] = list(existing_unassigned_fields)
        else:
            unassigned_visit["fields"] = []

    for visit_field in visit_scoped_fields:
        evidence_snippet = _extract_evidence_snippet(visit_field)
        evidence_visit_dates = _extract_visit_date_candidates_from_text(text=evidence_snippet)
        has_ambiguous_date_token = _contains_any_date_token(text=evidence_snippet)
        evidence_anchor_offset = _resolve_snippet_anchor_offset(
            raw_text=raw_text,
            snippet=evidence_snippet,
        )

        target_visit: dict[str, object] | None = None
        if evidence_visit_dates:
            target_visit = _resolve_visit_from_anchor(
                candidate_dates=evidence_visit_dates,
                anchor_offset=evidence_anchor_offset,
                visit_by_date=visit_by_date,
                visit_occurrences_by_date=visit_occurrences_by_date,
                raw_text_offsets_by_date=raw_text_offsets_by_date,
                visit_boundary_offsets=visit_boundary_offsets,
            )

        if (
            target_visit is None
            and not has_ambiguous_date_token
            and evidence_anchor_offset is not None
            and len(visit_by_date) > 1
        ):
            target_visit = _resolve_visit_from_anchor(
                candidate_dates=[],
                anchor_offset=evidence_anchor_offset,
                visit_by_date=visit_by_date,
                visit_occurrences_by_date=visit_occurrences_by_date,
                raw_text_offsets_by_date=raw_text_offsets_by_date,
                visit_boundary_offsets=visit_boundary_offsets,
            )

        if target_visit is None and len(visit_by_date) == 1 and not has_ambiguous_date_token:
            target_visit = next(iter(visit_by_date.values()))

        if target_visit is None:
            if unassigned_visit is None:
                unassigned_visit = {
                    "visit_id": "unassigned",
                    "visit_date": None,
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [],
                }
            unassigned_fields = unassigned_visit.get("fields")
            if not isinstance(unassigned_fields, list):
                unassigned_fields = []
                unassigned_visit["fields"] = unassigned_fields
            unassigned_fields.append(visit_field)
            continue

        target_visit_fields = target_visit.get("fields")
        if not isinstance(target_visit_fields, list):
            target_visit_fields = []
            target_visit["fields"] = target_visit_fields
        target_visit_fields.append(visit_field)

    visit_segments_by_id = _build_visit_segment_text_by_visit_id(
        raw_text=raw_text,
        visit_occurrences_by_date=visit_occurrences_by_date,
        raw_text_date_occurrences=raw_text_date_occurrences,
        visit_boundary_offsets=visit_boundary_offsets,
    )
    _populate_missing_reason_for_visit_from_segments(
        assigned_visits=assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
    )
    _populate_visit_scoped_fields_from_segment_candidates(
        assigned_visits=assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
        candidate_keys=("diagnosis", "symptoms", "medication", "procedure", "weight"),
    )
    _populate_visit_observations_actions_from_segments(
        assigned_visits=assigned_visits,
        visit_segments_by_id=visit_segments_by_id,
    )

    metadata_values_for_unassigned: dict[str, object] = {}
    for metadata_key in _VISIT_GROUP_METADATA_KEYS:
        values = visit_group_metadata.get(metadata_key, [])
        if metadata_key == "visit_date":
            for value in values:
                normalized_visit_date = _normalize_visit_date_candidate(value)
                if normalized_visit_date is None:
                    continue
                target_visit = visit_by_date.get(normalized_visit_date)
                if target_visit is None:
                    metadata_values_for_unassigned.setdefault(metadata_key, normalized_visit_date)
                    continue
                target_visit["visit_date"] = normalized_visit_date
            continue

        if values:
            metadata_values_for_unassigned.setdefault(metadata_key, values[0])

    if unassigned_visit is not None:
        for metadata_key in _VISIT_GROUP_METADATA_KEYS:
            if metadata_key in metadata_values_for_unassigned:
                unassigned_visit[metadata_key] = metadata_values_for_unassigned[metadata_key]
            elif metadata_key not in unassigned_visit:
                unassigned_visit[metadata_key] = None

    # --- Weight post-processing (hybrid rule) ---
    # (b) Move weight fields from unassigned back to document-scoped.
    unassigned_weight_fields_for_derivation: list[dict[str, object]] = []
    if unassigned_visit is not None:
        raw_unassigned_fields = unassigned_visit.get("fields")
        if isinstance(raw_unassigned_fields, list):
            weight_fields_in_unassigned = [
                f for f in raw_unassigned_fields if isinstance(f, dict) and f.get("key") == "weight"
            ]
            if weight_fields_in_unassigned:
                for wf in weight_fields_in_unassigned:
                    restored = dict(wf)
                    restored["scope"] = "document"
                    restored["section"] = "patient"
                    raw_val = restored.get("value")
                    normalized_val = _normalize_weight(raw_val)
                    if normalized_val:
                        restored["value"] = normalized_val
                    fields_to_keep.append(restored)
                    unassigned_weight_fields_for_derivation.append(restored)
                unassigned_visit["fields"] = [
                    f
                    for f in raw_unassigned_fields
                    if not (isinstance(f, dict) and f.get("key") == "weight")
                ]

    # (a) Derive document-level weight from most-recent visit.
    visit_weights: list[tuple[str, float, int, int, dict[str, object]]] = []
    for visit_index, visit in enumerate(assigned_visits):
        vf = visit.get("fields")
        if not isinstance(vf, list):
            continue
        for field_index, field in enumerate(vf):
            if isinstance(field, dict) and field.get("key") == "weight":
                effective_visit_date = _weight_effective_visit_date(
                    visit=visit,
                    weight_field=field,
                )
                if effective_visit_date is None:
                    continue
                visit_weights.append(
                    (
                        effective_visit_date,
                        _weight_evidence_offset(field),
                        visit_index,
                        field_index,
                        field,
                    )
                )

    # Include unassigned weights when they can be temporally anchored by evidence date.
    # This prevents losing the true latest weight if assignment to a visit failed.
    for unassigned_index, unassigned_weight in enumerate(unassigned_weight_fields_for_derivation):
        effective_date = _normalize_visit_date_candidate(
            _extract_evidence_snippet(unassigned_weight)
        )
        if effective_date is None:
            continue
        visit_weights.append(
            (
                effective_date,
                _weight_evidence_offset(unassigned_weight),
                len(assigned_visits),
                unassigned_index,
                unassigned_weight,
            )
        )

    latest_weight_from_raw = _extract_latest_visit_weight_from_raw_text(raw_text)
    if latest_weight_from_raw is not None:
        visit_weights.append(
            (
                str(latest_weight_from_raw["date"]),
                -1.0,
                len(assigned_visits) + 1,
                0,
                {
                    "value": latest_weight_from_raw["value"],
                    "value_type": "string",
                    "classification": "medical_record",
                    "evidence": latest_weight_from_raw["evidence"],
                },
            )
        )

    if visit_weights:
        visit_weights.sort(key=lambda entry: (entry[0], entry[1], entry[2], entry[3]))
        most_recent_weight = visit_weights[-1][4]
        fields_to_keep = [
            f for f in fields_to_keep if not (isinstance(f, dict) and f.get("key") == "weight")
        ]
        raw_derived_val = most_recent_weight.get("value")
        normalized_derived_val = _normalize_weight(raw_derived_val)
        fields_to_keep.append(
            {
                "field_id": "derived-weight-current",
                "key": "weight",
                "value": normalized_derived_val if normalized_derived_val else raw_derived_val,
                "value_type": most_recent_weight.get("value_type", "string"),
                "scope": "document",
                "section": "patient",
                "classification": most_recent_weight.get("classification", "medical_record"),
                "origin": "derived",
                "evidence": most_recent_weight.get("evidence"),
            }
        )

    assigned_visits.sort(
        key=lambda visit: (
            str(visit.get("visit_date") or "9999-12-31"),
            str(visit.get("visit_id") or ""),
        )
    )

    normalized_visits: list[dict[str, object]] = list(assigned_visits)
    if unassigned_visit is not None:
        unassigned_fields = unassigned_visit.get("fields")
        has_unassigned_fields = isinstance(unassigned_fields, list) and any(
            isinstance(field, dict) for field in unassigned_fields
        )
        has_unassigned_metadata = any(
            unassigned_visit.get(metadata_key) not in (None, "")
            for metadata_key in _VISIT_GROUP_METADATA_KEYS
        )
        if has_unassigned_fields or has_unassigned_metadata:
            normalized_visits.append(unassigned_visit)

    projected["fields"] = fields_to_keep
    projected["visits"] = normalized_visits
    return projected


@dataclass(frozen=True, slots=True)
class ReviewToggleResult:
    document_id: str
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


def mark_document_reviewed(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
    reviewed_by: str | None = None,
) -> ReviewToggleResult | None:
    logger.info("mark_document_reviewed called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.REVIEWED:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reviewed_at = now_provider()
    latest_completed_run = repository.get_latest_completed_run(document_id)
    reviewed_run_id = latest_completed_run.run_id if latest_completed_run is not None else None
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.REVIEWED.value,
        updated_at=reviewed_at,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        reviewed_run_id=reviewed_run_id,
    )
    if updated is None:
        return None

    _apply_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=reviewed_run_id,
        repository=repository,
        created_at=reviewed_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )


def reopen_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
) -> ReviewToggleResult | None:
    logger.info("reopen_document_review called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.IN_REVIEW:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reopened_at = now_provider()
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.IN_REVIEW.value,
        updated_at=reopened_at,
        reviewed_at=None,
        reviewed_by=None,
        reviewed_run_id=None,
    )
    if updated is None:
        return None

    _revert_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=document.reviewed_run_id,
        repository=repository,
        created_at=reopened_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )
