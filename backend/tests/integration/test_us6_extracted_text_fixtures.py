from __future__ import annotations

import importlib.util
import os
import re
import time
from pathlib import Path

import pytest

from backend.app.application.extraction_quality import is_usable_extracted_text
from backend.app.application.processing_runner import PDF_EXTRACTOR_FORCE_ENV, extract_pdf_text

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pdfs"
HAS_FITZ = importlib.util.find_spec("fitz") is not None


def _fixture_path(filename: str) -> Path:
    path = FIXTURES_DIR / filename
    assert path.exists(), f"Missing fixture: {path}"
    return path


def _strip_accents(value: str) -> str:
    return (
        value.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
    )


def test_clinical_history_1_fallback_is_rejected_as_low_quality() -> None:
    os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fallback"
    try:
        text = extract_pdf_text(_fixture_path("clinical_history_1.pdf"))
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    normalized = _strip_accents(text).lower()
    tokens = re.findall(r"\b\w+\b", normalized)
    single_letter_ratio = sum(1 for token in tokens if len(token) == 1 and token.isalpha()) / max(
        1, len(tokens)
    )

    assert not is_usable_extracted_text(text)
    assert "dratamiento" in normalized or "draquea" in normalized or "diene" in normalized
    assert single_letter_ratio > 0.02


def test_clinical_history_1_fitz_quality_when_available() -> None:
    if not HAS_FITZ:
        pytest.skip("PyMuPDF is not installed in this environment")

    os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fitz"
    try:
        text = extract_pdf_text(_fixture_path("clinical_history_1.pdf"))
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    normalized = _strip_accents(text).lower()
    tokens = re.findall(r"\b\w+\b", normalized)
    single_letter_ratio = sum(1 for token in tokens if len(token) == 1 and token.isalpha()) / max(
        1, len(tokens)
    )

    assert is_usable_extracted_text(text)
    assert "beatriz" in normalized
    assert "copro seriado" in normalized
    assert "coprologico" in normalized
    assert "dratamiento" not in normalized
    assert "draquea" not in normalized
    assert "diene" not in normalized
    # Fitz output can include isolated one-letter tokens in table-like layouts.
    # Keep a guard, but avoid an unrealistically strict threshold.
    assert single_letter_ratio < 0.09


def test_clinical_history_1_extracts_usable_readable_text() -> None:
    if HAS_FITZ:
        os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fitz"
    else:
        os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fallback"
    try:
        text = extract_pdf_text(_fixture_path("clinical_history_1.pdf"))
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    if not HAS_FITZ:
        assert not is_usable_extracted_text(text)
        return

    assert is_usable_extracted_text(text)
    assert "D%G!" not in text
    assert "Mascota" in text or "Datos" in text


def test_clinical_history_2_extracts_partial_but_usable_text() -> None:
    os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fallback"
    try:
        started_at = time.monotonic()
        text = extract_pdf_text(_fixture_path("clinical_history_2.pdf"))
        elapsed = time.monotonic() - started_at
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    # Keep a broad guard against pathological slowdowns without making the
    # integration test flaky on loaded Windows runners.
    assert elapsed < 10.0

    if not HAS_FITZ:
        assert not is_usable_extracted_text(text)
        return

    os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fitz"
    try:
        text = extract_pdf_text(_fixture_path("clinical_history_2.pdf"))
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    assert is_usable_extracted_text(text)
    alpha_tokens = [token for token in text.split() if sum(ch.isalpha() for ch in token) >= 3]
    assert len(alpha_tokens) >= 6


def test_clinical_history_4_scanned_is_usable_only_when_output_is_readable() -> None:
    if HAS_FITZ:
        os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fitz"
    else:
        os.environ[PDF_EXTRACTOR_FORCE_ENV] = "fallback"
    try:
        text = extract_pdf_text(_fixture_path("clinical_history_4-scanned.pdf"))
    finally:
        os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)

    lower_text = text.lower()
    assert "neoplasias" in lower_text
    assert "penicilium" in lower_text

    if HAS_FITZ:
        # With fitz available in this fixture set, extracted text is readable enough.
        assert is_usable_extracted_text(text)
    else:
        # Fallback-only mode must not mark degraded scanned output as usable.
        assert not is_usable_extracted_text(text)
