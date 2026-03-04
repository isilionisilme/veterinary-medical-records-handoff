from __future__ import annotations

import re
from pathlib import Path

from backend.app.application.processing_runner import (
    _build_interpretation_artifact,
    _mine_interpretation_candidates,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "raw_text"

_DATE_LIKE_PATTERN = re.compile(r"^\d{1,4}[\/\-.]\d{1,2}[\/\-.]\d{1,4}$")
_DIGIT_LIKE_PATTERN = re.compile(r"\d{9,15}")
_PERSON_LIKE_PATTERN = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.-]*(?:\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.-]*){1,4}$"
)
_ADDRESS_TOKEN_PATTERN = re.compile(
    r"(?i)\b(?:c/|calle|av\.?|avenida|cp\b|codigo\s+postal|portal|piso|puerta|n[º°o]|no\.)\b"
)


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _build_with_candidates(monkeypatch, *, doc_id: str, raw_text: str) -> dict[str, object]:
    monkeypatch.setenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES", "true")
    payload = _build_interpretation_artifact(
        document_id=doc_id,
        run_id="golden-run",
        raw_text=raw_text,
    )
    data = payload["data"]
    assert isinstance(data, dict)
    return data


def _assert_owner_or_vet_invariant(
    *,
    schema: dict[str, object],
    candidates: dict[str, object],
    field_key: str,
) -> None:
    value = schema.get(field_key)
    if isinstance(value, str) and value.strip():
        compact = value.strip()
        assert _PERSON_LIKE_PATTERN.search(compact)
        assert _ADDRESS_TOKEN_PATTERN.search(compact) is None
        return

    assert value in ("", None)
    raw_candidates = candidates.get(field_key, [])
    assert isinstance(raw_candidates, list)
    if not raw_candidates:
        return

    top1 = raw_candidates[0]
    assert isinstance(top1, dict)
    top1_value = top1.get("value")
    assert isinstance(top1_value, str) and top1_value.strip()


def test_doc_a_golden_goal_fields_regression(monkeypatch) -> None:
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-a",
        raw_text=_load_fixture("docA.txt"),
    )

    schema = data["global_schema"]
    candidates = data.get("candidate_bundle", {})
    assert isinstance(schema, dict)
    assert isinstance(candidates, dict)

    microchip = schema.get("microchip_id")
    assert isinstance(microchip, str) and _DIGIT_LIKE_PATTERN.search(microchip)

    # pet_name — docA first line follows "<NAME> - Nacimiento" pattern.
    pet_name = schema.get("pet_name")
    assert pet_name == "Alya", f"pet_name regression: expected 'Alya', got {pet_name!r}"

    _assert_owner_or_vet_invariant(
        schema=schema,
        candidates=candidates,
        field_key="owner_name",
    )

    weight = schema.get("weight")
    assert weight in ("", None)

    visit_date = schema.get("visit_date")
    assert visit_date is None or (
        isinstance(visit_date, str) and _DATE_LIKE_PATTERN.search(visit_date)
    )

    discharge_date = schema.get("discharge_date")
    assert discharge_date in ("", None)

    clinic_name = schema.get("clinic_name")
    assert clinic_name == "CENTRO COSTA AZAHAR", (
        f"clinic_name regression: expected 'CENTRO COSTA AZAHAR', got {clinic_name!r}"
    )

    # clinic_address is NOT auto-enriched — user must trigger lookup explicitly
    clinic_address = schema.get("clinic_address")
    assert clinic_address in ("", None), (
        "clinic_address should be empty for docA (enrichment is now user-initiated), "
        f"got {clinic_address!r}"
    )

    _assert_owner_or_vet_invariant(
        schema=schema,
        candidates=candidates,
        field_key="vet_name",
    )


def test_doc_b_golden_goal_fields_regression(monkeypatch) -> None:
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-b",
        raw_text=_load_fixture("docB.txt"),
    )

    schema = data["global_schema"]
    candidates = data.get("candidate_bundle", {})
    assert isinstance(schema, dict)
    assert isinstance(candidates, dict)

    microchip = schema.get("microchip_id")
    assert microchip == "941000024967769"
    microchip_candidates = candidates.get("microchip_id", [])
    assert microchip_candidates

    # pet_name — docB has "NOMBRE DEMO" (actually owner name) picked up by
    # unlabeled heuristic near "chip" context. Known false positive.
    pet_name = schema.get("pet_name")
    assert pet_name == "Nombre Demo", (
        f"pet_name regression: expected 'Nombre Demo', got {pet_name!r}"
    )

    _assert_owner_or_vet_invariant(
        schema=schema,
        candidates=candidates,
        field_key="owner_name",
    )

    weight = schema.get("weight")
    assert weight in ("", None)

    visit_date = schema.get("visit_date")
    assert visit_date is None or (
        isinstance(visit_date, str) and _DATE_LIKE_PATTERN.search(visit_date)
    )

    discharge_date = schema.get("discharge_date")
    assert discharge_date in ("", None)

    clinic_name = schema.get("clinic_name")
    assert clinic_name in ("", None)

    clinic_address = schema.get("clinic_address")
    assert clinic_address in ("", None)

    _assert_owner_or_vet_invariant(
        schema=schema,
        candidates=candidates,
        field_key="vet_name",
    )


def test_owner_name_trim_uses_fixture_owner_and_address_lines() -> None:
    raw_text = _load_fixture("docB.txt")
    owner_line = next(line for line in raw_text.splitlines() if "NOMBRE DEMO" in line)
    address_line = next(line for line in raw_text.splitlines() if "C/ CALLE DEMO" in line)

    synthetic = f"Propietario: {owner_line} {address_line}\nPaciente: Luna"
    candidates = _mine_interpretation_candidates(synthetic)

    owner_candidates = candidates.get("owner_name", [])
    assert owner_candidates
    assert owner_candidates[0]["value"] == "NOMBRE DEMO"


def test_doc_b_hidden_header_clinic_name_is_detected(monkeypatch) -> None:
    raw_text = "HV COSTA AZAHAR\n" + _load_fixture("docB.txt")
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-b-hidden-clinic",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("clinic_name") == "HV COSTA AZAHAR"


def test_doc_b_header_context_clinic_name_is_detected(monkeypatch) -> None:
    raw_text = "\n".join(
        [
            "PARQUE OESTE",
            "AVDA EUROPA",
            "28922 ALCORCÓN",
            "Datos de la Mascota",
            "Datos del Cliente",
            "Nº Chip",
            "941000024967769",
        ]
    )
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-b-header-context-clinic",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("clinic_name") == "PARQUE OESTE"


def test_generic_uppercase_header_is_not_detected_as_clinic_name(monkeypatch) -> None:
    raw_text = "\n".join(
        [
            "INFORME",
            "AVDA EUROPA",
            "28922 ALCORCÓN",
            "Datos de la Mascota",
            "Datos del Cliente",
            "Nº Chip",
            "941000024967769",
        ]
    )
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-generic-header-not-clinic",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("clinic_name") in ("", None)


def test_owner_name_trim_does_not_convert_pure_address_into_owner() -> None:
    raw_text = _load_fixture("docB.txt")
    address_line = next(line for line in raw_text.splitlines() if "C/ CALLE DEMO" in line)

    synthetic = f"Propietario: {address_line}\nPaciente: Luna"
    candidates = _mine_interpretation_candidates(synthetic)

    assert candidates.get("owner_name", []) == []


def test_clinic_address_labeled_disambiguates_owner_address(monkeypatch) -> None:
    raw_text = "\n".join(
        [
            "Propietario: Ana Pérez",
            "Dirección del propietario: C/ Luna 5, 28080 Madrid",
            "Clínica: Centro Vet Norte",
            "Dirección de la clínica: Av. Moratalaz 10, 28030 Madrid",
            "Paciente: Rocky",
        ]
    )
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-clinic-address-disambiguation",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("clinic_address") == "Av. Moratalaz 10, 28030 Madrid"


def test_microchip_transponder_label_regression(monkeypatch) -> None:
    raw_text = "\n".join(
        [
            "Paciente: Kira",
            "Transponder 100000123456789",
            "Especie: Felina",
        ]
    )
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-microchip-transponder",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("microchip_id") == "100000123456789"


def test_microchip_separated_digits_regression(monkeypatch) -> None:
    raw_text = "\n".join(
        [
            "Paciente: Max",
            "Chip: 941 0000-2496 7769",
            "Especie: Canina",
        ]
    )
    data = _build_with_candidates(
        monkeypatch,
        doc_id="golden-doc-microchip-separated-digits",
        raw_text=raw_text,
    )

    schema = data["global_schema"]
    assert isinstance(schema, dict)
    assert schema.get("microchip_id") == "941000024967769"
