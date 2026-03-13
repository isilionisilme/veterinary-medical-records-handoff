from __future__ import annotations

import asyncio
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.app.application.extraction_quality import (
    evaluate_extracted_text_quality,
    is_usable_extracted_text,
    looks_human_readable_text,
)
from backend.app.application.processing_runner import (
    PDF_EXTRACTOR_FORCE_ENV,
    _process_document,
    extract_pdf_text_with_extractor,
    extract_pdf_text_without_external_dependencies,
    parse_pdf_literal_string,
)


def test_parse_pdf_literal_string_handles_common_escapes() -> None:
    payload = b"(Linea\\nDos\\t\\050ok\\051\\\\)"
    parsed, next_index = parse_pdf_literal_string(payload, 1)

    assert parsed == "Linea\nDos\t(ok)\\"
    assert next_index == len(payload)


def test_fallback_extractor_reads_text_from_compressed_stream(tmp_path) -> None:
    stream = zlib.compress(b"BT (Historia clinica) Tj ET")
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nstream\n" + stream + b"\nendstream\n%%EOF"
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(pdf_bytes)

    extracted = extract_pdf_text_without_external_dependencies(pdf_path)

    assert "Historia clinica" in extracted


def test_readability_filter_rejects_gibberish() -> None:
    assert not looks_human_readable_text("©+/Vã§ga/ÚæÃAäj¦suâìù")


def test_usable_extracted_text_rejects_mojibake_like_output() -> None:
    gibberish = "©+/Vã§ga/ÚæÃAäj¦suâìùJA¨·ö<]¦¶Ý"
    assert not is_usable_extracted_text(gibberish)


def test_usable_extracted_text_rejects_symbol_heavy_garbage() -> None:
    gibberish = (
        "D%G! $G!II%D /T?UL Da$-N;.8Q- /T/UL /T@UL ?'BCADEF? /T@/UL "
        ".EI?'JEAKDLLEM'JND@ cT/UL O7,L7$OKOOR .MM-N7$.$MK-9O7N$-Z;9.X7NT$"
    )
    assert not is_usable_extracted_text(gibberish)


def test_usable_extracted_text_accepts_real_sentence() -> None:
    text = (
        "Historia clinica: perro macho de 7 anos con fiebre y vomitos. "
        "Se realiza analitica y tratamiento sintomatico."
    )
    assert is_usable_extracted_text(text)


def test_quality_evaluator_rejects_known_substitution_pattern() -> None:
    text = "Se queda hospitalizado y se recomienda Dratamiento por Draquea. Diene control."
    score, quality_pass, reasons = evaluate_extracted_text_quality(text)

    assert score <= 0.60
    assert not quality_pass
    assert "SUSPICIOUS_SUBSTITUTIONS" in reasons


def test_extractor_auto_mode_falls_back_when_fitz_is_unavailable(monkeypatch, tmp_path) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")

    monkeypatch.delenv(PDF_EXTRACTOR_FORCE_ENV, raising=False)
    monkeypatch.setattr(
        "backend.app.application.processing.pdf_extraction._extract_pdf_text_with_fitz",
        lambda _path: (_ for _ in ()).throw(ImportError("missing fitz")),
    )
    monkeypatch.setattr(
        "backend.app.application.processing.pdf_extraction._extract_pdf_text_without_external_dependencies",
        lambda _path: "fallback text",
    )

    text, extractor = extract_pdf_text_with_extractor(sample)

    assert extractor == "fallback"
    assert text == "fallback text"


def test_extractor_force_modes_choose_expected_path(monkeypatch, tmp_path) -> None:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n%%EOF")

    monkeypatch.setattr(
        "backend.app.application.processing.pdf_extraction._extract_pdf_text_with_fitz",
        lambda _path: "fitz text",
    )
    monkeypatch.setattr(
        "backend.app.application.processing.pdf_extraction._extract_pdf_text_without_external_dependencies",
        lambda _path: "fallback text",
    )

    monkeypatch.setenv(PDF_EXTRACTOR_FORCE_ENV, "fitz")
    fitz_text, fitz_extractor = extract_pdf_text_with_extractor(sample)
    assert fitz_extractor == "fitz"
    assert fitz_text == "fitz text"

    monkeypatch.setenv(PDF_EXTRACTOR_FORCE_ENV, "fallback")
    fallback_text, fallback_extractor = extract_pdf_text_with_extractor(sample)
    assert fallback_extractor == "fallback"
    assert fallback_text == "fallback text"


def test_process_document_converts_keyerror_during_interpretation_to_processing_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.app.application.processing import orchestrator

    repository = Mock()
    storage = Mock()
    sample_pdf = Path(__file__)
    repository.get.return_value = SimpleNamespace(storage_path="doc/original.pdf")
    storage.exists.return_value = True
    storage.resolve.return_value = sample_pdf

    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.pdf_extraction._extract_pdf_text_with_extractor",
        lambda _path: ("historia clinica suficiente para procesamiento", "fitz"),
    )
    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.evaluate_extracted_text_quality",
        lambda _text: (0.9, True, []),
    )
    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator._build_interpretation_artifact",
        lambda **_kwargs: (_ for _ in ()).throw(KeyError("field_mapping")),
    )

    with pytest.raises(orchestrator.ProcessingError, match="INTERPRETATION_FAILED"):
        asyncio.run(
            _process_document(
                run_id="run-keyerror-1",
                document_id="doc-keyerror-1",
                repository=repository,
                storage=storage,
            )
        )


def test_process_document_with_empty_extraction_creates_low_quality_failure_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.app.application.processing import orchestrator

    repository = Mock()
    storage = Mock()
    sample_pdf = Path(__file__)
    repository.get.return_value = SimpleNamespace(storage_path="doc/original.pdf")
    storage.exists.return_value = True
    storage.resolve.return_value = sample_pdf

    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.pdf_extraction._extract_pdf_text_with_extractor",
        lambda _path: ("", "fitz"),
    )

    with pytest.raises(orchestrator.ProcessingError, match="EXTRACTION_LOW_QUALITY"):
        asyncio.run(
            _process_document(
                run_id="run-empty-1",
                document_id="doc-empty-1",
                repository=repository,
                storage=storage,
            )
        )

    failed_extraction_artifacts = [
        call.kwargs["payload"]
        for call in repository.append_artifact.call_args_list
        if call.kwargs.get("artifact_type") == "STEP_STATUS"
        and call.kwargs["payload"]["step_name"] == "EXTRACTION"
        and call.kwargs["payload"]["step_status"] == "FAILED"
    ]
    assert failed_extraction_artifacts
    assert failed_extraction_artifacts[0]["error_code"] == "EXTRACTION_LOW_QUALITY"
