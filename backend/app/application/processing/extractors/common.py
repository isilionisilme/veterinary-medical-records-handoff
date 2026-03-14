"""Shared context and collector helpers for candidate mining extractors."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from ...field_normalizers import SPECIES_TOKEN_TO_CANONICAL
from ..constants import (
    _ADDRESS_LIKE_PATTERN,
    _MICROCHIP_DIGITS_PATTERN,
    _OWNER_CONTEXT_PATTERN,
    _VET_OR_CLINIC_CONTEXT_PATTERN,
    _WHITESPACE_PATTERN,
    COVERAGE_CONFIDENCE_FALLBACK,
    COVERAGE_CONFIDENCE_LABEL,
)
from ..date_parsing import (
    _normalize_person_fragment,
    _split_owner_before_address_tokens,
)
from ..field_patterns import (
    _AMBIGUOUS_ADDRESS_CONTEXT_WINDOW_LINES,
    _CLINIC_ADDRESS_CONTEXT_RE,
    _OWNER_ADDRESS_CONTEXT_RE,
    _WEIGHT_DOSAGE_GUARD_RE,
    _WEIGHT_EXPLICIT_CONTEXT_RE,
    _WEIGHT_LAB_GUARD_RE,
    _WEIGHT_PRICE_GUARD_RE,
)


@dataclass(frozen=True)
class MiningContext:
    raw_text: str
    compact_text: str
    lines: list[str]

    @classmethod
    def from_raw_text(cls, raw_text: str) -> MiningContext:
        compact_text = _WHITESPACE_PATTERN.sub(" ", raw_text).strip()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return cls(raw_text=raw_text, compact_text=compact_text, lines=lines)

    @property
    def species_keywords(self) -> dict[str, str]:
        return SPECIES_TOKEN_TO_CANONICAL


class CandidateCollector:
    def __init__(self, context: MiningContext) -> None:
        self.context = context
        self.candidates: dict[str, list[dict[str, object]]] = defaultdict(list)
        self.seen_values: dict[str, set[str]] = defaultdict(set)

    def add_payloads(self, payloads: Iterable[dict[str, object]]) -> None:
        for payload in payloads:
            self.add_candidate(
                key=str(payload["key"]),
                value=str(payload["value"]),
                confidence=float(payload["confidence"]),
                snippet=str(payload["snippet"]),
            )

    def add_candidate(
        self,
        *,
        key: str,
        value: str,
        confidence: float,
        snippet: str,
        page: int | None = 1,
        anchor: str | None = None,
        anchor_priority: int = 0,
        target_reason: str | None = None,
    ) -> None:
        cleaned_value = self._normalize_candidate_value(key, value, snippet)
        if cleaned_value is None:
            return
        normalized_key = cleaned_value.casefold()
        if normalized_key in self.seen_values[key]:
            return
        self.seen_values[key].add(normalized_key)

        normalized_snippet = snippet.strip()
        snippet_offset = (
            self.context.raw_text.rfind(normalized_snippet) if normalized_snippet else -1
        )
        self.candidates[key].append(
            {
                "value": cleaned_value,
                "confidence": self._effective_confidence(confidence),
                "anchor": anchor,
                "anchor_priority": anchor_priority,
                "target_reason": target_reason,
                "evidence": {
                    "page": page,
                    "snippet": normalized_snippet[:220],
                    "offset": snippet_offset,
                },
            }
        )

    def line_index_for_snippet(self, snippet: str) -> int | None:
        first_line = snippet.splitlines()[0].strip() if snippet else ""
        if not first_line:
            return None
        for idx, line in enumerate(self.context.lines):
            if line == first_line:
                return idx
        return None

    def classify_address_context(self, line_index: int) -> str:
        start = max(0, line_index - _AMBIGUOUS_ADDRESS_CONTEXT_WINDOW_LINES)
        end = min(
            len(self.context.lines),
            line_index + _AMBIGUOUS_ADDRESS_CONTEXT_WINDOW_LINES + 1,
        )
        context_lines = (
            self.context.lines[start:line_index] + self.context.lines[line_index + 1 : end]
        )
        context_text = " ".join(context_lines).casefold()
        owner_hits = bool(_OWNER_ADDRESS_CONTEXT_RE.search(context_text))
        clinic_hits = bool(_CLINIC_ADDRESS_CONTEXT_RE.search(context_text))
        if owner_hits and not clinic_hits:
            return "owner"
        if clinic_hits and not owner_hits:
            return "clinic"
        return "ambiguous"

    def build(self) -> dict[str, list[dict[str, object]]]:
        return dict(self.candidates)

    def _normalize_candidate_value(self, key: str, value: str, snippet: str) -> str | None:
        cleaned_value = value.strip(" .,:;\t\r\n")
        if not cleaned_value:
            return None
        if key == "microchip_id":
            return self._normalize_microchip(cleaned_value, snippet)
        if key == "owner_name":
            return self._normalize_owner_name(cleaned_value, snippet)
        if key == "vet_name":
            return self._normalize_vet_name(cleaned_value)
        if key == "clinic_name":
            return self._normalize_clinic_name(cleaned_value, snippet)
        if key == "clinic_address" and not self._accept_clinic_address(snippet):
            return None
        if key == "owner_address" and not self._accept_owner_address(snippet):
            return None
        if key == "weight" and not self._accept_weight(snippet):
            return None
        return cleaned_value

    def _normalize_microchip(self, cleaned_value: str, snippet: str) -> str | None:
        digit_match = _MICROCHIP_DIGITS_PATTERN.search(cleaned_value)
        if digit_match is None:
            return None
        cleaned_value = digit_match.group(1)
        safe_collapsed = re.sub(r"[\s\-.]", "", snippet)
        if cleaned_value not in safe_collapsed:
            return None
        return cleaned_value

    def _normalize_owner_name(self, cleaned_value: str, snippet: str) -> str | None:
        cleaned_value = _split_owner_before_address_tokens(cleaned_value)
        normalized_person = _normalize_person_fragment(cleaned_value)
        if normalized_person is None:
            return None
        if _VET_OR_CLINIC_CONTEXT_PATTERN.search(snippet) is not None:
            return None
        return normalized_person

    def _normalize_vet_name(self, cleaned_value: str) -> str | None:
        normalized_person = _normalize_person_fragment(cleaned_value)
        if normalized_person is None or _ADDRESS_LIKE_PATTERN.search(normalized_person):
            return None
        return normalized_person

    def _normalize_clinic_name(self, cleaned_value: str, snippet: str) -> str | None:
        snippet_folded = snippet.casefold()
        if (
            "dirección" in snippet_folded
            or "direccion" in snippet_folded
            or "domicilio" in snippet_folded
        ):
            return None
        compact_clinic = cleaned_value.casefold()
        if _ADDRESS_LIKE_PATTERN.search(compact_clinic) and re.search(r"\d", compact_clinic):
            return None
        return cleaned_value

    def _accept_clinic_address(self, snippet: str) -> bool:
        snippet_folded = snippet.casefold()
        has_owner_context = _OWNER_CONTEXT_PATTERN.search(snippet_folded) is not None
        has_clinic_context = _CLINIC_ADDRESS_CONTEXT_RE.search(snippet_folded) is not None
        if has_owner_context and not has_clinic_context:
            return False
        has_generic_label = bool(
            re.search(r"\b(?:direcci[oó]n|domicilio|dir\.?)\s*[:\-]", snippet_folded)
        )
        has_explicit_clinic_label = bool(
            re.search(r"\b(?:direcci[oó]n|domicilio)\s+de\s+la\s+cl[ií]nica\b", snippet_folded)
        )
        if not has_generic_label or has_explicit_clinic_label:
            return True
        line_index = self.line_index_for_snippet(snippet)
        if line_index is None:
            return True
        prev_context = " ".join(self.context.lines[max(0, line_index - 2) : line_index]).casefold()
        return _OWNER_CONTEXT_PATTERN.search(prev_context) is None

    def _accept_owner_address(self, snippet: str) -> bool:
        snippet_folded = snippet.casefold()
        has_owner_context = _OWNER_ADDRESS_CONTEXT_RE.search(snippet_folded) is not None
        has_clinic_context = _CLINIC_ADDRESS_CONTEXT_RE.search(snippet_folded) is not None
        return not (has_clinic_context and not has_owner_context)

    def _accept_weight(self, snippet: str) -> bool:
        explicit_weight_context = _WEIGHT_EXPLICIT_CONTEXT_RE.search(snippet) is not None
        has_guard = any(
            pattern.search(snippet) is not None
            for pattern in (
                _WEIGHT_DOSAGE_GUARD_RE,
                _WEIGHT_LAB_GUARD_RE,
                _WEIGHT_PRICE_GUARD_RE,
            )
        )
        return (not has_guard) or explicit_weight_context

    @staticmethod
    def _effective_confidence(confidence: float) -> float:
        effective_confidence = (
            COVERAGE_CONFIDENCE_LABEL
            if confidence >= COVERAGE_CONFIDENCE_LABEL
            else COVERAGE_CONFIDENCE_FALLBACK
        )
        return round(min(max(effective_confidence, 0.0), 1.0), 2)
