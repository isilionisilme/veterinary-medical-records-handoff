"""Shared route parameter types and message constants for API modules."""

from __future__ import annotations

from typing import Annotated

from fastapi import Path

UUID_PATH_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
SAFE_IDENTIFIER_PATH_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9-]{0,127}$"
DOCUMENT_NOT_FOUND_MSG = "Document not found."
ERROR_NOT_FOUND = "NOT_FOUND"
ERROR_CONFLICT = "CONFLICT"
ERROR_ARTIFACT_MISSING = "ARTIFACT_MISSING"
ERROR_INTERNAL = "INTERNAL_ERROR"
DocumentIdPath = Annotated[str, Path(..., pattern=UUID_PATH_PATTERN)]
RunIdPath = Annotated[str, Path(..., pattern=SAFE_IDENTIFIER_PATH_PATTERN)]
DebugDocumentIdPath = Annotated[str, Path(..., pattern=SAFE_IDENTIFIER_PATH_PATTERN)]
