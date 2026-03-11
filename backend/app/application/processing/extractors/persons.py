"""Person-focused candidate extraction helpers."""

from __future__ import annotations

from ..constants import COVERAGE_CONFIDENCE_LABEL
from ..date_parsing import extract_labeled_person_candidates, extract_owner_nombre_candidates
from .common import CandidateCollector, MiningContext


def extract_person_candidates(context: MiningContext, collector: CandidateCollector) -> None:
    collector.add_payloads(
        extract_labeled_person_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_LABEL,
        )
    )
    collector.add_payloads(
        extract_owner_nombre_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_LABEL,
        )
    )
