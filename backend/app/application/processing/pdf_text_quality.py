"""Text quality helpers for fallback PDF extraction."""

from __future__ import annotations

import re

from .constants import _WHITESPACE_PATTERN


def _sanitize_text_chunks(chunks: list[str]) -> list[str]:
    sanitized: list[str] = []
    for chunk in chunks:
        cleaned = chunk.replace("\x00", "").replace("\ufeff", "")
        normalized = _normalize_candidate_text(cleaned)
        if not normalized:
            continue
        if sanitized and normalized == sanitized[-1]:
            continue
        if len(normalized) <= 2 and normalized.isalpha():
            sanitized.append(normalized)
            continue
        if _is_readable_text_chunk(normalized):
            sanitized.append(normalized)
    return sanitized


def _stitch_text_chunks(chunks: list[str]) -> str:
    if not chunks:
        return ""

    first = chunks[0].strip()
    if not first:
        return ""

    pieces: list[str] = [first]
    tail = first[-80:]
    for chunk in chunks[1:]:
        current = chunk.strip()
        if not current:
            continue

        if _should_join_without_space(tail, current):
            pieces.append(current)
            tail = (tail + current)[-80:]
            continue
        if tail.endswith((" ", "\n")):
            pieces.append(current)
            tail = (tail + current)[-80:]
            continue

        pieces.append(" ")
        pieces.append(current)
        tail = (tail + " " + current)[-80:]

    stitched = "".join(pieces)
    stitched = re.sub(r"\s+([,.;:!?])", r"\1", stitched)
    stitched = re.sub(r"\(\s+", "(", stitched)
    stitched = re.sub(r"\s+\)", ")", stitched)
    return _WHITESPACE_PATTERN.sub(" ", stitched).strip()


def _should_join_without_space(previous: str, current: str) -> bool:
    if not previous:
        return True
    prev_char = previous[-1]
    cur_char = current[0]

    if cur_char in ",.;:!?)]}":
        return True
    if prev_char in "([{" or prev_char == "-" or cur_char == "-":
        return True
    if prev_char.isalpha() and cur_char.isalpha():
        prev_word_match = re.search(r"([A-Za-zÀ-ÿ]+)$", previous)
        cur_word_match = re.match(r"([A-Za-zÀ-ÿ]+)", current)
        if prev_word_match and cur_word_match:
            prev_word = prev_word_match.group(1)
            cur_word = cur_word_match.group(1)
            if len(prev_word) <= 3 or len(cur_word) <= 2:
                return True
            if prev_word.isupper() and cur_word.isupper():
                return True
    return False


def _is_readable_text_chunk(chunk: str) -> bool:
    if len(chunk) < 3:
        return False

    letters = sum(char.isalpha() for char in chunk)
    digits = sum(char.isdigit() for char in chunk)
    punctuation = sum((not char.isalnum()) and (not char.isspace()) for char in chunk)
    if letters == 0:
        return False

    length = len(chunk)
    letter_ratio = letters / length
    digit_ratio = digits / length
    punctuation_ratio = punctuation / length
    vowels = sum(char.lower() in "aeiouáéíóúü" for char in chunk if char.isalpha())
    vowel_ratio = vowels / letters
    uppercase_letters = sum(char.isupper() for char in chunk if char.isalpha())
    uppercase_ratio = uppercase_letters / letters
    score = _decoded_text_score(chunk)

    if score < 1.1 or letter_ratio < 0.45 or digit_ratio > 0.15 or punctuation_ratio > 0.25:
        return False
    if vowel_ratio < 0.25:
        return False
    if len(chunk) > 12 and uppercase_ratio > 0.8 and vowel_ratio < 0.4:
        return False
    if "'" in chunk and chunk.count("'") > max(1, len(chunk) // 60):
        return False
    return _max_consonant_run(chunk) <= 5


def _max_consonant_run(text: str) -> int:
    max_run = 0
    current_run = 0
    vowels = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")
    for char in text:
        if not char.isalpha() or char in vowels:
            current_run = 0
            continue
        current_run += 1
        if current_run > max_run:
            max_run = current_run
    return max_run


def _decoded_text_score(text: str) -> float:
    letters = sum(char.isalpha() for char in text)
    if letters == 0:
        return -100.0
    spaces = sum(char.isspace() for char in text)
    punctuation = sum((not char.isalnum()) and (not char.isspace()) for char in text)
    vowels = sum(char.lower() in "aeiouáéíóúü" for char in text if char.isalpha())
    length = len(text)
    space_ratio = (spaces / length) * 0.5
    punct_ratio = (punctuation / length) * 1.5
    return letters / length + vowels / letters + space_ratio - punct_ratio


def _normalize_candidate_text(text: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", text).strip()
