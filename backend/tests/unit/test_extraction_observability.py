from __future__ import annotations

import json
from pathlib import Path

from backend.app.application import extraction_observability


def _snapshot(
    *,
    run_id: str,
    document_id: str,
    status: str,
    confidence: str | None,
) -> dict[str, object]:
    return {
        "runId": run_id,
        "documentId": document_id,
        "createdAt": "2026-02-13T20:00:00Z",
        "schemaVersion": "canonical",
        "fields": {
            "pet_name": {
                "status": status,
                "confidence": confidence,
                "valueNormalized": "Luna" if status == "accepted" else None,
                "valueRaw": "Luna" if status == "accepted" else None,
                "reason": "invalid-value" if status == "rejected" else None,
            },
        },
        "counts": {
            "totalFields": 1,
            "accepted": 1 if status == "accepted" else 0,
            "rejected": 1 if status == "rejected" else 0,
            "missing": 1 if status == "missing" else 0,
            "low": 1 if confidence == "low" else 0,
            "mid": 1 if confidence == "mid" else 0,
            "high": 1 if confidence == "high" else 0,
        },
    }


def test_persist_snapshot_keeps_only_latest_20_runs(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    document_id = "doc-ring"
    for index in range(25):
        extraction_observability.persist_extraction_run_snapshot(
            _snapshot(
                run_id=f"run-{index}",
                document_id=document_id,
                status="accepted",
                confidence="mid",
            )
        )

    runs = extraction_observability.get_extraction_runs(document_id)
    assert len(runs) == 20
    assert runs[0]["runId"] == "run-5"
    assert runs[-1]["runId"] == "run-24"


def test_persist_snapshot_reports_changed_fields_against_previous(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    document_id = "doc-diff"
    first = extraction_observability.persist_extraction_run_snapshot(
        _snapshot(run_id="run-1", document_id=document_id, status="missing", confidence=None)
    )
    second = extraction_observability.persist_extraction_run_snapshot(
        _snapshot(run_id="run-2", document_id=document_id, status="accepted", confidence="high")
    )

    assert first["changed_fields"] == 0
    assert second["changed_fields"] >= 1


def test_persist_snapshot_is_idempotent_per_document_and_run_id(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    document_id = "doc-idempotent"
    first = extraction_observability.persist_extraction_run_snapshot(
        _snapshot(run_id="run-1", document_id=document_id, status="missing", confidence=None)
    )
    second = extraction_observability.persist_extraction_run_snapshot(
        _snapshot(run_id="run-1", document_id=document_id, status="accepted", confidence="high")
    )

    runs = extraction_observability.get_extraction_runs(document_id)
    assert len(runs) == 1
    assert runs[0]["runId"] == "run-1"
    assert runs[0]["fields"]["pet_name"]["status"] == "accepted"
    assert first["was_created"] is True
    assert second["was_created"] is False


def test_get_extraction_runs_preserves_canonical_schema_version(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    extraction_observability.persist_extraction_run_snapshot(
        {
            **_snapshot(
                run_id="run-schema-version-coercion",
                document_id="doc-schema-version-coercion",
                status="accepted",
                confidence="mid",
            ),
            "schemaVersion": "canonical",
        }
    )

    runs = extraction_observability.get_extraction_runs("doc-schema-version-coercion")
    assert len(runs) == 1
    assert runs[0]["schemaVersion"] == "canonical"


def test_get_extraction_runs_coerces_historical_schema_version_to_canonical(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    document_id = "doc-historical-schema-version"
    path = extraction_observability._document_runs_path(document_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            [
                {
                    **_snapshot(
                        run_id="run-legacy-schema-version",
                        document_id=document_id,
                        status="accepted",
                        confidence="mid",
                    ),
                    "schemaVersion": "v1",
                }
            ]
        ),
        encoding="utf-8",
    )

    runs = extraction_observability.get_extraction_runs(document_id)
    assert len(runs) == 1
    assert runs[0]["schemaVersion"] == "canonical"


def test_build_extraction_triage_populates_missing_and_rejected_lists() -> None:
    snapshot = {
        "runId": "run-triage",
        "documentId": "doc-triage",
        "createdAt": "2026-02-13T20:05:00Z",
        "fields": {
            "claim_id": {"status": "missing", "confidence": None},
            "weight": {
                "status": "rejected",
                "confidence": None,
                "valueRaw": "cien kilos",
                "reason": "invalid-format",
                "rawCandidate": "cien kilos",
            },
        },
        "counts": {"accepted": 0, "missing": 1, "rejected": 1, "low": 0, "mid": 0, "high": 0},
    }

    triage = extraction_observability.build_extraction_triage(snapshot)

    assert triage["missing"][0]["field"] == "claim_id"
    assert triage["missing"][0]["reason"] == "missing"
    assert triage["rejected"][0]["field"] == "weight"
    assert triage["rejected"][0]["reason"] == "invalid-format"
    assert triage["rejected"][0]["rawCandidate"] == "cien kilos"


def test_build_extraction_triage_flags_suspicious_accepted_fields() -> None:
    snapshot = {
        "runId": "run-flags",
        "documentId": "doc-flags",
        "createdAt": "2026-02-13T20:06:00Z",
        "fields": {
            "microchip_id": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "Maria Lopez Calle 123",
            },
            "weight": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "500 kg",
            },
            "species": {
                "status": "accepted",
                "confidence": "low",
                "valueNormalized": "equino",
            },
            "sex": {
                "status": "accepted",
                "confidence": "low",
                "valueNormalized": "desconocido",
            },
            "notes": {
                "status": "accepted",
                "confidence": "high",
                "valueNormalized": "x" * 120,
            },
            "clinic_address": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "PO Box 123 contacto@vet.es",
            },
        },
        "counts": {"accepted": 6, "missing": 0, "rejected": 0, "low": 2, "mid": 3, "high": 1},
    }

    triage = extraction_observability.build_extraction_triage(snapshot)
    suspicious_by_field = {item["field"]: item for item in triage["suspiciousAccepted"]}

    assert "microchip_non_digit_characters" in suspicious_by_field["microchip_id"]["flags"]
    assert "weight_out_of_range" in suspicious_by_field["weight"]["flags"]
    assert "species_outside_allowed_set" in suspicious_by_field["species"]["flags"]
    assert "sex_outside_allowed_set" in suspicious_by_field["sex"]["flags"]
    assert "value_too_long" in suspicious_by_field["notes"]["flags"]
    clinic_address_flags = suspicious_by_field["clinic_address"]["flags"]
    assert "clinic_address_contains_email" in clinic_address_flags
    assert "clinic_address_po_box_without_street" in clinic_address_flags


def test_build_extraction_triage_flags_microchip_phone_and_document_context() -> None:
    phone_snapshot = {
        "runId": "run-microchip-context",
        "documentId": "doc-microchip-context",
        "createdAt": "2026-02-13T20:06:00Z",
        "fields": {
            "microchip_id": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "Teléfono 612345678",
            },
        },
        "counts": {"accepted": 1, "missing": 0, "rejected": 0, "low": 0, "mid": 1, "high": 0},
    }

    triage = extraction_observability.build_extraction_triage(phone_snapshot)
    suspicious_by_field = {item["field"]: item for item in triage["suspiciousAccepted"]}

    phone_flags = suspicious_by_field["microchip_id"]["flags"]
    assert "microchip_phone_context" in phone_flags
    assert "microchip_phone_like_digits" in phone_flags

    document_snapshot = {
        "runId": "run-microchip-document-context",
        "documentId": "doc-microchip-document-context",
        "createdAt": "2026-02-13T20:06:00Z",
        "fields": {
            "microchip_id": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "NIF 12345678Z",
            },
        },
        "counts": {"accepted": 1, "missing": 0, "rejected": 0, "low": 0, "mid": 1, "high": 0},
    }

    triage = extraction_observability.build_extraction_triage(document_snapshot)
    suspicious_by_field = {item["field"]: item for item in triage["suspiciousAccepted"]}

    doc_flags = suspicious_by_field["microchip_id"]["flags"]
    assert "microchip_document_id_context" in doc_flags


def test_build_extraction_triage_keeps_top_candidates_shape() -> None:
    snapshot = {
        "runId": "run-top-candidates",
        "documentId": "doc-top-candidates",
        "createdAt": "2026-02-13T20:06:00Z",
        "fields": {
            "microchip_id": {
                "status": "rejected",
                "confidence": None,
                "valueRaw": "00023035139 NHC",
                "reason": "non-digit",
                "rawCandidate": "00023035139 NHC",
                "topCandidates": [
                    {"value": "00023035139 NHC", "confidence": 0.86},
                    {"value": "NHC 2.c", "confidence": 0.42},
                ],
            },
            "owner_id": {
                "status": "missing",
                "confidence": None,
                "topCandidates": [
                    {"value": "DNI 12345678A", "confidence": 0.51},
                ],
            },
        },
        "counts": {"accepted": 0, "missing": 1, "rejected": 1, "low": 0, "mid": 0, "high": 0},
    }

    triage = extraction_observability.build_extraction_triage(snapshot)
    rejected_item = triage["rejected"][0]
    missing_item = triage["missing"][0]

    assert rejected_item["topCandidates"][0]["value"] == "00023035139 NHC"
    assert missing_item["topCandidates"][0]["value"] == "DNI 12345678A"


def test_persist_snapshot_logs_goal_fields_status_and_diff(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path)

    emitted_logs: list[str] = []

    def _capture(message: str) -> None:
        emitted_logs.append(message)

    monkeypatch.setattr(extraction_observability, "_emit_info", _capture)

    first_snapshot = {
        "runId": "run-goal-1",
        "documentId": "doc-goal",
        "createdAt": "2026-02-14T07:40:00Z",
        "schemaVersion": "canonical",
        "fields": {
            "owner_name": {
                "status": "missing",
                "confidence": None,
                "topCandidates": [
                    {"value": "BEATRIZ ABARCA", "confidence": 0.66},
                ],
            },
            "vet_name": {
                "status": "missing",
                "confidence": None,
            },
        },
        "counts": {
            "totalFields": 2,
            "accepted": 0,
            "rejected": 0,
            "missing": 2,
            "low": 0,
            "mid": 0,
            "high": 0,
        },
    }
    second_snapshot = {
        "runId": "run-goal-2",
        "documentId": "doc-goal",
        "createdAt": "2026-02-14T07:41:00Z",
        "schemaVersion": "canonical",
        "fields": {
            "owner_name": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "BEATRIZ ABARCA",
                "topCandidates": [
                    {"value": "BEATRIZ ABARCA", "confidence": 0.66},
                ],
            },
            "vet_name": {
                "status": "missing",
                "confidence": None,
            },
        },
        "counts": {
            "totalFields": 2,
            "accepted": 1,
            "rejected": 0,
            "missing": 1,
            "low": 0,
            "mid": 1,
            "high": 0,
        },
    }

    extraction_observability.persist_extraction_run_snapshot(first_snapshot)
    extraction_observability.persist_extraction_run_snapshot(second_snapshot)

    logs_joined = "\n".join(emitted_logs)
    assert "goal_fields" in logs_joined
    assert "GOAL_FIELDS_DIFF" in logs_joined
    assert "owner_name: status=missing" in logs_joined
    assert "owner_name: status=missing" in logs_joined and "-> status=accepted" in logs_joined


def test_build_snapshot_from_interpretation_returns_expected_shape() -> None:
    interpretation_payload = {
        "interpretation_id": "int-1",
        "version_number": 1,
        "data": {
            "global_schema": {
                "pet_name": "Luna",
                "owner_name": "BEATRIZ ABARCA",
                "microchip_id": "00023035139",
            },
            "fields": [
                {
                    "key": "pet_name",
                    "value": "Luna",
                    "confidence": 0.72,
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                },
                {
                    "key": "owner_name",
                    "value": "BEATRIZ ABARCA",
                    "confidence": 0.66,
                    "evidence": {"page": 2, "snippet": "Nombre BEATRIZ ABARCA"},
                },
                {
                    "key": "microchip_id",
                    "value": "00023035139",
                    "confidence": 0.91,
                    "evidence": {"page": 2, "snippet": "Chip 00023035139"},
                },
            ],
        },
    }

    snapshot = extraction_observability.build_extraction_snapshot_from_interpretation(
        document_id="doc-auto",
        run_id="run-auto-1",
        created_at="2026-02-14T08:00:00Z",
        interpretation_payload=interpretation_payload,
    )

    assert snapshot is not None
    assert snapshot["documentId"] == "doc-auto"
    assert snapshot["runId"] == "run-auto-1"
    assert snapshot["counts"]["accepted"] == 3
    assert snapshot["counts"]["rejected"] == 0
    assert snapshot["fields"]["pet_name"]["status"] == "accepted"
    assert snapshot["fields"]["owner_name"]["status"] == "accepted"
    assert snapshot["fields"]["microchip_id"]["status"] == "accepted"
    assert snapshot["fields"]["pet_name"]["topCandidates"][0]["value"] == "Luna"


def test_build_snapshot_from_interpretation_uses_first_repeatable_value() -> None:
    interpretation_payload = {
        "interpretation_id": "int-2",
        "version_number": 1,
        "data": {
            "global_schema": {
                "medication": ["Amoxicilina", "Meloxicam"],
            },
            "fields": [
                {
                    "key": "medication",
                    "value": "Amoxicilina",
                    "confidence": 0.81,
                    "evidence": {"page": 1, "snippet": "Medicacion: Amoxicilina"},
                },
                {
                    "key": "medication",
                    "value": "Meloxicam",
                    "confidence": 0.62,
                    "evidence": {"page": 1, "snippet": "Medicacion: Meloxicam"},
                },
            ],
        },
    }

    snapshot = extraction_observability.build_extraction_snapshot_from_interpretation(
        document_id="doc-auto",
        run_id="run-auto-2",
        created_at="2026-02-14T08:01:00Z",
        interpretation_payload=interpretation_payload,
    )

    assert snapshot is not None
    assert snapshot["fields"]["medication"]["status"] == "accepted"
    assert snapshot["fields"]["medication"]["valueNormalized"] == "Amoxicilina"
    assert snapshot["fields"]["medication"]["topCandidates"][0]["value"] == "Amoxicilina"
