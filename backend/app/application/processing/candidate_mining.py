"""Candidate mining orchestration for interpretation extraction."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from . import candidate_ranking
from .constants import COVERAGE_CONFIDENCE_FALLBACK
from .date_parsing import (
    extract_date_candidates_with_classification,
    extract_regex_labeled_candidates,
    extract_timeline_document_date_candidates,
    extract_unanchored_document_date_candidates,
    extract_unlabeled_header_dob_candidates,
)
from .extractors import (
    CandidateCollector,
    MiningContext,
    extract_clinical_candidates,
    extract_identifier_candidates,
    extract_location_candidates,
    extract_person_candidates,
    extract_physical_candidates,
)

logger = logging.getLogger(__name__)


def _mine_interpretation_candidates(raw_text: str) -> dict[str, list[dict[str, object]]]:
    logger.debug("_mine_interpretation_candidates start chars=%d", len(raw_text))
    context = MiningContext.from_raw_text(raw_text)
    collector = CandidateCollector(context)
    _collect_external_candidates(context, collector)
    extract_identifier_candidates(context, collector)
    extract_person_candidates(context, collector)
    extract_location_candidates(context, collector)
    extract_clinical_candidates(context, collector)
    extract_physical_candidates(context, collector)
    return collector.build()


def _map_candidates_to_global_schema(
    candidate_bundle: Mapping[str, list[dict[str, object]]],
) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    logger.debug("_map_candidates_to_global_schema start")
    return candidate_ranking._map_candidates_to_global_schema(candidate_bundle)


def _candidate_sort_key(item: dict[str, object], key: str) -> tuple[float, float, float]:
    return candidate_ranking._candidate_sort_key(item, key)


def _collect_external_candidates(context: MiningContext, collector: CandidateCollector) -> None:
    logger.debug("_collect_external_candidates start lines=%d", len(context.lines))
    collector.add_payloads(extract_regex_labeled_candidates(context.raw_text))
    collector.add_payloads(
        extract_unlabeled_header_dob_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
        )
    )
    collector.add_payloads(
        extract_unanchored_document_date_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
        )
    )
    for date_candidate in extract_date_candidates_with_classification(context.raw_text):
        collector.add_candidate(
            key=str(date_candidate["target_key"]),
            value=str(date_candidate["value"]),
            confidence=float(date_candidate["confidence"]),
            snippet=str(date_candidate["snippet"]),
            page=1,
            anchor=(str(date_candidate["anchor"]) if date_candidate.get("anchor") else None),
            anchor_priority=int(date_candidate["anchor_priority"]),
            target_reason=str(date_candidate["target_reason"]),
        )
    for payload in extract_timeline_document_date_candidates(
        context.lines,
        confidence=COVERAGE_CONFIDENCE_FALLBACK,
    ):
        collector.add_candidate(
            key=str(payload["key"]),
            value=str(payload["value"]),
            confidence=float(payload["confidence"]),
            snippet=str(payload["snippet"]),
            target_reason=str(payload["target_reason"]),
        )
