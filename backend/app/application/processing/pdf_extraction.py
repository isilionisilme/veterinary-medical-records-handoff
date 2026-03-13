"""PDF extraction dispatcher and compatibility surface."""

from __future__ import annotations

import logging
from pathlib import Path

from backend.app.settings import get_pdf_extractor_force

from . import pdf_cmap_parsing as _cmap
from . import pdf_content_tokenizer as _tokenizer
from . import pdf_extraction_nodeps as nodeps
from . import pdf_fallback_shared as _shared
from . import pdf_page_structure as _page
from . import pdf_text_decoder as _decoder
from . import pdf_text_quality as _quality
from .constants import PDF_EXTRACTOR_FORCE_ENV

logger = logging.getLogger(__name__)

# Explicit compatibility surface for tests and processing_runner consumers.
PdfCMap = _shared.PdfCMap
parse_tounicode_cmap = _cmap._parse_tounicode_cmap
extract_pdf_text_tokens = _tokenizer._extract_pdf_text_tokens
tokenize_pdf_content = _tokenizer._tokenize_pdf_content
parse_pdf_array = _tokenizer._parse_pdf_array
parse_pdf_literal_string = _tokenizer._parse_pdf_literal_string
parse_pdf_literal_string_bytes = _tokenizer._parse_pdf_literal_string_bytes
decode_bytes_with_cmap = _decoder._decode_bytes_with_cmap
decode_tj_array_for_font = _decoder._decode_tj_array_for_font
decode_token_for_font = _decoder._decode_token_for_font
extract_text_chunks_from_content_stream = _decoder._extract_text_chunks_from_content_stream
sanitize_text_chunks = _quality._sanitize_text_chunks
stitch_text_chunks = _quality._stitch_text_chunks
should_join_without_space = _quality._should_join_without_space
looks_textual_bytes = _page._looks_textual_bytes
collect_page_content_streams = _page._collect_page_content_streams
parse_pdf_objects = nodeps._parse_pdf_objects
extract_cmaps_by_object = _cmap._extract_cmaps_by_object
inflate_pdf_stream = _shared.inflate_pdf_stream


def _extract_pdf_text(file_path: Path) -> str:
    text, _ = _extract_pdf_text_with_extractor(file_path)
    return text


def extract_text_from_pdf(file_path: Path) -> str:
    """Public compatibility alias used by legacy imports/checks."""

    return _extract_pdf_text(file_path)


def _extract_pdf_text_with_extractor(file_path: Path) -> tuple[str, str]:
    forced = get_pdf_extractor_force().lower()
    if forced not in ("", "auto", "fitz", "fallback"):
        logger.warning(
            "Unknown %s value '%s'; using auto mode",
            PDF_EXTRACTOR_FORCE_ENV,
            forced,
        )
        forced = "auto"

    if forced == "fallback":
        return _extract_pdf_text_without_external_dependencies(file_path), "fallback"

    if forced == "fitz":
        try:
            return _extract_pdf_text_with_fitz(file_path), "fitz"
        except ImportError as exc:
            from .orchestrator import ProcessingError

            raise ProcessingError("EXTRACTION_FAILED") from exc

    try:
        return _extract_pdf_text_with_fitz(file_path), "fitz"
    except ImportError:
        return _extract_pdf_text_without_external_dependencies(file_path), "fallback"


def _extract_pdf_text_with_fitz(file_path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ImportError("PyMuPDF is not installed") from exc

    try:
        with fitz.open(file_path) as document:
            parts = [page.get_text("text") for page in document]
    except Exception as exc:  # pragma: no cover - defensive
        from .orchestrator import ProcessingError

        raise ProcessingError("EXTRACTION_FAILED") from exc

    return "\n".join(parts)


def _extract_pdf_text_without_external_dependencies(file_path: Path) -> str:
    """Wrapper keeps monkeypatch compatibility for tests targeting this module."""

    try:
        return nodeps._extract_pdf_text_without_external_dependencies(
            file_path,
            parse_pdf_objects=parse_pdf_objects,
            extract_cmaps_by_object=extract_cmaps_by_object,
            collect_page_content_streams=collect_page_content_streams,
            inflate_pdf_stream=inflate_pdf_stream,
            extract_text_chunks_from_content_stream=extract_text_chunks_from_content_stream,
        )
    except OSError as exc:  # pragma: no cover - defensive
        from .orchestrator import ProcessingError

        raise ProcessingError("EXTRACTION_FAILED") from exc


extract_pdf_text = extract_text_from_pdf
extract_pdf_text_with_extractor = _extract_pdf_text_with_extractor
extract_pdf_text_without_external_dependencies = _extract_pdf_text_without_external_dependencies

__all__ = [
    "PDF_EXTRACTOR_FORCE_ENV",
    "PdfCMap",
    "collect_page_content_streams",
    "decode_bytes_with_cmap",
    "decode_tj_array_for_font",
    "decode_token_for_font",
    "extract_cmaps_by_object",
    "extract_pdf_text",
    "extract_pdf_text_tokens",
    "extract_pdf_text_with_extractor",
    "extract_pdf_text_without_external_dependencies",
    "extract_text_chunks_from_content_stream",
    "extract_text_from_pdf",
    "inflate_pdf_stream",
    "looks_textual_bytes",
    "parse_pdf_array",
    "parse_pdf_literal_string",
    "parse_pdf_literal_string_bytes",
    "parse_pdf_objects",
    "parse_tounicode_cmap",
    "sanitize_text_chunks",
    "should_join_without_space",
    "stitch_text_chunks",
    "tokenize_pdf_content",
]
