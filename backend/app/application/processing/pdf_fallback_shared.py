"""Shared types, limits, and helpers for fallback PDF extraction."""

from __future__ import annotations

import time
import zlib
from contextvars import ContextVar, Token
from dataclasses import dataclass

MAX_CONTENT_STREAM_BYTES = 8 * 1024 * 1024
MAX_TEXT_CHUNKS = 20000
MAX_TOKENS_PER_STREAM = 25000
MAX_ARRAY_ITEMS = 3000
MAX_SINGLE_STREAM_BYTES = 1 * 1024 * 1024
MAX_EXTRACTION_SECONDS = 20.0
MAX_CMAP_STREAM_BYTES = 256 * 1024

_ACTIVE_EXTRACTION_DEADLINE: ContextVar[float | None] = ContextVar(
    "_ACTIVE_EXTRACTION_DEADLINE", default=None
)


@dataclass(frozen=True, slots=True)
class PdfCMap:
    codepoints: dict[int, str]
    code_lengths: tuple[int, ...]


def deadline_exceeded() -> bool:
    deadline = _ACTIVE_EXTRACTION_DEADLINE.get()
    if deadline is None:
        return False
    return time.monotonic() > deadline


def start_extraction_deadline(timeout_seconds: float) -> Token:
    return _ACTIVE_EXTRACTION_DEADLINE.set(time.monotonic() + timeout_seconds)


def restore_extraction_deadline(token: Token) -> None:
    _ACTIVE_EXTRACTION_DEADLINE.reset(token)


def inflate_pdf_stream(stream: bytes) -> bytes | None:
    try:
        return zlib.decompress(stream)
    except zlib.error:
        return None
