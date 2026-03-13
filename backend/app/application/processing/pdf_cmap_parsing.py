"""CMap parsing helpers for fallback PDF extraction."""

from __future__ import annotations

import re

from . import pdf_fallback_shared as shared
from .pdf_page_structure import _extract_object_stream

_CODESPACE_RANGE_PATTERN = re.compile(
    rb"\d+\s+begincodespacerange(.*?)endcodespacerange",
    re.DOTALL,
)
_BFCHAR_BLOCK_PATTERN = re.compile(rb"\d+\s+beginbfchar(.*?)endbfchar", re.DOTALL)
_BFRANGE_BLOCK_PATTERN = re.compile(rb"\d+\s+beginbfrange(.*?)endbfrange", re.DOTALL)
_HEX_PAIR_PATTERN = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_BFRANGE_INLINE_PATTERN = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_BFRANGE_ARRAY_PATTERN = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*)\]")
_BFRANGE_ARRAY_ENTRY_PATTERN = re.compile(rb"<([0-9A-Fa-f]+)>")


def _parse_tounicode_cmap(chunk: bytes) -> shared.PdfCMap | None:
    if b"begincmap" not in chunk:
        return None

    code_lengths: set[int] = set()
    for block in _CODESPACE_RANGE_PATTERN.findall(chunk):
        for start_hex, _ in _HEX_PAIR_PATTERN.findall(block):
            code_lengths.add(max(1, len(start_hex) // 2))
    if not code_lengths:
        code_lengths.add(1)

    mapping: dict[int, str] = {}
    for block in _BFCHAR_BLOCK_PATTERN.findall(chunk):
        for src_hex, dst_hex in _HEX_PAIR_PATTERN.findall(block):
            mapping[int(src_hex, 16)] = _decode_unicode_hex(dst_hex)

    for block in _BFRANGE_BLOCK_PATTERN.findall(chunk):
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue

            inline_match = _BFRANGE_INLINE_PATTERN.match(line)
            if inline_match:
                start_hex, end_hex, dst_start_hex = inline_match.groups()
                start = int(start_hex, 16)
                end = int(end_hex, 16)
                dst_start = int(dst_start_hex, 16)
                for offset, code in enumerate(range(start, end + 1)):
                    mapping[code] = _decode_unicode_hex(
                        f"{dst_start + offset:0{len(dst_start_hex)}X}".encode("ascii")
                    )
                continue

            array_match = _BFRANGE_ARRAY_PATTERN.match(line)
            if not array_match:
                continue
            start_hex, end_hex, destinations = array_match.groups()
            destination_values = _BFRANGE_ARRAY_ENTRY_PATTERN.findall(destinations)
            for offset, code in enumerate(range(int(start_hex, 16), int(end_hex, 16) + 1)):
                if offset >= len(destination_values):
                    break
                mapping[code] = _decode_unicode_hex(destination_values[offset])

    if not mapping:
        return None
    return shared.PdfCMap(
        codepoints=mapping,
        code_lengths=tuple(sorted(code_lengths, reverse=True)),
    )


def _decode_unicode_hex(hex_value: bytes) -> str:
    if len(hex_value) % 2 == 1:
        hex_value = b"0" + hex_value
    raw = bytes.fromhex(hex_value.decode("ascii"))
    if len(raw) % 2 == 0 and len(raw) >= 2:
        try:
            return raw.decode("utf-16-be")
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1", errors="ignore")


def _extract_cmaps_by_object(objects: dict[int, bytes]) -> dict[int, shared.PdfCMap]:
    cmaps: dict[int, shared.PdfCMap] = {}
    for object_id, object_payload in objects.items():
        if shared.deadline_exceeded():
            break
        stream = _extract_object_stream(object_payload, max_bytes=shared.MAX_CMAP_STREAM_BYTES)
        if stream is None:
            continue
        cmap = _parse_tounicode_cmap(stream)
        if cmap is not None:
            cmaps[object_id] = cmap
    return cmaps
