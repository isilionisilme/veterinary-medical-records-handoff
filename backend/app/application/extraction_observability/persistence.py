"""Persistence for extraction observability runs and diff logging."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from .snapshot import SNAPSHOT_SCHEMA_VERSION_CANONICAL
from .triage import _log_goal_fields_report, _log_triage_report, build_extraction_triage

logger = logging.getLogger(__name__)
_uvicorn_logger = logging.getLogger("uvicorn.error")
_MAX_RUNS_PER_DOCUMENT = 20
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_OBSERVABILITY_DIR = _PROJECT_ROOT / ".local" / "extraction_runs"


def _emit_info(message: str) -> None:
    if _uvicorn_logger.handlers:
        _uvicorn_logger.info(message)
        return
    logger.info(message)


def _safe_document_filename(document_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", document_id.strip())
    return cleaned or "unknown"


def _document_runs_path(document_id: str) -> Path:
    return _OBSERVABILITY_DIR / f"{_safe_document_filename(document_id)}.json"


def _read_runs(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    normalized_runs: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        normalized["schemaVersion"] = SNAPSHOT_SCHEMA_VERSION_CANONICAL
        normalized_runs.append(normalized)
    return normalized_runs


def _write_runs(path: Path, runs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runs, ensure_ascii=False, indent=2), encoding="utf-8")


def _count_deltas(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    previous_counts = previous.get("counts") if isinstance(previous, dict) else None
    current_counts = current.get("counts") if isinstance(current, dict) else None
    if not isinstance(previous_counts, dict) or not isinstance(current_counts, dict):
        return []
    lines: list[str] = []
    for key in ("accepted", "missing", "rejected", "low", "mid", "high"):
        old_value = int(previous_counts.get(key, 0) or 0)
        new_value = int(current_counts.get(key, 0) or 0)
        lines.append(f"- {key}: {old_value} -> {new_value} ({new_value - old_value:+d})")
    return lines


def _field_changes(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    previous_fields = previous.get("fields") if isinstance(previous, dict) else None
    current_fields = current.get("fields") if isinstance(current, dict) else None
    if not isinstance(previous_fields, dict) or not isinstance(current_fields, dict):
        return []
    changes: list[str] = []
    for key in sorted(set(previous_fields.keys()) | set(current_fields.keys())):
        old_raw = previous_fields.get(key)
        new_raw = current_fields.get(key)
        if not isinstance(old_raw, dict) or not isinstance(new_raw, dict):
            continue
        old_status, new_status = old_raw.get("status"), new_raw.get("status")
        old_conf, new_conf = old_raw.get("confidence"), new_raw.get("confidence")
        old_value, new_value = old_raw.get("valueNormalized"), new_raw.get("valueNormalized")
        new_reason = new_raw.get("reason")
        if old_status == new_status and old_conf == new_conf and old_value == new_value:
            continue
        change_line = f"- {key}: {old_status}"
        if old_conf:
            change_line += f" ({old_conf})"
        change_line += f" -> {new_status}"
        if new_conf:
            change_line += f" ({new_conf})"
        if new_status == "rejected" and isinstance(new_reason, str) and new_reason:
            change_line += f" [reason: {new_reason}]"
        if isinstance(old_value, str) and isinstance(new_value, str) and old_value != new_value:
            change_line += f" [value: {old_value!r} -> {new_value!r}]"
        elif not isinstance(old_value, str) and isinstance(new_value, str):
            change_line += f" [value: {new_value!r}]"
        changes.append(change_line)
    return changes


def _log_diff(*, document_id: str, previous: dict[str, Any] | None, current: dict[str, Any]) -> int:
    if previous is None:
        _emit_info(
            "[extraction-observability] "
            f"document={document_id} run={current.get('runId')} "
            "first snapshot persisted"
        )
        return 0
    summary_lines = _count_deltas(previous, current)
    change_lines = _field_changes(previous, current)
    lines = [
        "[extraction-observability] "
        f"document={document_id} run={current.get('runId')} "
        "diff vs previous:",
        "Summary:",
        *summary_lines,
        "Changes:" if change_lines else "Changes: none",
        *change_lines,
    ]
    _emit_info("\n".join(lines))
    return len(change_lines)


def persist_extraction_run_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(snapshot)
    schema_version = str(snapshot.get("schemaVersion", "")).strip().lower()
    if schema_version != SNAPSHOT_SCHEMA_VERSION_CANONICAL:
        raise ValueError("schemaVersion must be canonical")
    snapshot["schemaVersion"] = SNAPSHOT_SCHEMA_VERSION_CANONICAL
    document_id = str(snapshot.get("documentId", "")).strip()
    if not document_id:
        raise ValueError("documentId is required")
    run_id = str(snapshot.get("runId", "")).strip()
    if not run_id:
        raise ValueError("runId is required")

    path = _document_runs_path(document_id)
    runs = _read_runs(path)
    existing_index: int | None = None
    for index, item in enumerate(runs):
        if str(item.get("runId", "")).strip() == run_id:
            existing_index = index
            break

    was_created = existing_index is None
    if existing_index is None:
        previous = runs[-1] if runs else None
        runs.append(snapshot)
        if len(runs) > _MAX_RUNS_PER_DOCUMENT:
            runs = runs[-_MAX_RUNS_PER_DOCUMENT:]
    else:
        previous = runs[existing_index]
        runs[existing_index] = snapshot

    _write_runs(path, runs)
    triage = build_extraction_triage(snapshot)
    _log_triage_report(document_id, triage)
    _log_goal_fields_report(document_id=document_id, current=snapshot, previous=previous)
    changed_fields = _log_diff(document_id=document_id, previous=previous, current=snapshot)
    return {
        "document_id": document_id,
        "run_id": run_id,
        "stored_runs": len(runs),
        "changed_fields": changed_fields,
        "was_created": was_created,
    }


def get_extraction_runs(document_id: str) -> list[dict[str, Any]]:
    return _read_runs(_document_runs_path(document_id))


def get_latest_extraction_run_triage(document_id: str) -> dict[str, Any] | None:
    runs = get_extraction_runs(document_id)
    return build_extraction_triage(runs[-1]) if runs else None
