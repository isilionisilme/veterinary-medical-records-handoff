from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.application.processing import pdf_extraction


def test_extract_pdf_text_returns_text_from_pair(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")
    monkeypatch.setattr(
        pdf_extraction,
        "_extract_pdf_text_with_extractor",
        lambda _path: ("texto", "fitz"),
    )

    assert pdf_extraction._extract_pdf_text(sample) == "texto"


def test_extract_pdf_text_with_extractor_handles_unknown_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")
    monkeypatch.setenv(pdf_extraction.PDF_EXTRACTOR_FORCE_ENV, "unexpected")
    monkeypatch.setattr(pdf_extraction, "_extract_pdf_text_with_fitz", lambda _path: "fitz text")

    text, extractor = pdf_extraction._extract_pdf_text_with_extractor(sample)

    assert extractor == "fitz"
    assert text == "fitz text"


def test_extract_pdf_text_with_extractor_force_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")
    monkeypatch.setenv(pdf_extraction.PDF_EXTRACTOR_FORCE_ENV, "fallback")
    monkeypatch.setattr(
        pdf_extraction,
        "_extract_pdf_text_without_external_dependencies",
        lambda _path: "fallback text",
    )

    text, extractor = pdf_extraction._extract_pdf_text_with_extractor(sample)

    assert extractor == "fallback"
    assert text == "fallback text"


def test_extract_pdf_text_with_extractor_force_fitz_import_error_raises_processing_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")
    monkeypatch.setenv(pdf_extraction.PDF_EXTRACTOR_FORCE_ENV, "fitz")
    monkeypatch.setattr(
        pdf_extraction,
        "_extract_pdf_text_with_fitz",
        lambda _path: (_ for _ in ()).throw(ImportError("missing fitz")),
    )

    from backend.app.application.processing.orchestrator import ProcessingError

    with pytest.raises(ProcessingError, match="EXTRACTION_FAILED"):
        pdf_extraction._extract_pdf_text_with_extractor(sample)


def test_extract_pdf_text_with_fitz_wraps_runtime_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")

    class _BrokenDoc:
        def __enter__(self):
            raise RuntimeError("cannot read")

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setitem(sys.modules, "fitz", SimpleNamespace(open=lambda _path: _BrokenDoc()))

    from backend.app.application.processing.orchestrator import ProcessingError

    with pytest.raises(ProcessingError, match="EXTRACTION_FAILED"):
        pdf_extraction._extract_pdf_text_with_fitz(sample)


def test_parse_tounicode_cmap_parses_bfchar_and_bfrange() -> None:
    cmap_payload = b"""
    begincmap
    1 begincodespacerange
    <00> <FF>
    endcodespacerange
    2 beginbfchar
    <41> <0041>
    <42> <0042>
    endbfchar
    1 beginbfrange
    <43> <44> <0043>
    endbfrange
    endcmap
    """

    cmap = pdf_extraction.parse_tounicode_cmap(cmap_payload)

    assert cmap is not None
    assert cmap.codepoints[0x41] == "A"
    assert cmap.codepoints[0x42] == "B"
    assert cmap.codepoints[0x43] == "C"
    assert cmap.codepoints[0x44] == "D"


def test_parse_tounicode_cmap_supports_bfrange_array_destination() -> None:
    cmap_payload = b"""
    begincmap
    1 begincodespacerange
    <00> <FF>
    endcodespacerange
    1 beginbfrange
    <30> <31> [<0041> <0042>]
    endbfrange
    endcmap
    """

    cmap = pdf_extraction.parse_tounicode_cmap(cmap_payload)

    assert cmap is not None
    assert cmap.codepoints[0x30] == "A"
    assert cmap.codepoints[0x31] == "B"


def test_extract_pdf_text_tokens_collects_hex_and_literal_tokens() -> None:
    chunk = b"<48656c6c6f> (Mundo\\nPDF) <invalid>"

    tokens = pdf_extraction.extract_pdf_text_tokens(chunk)

    values = [token for _, token in tokens]
    assert b"Hello" in values
    assert b"Mundo\nPDF" in values


def test_tokenize_pdf_content_parses_arrays_names_numbers_and_strings() -> None:
    content = b"BT /F1 12 Tf [(Hola) -250 <4D756E646F>] TJ ET"

    tokens = pdf_extraction.tokenize_pdf_content(content)

    assert "BT" in tokens
    assert "/F1" in tokens
    assert 12 in tokens
    assert "Tf" in tokens
    assert any(isinstance(token, list) for token in tokens)


def test_parse_pdf_array_supports_nested_arrays_names_numbers_and_hex() -> None:
    parsed, next_index = pdf_extraction.parse_pdf_array(
        b"(Uno) [<446f73> 3.5] /Tag 7 ] trailing", 0
    )

    assert parsed[0] == b"Uno"
    assert isinstance(parsed[1], list)
    assert parsed[1][0] == b"Dos"
    assert parsed[1][1] == 3.5
    assert parsed[2] == "/Tag"
    assert parsed[3] == 7
    assert next_index > 0


def test_decode_bytes_with_cmap_supports_multi_length_codes() -> None:
    cmap = pdf_extraction.PdfCMap(codepoints={0x41: "A", 0x0102: "Ç"}, code_lengths=(2, 1))

    decoded = pdf_extraction.decode_bytes_with_cmap(b"\x01\x02A", cmap)

    assert decoded == "ÇA"


def test_decode_tj_array_for_font_uses_spacing_and_best_cmap() -> None:
    cmap = pdf_extraction.PdfCMap(codepoints={0x41: "A", 0x42: "B"}, code_lengths=(1,))
    text, selected_cmap = pdf_extraction.decode_tj_array_for_font(
        array_items=[b"A", -250, b"B"],
        active_cmap=None,
        active_font="F1",
        font_to_cmap={"F1": cmap},
        fallback_cmaps=[],
    )

    assert text == "A B"
    assert selected_cmap is cmap


def test_decode_token_for_font_without_cmap_uses_raw_text() -> None:
    decoded, selected = pdf_extraction.decode_token_for_font(
        token_bytes=b"Hola",
        active_cmap=None,
        active_font=None,
        font_to_cmap={},
        fallback_cmaps=[],
    )

    assert decoded == "Hola"
    assert selected is None


def test_sanitize_text_chunks_deduplicates_and_filters_noise() -> None:
    chunks = [
        "  Diagnóstico\x00  ",
        "Diagnóstico",
        "A",
        "###$$$",
        "Tratamiento recomendado",
    ]

    sanitized = pdf_extraction.sanitize_text_chunks(chunks)

    assert "Diagnóstico" in sanitized
    assert sanitized.count("Diagnóstico") == 1
    assert "Tratamiento recomendado" in sanitized
    assert "###$$$" not in sanitized


def test_stitch_text_chunks_handles_spaces_punctuation_and_parenthesis() -> None:
    stitched = pdf_extraction.stitch_text_chunks(["Hola", ",", "mundo", "(", "test", ")"])

    assert stitched == "Hola, mundo (test)"


def test_should_join_without_space_rules() -> None:
    assert pdf_extraction.should_join_without_space("(", "valor")
    assert pdf_extraction.should_join_without_space("ABC", "DEF")
    assert not pdf_extraction.should_join_without_space("palabra", "larga")


def test_parse_pdf_literal_string_bytes_and_looks_textual_bytes() -> None:
    parsed, _ = pdf_extraction.parse_pdf_literal_string_bytes(b"(Linea\\nDos\\050ok\\051)", 1)
    parsed_text, _ = pdf_extraction.parse_pdf_literal_string(b"(Texto)", 1)

    assert parsed == b"Linea\nDos(ok)"
    assert parsed_text == "Texto"
    assert pdf_extraction.looks_textual_bytes(b"Texto 123")
    assert not pdf_extraction.looks_textual_bytes(b"\x00\x01\x02\x03")


def test_extract_without_external_dependencies_uses_stream_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\nstream\nBT (Hola) Tj ET\nendstream\n%%EOF")

    monkeypatch.setattr(pdf_extraction, "parse_pdf_objects", lambda _b: {})
    monkeypatch.setattr(pdf_extraction, "extract_cmaps_by_object", lambda _o: {})
    monkeypatch.setattr(pdf_extraction, "collect_page_content_streams", lambda **_k: [])
    monkeypatch.setattr(pdf_extraction, "inflate_pdf_stream", lambda stream: stream)
    monkeypatch.setattr(
        pdf_extraction,
        "extract_text_chunks_from_content_stream",
        lambda **_k: ["Hola"],
    )

    extracted = pdf_extraction._extract_pdf_text_without_external_dependencies(sample)

    assert "Hola" in extracted
