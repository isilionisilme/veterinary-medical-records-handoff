"""Port for filesystem storage operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredFile:
    """Result of storing a file in persistent storage."""

    storage_path: str
    file_size: int


class FileStorage(Protocol):
    """Storage contract for saving uploaded files."""

    def save(self, *, document_id: str, content: bytes) -> StoredFile:
        """Persist the uploaded file and return its storage metadata."""

    def delete(self, *, storage_path: str) -> None:
        """Remove a stored file if it exists."""

    def resolve(self, *, storage_path: str) -> Path:
        """Return the absolute filesystem path for a stored file."""

    def exists(self, *, storage_path: str) -> bool:
        """Return True when the stored file exists."""

    def save_raw_text(self, *, document_id: str, run_id: str, text: str) -> StoredFile:
        """Persist raw extracted text for a processing run."""

    def resolve_raw_text(self, *, document_id: str, run_id: str) -> Path:
        """Return the absolute filesystem path for a raw text artifact."""

    def exists_raw_text(self, *, document_id: str, run_id: str) -> bool:
        """Return True when the raw text artifact exists."""
