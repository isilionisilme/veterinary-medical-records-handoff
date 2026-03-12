"""Quality gate helpers for extracted text usability."""

from __future__ import annotations

import re

from backend.app.application.extraction_constants import (
    QUALITY_SCORE_THRESHOLD,
)

SUSPICIOUS_SUBSTITUTIONS = (
    "dratamiento",
    "draquea",
    "diene",
)
_WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_candidate_text(text: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def looks_human_readable_text(text: str) -> bool:
    if not text or len(text) < 3:
        return False
    printable = sum(char.isprintable() for char in text)
    if printable / len(text) < 0.9:
        return False
    letters = sum(char.isalpha() for char in text)
    if letters == 0:
        return False
    if letters / len(text) < 0.35:
        return False
    strange = sum(
        not (char.isalnum() or char.isspace() or char in ".,;:!?()[]{}'\"-_/\\%&+*#@")
        for char in text
    )
    return strange / len(text) < 0.15


def is_usable_extracted_text(text: str) -> bool:
    _, quality_pass, _ = evaluate_extracted_text_quality(text)
    return quality_pass


def evaluate_extracted_text_quality(text: str) -> tuple[float, bool, list[str]]:
    normalized = normalize_candidate_text(text)
    if len(normalized) < 20:
        return 0.0, False, ["TOO_SHORT"]

    if not looks_human_readable_text(normalized):
        return 0.0, False, ["NOT_HUMAN_READABLE"]

    word_like_tokens = re.findall(r"[A-Za-zÀ-ÿ]{3,}", normalized)
    if len(word_like_tokens) < 3:
        return 0.0, False, ["TOO_FEW_WORDS"]

    letters = [char.lower() for char in normalized if char.isalpha()]
    if not letters:
        return 0.0, False, ["NO_LETTERS"]

    vowels = sum(char in "aeiouáéíóúü" for char in letters)
    vowel_ratio = vowels / len(letters)
    punctuation = sum((not char.isalnum()) and (not char.isspace()) for char in normalized)
    punctuation_ratio = punctuation / len(normalized)
    whitespace_ratio = sum(char.isspace() for char in text) / len(text)
    newline_ratio = text.count("\n") / len(text)
    tokens = re.findall(r"\b\w+\b", normalized)
    alpha_tokens = [token for token in tokens if any(char.isalpha() for char in token)]
    long_alpha_tokens = [token for token in alpha_tokens if len(token) >= 12]
    single_alpha_tokens = [token for token in alpha_tokens if len(token) == 1 and token.isalpha()]
    single_alpha_ratio = len(single_alpha_tokens) / max(1, len(alpha_tokens))
    long_alpha_ratio = len(long_alpha_tokens) / max(1, len(alpha_tokens))
    uppercase_letters = sum(char.isupper() for char in normalized if char.isalpha())
    uppercase_ratio = uppercase_letters / max(1, len(letters))
    lowered_text = normalized.lower()
    suspicious_hits = [word for word in SUSPICIOUS_SUBSTITUTIONS if word in lowered_text]

    score = 1.0
    reasons: list[str] = []

    if vowel_ratio < 0.30:
        score -= 0.20
        reasons.append("LOW_VOWEL_RATIO")
    if punctuation_ratio > 0.25:
        score -= 0.25
        reasons.append("HIGH_PUNCTUATION_RATIO")
    if whitespace_ratio < 0.10:
        score -= 0.20
        reasons.append("LOW_WHITESPACE_STRUCTURE")
    if newline_ratio < 0.0005 and len(normalized) > 800:
        score -= 0.10
        reasons.append("LOW_LINEBREAK_STRUCTURE")
    if long_alpha_ratio > 0.20 and len(alpha_tokens) >= 80:
        score -= 0.35
        reasons.append("EXCESS_LONG_TOKENS")
    if single_alpha_ratio > 0.045 and len(alpha_tokens) > 120:
        score -= 0.35
        reasons.append("EXCESS_SINGLE_LETTER_TOKENS")
    if uppercase_ratio > 0.80 and len(alpha_tokens) < 250:
        score -= 0.20
        reasons.append("SUSPICIOUS_ALL_CAPS_DENSITY")
    if suspicious_hits:
        score -= 0.40
        reasons.append("SUSPICIOUS_SUBSTITUTIONS")

    quality_pass = score >= QUALITY_SCORE_THRESHOLD and not suspicious_hits
    return score, quality_pass, reasons
