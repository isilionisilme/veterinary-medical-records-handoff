from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from backend.app.application.confidence_calibration import (
    build_context_key_from_interpretation_data,
    normalize_mapping_id,
    resolve_calibration_policy_version,
)
from backend.app.application.documents._edit_helpers import (
    _build_field_change_log,
    _build_global_schema_from_fields,
    _compose_field_mapping_confidence,
    _is_noop_update,
    _resolve_human_edit_candidate_confidence,
    _sanitize_confidence_breakdown,
    _sanitize_field_review_history_adjustment,
    _sanitize_text_extraction_reliability,
)
from backend.app.application.documents._edit_helpers import (
    is_field_value_empty as _is_field_value_empty,
)
from backend.app.application.documents.upload_service import _default_now_iso, _to_utc_z
from backend.app.application.global_schema import (
    CRITICAL_KEYS,
    VALUE_TYPE_BY_KEY,
)
from backend.app.config import human_edit_neutral_candidate_confidence
from backend.app.domain.models import ProcessingRunState
from backend.app.ports.document_repository import DocumentRepository


@dataclass(frozen=True, slots=True)
class InterpretationEditResult:
    """Successful interpretation edit result."""

    run_id: str
    interpretation_id: str
    version_number: int
    data: dict[str, object]


@dataclass(frozen=True, slots=True)
class InterpretationEditOutcome:
    """Outcome for interpretation edit attempts."""

    result: InterpretationEditResult | None
    conflict_reason: str | None = None
    invalid_reason: str | None = None


@dataclass(frozen=True, slots=True)
class _EditMutationContext:
    document_id: str
    run_id: str
    base_version_number: int
    new_version_number: int
    context_key: str
    calibration_policy_version: str
    neutral_candidate_confidence: float
    now_iso: str
    occurred_at: str


def apply_interpretation_edits(
    *,
    run_id: str,
    base_version_number: int,
    changes: list[dict[str, object]],
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
) -> InterpretationEditOutcome | None:
    """Apply veterinarian edits and append a new active interpretation version."""

    run = repository.get_run(run_id)
    if run is None:
        return None

    if any(
        row.state == ProcessingRunState.RUNNING
        for row in repository.list_processing_runs(document_id=run.document_id)
    ):
        return InterpretationEditOutcome(
            result=None,
            conflict_reason="REVIEW_BLOCKED_BY_ACTIVE_RUN",
        )

    if run.state != ProcessingRunState.COMPLETED:
        return InterpretationEditOutcome(
            result=None,
            conflict_reason="INTERPRETATION_NOT_AVAILABLE",
        )

    active_payload = repository.get_latest_artifact_payload(
        run_id=run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if active_payload is None:
        return InterpretationEditOutcome(result=None, conflict_reason="INTERPRETATION_MISSING")

    active_version_raw = active_payload.get("version_number", 1)
    active_version_number = active_version_raw if isinstance(active_version_raw, int) else 1
    if base_version_number != active_version_number:
        return InterpretationEditOutcome(
            result=None,
            conflict_reason="BASE_VERSION_MISMATCH",
        )

    active_data_raw = active_payload.get("data")
    active_data = dict(active_data_raw) if isinstance(active_data_raw, dict) else {}
    active_fields = _coerce_interpretation_fields(active_data.get("fields"))
    context_key = _resolve_context_key_for_edit_scopes(active_data, active_fields)
    calibration_policy_version = resolve_calibration_policy_version()
    neutral_candidate_confidence = human_edit_neutral_candidate_confidence()

    updated_fields = [dict(field) for field in active_fields]
    field_change_logs: list[dict[str, object]] = []
    now_iso = now_provider()
    occurred_at = _to_utc_z(now_iso)
    edit_context = _EditMutationContext(
        document_id=run.document_id,
        run_id=run_id,
        base_version_number=base_version_number,
        new_version_number=active_version_number + 1,
        context_key=context_key,
        calibration_policy_version=calibration_policy_version,
        neutral_candidate_confidence=neutral_candidate_confidence,
        now_iso=now_iso,
        occurred_at=occurred_at,
    )

    for index, change in enumerate(changes):
        op_raw = change.get("op")
        op = str(op_raw).upper() if isinstance(op_raw, str) else ""
        if op not in {"ADD", "UPDATE", "DELETE"}:
            return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].op")

        if op == "ADD":
            add_outcome = _apply_add_change(
                change=change,
                index=index,
                updated_fields=updated_fields,
                field_change_logs=field_change_logs,
                edit_context=edit_context,
            )
            if add_outcome is not None:
                return add_outcome
            continue

        existing_field_state = _resolve_existing_field_state(
            change=change,
            index=index,
            updated_fields=updated_fields,
        )
        if isinstance(existing_field_state, InterpretationEditOutcome):
            return existing_field_state

        existing_index, existing_field = existing_field_state
        existing_change_outcome = _apply_existing_field_change(
            op=op,
            change=change,
            index=index,
            existing_index=existing_index,
            existing_field=existing_field,
            updated_fields=updated_fields,
            field_change_logs=field_change_logs,
            edit_context=edit_context,
        )
        if existing_change_outcome is not None:
            return existing_change_outcome

    new_interpretation_id = str(uuid4())
    for log in field_change_logs:
        log["interpretation_id"] = new_interpretation_id

    new_data: dict[str, object] = dict(active_data)
    new_data["created_at"] = now_iso
    new_data["processing_run_id"] = run_id
    new_data["fields"] = [_sanitize_confidence_breakdown(field) for field in updated_fields]
    projected_global_schema = _build_global_schema_from_fields(updated_fields)
    new_data["global_schema"] = projected_global_schema

    new_payload = {
        "interpretation_id": new_interpretation_id,
        "version_number": active_version_number + 1,
        "data": new_data,
    }
    repository.append_artifact(
        run_id=run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
        payload=new_payload,
        created_at=now_iso,
    )
    for change_log in field_change_logs:
        repository.append_artifact(
            run_id=run_id,
            artifact_type="FIELD_CHANGE_LOG",
            payload=change_log,
            created_at=now_iso,
        )

    from backend.app.application.documents.review_payload_projector import (
        _normalize_review_interpretation_data,
    )

    return InterpretationEditOutcome(
        result=InterpretationEditResult(
            run_id=run_id,
            interpretation_id=new_interpretation_id,
            version_number=active_version_number + 1,
            data=_normalize_review_interpretation_data(new_data),
        )
    )


def _coerce_interpretation_fields(raw_fields: object) -> list[dict[str, object]]:
    if not isinstance(raw_fields, list):
        return []
    fields: list[dict[str, object]] = []
    for item in raw_fields:
        if isinstance(item, dict):
            fields.append(dict(item))
    return fields


def _resolve_context_key_for_edit_scopes(
    interpretation_data: dict[str, object],
    fields: list[dict[str, object]],
) -> str:
    for field in fields:
        context_key = field.get("context_key")
        if isinstance(context_key, str) and context_key.strip():
            return context_key
    return build_context_key_from_interpretation_data(interpretation_data)


def is_field_value_empty(value: object) -> bool:
    return _is_field_value_empty(value)


def _apply_add_change(
    *,
    change: dict[str, object],
    index: int,
    updated_fields: list[dict[str, object]],
    field_change_logs: list[dict[str, object]],
    edit_context: _EditMutationContext,
) -> InterpretationEditOutcome | None:
    key = str(change.get("key", "")).strip()
    if not key:
        return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].key")

    value_type = str(change.get("value_type", "")).strip() or VALUE_TYPE_BY_KEY.get(key, "string")
    if "value" not in change:
        return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].value")

    new_field_id = str(uuid4())
    new_candidate_confidence = edit_context.neutral_candidate_confidence
    new_review_history_adjustment = _sanitize_field_review_history_adjustment(0)
    new_field = {
        "field_id": new_field_id,
        "key": key,
        "value": change.get("value"),
        "value_type": value_type,
        "field_candidate_confidence": new_candidate_confidence,
        "field_mapping_confidence": _compose_field_mapping_confidence(
            candidate_confidence=new_candidate_confidence,
            review_history_adjustment=new_review_history_adjustment,
        ),
        "text_extraction_reliability": _sanitize_text_extraction_reliability(None),
        "field_review_history_adjustment": new_review_history_adjustment,
        "context_key": edit_context.context_key,
        "mapping_id": None,
        "policy_version": edit_context.calibration_policy_version,
        "is_critical": key in CRITICAL_KEYS,
        "origin": "human",
    }
    new_field_key = new_field.get("key")
    resolved_field_key = new_field_key if isinstance(new_field_key, str) else None
    updated_fields.append(new_field)
    field_change_logs.append(
        _build_field_change_log(
            document_id=edit_context.document_id,
            run_id=edit_context.run_id,
            interpretation_id="",
            base_version_number=edit_context.base_version_number,
            new_version_number=edit_context.new_version_number,
            field_id=new_field_id,
            field_key=resolved_field_key,
            value_type=value_type,
            old_value=None,
            new_value=change.get("value"),
            change_type="ADD",
            created_at=edit_context.now_iso,
            occurred_at=edit_context.occurred_at,
            context_key=edit_context.context_key,
            mapping_id=None,
            policy_version=edit_context.calibration_policy_version,
        )
    )
    return None


def _resolve_existing_field_state(
    *,
    change: dict[str, object],
    index: int,
    updated_fields: list[dict[str, object]],
) -> tuple[int, dict[str, object]] | InterpretationEditOutcome:
    field_id = str(change.get("field_id", "")).strip()
    if not field_id:
        return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].field_id")

    existing_index = next(
        (
            row_index
            for row_index, row in enumerate(updated_fields)
            if row.get("field_id") == field_id
        ),
        None,
    )
    if existing_index is None:
        return InterpretationEditOutcome(
            result=None,
            invalid_reason=f"changes[{index}].field_id_not_found",
        )
    return existing_index, updated_fields[existing_index]


def _apply_existing_field_change(
    *,
    op: str,
    change: dict[str, object],
    index: int,
    existing_index: int,
    existing_field: dict[str, object],
    updated_fields: list[dict[str, object]],
    field_change_logs: list[dict[str, object]],
    edit_context: _EditMutationContext,
) -> InterpretationEditOutcome | None:
    field_id = str(change.get("field_id", "")).strip()
    old_value = existing_field.get("value")
    field_key = existing_field.get("key")
    resolved_field_key = str(field_key) if isinstance(field_key, str) else None
    existing_value_type = existing_field.get("value_type")
    resolved_value_type = str(existing_value_type) if isinstance(existing_value_type, str) else None
    mapping_id = normalize_mapping_id(existing_field.get("mapping_id"))

    if op == "DELETE":
        updated_fields.pop(existing_index)
        field_change_logs.append(
            _build_field_change_log(
                document_id=edit_context.document_id,
                run_id=edit_context.run_id,
                interpretation_id="",
                base_version_number=edit_context.base_version_number,
                new_version_number=edit_context.new_version_number,
                field_id=field_id,
                field_key=resolved_field_key,
                value_type=resolved_value_type,
                old_value=old_value,
                new_value=None,
                change_type="DELETE",
                created_at=edit_context.now_iso,
                occurred_at=edit_context.occurred_at,
                context_key=edit_context.context_key,
                mapping_id=mapping_id,
                policy_version=edit_context.calibration_policy_version,
            )
        )
        return None

    if "value" not in change:
        return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].value")

    value_type = str(change.get("value_type", "")).strip()
    if not value_type:
        return InterpretationEditOutcome(result=None, invalid_reason=f"changes[{index}].value_type")

    if _is_noop_update(
        old_value=old_value,
        new_value=change.get("value"),
        existing_value_type=resolved_value_type,
        incoming_value_type=value_type,
    ):
        return None

    next_candidate_confidence = _resolve_human_edit_candidate_confidence(
        existing_field,
        neutral_candidate_confidence=edit_context.neutral_candidate_confidence,
    )
    next_review_history_adjustment = _sanitize_field_review_history_adjustment(0)
    next_mapping_confidence = _compose_field_mapping_confidence(
        candidate_confidence=next_candidate_confidence,
        review_history_adjustment=next_review_history_adjustment,
    )
    updated_fields[existing_index] = {
        **updated_fields[existing_index],
        "value": change.get("value"),
        "value_type": value_type,
        "origin": "human",
        "field_candidate_confidence": next_candidate_confidence,
        "field_mapping_confidence": next_mapping_confidence,
        "text_extraction_reliability": _sanitize_text_extraction_reliability(None),
        "field_review_history_adjustment": next_review_history_adjustment,
        "context_key": edit_context.context_key,
        "mapping_id": mapping_id,
        "policy_version": edit_context.calibration_policy_version,
    }
    field_change_logs.append(
        _build_field_change_log(
            document_id=edit_context.document_id,
            run_id=edit_context.run_id,
            interpretation_id="",
            base_version_number=edit_context.base_version_number,
            new_version_number=edit_context.new_version_number,
            field_id=field_id,
            field_key=resolved_field_key,
            value_type=value_type,
            old_value=old_value,
            new_value=change.get("value"),
            change_type="UPDATE",
            created_at=edit_context.now_iso,
            occurred_at=edit_context.occurred_at,
            context_key=edit_context.context_key,
            mapping_id=mapping_id,
            policy_version=edit_context.calibration_policy_version,
        )
    )
    return None
