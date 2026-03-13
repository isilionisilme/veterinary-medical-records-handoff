"""Aggregate reporting over persisted extraction observability runs."""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from typing import Any

from .persistence import get_extraction_runs
from .snapshot import _as_text, _coerce_confidence, _extract_top_candidates, _truncate_text
from .triage import _suspicious_accepted_flags

logger = logging.getLogger(__name__)
_uvicorn_logger = logging.getLogger("uvicorn.error")


def _emit_info(message: str) -> None:
    if _uvicorn_logger.handlers:
        _uvicorn_logger.info(message)
        return
    logger.info(message)


def _update_field_statistics(
    field_stats: dict[str, Any],
    field_key: str,
    raw_payload: dict[str, Any],
) -> None:
    status = str(raw_payload.get("status", "")).strip().lower()
    counter_key = {
        "missing": "missing_count",
        "rejected": "rejected_count",
        "accepted": "accepted_count",
    }.get(status)
    if counter_key:
        field_stats[counter_key] += 1

    top_candidates = _extract_top_candidates(raw_payload)
    top1 = top_candidates[0] if top_candidates else None
    top1_value = _as_text(top1.get("value")) if isinstance(top1, dict) else None
    if status in {"missing", "rejected"} and top1_value:
        field_stats["top1_counter"][top1_value] += 1
        top1_conf = _coerce_confidence(top1.get("confidence")) if isinstance(top1, dict) else None
        if top1_conf is not None:
            field_stats["top1_confidences"].append(top1_conf)

    if status == "missing":
        if top1_value:
            field_stats["missing_with_candidates_count"] += 1
            field_stats["missing_top1_counter"][top1_value] += 1
            missing_top1_conf = (
                _coerce_confidence(top1.get("confidence")) if isinstance(top1, dict) else None
            )
            if missing_top1_conf is not None:
                field_stats["missing_top1_confidences"].append(missing_top1_conf)
        else:
            field_stats["missing_without_candidates_count"] += 1

    if status == "accepted":
        value_for_flags = (
            _as_text(raw_payload.get("valueNormalized"))
            or _as_text(raw_payload.get("valueRaw"))
            or _as_text(raw_payload.get("rawCandidate"))
            or top1_value
        )
        if _suspicious_accepted_flags(field_key, value_for_flags):
            field_stats["suspicious_count"] += 1


def _accumulate_field_statistics(selected_runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "missing_count": 0,
            "rejected_count": 0,
            "accepted_count": 0,
            "suspicious_count": 0,
            "top1_counter": Counter(),
            "top1_confidences": [],
            "missing_top1_counter": Counter(),
            "missing_top1_confidences": [],
            "missing_with_candidates_count": 0,
            "missing_without_candidates_count": 0,
        }
    )

    for run in selected_runs:
        fields = run.get("fields") if isinstance(run.get("fields"), dict) else {}
        for field_key, raw_payload in fields.items():
            if not isinstance(raw_payload, dict):
                continue
            _update_field_statistics(stats[str(field_key)], str(field_key), raw_payload)

    return stats


def _compute_field_rows(stats: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    field_rows: list[dict[str, Any]] = []
    for field, field_stats in stats.items():
        top1_sample = (
            field_stats["top1_counter"].most_common(1)[0][0]
            if field_stats["top1_counter"]
            else None
        )
        confidences = field_stats["top1_confidences"]
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else None
        missing_top1_sample = (
            field_stats["missing_top1_counter"].most_common(1)[0][0]
            if field_stats["missing_top1_counter"]
            else None
        )
        missing_confidences = field_stats["missing_top1_confidences"]
        avg_top1_conf = (
            round(sum(missing_confidences) / len(missing_confidences), 2)
            if missing_confidences
            else None
        )
        missing_with_candidates_count = int(field_stats["missing_with_candidates_count"])
        field_rows.append(
            {
                "field": field,
                "missing_count": int(field_stats["missing_count"]),
                "rejected_count": int(field_stats["rejected_count"]),
                "accepted_count": int(field_stats["accepted_count"]),
                "suspicious_count": int(field_stats["suspicious_count"]),
                "top1_sample": _truncate_text(top1_sample),
                "avg_conf": avg_conf,
                "has_candidates": missing_with_candidates_count > 0,
                "missing_with_candidates_count": missing_with_candidates_count,
                "missing_without_candidates_count": int(
                    field_stats["missing_without_candidates_count"]
                ),
                "avg_top1_conf": avg_top1_conf,
                "top_key_tokens": _truncate_text(missing_top1_sample, limit=30),
            }
        )

    field_rows.sort(
        key=lambda item: (
            int(item.get("missing_count", 0) or 0),
            int(item.get("rejected_count", 0) or 0),
            int(item.get("suspicious_count", 0) or 0),
            str(item.get("field", "")),
        ),
        reverse=True,
    )
    return field_rows


def _build_extraction_summary(
    document_id: str,
    total_runs: int,
    considered_runs: int,
    field_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    most_missing = sorted(
        [item for item in field_rows if int(item.get("missing_count", 0) or 0) > 0],
        key=lambda item: (
            int(item.get("missing_count", 0) or 0),
            int(item.get("rejected_count", 0) or 0),
            str(item.get("field", "")),
        ),
        reverse=True,
    )
    most_rejected = sorted(
        [item for item in field_rows if int(item.get("rejected_count", 0) or 0) > 0],
        key=lambda item: (
            int(item.get("rejected_count", 0) or 0),
            int(item.get("missing_count", 0) or 0),
            str(item.get("field", "")),
        ),
        reverse=True,
    )
    return {
        "document_id": document_id,
        "total_runs": total_runs,
        "considered_runs": considered_runs,
        "missing_fields_with_candidates": sum(
            1 for item in most_missing if bool(item.get("has_candidates"))
        ),
        "missing_fields_without_candidates": sum(
            1 for item in most_missing if not bool(item.get("has_candidates"))
        ),
        "fields": field_rows,
        "most_missing_fields": most_missing[:10],
        "most_rejected_fields": most_rejected[:10],
    }


def summarize_extraction_runs(
    document_id: str,
    *,
    limit: int = 20,
    run_id: str | None = None,
) -> dict[str, Any] | None:
    runs = get_extraction_runs(document_id)
    if not runs:
        return None
    selected_runs = (
        [run for run in runs if str(run.get("runId", "")).strip() == run_id]
        if run_id
        else runs[-max(1, limit) :]
    )
    if not selected_runs:
        return None

    stats = _accumulate_field_statistics(selected_runs)
    field_rows = _compute_field_rows(stats)
    summary = _build_extraction_summary(
        document_id=document_id,
        total_runs=len(runs),
        considered_runs=len(selected_runs),
        field_rows=field_rows,
    )
    _log_extraction_runs_summary(summary)
    return summary


def _log_extraction_runs_summary(summary: dict[str, Any]) -> None:
    document_id = _as_text(summary.get("document_id")) or ""
    considered_runs = int(summary.get("considered_runs", 0) or 0)
    missing_with_candidates = int(summary.get("missing_fields_with_candidates", 0) or 0)
    missing_without_candidates = int(summary.get("missing_fields_without_candidates", 0) or 0)
    fields = summary.get("fields") if isinstance(summary.get("fields"), list) else []
    most_missing = (
        summary.get("most_missing_fields")
        if isinstance(summary.get("most_missing_fields"), list)
        else []
    )
    most_rejected = (
        summary.get("most_rejected_fields")
        if isinstance(summary.get("most_rejected_fields"), list)
        else []
    )

    lines = [
        "[extraction-observability] "
        f"document={document_id} runs_summary "
        f"considered_runs={considered_runs} tracked_fields={len(fields)} "
        f"missing_fields_with_candidates={missing_with_candidates} "
        f"missing_fields_without_candidates={missing_without_candidates}",
        "MOST_MISSING:",
    ]
    if not most_missing:
        lines.append("- none")
    else:
        for item in most_missing[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('field')}: "
                f"missing={int(item.get('missing_count', 0) or 0)} "
                f"rejected={int(item.get('rejected_count', 0) or 0)} "
                f"has_candidates={bool(item.get('has_candidates'))} "
                f"top1={item.get('top1_sample')!r} "
                f"avg_top1_conf={item.get('avg_top1_conf')} "
                f"top_key_tokens={item.get('top_key_tokens')!r}"
            )

    lines.append("MOST_REJECTED:")
    if not most_rejected:
        lines.append("- none")
    else:
        for item in most_rejected[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('field')}: "
                f"rejected={int(item.get('rejected_count', 0) or 0)} "
                f"missing={int(item.get('missing_count', 0) or 0)} "
                f"top1={item.get('top1_sample')!r} "
                f"avg_conf={item.get('avg_conf')}"
            )

    _emit_info("\n".join(lines))
