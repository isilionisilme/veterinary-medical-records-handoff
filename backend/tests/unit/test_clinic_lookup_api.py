"""Tests for the clinic address lookup API endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.api import routes_clinics
from backend.app.main import app

client = TestClient(app)


def test_lookup_clinic_address_found(monkeypatch) -> None:
    monkeypatch.setattr(
        routes_clinics,
        "lookup_address_by_name",
        lambda _name: {
            "found": True,
            "address": "Avinguda del Mar, 12, 12003 Castelló, España",
            "source": "nominatim",
        },
    )

    response = client.post(
        "/clinics/lookup-address",
        json={"clinic_name": "CENTRO COSTA AZAHAR"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["address"] == "Avinguda del Mar, 12, 12003 Castelló, España"
    assert data["source"] == "nominatim"


def test_lookup_clinic_address_case_insensitive(monkeypatch) -> None:
    monkeypatch.setattr(
        routes_clinics,
        "lookup_address_by_name",
        lambda _name: {
            "found": True,
            "address": "Avinguda del Mar, 12, 12003 Castelló, España",
            "source": "nominatim",
        },
    )

    response = client.post(
        "/clinics/lookup-address",
        json={"clinic_name": "centro costa azahar"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["address"] == "Avinguda del Mar, 12, 12003 Castelló, España"


def test_lookup_clinic_address_alias(monkeypatch) -> None:
    monkeypatch.setattr(
        routes_clinics,
        "lookup_address_by_name",
        lambda _name: {
            "found": True,
            "address": "Avinguda del Mar, 12, 12003 Castelló, España",
            "source": "nominatim",
        },
    )

    response = client.post(
        "/clinics/lookup-address",
        json={"clinic_name": "HV COSTA AZAHAR"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["address"] == "Avinguda del Mar, 12, 12003 Castelló, España"


def test_lookup_clinic_address_not_found(monkeypatch) -> None:
    monkeypatch.setattr(
        routes_clinics,
        "lookup_address_by_name",
        lambda _name: {"found": False, "address": None, "source": "none"},
    )

    response = client.post(
        "/clinics/lookup-address",
        json={"clinic_name": "CLINICA DESCONOCIDA"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
    assert data["address"] is None
    assert data["source"] == "none"


def test_lookup_clinic_address_empty_name() -> None:
    response = client.post(
        "/clinics/lookup-address",
        json={"clinic_name": ""},
    )
    # Pydantic enforces min_length=1
    assert response.status_code == 422
