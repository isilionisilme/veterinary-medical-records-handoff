"""Name normalization helpers for person-name extraction."""

from __future__ import annotations

from .constants import (
    _ADDRESS_LIKE_PATTERN,
    _LICENSE_ONLY_PATTERN,
    _NAME_TOKEN_PATTERN,
    _PHONE_LIKE_PATTERN,
    _WHITESPACE_PATTERN,
)


def _split_owner_before_address_tokens(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return ""

    address_markers = {
        "calle",
        "av",
        "av.",
        "avenida",
        "cp",
        "codigo",
        "postal",
        "no",
        "no.",
        "nº",
        "n°",
        "num",
        "num.",
        "número",
        "plaza",
        "pte",
        "pte.",
        "portal",
        "piso",
        "puerta",
    }
    for index, token in enumerate(tokens):
        normalized_token = token.casefold().strip(".,:;()[]{}")
        if (
            normalized_token == "codigo"
            and index + 1 < len(tokens)
            and tokens[index + 1].casefold().strip(".,:;()[]{}") == "postal"
        ):
            return " ".join(tokens[:index]).strip()
        if normalized_token.startswith("c/") or normalized_token in address_markers:
            return " ".join(tokens[:index]).strip()
    return text


def _normalize_person_fragment(fragment: str) -> str | None:
    value = _WHITESPACE_PATTERN.sub(" ", fragment).strip(" .,:;\t\r\n")
    if not value:
        return None
    if "@" in value or _PHONE_LIKE_PATTERN.search(value):
        return None
    if _LICENSE_ONLY_PATTERN.match(value):
        return None
    if _ADDRESS_LIKE_PATTERN.search(value):
        return None

    tokens = value.split()
    if not 2 <= len(tokens) <= 5:
        return None
    letter_tokens = [token for token in tokens if _NAME_TOKEN_PATTERN.match(token)]
    if len(letter_tokens) < max(2, int(len(tokens) * 0.6)):
        return None
    return " ".join(tokens)
