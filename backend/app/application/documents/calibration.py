from __future__ import annotations

import logging

from backend.app.application.confidence_calibration import (
    CALIBRATION_SIGNAL_ACCEPTED_UNCHANGED,
    CALIBRATION_SIGNAL_EDITED,
    is_empty_value,
    normalize_mapping_id,
    resolve_calibration_policy_version,
)
from backend.app.application.documents.edit_service import (
    _coerce_interpretation_fields,
    _resolve_context_key_for_edit_scopes,
)
from backend.app.ports.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


def _build_review_calibration_deltas(
    *,
    document_id: str,
    run_id: str,
    interpretation_data: dict[str, object],
) -> list[dict[str, object]]:
    fields = _coerce_interpretation_fields(interpretation_data.get("fields"))
    context_key = _resolve_context_key_for_edit_scopes(interpretation_data, fields)
    policy_version = next(
        (
            str(field_policy_version).strip()
            for field in fields
            if isinstance((field_policy_version := field.get("policy_version")), str)
            and str(field_policy_version).strip()
        ),
        resolve_calibration_policy_version(),
    )
    scoped_deltas: dict[tuple[str, str | None], dict[str, object]] = {}
    for field in fields:
        field_key = field.get("key")
        if not isinstance(field_key, str) or not field_key.strip():
            continue
        if is_empty_value(field.get("value")):
            continue

        mapping_id = normalize_mapping_id(field.get("mapping_id"))
        scope = (field_key, mapping_id)
        entry = scoped_deltas.setdefault(
            scope,
            {
                "context_key": context_key,
                "field_key": field_key,
                "mapping_id": mapping_id,
                "policy_version": policy_version,
                "accept_delta": 0,
                "edit_delta": 0,
            },
        )

        origin = field.get("origin")
        if origin == "human":
            entry["edit_delta"] = 1
            entry["accept_delta"] = 0
        elif origin == "machine" and int(entry["edit_delta"]) == 0:
            entry["accept_delta"] = 1

    return [
        {
            "event_type": (
                "field_accepted_unchanged"
                if delta["accept_delta"] == 1
                else "field_edited_confirmed"
            ),
            "source": "mark_reviewed",
            "document_id": document_id,
            "run_id": run_id,
            "field_key": delta["field_key"],
            "mapping_id": delta["mapping_id"],
            "context_key": delta["context_key"],
            "policy_version": delta["policy_version"],
            "accept_delta": delta["accept_delta"],
            "edit_delta": delta["edit_delta"],
        }
        for delta in scoped_deltas.values()
        if delta["accept_delta"] != 0 or delta["edit_delta"] != 0
    ]


def _apply_reviewed_document_calibration(
    *,
    document_id: str,
    reviewed_run_id: str | None,
    repository: DocumentRepository,
    created_at: str,
) -> None:
    if reviewed_run_id is None:
        return
    payload = repository.get_latest_artifact_payload(
        run_id=reviewed_run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if not isinstance(payload, dict):
        return
    interpretation_data = payload.get("data")
    if not isinstance(interpretation_data, dict):
        return

    signal_events = _build_review_calibration_deltas(
        document_id=document_id,
        run_id=reviewed_run_id,
        interpretation_data=interpretation_data,
    )
    for event in signal_events:
        repository.apply_calibration_deltas(
            context_key=str(event["context_key"]),
            field_key=str(event["field_key"]),
            mapping_id=normalize_mapping_id(event.get("mapping_id")),
            policy_version=str(event["policy_version"]),
            accept_delta=int(event["accept_delta"]),
            edit_delta=int(event["edit_delta"]),
            updated_at=created_at,
        )
        signal_type = (
            CALIBRATION_SIGNAL_ACCEPTED_UNCHANGED
            if int(event["accept_delta"]) == 1
            else CALIBRATION_SIGNAL_EDITED
        )
        repository.append_artifact(
            run_id=reviewed_run_id,
            artifact_type="CALIBRATION_SIGNAL",
            payload={
                **event,
                "signal_type": signal_type,
                "created_at": created_at,
            },
            created_at=created_at,
        )

    snapshot_payload = {
        "event_type": "calibration_review_snapshot",
        "source": "mark_reviewed",
        "document_id": document_id,
        "run_id": reviewed_run_id,
        "status": "applied",
        "created_at": created_at,
        "deltas": signal_events,
    }
    repository.append_artifact(
        run_id=reviewed_run_id,
        artifact_type="CALIBRATION_REVIEW_SNAPSHOT",
        payload=snapshot_payload,
        created_at=created_at,
    )


def _revert_reviewed_document_calibration(
    *,
    document_id: str,
    reviewed_run_id: str | None,
    repository: DocumentRepository,
    created_at: str,
) -> None:
    snapshot_run_id = reviewed_run_id
    snapshot: dict[str, object] | None = None

    if reviewed_run_id is not None:
        candidate_snapshot = repository.get_latest_artifact_payload(
            run_id=reviewed_run_id,
            artifact_type="CALIBRATION_REVIEW_SNAPSHOT",
        )
        if isinstance(candidate_snapshot, dict):
            if candidate_snapshot.get("status") == "reverted":
                return
            snapshot = candidate_snapshot
        else:
            logger.warning(
                "Calibration snapshot missing while reopening document_id=%s run_id=%s",
                document_id,
                reviewed_run_id,
            )

    if snapshot is None:
        fallback = repository.get_latest_applied_calibration_snapshot(document_id=document_id)
        if fallback is None:
            logger.warning(
                "Calibration snapshot missing while reopening document_id=%s reviewed_run_id=%s",
                document_id,
                reviewed_run_id,
            )
            return
        snapshot_run_id, snapshot = fallback

    raw_deltas = snapshot.get("deltas")
    if not isinstance(raw_deltas, list):
        logger.warning(
            "Calibration snapshot malformed while reopening document_id=%s run_id=%s",
            document_id,
            snapshot_run_id,
        )
        return

    reverted_deltas: list[dict[str, object]] = []
    for raw_delta in raw_deltas:
        if not isinstance(raw_delta, dict):
            continue
        context_key = raw_delta.get("context_key")
        field_key = raw_delta.get("field_key")
        policy_version = raw_delta.get("policy_version")
        if not isinstance(context_key, str) or not context_key.strip():
            continue
        if not isinstance(field_key, str) or not field_key.strip():
            continue
        if not isinstance(policy_version, str) or not policy_version.strip():
            continue

        accept_delta = int(raw_delta.get("accept_delta", 0))
        edit_delta = int(raw_delta.get("edit_delta", 0))
        if accept_delta == 0 and edit_delta == 0:
            continue

        mapping_id = normalize_mapping_id(raw_delta.get("mapping_id"))
        repository.apply_calibration_deltas(
            context_key=context_key,
            field_key=field_key,
            mapping_id=mapping_id,
            policy_version=policy_version,
            accept_delta=-accept_delta,
            edit_delta=-edit_delta,
            updated_at=created_at,
        )
        reverted_deltas.append(
            {
                "context_key": context_key,
                "field_key": field_key,
                "mapping_id": mapping_id,
                "policy_version": policy_version,
                "accept_delta": -accept_delta,
                "edit_delta": -edit_delta,
            }
        )

    repository.append_artifact(
        run_id=snapshot_run_id,
        artifact_type="CALIBRATION_REVIEW_REVERTED",
        payload={
            "event_type": "calibration_review_reverted",
            "source": "reopen_reviewed_document",
            "document_id": document_id,
            "run_id": snapshot_run_id,
            "reverted_from_snapshot_created_at": snapshot.get("created_at"),
            "created_at": created_at,
            "deltas": reverted_deltas,
        },
        created_at=created_at,
    )
    repository.append_artifact(
        run_id=snapshot_run_id,
        artifact_type="CALIBRATION_REVIEW_SNAPSHOT",
        payload={
            **snapshot,
            "status": "reverted",
            "reverted_at": created_at,
        },
        created_at=created_at,
    )
