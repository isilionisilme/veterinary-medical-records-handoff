from __future__ import annotations

import json

import pytest

import backend.app.application.global_schema as schema_module
from backend.app.application.global_schema import (
    CONTRACT_NAME,
    CONTRACT_REVISION,
    CRITICAL_KEYS,
    GLOBAL_SCHEMA_KEYS,
)


def test_global_schema_contract_order() -> None:
    expected_keys = [
        "claim_id",
        "clinic_name",
        "clinic_address",
        "vet_name",
        "document_date",
        "pet_name",
        "species",
        "breed",
        "sex",
        "age",
        "dob",
        "microchip_id",
        "weight",
        "owner_name",
        "owner_id",
        "owner_address",
        "visit_date",
        "admission_date",
        "discharge_date",
        "reason_for_visit",
        "observations",
        "actions",
        "diagnosis",
        "symptoms",
        "procedure",
        "medication",
        "treatment_plan",
        "allergies",
        "vaccinations",
        "lab_result",
        "imaging",
        "invoice_total",
        "covered_amount",
        "non_covered_amount",
        "line_item",
        "notes",
        "language",
    ]

    assert list(GLOBAL_SCHEMA_KEYS) == expected_keys
    assert len(GLOBAL_SCHEMA_KEYS) == 37


def test_global_schema_contract_critical_subset() -> None:
    expected_critical = {
        "pet_name",
        "species",
        "breed",
        "sex",
        "age",
        "weight",
        "visit_date",
        "diagnosis",
        "medication",
        "procedure",
    }

    assert CRITICAL_KEYS == expected_critical


def test_global_schema_contract_exposes_metadata() -> None:
    assert CONTRACT_NAME == "global-schema-flat"
    assert CONTRACT_REVISION == "2026-02-canonical"


def test_load_schema_contract_rejects_missing_required_field_keys(tmp_path, monkeypatch) -> None:
    invalid_contract_path = tmp_path / "invalid_schema_contract.json"
    invalid_contract_path.write_text(
        json.dumps(
            {
                "fields": [
                    {
                        "label": "Missing key",
                        "section": "Test",
                        "value_type": "string",
                        "repeatable": False,
                        "critical": False,
                        "optional": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(schema_module, "_SCHEMA_CONTRACT_PATH", invalid_contract_path)

    with pytest.raises(RuntimeError, match="missing keys: key"):
        schema_module._load_schema_contract()


def test_load_schema_contract_rejects_duplicate_keys(tmp_path, monkeypatch) -> None:
    invalid_contract_path = tmp_path / "duplicate_schema_contract.json"
    invalid_contract_path.write_text(
        json.dumps(
            {
                "fields": [
                    {
                        "key": "pet_name",
                        "label": "Nombre",
                        "section": "Paciente",
                        "value_type": "string",
                        "repeatable": False,
                        "critical": True,
                        "optional": False,
                    },
                    {
                        "key": "pet_name",
                        "label": "Nombre duplicado",
                        "section": "Paciente",
                        "value_type": "string",
                        "repeatable": False,
                        "critical": True,
                        "optional": False,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(schema_module, "_SCHEMA_CONTRACT_PATH", invalid_contract_path)

    with pytest.raises(RuntimeError, match="duplicate key: pet_name"):
        schema_module._load_schema_contract()


def test_load_schema_contract_rejects_missing_file(tmp_path, monkeypatch) -> None:
    missing_contract_path = tmp_path / "missing_schema_contract.json"
    monkeypatch.setattr(schema_module, "_SCHEMA_CONTRACT_PATH", missing_contract_path)

    with pytest.raises(RuntimeError, match="contract file not found"):
        schema_module._load_schema_contract()


def test_load_schema_contract_rejects_invalid_json(tmp_path, monkeypatch) -> None:
    invalid_contract_path = tmp_path / "invalid_json_contract.json"
    invalid_contract_path.write_text("{ invalid json", encoding="utf-8")
    monkeypatch.setattr(schema_module, "_SCHEMA_CONTRACT_PATH", invalid_contract_path)

    with pytest.raises(RuntimeError, match="contract JSON is invalid"):
        schema_module._load_schema_contract()
