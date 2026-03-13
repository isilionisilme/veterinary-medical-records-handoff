"""Thin fallback PDF extraction orchestrator without external dependencies."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from . import pdf_fallback_shared as shared

_PDF_STREAM_PATTERN = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)
_OBJECT_PATTERN = re.compile(rb"(\d+)\s+(\d+)\s+obj(.*?)endobj", re.DOTALL)


def _deadline_exceeded() -> bool:
    return shared.deadline_exceeded()


def _inflate_pdf_stream(stream: bytes) -> bytes | None:
    return shared.inflate_pdf_stream(stream)


def _parse_pdf_objects(pdf_bytes: bytes) -> dict[int, bytes]:
    objects: dict[int, bytes] = {}
    for match in _OBJECT_PATTERN.finditer(pdf_bytes):
        objects[int(match.group(1))] = match.group(3)
    return objects


def _extract_pdf_text_without_external_dependencies(
    file_path: Path,
    *,
    parse_pdf_objects: Callable[[bytes], dict[int, bytes]] | None = None,
    extract_cmaps_by_object: Callable[[dict[int, bytes]], dict[int, shared.PdfCMap]] | None = None,
    collect_page_content_streams: Callable[..., list[tuple[bytes, dict[str, shared.PdfCMap]]]]
    | None = None,
    inflate_pdf_stream: Callable[[bytes], bytes | None] | None = None,
    extract_text_chunks_from_content_stream: Callable[..., list[str]] | None = None,
) -> str:
    from .pdf_cmap_parsing import _extract_cmaps_by_object
    from .pdf_page_structure import _collect_page_content_streams
    from .pdf_text_decoder import _extract_text_chunks_from_content_stream
    from .pdf_text_quality import _sanitize_text_chunks, _stitch_text_chunks

    _deadline_token = shared.start_extraction_deadline(shared.MAX_EXTRACTION_SECONDS)

    parse_pdf_objects_fn = parse_pdf_objects or _parse_pdf_objects
    extract_cmaps_by_object_fn = extract_cmaps_by_object or _extract_cmaps_by_object
    collect_page_content_streams_fn = collect_page_content_streams or _collect_page_content_streams
    inflate_pdf_stream_fn = inflate_pdf_stream or _inflate_pdf_stream
    extract_text_chunks_fn = (
        extract_text_chunks_from_content_stream or _extract_text_chunks_from_content_stream
    )

    try:
        pdf_bytes = file_path.read_bytes()
        objects = parse_pdf_objects_fn(pdf_bytes)
        cmap_by_object = extract_cmaps_by_object_fn(objects)
        page_streams = collect_page_content_streams_fn(
            objects=objects,
            cmap_by_object=cmap_by_object,
        )
        text_chunks: list[str] = []
        total_bytes = 0

        for chunk, font_to_cmap in page_streams:
            if _deadline_exceeded():
                break
            if not chunk or len(chunk) > shared.MAX_SINGLE_STREAM_BYTES:
                continue
            total_bytes += len(chunk)
            if total_bytes > shared.MAX_CONTENT_STREAM_BYTES:
                break
            text_chunks.extend(
                extract_text_chunks_fn(
                    chunk=chunk,
                    font_to_cmap=font_to_cmap,
                    fallback_cmaps=list(font_to_cmap.values()),
                )
            )
            if len(text_chunks) > shared.MAX_TEXT_CHUNKS:
                break

        if not page_streams:
            for match in _PDF_STREAM_PATTERN.finditer(pdf_bytes):
                if _deadline_exceeded():
                    break
                inflated = inflate_pdf_stream_fn(match.group(1))
                if inflated is None or b"BT" not in inflated or b"ET" not in inflated:
                    continue
                text_chunks.extend(
                    extract_text_chunks_fn(
                        chunk=inflated,
                        font_to_cmap={},
                        fallback_cmaps=[],
                    )
                )
                if len(text_chunks) > shared.MAX_TEXT_CHUNKS:
                    break

        return _stitch_text_chunks(_sanitize_text_chunks(text_chunks))
    finally:
        shared.restore_extraction_deadline(_deadline_token)
