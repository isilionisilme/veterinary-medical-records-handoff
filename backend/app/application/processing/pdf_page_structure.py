"""Page structure helpers for fallback PDF extraction."""

from __future__ import annotations

import re

from . import pdf_fallback_shared as shared

_PAGE_TYPE_PATTERN = re.compile(rb"/Type\s*/Page\b")
_PAGE_CONTENTS_ARRAY_PATTERN = re.compile(rb"/Contents\s*\[(.*?)\]", re.DOTALL)
_PAGE_CONTENTS_SINGLE_PATTERN = re.compile(rb"/Contents\s+(\d+)\s+\d+\s+R")
_PAGE_RESOURCES_REF_PATTERN = re.compile(rb"/Resources\s+(\d+)\s+\d+\s+R")
_PAGE_RESOURCES_INLINE_PATTERN = re.compile(rb"/Resources\s*<<(.*?)>>", re.DOTALL)
_OBJECT_REF_PATTERN = re.compile(rb"(\d+)\s+\d+\s+R")
_FONT_DICT_INLINE_PATTERN = re.compile(rb"/Font\s*<<(.*?)>>", re.DOTALL)
_FONT_DICT_REF_PATTERN = re.compile(rb"/Font\s+(\d+)\s+0\s+R")
_FONT_ENTRY_PATTERN = re.compile(rb"/([^\s/<>{}\[\]()]+)\s+(\d+)\s+0\s+R")
_TOUNICODE_REF_PATTERN = re.compile(rb"/ToUnicode\s+(\d+)\s+0\s+R")
_OBJECT_STREAM_PATTERN = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)


def _collect_page_content_streams(
    *,
    objects: dict[int, bytes],
    cmap_by_object: dict[int, shared.PdfCMap],
) -> list[tuple[bytes, dict[str, shared.PdfCMap]]]:
    page_streams: list[tuple[bytes, dict[str, shared.PdfCMap]]] = []
    for page_payload in objects.values():
        if not _PAGE_TYPE_PATTERN.search(page_payload):
            continue

        font_to_cmap = _extract_font_to_cmap_for_page(
            page_payload=page_payload,
            objects=objects,
            cmap_by_object=cmap_by_object,
        )
        for content_object_id in _extract_page_content_object_ids(page_payload):
            content_payload = objects.get(content_object_id)
            if content_payload is None:
                continue
            stream = _extract_object_stream(content_payload)
            if stream is not None:
                page_streams.append((stream, font_to_cmap))
    return page_streams


def _extract_page_content_object_ids(page_payload: bytes) -> list[int]:
    array_match = _PAGE_CONTENTS_ARRAY_PATTERN.search(page_payload)
    if array_match:
        return [int(ref) for ref in _OBJECT_REF_PATTERN.findall(array_match.group(1))]

    single_match = _PAGE_CONTENTS_SINGLE_PATTERN.search(page_payload)
    if single_match:
        return [int(single_match.group(1))]
    return []


def _extract_font_to_cmap_for_page(
    *,
    page_payload: bytes,
    objects: dict[int, bytes],
    cmap_by_object: dict[int, shared.PdfCMap],
) -> dict[str, shared.PdfCMap]:
    resource_payload = _resolve_page_resources(page_payload=page_payload, objects=objects)
    if resource_payload is None:
        return {}
    return _build_font_to_cmap_from_page_resources(
        resource_payload=resource_payload,
        objects=objects,
        cmap_by_object=cmap_by_object,
    )


def _resolve_page_resources(*, page_payload: bytes, objects: dict[int, bytes]) -> bytes | None:
    inline_match = _PAGE_RESOURCES_INLINE_PATTERN.search(page_payload)
    if inline_match:
        return inline_match.group(1)

    ref_match = _PAGE_RESOURCES_REF_PATTERN.search(page_payload)
    if ref_match is None:
        return None
    return objects.get(int(ref_match.group(1)))


def _build_font_to_cmap_from_page_resources(
    *,
    resource_payload: bytes,
    objects: dict[int, bytes],
    cmap_by_object: dict[int, shared.PdfCMap],
) -> dict[str, shared.PdfCMap]:
    mapping: dict[str, shared.PdfCMap] = {}
    for font_name, font_object_id in _extract_font_entries_from_resource_payload(
        resource_payload=resource_payload,
        objects=objects,
    ).items():
        font_payload = objects.get(font_object_id)
        if font_payload is None:
            continue
        to_unicode_ref = _TOUNICODE_REF_PATTERN.search(font_payload)
        if to_unicode_ref is None:
            continue
        cmap = cmap_by_object.get(int(to_unicode_ref.group(1)))
        if cmap is not None:
            mapping[font_name] = cmap
    return mapping


def _extract_font_entries_from_resource_payload(
    *,
    resource_payload: bytes,
    objects: dict[int, bytes],
) -> dict[str, int]:
    font_name_to_font_object: dict[str, int] = {}

    for inline_dict in _FONT_DICT_INLINE_PATTERN.findall(resource_payload):
        for font_name, font_object in _FONT_ENTRY_PATTERN.findall(inline_dict):
            parsed_name = font_name.decode("ascii", "ignore")
            if parsed_name:
                font_name_to_font_object[parsed_name] = int(font_object)

    for font_dict_object in _FONT_DICT_REF_PATTERN.findall(resource_payload):
        referenced = objects.get(int(font_dict_object))
        if referenced is None:
            continue
        for font_name, font_object in _FONT_ENTRY_PATTERN.findall(referenced):
            parsed_name = font_name.decode("ascii", "ignore")
            if parsed_name:
                font_name_to_font_object[parsed_name] = int(font_object)

    return font_name_to_font_object


def _extract_object_stream(object_payload: bytes, max_bytes: int | None = None) -> bytes | None:
    match = _OBJECT_STREAM_PATTERN.search(object_payload)
    if match is None:
        return None
    raw_stream = match.group(1)
    if max_bytes is not None and len(raw_stream) > max_bytes:
        return None
    inflated = shared.inflate_pdf_stream(raw_stream)
    if inflated is not None:
        if max_bytes is not None and len(inflated) > max_bytes:
            return None
        return inflated
    if _looks_textual_bytes(raw_stream) and b"BT" in raw_stream and b"ET" in raw_stream:
        return raw_stream
    return None


def _looks_textual_bytes(payload: bytes) -> bool:
    if not payload:
        return False
    printable = sum((32 <= byte <= 126) or byte in (9, 10, 13) for byte in payload)
    return printable / len(payload) >= 0.75
