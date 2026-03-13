"""Content tokenization helpers for fallback PDF extraction."""

from __future__ import annotations

import re

from . import pdf_fallback_shared as shared

_HEX_STRING_PATTERN = re.compile(rb"<([0-9A-Fa-f\s]+)>")
_WHITESPACE_BYTES_PATTERN = re.compile(rb"\s+")


def _decode_hex_string(content: bytes, start: int) -> tuple[bytes | None, int]:
    """Parse a PDF hex string starting after the opening '<'.

    Returns ``(decoded_bytes, next_index)`` or ``(None, next_index)``.
    """
    hex_end = content.find(b">", start)
    if hex_end == -1:
        return None, len(content)
    compact = _WHITESPACE_BYTES_PATTERN.sub(b"", content[start:hex_end])
    if not compact:
        return None, hex_end + 1
    if len(compact) % 2 == 1:
        compact = b"0" + compact
    try:
        return bytes.fromhex(compact.decode("ascii")), hex_end + 1
    except ValueError:
        return None, hex_end + 1


def _tokenize_pdf_content(content: bytes) -> list[object]:
    tokens: list[object] = []
    index = 0
    length = len(content)
    while index < length:
        if shared.deadline_exceeded():
            return tokens
        byte = content[index]

        if byte in b" \t\r\n\x00":
            index += 1
            continue
        if byte == 37:
            while index < length and content[index] not in b"\r\n":
                index += 1
            continue
        if byte == 40:
            parsed, index = _parse_pdf_literal_string_bytes(content, index + 1)
            tokens.append(parsed)
        elif byte == 91:
            parsed_array, index = _parse_pdf_array(content, index + 1)
            tokens.append(parsed_array)
        elif byte == 60 and index + 1 < length and content[index + 1] != 60:
            decoded, index = _decode_hex_string(content, index + 1)
            if decoded is None and index >= length:
                break
            if decoded is not None:
                tokens.append(decoded)
        else:
            token, index = _parse_word_or_name(content, index)
            if token is None:
                continue
            tokens.append(token)

        if len(tokens) >= shared.MAX_TOKENS_PER_STREAM:
            return tokens
    return tokens


def _parse_pdf_array(content: bytes, index: int) -> tuple[list[object], int]:
    values: list[object] = []
    length = len(content)
    while index < length:
        if shared.deadline_exceeded() or len(values) >= shared.MAX_ARRAY_ITEMS:
            return values, length
        byte = content[index]

        if byte in b" \t\r\n\x00":
            index += 1
            continue
        if byte == 93:
            return values, index + 1
        if byte == 40:
            parsed, index = _parse_pdf_literal_string_bytes(content, index + 1)
            values.append(parsed)
            continue
        if byte == 91:
            nested, index = _parse_pdf_array(content, index + 1)
            values.append(nested)
            continue
        if byte == 60 and index + 1 < length and content[index + 1] != 60:
            decoded, index = _decode_hex_string(content, index + 1)
            if decoded is None and index >= length:
                return values, length
            if decoded is not None:
                values.append(decoded)
            continue

        token, index = _parse_word_or_name(content, index)
        if token is not None:
            values.append(token)

    return values, length


def _parse_pdf_literal_string(blob: bytes, index: int) -> tuple[str, int]:
    raw, next_index = _parse_pdf_literal_string_bytes(blob, index)
    return raw.decode("utf-8", errors="ignore"), next_index


def _parse_pdf_literal_string_bytes(blob: bytes, index: int) -> tuple[bytes, int]:
    result = bytearray()
    depth = 1
    length = len(blob)

    while index < length:
        if shared.deadline_exceeded():
            return bytes(result), length
        byte = blob[index]
        index += 1

        if byte == 92:
            if index >= length:
                break
            escaped = blob[index]
            index += 1
            if escaped in (40, 41, 92):
                result.append(escaped)
                continue
            if escaped == 110:
                result.append(10)
                continue
            if escaped == 114:
                result.append(13)
                continue
            if escaped == 116:
                result.append(9)
                continue
            if escaped == 98:
                result.append(8)
                continue
            if escaped == 102:
                result.append(12)
                continue
            if 48 <= escaped <= 55:
                oct_digits = bytearray([escaped])
                for _ in range(2):
                    if index < length and 48 <= blob[index] <= 55:
                        oct_digits.append(blob[index])
                        index += 1
                    else:
                        break
                result.append(int(oct_digits.decode("ascii"), 8))
                continue
            result.append(escaped)
            continue

        if byte == 40:
            depth += 1
            result.append(byte)
            continue
        if byte == 41:
            depth -= 1
            if depth == 0:
                break
            result.append(byte)
            continue
        result.append(byte)

    return bytes(result), index


def _parse_number_token(token: str) -> int | float | None:
    if not token:
        return None
    try:
        if "." in token:
            return float(token)
        return int(token)
    except ValueError:
        return None


def _extract_pdf_text_tokens(chunk: bytes) -> list[tuple[int, bytes]]:
    tokens: list[tuple[int, bytes]] = []

    for hex_match in _HEX_STRING_PATTERN.finditer(chunk):
        compact = _WHITESPACE_BYTES_PATTERN.sub(b"", hex_match.group(1))
        if not compact:
            continue
        if len(compact) % 2 == 1:
            compact = b"0" + compact
        try:
            tokens.append((hex_match.start(), bytes.fromhex(compact.decode("ascii"))))
        except ValueError:
            continue

    index = 0
    length = len(chunk)
    while index < length:
        if chunk[index] != 40:
            index += 1
            continue
        start_index = index
        parsed, index = _parse_pdf_literal_string_bytes(chunk, index + 1)
        if parsed:
            tokens.append((start_index, parsed))

    tokens.sort(key=lambda item: item[0])
    return tokens


def _parse_word_or_name(content: bytes, index: int) -> tuple[object | None, int]:
    length = len(content)
    start = index
    if content[index] == 47:
        index += 1
        while index < length and content[index] not in b" \t\r\n[]()<>\x00":
            index += 1
        return content[start:index].decode("latin-1", errors="ignore"), index

    while index < length and content[index] not in b" \t\r\n[]()<>/\x00":
        index += 1
    if start == index:
        return None, index + 1
    word = content[start:index].decode("latin-1", errors="ignore")
    numeric = _parse_number_token(word)
    return numeric if numeric is not None else word, index
