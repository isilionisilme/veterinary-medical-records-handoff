from __future__ import annotations

from backend.app.api.routes_documents import _safe_content_disposition


def test_safe_content_disposition_keeps_basic_filename() -> None:
    header = _safe_content_disposition("inline", "record.pdf")

    assert header.startswith("inline; ")
    assert 'filename="record.pdf"' in header
    assert "filename*=UTF-8''record.pdf" in header


def test_safe_content_disposition_escapes_double_quotes() -> None:
    header = _safe_content_disposition("attachment", 'my"record".pdf')

    assert "filename=\"my'record'.pdf\"" in header
    assert "%22" in header


def test_safe_content_disposition_adds_utf8_rfc5987_encoding() -> None:
    header = _safe_content_disposition("attachment", "histórico_clínico.pdf")

    assert "filename*=UTF-8''hist%C3%B3rico_cl%C3%ADnico.pdf" in header


def test_safe_content_disposition_strips_newlines_to_prevent_header_injection() -> None:
    header = _safe_content_disposition("attachment", "safe\nname\r.pdf")

    assert "\n" not in header
    assert "\r" not in header
    assert "%0A" not in header
    assert "%0D" not in header
