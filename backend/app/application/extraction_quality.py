"""Quality gate helpers for extracted text usability."""

from __future__ import annotations

import re

from backend.app.application.extraction_constants import (
    ALL_CAPS_MAX_SAMPLE,
    ALL_CAPS_RATIO_MAX,
    HUMAN_READABLE_LETTER_RATIO,
    HUMAN_READABLE_MIN_LENGTH,
    HUMAN_READABLE_PRINTABLE_RATIO,
    HUMAN_READABLE_STRANGE_CHAR_RATIO,
    LINEBREAK_MIN_TEXT_LENGTH,
    LINEBREAK_RATIO_MIN,
    LONG_TOKEN_MIN_LENGTH,
    LONG_TOKEN_MIN_SAMPLE,
    LONG_TOKEN_RATIO_MAX,
    PUNCTUATION_RATIO_MAX,
    QUALITY_MIN_TEXT_LENGTH,
    QUALITY_MIN_WORD_TOKENS,
    QUALITY_SCORE_THRESHOLD,
    SINGLE_LETTER_MIN_SAMPLE,
    SINGLE_LETTER_RATIO_MAX,
    VOWEL_RATIO_MIN,
    WHITESPACE_RATIO_MIN,
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
    if not text or len(text) < HUMAN_READABLE_MIN_LENGTH:
        return False
    printable = sum(char.isprintable() for char in text)
    if printable / len(text) < HUMAN_READABLE_PRINTABLE_RATIO:
        return False
    letters = sum(char.isalpha() for char in text)
    if letters == 0:
        return False
    if letters / len(text) < HUMAN_READABLE_LETTER_RATIO:
        return False
    strange = sum(
        not (char.isalnum() or char.isspace() or char in ".,;:!?()[]{}'\"-_/\\%&+*#@")
        for char in text
    )
    return strange / len(text) < HUMAN_READABLE_STRANGE_CHAR_RATIO


def is_usable_extracted_text(text: str) -> bool:
    _, quality_pass, _ = evaluate_extracted_text_quality(text)
    return quality_pass


def evaluate_extracted_text_quality(text: str) -> tuple[float, bool, list[str]]:
    normalized = normalize_candidate_text(text)
    early_failure = _evaluate_quality_prerequisites(normalized)
    if early_failure is not None:
        return early_failure

    metrics = _build_quality_metrics(text=text, normalized=normalized)
    score, reasons = _score_quality_metrics(normalized=normalized, metrics=metrics)
    suspicious_hits = metrics["suspicious_hits"]
    quality_pass = score >= QUALITY_SCORE_THRESHOLD and not suspicious_hits
    return score, quality_pass, reasons


def _evaluate_quality_prerequisites(normalized: str) -> tuple[float, bool, list[str]] | None:
    if len(normalized) < QUALITY_MIN_TEXT_LENGTH:
        return 0.0, False, ["TOO_SHORT"]

    if not looks_human_readable_text(normalized):
        return 0.0, False, ["NOT_HUMAN_READABLE"]

    word_like_tokens = re.findall(r"[A-Za-zÀ-ÿ]{3,}", normalized)
    if len(word_like_tokens) < QUALITY_MIN_WORD_TOKENS:
        return 0.0, False, ["TOO_FEW_WORDS"]

    letters = [char.lower() for char in normalized if char.isalpha()]
    if not letters:
        return 0.0, False, ["NO_LETTERS"]

    return None


def _build_quality_metrics(*, text: str, normalized: str) -> dict[str, object]:
    letters = [char.lower() for char in normalized if char.isalpha()]
    vowels = sum(char in "aeiouáéíóúü" for char in letters)
    punctuation = sum((not char.isalnum()) and (not char.isspace()) for char in normalized)
    tokens = re.findall(r"\b\w+\b", normalized)
    alpha_tokens = [token for token in tokens if any(char.isalpha() for char in token)]
    long_alpha_tokens = [token for token in alpha_tokens if len(token) >= LONG_TOKEN_MIN_LENGTH]
    single_alpha_tokens = [token for token in alpha_tokens if len(token) == 1 and token.isalpha()]
    uppercase_letters = sum(char.isupper() for char in normalized if char.isalpha())
    lowered_text = normalized.lower()
    suspicious_hits = [word for word in SUSPICIOUS_SUBSTITUTIONS if word in lowered_text]

    return {
        "letters": letters,
        "alpha_tokens": alpha_tokens,
        "vowel_ratio": vowels / len(letters),
        "punctuation_ratio": punctuation / len(normalized),
        "whitespace_ratio": sum(char.isspace() for char in text) / len(text),
        "newline_ratio": text.count("\n") / len(text),
        "long_alpha_ratio": len(long_alpha_tokens) / max(1, len(alpha_tokens)),
        "single_alpha_ratio": len(single_alpha_tokens) / max(1, len(alpha_tokens)),
        "uppercase_ratio": uppercase_letters / max(1, len(letters)),
        "suspicious_hits": suspicious_hits,
    }


def _score_quality_metrics(
    *,
    normalized: str,
    metrics: dict[str, object],
) -> tuple[float, list[str]]:
    score = 1.0
    reasons: list[str] = []
    alpha_tokens = metrics["alpha_tokens"]
    suspicious_hits = metrics["suspicious_hits"]

    rules = (
        (metrics["vowel_ratio"] < VOWEL_RATIO_MIN, 0.20, "LOW_VOWEL_RATIO"),
        (metrics["punctuation_ratio"] > PUNCTUATION_RATIO_MAX, 0.25, "HIGH_PUNCTUATION_RATIO"),
        (metrics["whitespace_ratio"] < WHITESPACE_RATIO_MIN, 0.20, "LOW_WHITESPACE_STRUCTURE"),
        (
            metrics["newline_ratio"] < LINEBREAK_RATIO_MIN
            and len(normalized) > LINEBREAK_MIN_TEXT_LENGTH,
            0.10,
            "LOW_LINEBREAK_STRUCTURE",
        ),
        (
            metrics["long_alpha_ratio"] > LONG_TOKEN_RATIO_MAX
            and len(alpha_tokens) >= LONG_TOKEN_MIN_SAMPLE,
            0.35,
            "EXCESS_LONG_TOKENS",
        ),
        (
            metrics["single_alpha_ratio"] > SINGLE_LETTER_RATIO_MAX
            and len(alpha_tokens) > SINGLE_LETTER_MIN_SAMPLE,
            0.35,
            "EXCESS_SINGLE_LETTER_TOKENS",
        ),
        (
            metrics["uppercase_ratio"] > ALL_CAPS_RATIO_MAX
            and len(alpha_tokens) < ALL_CAPS_MAX_SAMPLE,
            0.20,
            "SUSPICIOUS_ALL_CAPS_DENSITY",
        ),
        (bool(suspicious_hits), 0.40, "SUSPICIOUS_SUBSTITUTIONS"),
    )

    for condition, penalty, reason in rules:
        if not condition:
            continue
        score -= penalty
        reasons.append(reason)

    return score, reasons
