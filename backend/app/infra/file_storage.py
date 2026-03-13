"""Filesystem storage adapter for uploaded documents."""

from __future__ import annotations

import os
from pathlib import Path

from backend.app.ports.file_storage import FileStorage, StoredFile
from backend.app.settings import get_settings

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STORAGE_ROOT = BASE_DIR / "storage"


def get_storage_root() -> Path:
    """Resolve the storage root for uploaded files.

    The path can be overridden via the `VET_RECORDS_STORAGE_PATH` environment
    variable. The directory is created if it does not exist.
    """

    settings = get_settings()
    root = Path(settings.vet_records_storage_path or str(DEFAULT_STORAGE_ROOT))
    root.mkdir(parents=True, exist_ok=True)
    return root


class LocalFileStorage(FileStorage):
    """Filesystem-backed storage adapter."""

    def save(self, *, document_id: str, content: bytes) -> StoredFile:
        """Persist a document file using an atomic write."""

        relative_path = Path(document_id) / "original.pdf"
        storage_root = get_storage_root()
        target_path = storage_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = target_path.with_suffix(".tmp")
        try:
            with open(temp_path, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, target_path)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

        return StoredFile(storage_path=str(relative_path), file_size=len(content))

    def delete(self, *, storage_path: str) -> None:
        """Best-effort cleanup of a stored file."""

        target_path = get_storage_root() / storage_path
        if target_path.exists():
            target_path.unlink(missing_ok=True)

    def resolve(self, *, storage_path: str) -> Path:
        """Resolve a stored file path to an absolute filesystem path."""

        return get_storage_root() / storage_path

    def exists(self, *, storage_path: str) -> bool:
        """Check whether the stored file exists."""

        return self.resolve(storage_path=storage_path).exists()

    def save_raw_text(self, *, document_id: str, run_id: str, text: str) -> StoredFile:
        """Persist extracted raw text for a processing run."""

        relative_path = Path(document_id) / "runs" / run_id / "raw-text.txt"
        storage_root = get_storage_root()
        target_path = storage_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        payload = text.encode("utf-8")
        temp_path = target_path.with_suffix(".tmp")
        try:
            with open(temp_path, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, target_path)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

        return StoredFile(storage_path=str(relative_path), file_size=len(payload))

    def resolve_raw_text(self, *, document_id: str, run_id: str) -> Path:
        """Resolve a raw text artifact path to an absolute filesystem path."""

        relative_path = Path(document_id) / "runs" / run_id / "raw-text.txt"
        return get_storage_root() / relative_path

    def exists_raw_text(self, *, document_id: str, run_id: str) -> bool:
        """Check whether the raw text artifact exists."""

        return self.resolve_raw_text(document_id=document_id, run_id=run_id).exists()
