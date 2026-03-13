"""Unit tests for owner_address normalization helpers."""

from __future__ import annotations

import pytest

from backend.app.application.field_normalizers import (
    _normalize_owner_address_value,
    normalize_canonical_fields,
)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("Direccion del propietario: C/ Sol 3, 28013 Madrid", "Calle Sol 3, 28013 Madrid"),
        (
            "Domicilio del titular: Avda. Libertad 22, 41001 Sevilla",
            "Avenida Libertad 22, 41001 Sevilla",
        ),
        (
            "Dir. propietario: Pza. Castilla 8, CP 28046 Madrid",
            "Plaza Castilla 8, C.P. 28046 Madrid",
        ),
        ("Direccion del propietario:\nCalle Rio 7\n28020 Madrid", "Calle Rio 7 28020 Madrid"),
        ("  Dir.:   C/  Mayor  12 ,  46001   Valencia  ", "Calle Mayor 12, 46001 Valencia"),
    ],
)
def test_normalize_owner_address_value_positive_cases(raw_value: str, expected: str) -> None:
    assert _normalize_owner_address_value(raw_value) == expected


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        "",
        "   ",
        "Direccion del propietario: S/N",
        "Telefono: 600123123",
        "Propietario: Juan Perez",
        "Calle sin numero",
        "Madrid 28013",
    ],
)
def test_normalize_owner_address_value_rejects_invalid_cases(invalid_value: str | None) -> None:
    assert _normalize_owner_address_value(invalid_value) is None


def test_normalize_canonical_fields_includes_owner_address() -> None:
    normalized = normalize_canonical_fields({"owner_address": "Dir.: C/ Sol 3, 28013 Madrid"})
    assert normalized["owner_address"] == "Calle Sol 3, 28013 Madrid"


def test_normalize_canonical_fields_handles_missing_owner_address() -> None:
    normalized = normalize_canonical_fields({"pet_name": "Luna"})
    assert "owner_address" in normalized
    assert normalized["owner_address"] is None
