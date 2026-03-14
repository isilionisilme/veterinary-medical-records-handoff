"""Identifier-focused candidate extraction helpers."""

from __future__ import annotations

from ..constants import COVERAGE_CONFIDENCE_FALLBACK, COVERAGE_CONFIDENCE_LABEL
from ..date_parsing import (
    extract_clinical_record_candidates,
    extract_microchip_adjacent_line_candidates,
    extract_microchip_keyword_candidates,
    extract_ocr_microchip_candidates,
)
from .common import CandidateCollector, MiningContext


def extract_identifier_candidates(context: MiningContext, collector: CandidateCollector) -> None:
    collector.add_payloads(
        extract_microchip_keyword_candidates(context.raw_text, confidence=COVERAGE_CONFIDENCE_LABEL)
    )
    collector.add_payloads(
        extract_microchip_adjacent_line_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_LABEL,
        )
    )
    collector.add_payloads(
        extract_clinical_record_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_LABEL,
        )
    )
    collector.add_payloads(
        extract_ocr_microchip_candidates(
            context.raw_text,
            confidence=COVERAGE_CONFIDENCE_FALLBACK,
        )
    )
