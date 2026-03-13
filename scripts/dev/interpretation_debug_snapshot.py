#!/usr/bin/env python3
"""Print a deterministic interpretation debug snapshot for one document."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.application.global_schema import (
    GLOBAL_SCHEMA_KEYS,
    REPEATABLE_KEYS,
    normalize_global_schema,
    validate_global_schema_shape,
)
from backend.app.infra import database
from backend.app.infra.file_storage import LocalFileStorage
from backend.app.infra.sqlite_document_repository import SqliteDocumentRepository


def _iso_from_timestamp(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=UTC).isoformat()


def _file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "size_bytes": None,
            "created_at": None,
            "modified_at": None,
        }
    stat = path.stat()
    return {
        "exists": True,
        "path": str(path),
        "size_bytes": stat.st_size,
        "created_at": _iso_from_timestamp(stat.st_ctime),
        "modified_at": _iso_from_timestamp(stat.st_mtime),
    }


def _latest_artifact_row(*, run_id: str, artifact_type: str) -> dict[str, Any] | None:
    with database.get_connection() as conn:
        row = conn.execute(
            """
            SELECT artifact_id, payload, created_at
            FROM artifacts
            WHERE run_id = ? AND artifact_type = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (run_id, artifact_type),
        ).fetchone()

    if row is None:
        return None
    return {
        "artifact_id": row["artifact_id"],
        "payload": row["payload"],
        "created_at": row["created_at"],
    }


def _latest_interpretation_failure(*, run_id: str) -> dict[str, Any] | None:
    with database.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT payload, created_at
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'STEP_STATUS'
            ORDER BY created_at DESC
            """,
            (run_id,),
        ).fetchall()

    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("step_name") != "INTERPRETATION":
            continue
        if payload.get("step_status") != "FAILED":
            continue
        return {
            "step_error_code": payload.get("error_code"),
            "step_details": payload.get("details"),
            "recorded_at": row["created_at"],
        }
    return None


def _build_key_summary(global_schema: dict[str, object]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for key in GLOBAL_SCHEMA_KEYS:
        value = global_schema.get(key)
        if key in REPEATABLE_KEYS:
            values = value if isinstance(value, list) else []
            summaries.append(
                {
                    "key": key,
                    "repeatable": True,
                    "count": len(values),
                    "non_empty": len(values) > 0,
                }
            )
        else:
            text = value if isinstance(value, str) else None
            summaries.append(
                {
                    "key": key,
                    "repeatable": False,
                    "non_empty": bool(text),
                }
            )
    return summaries


def build_snapshot(document_id: str) -> dict[str, Any]:
    database.ensure_schema()
    repository = SqliteDocumentRepository()
    storage = LocalFileStorage()

    document = repository.get(document_id)
    if document is None:
        return {
            "document_id": document_id,
            "error": "DOCUMENT_NOT_FOUND",
        }

    run = repository.get_latest_completed_run(document_id)
    if run is None:
        return {
            "document_id": document_id,
            "latest_completed_run": None,
            "raw_text_artifact": None,
            "structured_interpretation_artifact": None,
            "failure_reason": "NO_COMPLETED_RUN",
        }

    raw_text_info = _file_info(storage.resolve_raw_text(document_id=document_id, run_id=run.run_id))
    interpretation_row = _latest_artifact_row(
        run_id=run.run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )

    failure_reason: dict[str, Any] | None = None
    structured_info: dict[str, Any]
    if interpretation_row is None:
        failure_reason = _latest_interpretation_failure(run_id=run.run_id)
        if failure_reason is None and run.state.value == "TIMED_OUT":
            failure_reason = {"reason": "timeout"}
        elif failure_reason is None and run.failure_type:
            failure_reason = {"reason": run.failure_type}
        elif failure_reason is None:
            failure_reason = {"reason": "MISSING_ARTIFACT_WITHOUT_STEP_FAILURE"}

        structured_info = {
            "exists": False,
            "artifact_id": None,
            "created_at": None,
            "size_bytes": None,
            "fields_populated": 0,
            "keys_present": [],
            "key_summary": [],
            "validation_errors": [],
            "parsing_errors": [],
        }
    else:
        parsing_errors: list[str] = []
        validation_errors: list[str] = []
        try:
            payload = json.loads(interpretation_row["payload"])
        except json.JSONDecodeError as exc:
            payload = {}
            parsing_errors.append(f"Invalid interpretation JSON payload: {exc}")

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            data = {}
            parsing_errors.append("Interpretation payload is missing `data` object.")

        raw_global = data.get("global_schema")
        if raw_global is not None and not isinstance(raw_global, dict):
            parsing_errors.append("`data.global_schema` exists but is not an object.")
            raw_global = {}

        normalized_global = normalize_global_schema(
            raw_global if isinstance(raw_global, dict) else None
        )
        validation_errors.extend(validate_global_schema_shape(normalized_global))

        keys_present = [
            key
            for key in GLOBAL_SCHEMA_KEYS
            if (
                key in REPEATABLE_KEYS
                and isinstance(normalized_global.get(key), list)
                and len(normalized_global.get(key, [])) > 0
            )
            or (isinstance(normalized_global.get(key), str) and bool(normalized_global.get(key)))
        ]
        structured_info = {
            "exists": True,
            "artifact_id": interpretation_row["artifact_id"],
            "created_at": interpretation_row["created_at"],
            "size_bytes": len(interpretation_row["payload"].encode("utf-8")),
            "fields_populated": len(keys_present),
            "keys_present": keys_present,
            "key_summary": _build_key_summary(normalized_global),
            "validation_errors": validation_errors,
            "parsing_errors": parsing_errors,
        }

    return {
        "document_id": document_id,
        "latest_completed_run": {
            "run_id": run.run_id,
            "state": run.state.value,
            "completed_at": run.completed_at,
            "failure_type": run.failure_type,
        },
        "raw_text_artifact": raw_text_info,
        "structured_interpretation_artifact": structured_info,
        "failure_reason": failure_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", help="Target document identifier.")
    args = parser.parse_args()

    snapshot = build_snapshot(args.document_id)
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
