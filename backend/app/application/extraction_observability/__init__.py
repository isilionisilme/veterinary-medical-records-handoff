"""Extraction observability package with compatibility re-exports."""

from __future__ import annotations

from typing import Any

from . import persistence as _persistence
from . import triage as _triage
from .reporting import summarize_extraction_runs
from .snapshot import (
    SNAPSHOT_SCHEMA_VERSION_CANONICAL,
    build_extraction_snapshot_from_interpretation,
)
from .triage import build_extraction_triage

_OBSERVABILITY_DIR = _persistence._OBSERVABILITY_DIR
_emit_info = _persistence._emit_info


def _sync_runtime_overrides() -> None:
    _persistence._OBSERVABILITY_DIR = _OBSERVABILITY_DIR
    _persistence._emit_info = _emit_info
    _triage._emit_info = _emit_info


def _document_runs_path(document_id: str):
    return _OBSERVABILITY_DIR / f"{_persistence._safe_document_filename(document_id)}.json"


def persist_extraction_run_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    _sync_runtime_overrides()
    return _persistence.persist_extraction_run_snapshot(snapshot)


def get_extraction_runs(document_id: str) -> list[dict[str, Any]]:
    _sync_runtime_overrides()
    return _persistence.get_extraction_runs(document_id)


def get_latest_extraction_run_triage(document_id: str) -> dict[str, Any] | None:
    _sync_runtime_overrides()
    return _persistence.get_latest_extraction_run_triage(document_id)


__all__ = [
    "SNAPSHOT_SCHEMA_VERSION_CANONICAL",
    "build_extraction_snapshot_from_interpretation",
    "build_extraction_triage",
    "persist_extraction_run_snapshot",
    "get_extraction_runs",
    "get_latest_extraction_run_triage",
    "summarize_extraction_runs",
    "_OBSERVABILITY_DIR",
    "_document_runs_path",
    "_emit_info",
]
