"""Shared helpers for document review integration tests."""

from __future__ import annotations

import io
import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.domain import models as app_models
from backend.app.infra import database

_US46_BASELINE_VERSION = "mixed_multi_visit_assignment.baseline.canonical"
_US46_BASELINE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "review_baselines"
    / f"{_US46_BASELINE_VERSION}.json"
)
_RAW_TEXT_FIXTURES_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "raw_text"

_US46_VISIT_SCOPED_KEYS = {
    "symptoms",
    "diagnosis",
    "procedure",
    "medication",
    "treatment_plan",
    "allergies",
    "vaccinations",
    "lab_result",
    "imaging",
}


def _load_us46_mixed_multi_visit_assignment_baseline() -> dict[str, object]:
    payload = json.loads(_US46_BASELINE_PATH.read_text(encoding="utf-8"))
    visit_ids = payload.get("visit_ids")
    normalized_visit_ids = {
        str(visit_id)
        for visit_id in visit_ids
        if isinstance(visit_ids, list) and isinstance(visit_id, str)
    }

    return {
        "version": payload.get("version"),
        "visit_ids": normalized_visit_ids,
        "assigned_visit_scoped_fields": payload.get("assigned_visit_scoped_fields"),
        "unassigned_visit_scoped_fields": payload.get("unassigned_visit_scoped_fields"),
    }


def _upload_sample_document(test_client: TestClient) -> str:
    content = b"%PDF-1.5 sample"
    files = {"file": ("record.pdf", io.BytesIO(content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"]


def _insert_run(
    *, document_id: str, run_id: str, state: app_models.ProcessingRunState, failure_type: str | None
) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                document_id,
                state.value,
                "2026-02-10T10:00:00+00:00",
                "2026-02-10T10:00:01+00:00",
                (
                    "2026-02-10T10:00:05+00:00"
                    if state == app_models.ProcessingRunState.COMPLETED
                    else None
                ),
                failure_type,
            ),
        )
        conn.commit()


def _insert_structured_interpretation(
    *,
    run_id: str,
    data: dict[str, object] | None = None,
) -> None:
    payload_data = data or {
        "document_id": "doc",
        "processing_run_id": run_id,
        "created_at": "2026-02-10T10:00:05+00:00",
        "fields": [
            {
                "field_id": "field-1",
                "key": "pet_name",
                "value": "Luna",
                "value_type": "string",
                "is_critical": False,
                "origin": "machine",
                "evidence": {"page": 1, "snippet": "Paciente: Luna"},
            }
        ],
    }

    payload = {
        "interpretation_id": "interp-1",
        "version_number": 1,
        "data": payload_data,
    }

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO artifacts (artifact_id, run_id, artifact_type, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                f"artifact-review-{run_id}",
                run_id,
                "STRUCTURED_INTERPRETATION",
                json.dumps(payload, separators=(",", ":")),
                "2026-02-10T10:00:06+00:00",
            ),
        )
        conn.commit()


def _collect_visit_grouping_stats(visits: object) -> dict[str, object]:
    assigned_visit_ids: set[str] = set()
    assigned_keys: set[str] = set()
    assigned_count = 0
    unassigned_count = 0

    if not isinstance(visits, list):
        return {
            "assigned_visit_ids": assigned_visit_ids,
            "assigned_keys": assigned_keys,
            "assigned_count": assigned_count,
            "unassigned_count": unassigned_count,
        }

    for visit in visits:
        if not isinstance(visit, dict):
            continue

        visit_id = visit.get("visit_id")
        fields = visit.get("fields")
        if not isinstance(fields, list):
            continue

        if isinstance(visit_id, str) and visit_id != "unassigned":
            assigned_visit_ids.add(visit_id)
            for field in fields:
                if not isinstance(field, dict):
                    continue
                assigned_count += 1
                field_key = field.get("key")
                if isinstance(field_key, str):
                    assigned_keys.add(field_key)
            continue

        unassigned_count += sum(1 for field in fields if isinstance(field, dict))

    return {
        "assigned_visit_ids": assigned_visit_ids,
        "assigned_keys": assigned_keys,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
    }


def _load_raw_text_fixture(name: str) -> str:
    return (_RAW_TEXT_FIXTURES_PATH / name).read_text(encoding="utf-8")


def _extract_assigned_visits(visits: object) -> list[dict[str, object]]:
    if not isinstance(visits, list):
        return []
    return [
        visit
        for visit in visits
        if isinstance(visit, dict)
        and isinstance(visit.get("visit_id"), str)
        and visit.get("visit_id") != "unassigned"
    ]


def _extract_top_level_fields_by_key(data: dict[str, object], key: str) -> list[dict[str, object]]:
    fields = data.get("fields")
    if not isinstance(fields, list):
        return []
    return [field for field in fields if isinstance(field, dict) and field.get("key") == key]


def _extract_visit_field_value(visit: dict[str, object], *, key: str) -> str:
    fields = visit.get("fields")
    if not isinstance(fields, list):
        return ""
    for field in fields:
        if not isinstance(field, dict):
            continue
        if field.get("key") != key:
            continue
        value = field.get("value")
        if isinstance(value, str):
            return value
    return ""


def _coverage_ratio(source_text: str, candidate_text: str) -> float:
    normalized_source = re.sub(r"\W+", "", source_text.casefold())
    normalized_candidate = re.sub(r"\W+", "", candidate_text.casefold())
    if not normalized_source:
        return 0.0
    return len(normalized_candidate) / len(normalized_source)


def _get_calibration_counts(
    *,
    context_key: str,
    field_key: str,
    mapping_id: str | None,
    policy_version: str,
) -> tuple[int, int]:
    mapping_scope_key = mapping_id if mapping_id is not None else "__null__"
    with database.get_connection() as conn:
        row = conn.execute(
            """
            SELECT accept_count, edit_count
            FROM calibration_aggregates
            WHERE context_key = ?
              AND field_key = ?
              AND mapping_id_scope_key = ?
              AND policy_version = ?
            """,
            (context_key, field_key, mapping_scope_key, policy_version),
        ).fetchone()
    if row is None:
        return (0, 0)
    return (int(row["accept_count"]), int(row["edit_count"]))
