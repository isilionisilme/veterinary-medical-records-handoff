"""Text decoding helpers for fallback PDF extraction."""

from __future__ import annotations

from . import pdf_fallback_shared as shared
from .pdf_content_tokenizer import _tokenize_pdf_content
from .pdf_text_quality import _decoded_text_score, _normalize_candidate_text


def _extract_text_chunks_from_content_stream(
    *,
    chunk: bytes,
    font_to_cmap: dict[str, shared.PdfCMap],
    fallback_cmaps: list[shared.PdfCMap],
) -> list[str]:
    extracted: list[str] = []
    in_text_object = False
    active_font: str | None = None
    active_cmap: shared.PdfCMap | None = None
    operand_stack: list[object] = []

    for token in _tokenize_pdf_content(chunk):
        if not isinstance(token, str):
            operand_stack.append(token)
            continue

        if token.startswith("/"):
            operand_stack.append(token)
            continue
        if token == "BT":
            in_text_object = True
            operand_stack.clear()
            continue
        if token == "ET":
            in_text_object = False
            active_font = None
            active_cmap = None
            operand_stack.clear()
            continue
        if not in_text_object:
            operand_stack.clear()
            continue

        if token == "Tf":
            if len(operand_stack) >= 2 and isinstance(operand_stack[-2], str):
                font_name = operand_stack[-2]
                if font_name.startswith("/"):
                    active_font = font_name[1:]
                    active_cmap = font_to_cmap.get(active_font)
            operand_stack.clear()
            continue

        if token == "Tj":
            if operand_stack and isinstance(operand_stack[-1], bytes):
                decoded, selected_cmap = _decode_token_for_font(
                    token_bytes=operand_stack[-1],
                    active_cmap=active_cmap,
                    active_font=active_font,
                    font_to_cmap=font_to_cmap,
                    fallback_cmaps=fallback_cmaps,
                )
                if selected_cmap is not None and active_cmap is None:
                    active_cmap = selected_cmap
                if decoded:
                    extracted.append(decoded)
            operand_stack.clear()
            continue

        if token == "TJ":
            if operand_stack and isinstance(operand_stack[-1], list):
                decoded, selected_cmap = _decode_tj_array_for_font(
                    array_items=operand_stack[-1],
                    active_cmap=active_cmap,
                    active_font=active_font,
                    font_to_cmap=font_to_cmap,
                    fallback_cmaps=fallback_cmaps,
                )
                if selected_cmap is not None:
                    active_cmap = selected_cmap
                if decoded:
                    extracted.append(decoded)
            operand_stack.clear()
            continue

        operand_stack.clear()

    return extracted


def _decode_token_for_font(
    *,
    token_bytes: bytes,
    active_cmap: shared.PdfCMap | None,
    active_font: str | None,
    font_to_cmap: dict[str, shared.PdfCMap],
    fallback_cmaps: list[shared.PdfCMap],
) -> tuple[str, shared.PdfCMap | None]:
    if active_cmap is not None:
        return _decode_pdf_text_token(token_bytes, [active_cmap]), active_cmap

    primary = font_to_cmap.get(active_font) if active_font else None
    if primary is not None:
        return _decode_pdf_text_token(token_bytes, [primary]), primary

    if not fallback_cmaps:
        return _decode_pdf_text_token(token_bytes, []), None

    best_text = ""
    best_cmap: shared.PdfCMap | None = None
    best_score = float("-inf")
    for cmap in fallback_cmaps[:4]:
        decoded = _decode_pdf_text_token(token_bytes, [cmap])
        score = _decoded_text_score(_normalize_candidate_text(decoded))
        if score > best_score:
            best_score = score
            best_text = decoded
            best_cmap = cmap
    return best_text, best_cmap


def _decode_tj_array_for_font(
    *,
    array_items: list[object],
    active_cmap: shared.PdfCMap | None,
    active_font: str | None,
    font_to_cmap: dict[str, shared.PdfCMap],
    fallback_cmaps: list[shared.PdfCMap],
) -> tuple[str, shared.PdfCMap | None]:
    if active_cmap is not None:
        candidate_cmaps = [active_cmap]
    else:
        primary = font_to_cmap.get(active_font) if active_font else None
        candidate_cmaps = [primary] if primary is not None else fallback_cmaps[:4]

    if not candidate_cmaps:
        return "", None

    best_text = ""
    best_cmap: shared.PdfCMap | None = None
    best_score = float("-inf")
    for cmap in candidate_cmaps:
        parts: list[str] = []
        for item in array_items:
            if isinstance(item, bytes):
                decoded = _decode_pdf_text_token(item, [cmap])
                if decoded:
                    parts.append(decoded)
                continue
            if isinstance(item, int | float) and item < -180:
                parts.append(" ")
        candidate_text = "".join(parts)
        score = _decoded_text_score(_normalize_candidate_text(candidate_text))
        if score > best_score:
            best_score = score
            best_text = candidate_text
            best_cmap = cmap

    return best_text, best_cmap


def _decode_pdf_text_token(token: bytes, cmaps: list[shared.PdfCMap | None]) -> str:
    candidates: list[str] = [token.decode("latin-1", errors="ignore")]
    for cmap in cmaps:
        if cmap is None:
            continue
        decoded = _decode_bytes_with_cmap(token, cmap)
        if decoded:
            candidates.append(decoded)

    best_text = ""
    best_score = float("-inf")
    for candidate in candidates:
        normalized = _normalize_candidate_text(candidate)
        if not normalized:
            continue
        score = _decoded_text_score(normalized)
        if score > best_score:
            best_score = score
            best_text = candidate
    return best_text


def _decode_bytes_with_cmap(token: bytes, cmap: shared.PdfCMap) -> str:
    chars: list[str] = []
    index = 0
    while index < len(token):
        matched = False
        for code_length in cmap.code_lengths:
            if index + code_length > len(token):
                continue
            code = int.from_bytes(token[index : index + code_length], byteorder="big")
            mapped = cmap.codepoints.get(code)
            if mapped is None:
                continue
            chars.append(mapped)
            index += code_length
            matched = True
            break
        if matched:
            continue
        chars.append(bytes([token[index]]).decode("latin-1", errors="ignore"))
        index += 1
    return "".join(chars)
