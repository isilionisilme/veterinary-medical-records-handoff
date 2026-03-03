from __future__ import annotations

import json
from pathlib import Path

from backend.app.application.global_schema import (
    GLOBAL_SCHEMA_KEYS,
    REPEATABLE_KEYS,
    VALUE_TYPE_BY_KEY,
)
from backend.app.application.processing_runner import (
    _build_interpretation_artifact,
    _mine_interpretation_candidates,
)

_SHARED_CONTRACT_PATH = (
    Path(__file__).resolve().parents[3] / "shared" / "global_schema_contract.json"
)


def _parse_frontend_global_schema() -> dict[str, str]:
    raw_contract = json.loads(_SHARED_CONTRACT_PATH.read_text(encoding="utf-8"))
    fields = raw_contract.get("fields", []) if isinstance(raw_contract, dict) else []
    return {
        str(field.get("key")): str(field.get("value_type"))
        for field in fields
        if isinstance(field, dict)
    }


def test_interpretation_artifact_contains_full_global_schema_shape() -> None:
    raw_text = """
    Paciente: Luna
    Especie: Canina
    Raza: Mestiza
    Sexo: Hembra
    Edad: 7 años
    Peso: 22 kg
    Fecha de visita: 10/02/2026
    Diagnóstico: Gastroenteritis aguda
    Tratamiento: Omeprazol 10mg cada 24h
    Procedimiento: Ecografía abdominal
    """

    payload = _build_interpretation_artifact(
        document_id="doc-test",
        run_id="run-test",
        raw_text=raw_text,
    )

    data = payload["data"]
    assert isinstance(data, dict)

    global_schema = data.get("global_schema")
    assert isinstance(global_schema, dict)
    assert list(global_schema.keys()) == list(GLOBAL_SCHEMA_KEYS)

    for repeatable_key in REPEATABLE_KEYS:
        assert isinstance(global_schema[repeatable_key], list)

    assert data.get("schema_contract") == "visit-grouped-canonical"
    assert "schema_version" not in data


def test_interpretation_artifact_does_not_use_context_key_fallback_for_calibration() -> None:
    pet_name_lookup_count = 0

    class FakeRepository:
        def get_calibration_counts(
            self,
            *,
            context_key: str,
            field_key: str,
            mapping_id: str | None,
            policy_version: str,
        ) -> tuple[int, int] | None:
            nonlocal pet_name_lookup_count
            if field_key != "pet_name":
                return None
            pet_name_lookup_count += 1
            return None

    payload = _build_interpretation_artifact(
        document_id="doc-fallback-calibration",
        run_id="run-fallback-calibration",
        raw_text="Paciente: Luna",
        repository=FakeRepository(),
    )

    pet_name_field = next(
        field
        for field in payload["data"]["fields"]
        if isinstance(field, dict) and field.get("key") == "pet_name"
    )
    assert pet_name_lookup_count == 1
    assert pet_name_field["field_review_history_adjustment"] == 0


def test_interpretation_artifact_does_not_emit_schema_version_field() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-schema-contract",
        run_id="run-schema-contract",
        raw_text="Paciente: Luna",
    )

    data = payload["data"]
    assert data.get("schema_contract") == "visit-grouped-canonical"
    assert "schema_version" not in data


def test_interpretation_artifact_empty_raw_text_keeps_global_schema_shape() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-empty",
        run_id="run-empty",
        raw_text="   \n\t  ",
    )

    data = payload["data"]
    global_schema = data.get("global_schema")
    assert isinstance(global_schema, dict)
    assert list(global_schema.keys()) == list(GLOBAL_SCHEMA_KEYS)
    assert data["summary"]["warning_codes"] == ["EMPTY_RAW_TEXT"]


def test_candidate_bundle_is_not_persisted_by_default(monkeypatch) -> None:
    monkeypatch.delenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES", raising=False)
    payload = _build_interpretation_artifact(
        document_id="doc-no-candidates",
        run_id="run-no-candidates",
        raw_text="Paciente: Luna\nEspecie: Canina",
    )

    assert "candidate_bundle" not in payload["data"]


def test_candidate_bundle_is_persisted_when_debug_flag_enabled(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES", "true")
    payload = _build_interpretation_artifact(
        document_id="doc-with-candidates",
        run_id="run-with-candidates",
        raw_text="Paciente: Luna\nEspecie: Canina",
    )

    candidate_bundle = payload["data"].get("candidate_bundle")
    assert isinstance(candidate_bundle, dict)


def test_candidate_suggestions_are_ordered_and_capped_to_top_five(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.app.application.processing.interpretation._mine_interpretation_candidates",
        lambda _raw_text: {
            "pet_name": [
                {"value": "Milo", "confidence": 0.72, "evidence": {"page": 1, "snippet": "Milo"}},
                {"value": "Luna", "confidence": 0.91, "evidence": {"page": 1, "snippet": "Luna"}},
                {"value": "Nala", "confidence": 0.84, "evidence": {"page": 2, "snippet": "Nala"}},
                {"value": "Kira", "confidence": 0.84, "evidence": {"page": 2, "snippet": "Kira"}},
                {"value": "Mika", "confidence": 0.63, "evidence": {"page": 3, "snippet": "Mika"}},
                {"value": "Duna", "confidence": 0.51, "evidence": {"page": 3, "snippet": "Duna"}},
            ]
        },
    )

    payload = _build_interpretation_artifact(
        document_id="doc-candidate-suggestions",
        run_id="run-candidate-suggestions",
        raw_text="Paciente: Luna",
    )

    pet_name_field = next(
        field
        for field in payload["data"]["fields"]
        if isinstance(field, dict) and field.get("key") == "pet_name"
    )
    suggestions = pet_name_field.get("candidate_suggestions")
    assert isinstance(suggestions, list)
    assert [item["value"] for item in suggestions] == ["Luna", "Kira", "Nala", "Milo", "Mika"]
    assert len(suggestions) == 5


def test_candidate_suggestions_are_omitted_when_field_has_no_candidates(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.app.application.processing.interpretation._mine_interpretation_candidates",
        lambda _raw_text: {},
    )
    monkeypatch.setattr(
        "backend.app.application.processing.interpretation._map_candidates_to_global_schema",
        lambda _bundle: ({"pet_name": "Luna"}, {"pet_name": []}),
    )

    payload = _build_interpretation_artifact(
        document_id="doc-candidate-suggestions-omitted",
        run_id="run-candidate-suggestions-omitted",
        raw_text="Paciente: Luna",
    )

    pet_name_field = next(
        field
        for field in payload["data"]["fields"]
        if isinstance(field, dict) and field.get("key") == "pet_name"
    )
    assert "candidate_suggestions" not in pet_name_field


def test_microchip_heuristic_extracts_digits_from_keyworded_line() -> None:
    candidates = _mine_interpretation_candidates("Microchip: 00023035139 NHC\nPaciente: Luna")

    microchip_candidates = candidates.get("microchip_id", [])
    assert microchip_candidates
    assert microchip_candidates[0]["value"] == "00023035139"


def test_microchip_heuristic_skips_owner_address_without_chip_digits() -> None:
    candidates = _mine_interpretation_candidates("BEATRIZ ABARCA C/ ORTEGA")

    assert candidates.get("microchip_id", []) == []


def test_microchip_heuristic_extracts_digits_from_ocr_n_prefix_line() -> None:
    candidates = _mine_interpretation_candidates("N�: 941000024967769\nPaciente: Luna")

    microchip_candidates = candidates.get("microchip_id", [])
    assert microchip_candidates
    assert microchip_candidates[0]["value"] == "941000024967769"


def test_microchip_heuristic_rejects_generic_no_reference_without_chip_context() -> None:
    candidates = _mine_interpretation_candidates("No: 941000024967769\nFactura: 2026-02")

    assert candidates.get("microchip_id", []) == []


def test_vet_name_label_heuristic_extracts_name_candidate() -> None:
    candidates = _mine_interpretation_candidates(
        "Centro Veterinario Norte\nVeterinario: Dr. Juan Pérez\nPaciente: Luna"
    )

    vet_candidates = candidates.get("vet_name", [])
    assert vet_candidates
    assert vet_candidates[0]["value"] == "Dr. Juan Pérez"


def test_owner_name_label_heuristic_extracts_owner_candidate() -> None:
    candidates = _mine_interpretation_candidates("Propietario: BEATRIZ ABARCA\nPaciente: Luna")

    owner_candidates = candidates.get("owner_name", [])
    assert owner_candidates
    assert owner_candidates[0]["value"] == "BEATRIZ ABARCA"


def test_owner_name_heuristic_drops_address_suffix_after_split() -> None:
    candidates = _mine_interpretation_candidates(
        "Propietario: BEATRIZ ABARCA C/ ORTEGA 12\nPaciente: Luna"
    )

    owner_candidates = candidates.get("owner_name", [])
    assert owner_candidates
    assert owner_candidates[0]["value"] == "BEATRIZ ABARCA"


def test_owner_name_nombre_line_uses_datos_del_cliente_context() -> None:
    candidates = _mine_interpretation_candidates(
        "Datos del Cliente\nNombre: BEATRIZ ABARCA\nPaciente: Luna"
    )

    owner_candidates = candidates.get("owner_name", [])
    assert owner_candidates
    assert owner_candidates[0]["value"] == "BEATRIZ ABARCA"


def test_owner_name_nombre_line_rejects_patient_labeled_block() -> None:
    candidates = _mine_interpretation_candidates(
        "Datos del Cliente\nPaciente: LUNA BELLA\nNombre: LUNA BELLA"
    )

    assert candidates.get("owner_name", []) == []


def test_owner_name_tabular_nombre_header_extracts_owner_from_following_lines() -> None:
    candidates = _mine_interpretation_candidates(
        "Datos del Cliente\n"
        "MARLEY\n"
        "Canino\n"
        "Labrador Retriever\n"
        "04/10/19\n"
        "941000024967769\n"
        "Nombre\n"
        "Especie\n"
        "Raza\n"
        "F/Nto\n"
        "Capa\n"
        "Nº Chip\n"
        "BEATRIZ ABARCA\n"
        "C/ ORTEGA Y GASSET 1"
    )

    owner_candidates = candidates.get("owner_name", [])
    assert owner_candidates
    assert owner_candidates[0]["value"] == "BEATRIZ ABARCA"


def test_owner_name_tabular_nombre_rejects_when_client_header_is_too_far() -> None:
    candidates = _mine_interpretation_candidates(
        "Datos del Cliente\n"
        "Linea 01\n"
        "Linea 02\n"
        "Linea 03\n"
        "Linea 04\n"
        "Linea 05\n"
        "Linea 06\n"
        "Linea 07\n"
        "Linea 08\n"
        "Linea 09\n"
        "Nombre\n"
        "Especie\n"
        "Raza\n"
        "BEATRIZ ABARCA"
    )

    assert candidates.get("owner_name", []) == []


def test_vet_name_heuristic_rejects_address_like_line() -> None:
    candidates = _mine_interpretation_candidates(
        "Veterinario: Calle Mayor 123\nCentro Veterinario Central"
    )

    assert candidates.get("vet_name", []) == []


def test_clinic_name_heuristic_rejects_direction_labeled_line() -> None:
    candidates = _mine_interpretation_candidates(
        "Direccion de la clinica: Av. Norte 99\nPaciente: Rocky"
    )

    assert candidates.get("clinic_name", []) == []


def test_clinic_name_heuristic_accepts_ocr_zero_label() -> None:
    candidates = _mine_interpretation_candidates(
        "CENTR0 VETERINARI0: Vet Plus Sevilla\nPaciente: Max"
    )

    clinic_candidates = candidates.get("clinic_name", [])
    assert clinic_candidates
    assert clinic_candidates[0]["value"] == "Vet Plus Sevilla"


def test_clinic_name_heuristic_accepts_pipe_separator() -> None:
    candidates = _mine_interpretation_candidates("Clinica | Hospital Vet Costa\nEspecie: Canina")

    clinic_candidates = candidates.get("clinic_name", [])
    assert clinic_candidates
    assert clinic_candidates[0]["value"] == "Hospital Vet Costa"


def test_mvp_coverage_labeled_fields_are_extracted_with_label_confidence() -> None:
    candidates = _mine_interpretation_candidates(
        "NHC: H-7788\n"
        "Direccion del propietario: C/ Mayor 12, Madrid\n"
        "Capa: Tricolor\n"
        "Pelo: Corto\n"
        "Estado reproductivo: Castrado\n"
        "Direccion de la clinica: Av. Norte 99"
    )

    assert candidates["clinical_record_number"][0]["value"] == "H-7788"
    assert candidates["clinical_record_number"][0]["confidence"] == 0.66
    assert candidates["owner_address"][0]["value"] == "C/ Mayor 12, Madrid"
    assert candidates["owner_address"][0]["confidence"] == 0.66
    assert candidates["coat_color"][0]["value"] == "Tricolor"
    assert candidates["coat_color"][0]["confidence"] == 0.66
    assert candidates["hair_length"][0]["value"] == "Corto"
    assert candidates["hair_length"][0]["confidence"] == 0.66
    assert candidates["repro_status"][0]["value"] == "Castrado"
    assert candidates["repro_status"][0]["confidence"] == 0.66
    assert candidates["clinic_address"][0]["value"] == "Av. Norte 99"
    assert candidates["clinic_address"][0]["confidence"] == 0.66


def test_mvp_coverage_fallback_candidate_uses_low_medium_confidence() -> None:
    candidates = _mine_interpretation_candidates("Amoxicilina 250 mg cada 12h durante 7 dias")

    medication_candidates = candidates.get("medication", [])
    assert medication_candidates
    assert medication_candidates[0]["confidence"] == 0.5


def test_repeatable_fields_are_capped_to_three_candidates_in_global_schema() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-repeatable-cap",
        run_id="run-repeatable-cap",
        raw_text=("Diagnostico: uno\nDiagnostico: dos\nDiagnostico: tres\nDiagnostico: cuatro\n"),
    )

    diagnosis = payload["data"]["global_schema"]["diagnosis"]
    assert isinstance(diagnosis, list)
    assert len(diagnosis) == 3


def test_interpretation_artifact_exposes_confidence_policy_cutoffs(monkeypatch, caplog) -> None:
    caplog.set_level("INFO")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", "v1-test")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_LOW_MAX", "0.5")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_MID_MAX", "0.75")

    payload = _build_interpretation_artifact(
        document_id="doc-policy",
        run_id="run-policy",
        raw_text="Paciente: Luna",
    )

    confidence_policy = payload["data"]["confidence_policy"]
    assert confidence_policy["policy_version"] == "v1-test"
    assert confidence_policy["band_cutoffs"] == {"low_max": 0.5, "mid_max": 0.75}
    assert any(
        "confidence_policy included in interpretation payload" in record.message
        for record in caplog.records
    )


def test_interpretation_artifact_omits_confidence_policy_when_config_missing(
    monkeypatch,
    caplog,
) -> None:
    caplog.set_level("WARNING")
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_LOW_MAX", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_MID_MAX", raising=False)

    payload = _build_interpretation_artifact(
        document_id="doc-policy-missing",
        run_id="run-policy-missing",
        raw_text="Paciente: Luna",
    )

    assert "confidence_policy" not in payload["data"]
    assert any(
        "confidence_policy omitted from interpretation payload "
        "reason=policy_not_configured" in record.message
        for record in caplog.records
    )


def test_interpretation_artifact_omits_confidence_policy_when_config_invalid(
    monkeypatch, caplog
) -> None:
    caplog.set_level("WARNING")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", "v1-test")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_LOW_MAX", "0.9")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_MID_MAX", "0.7")

    payload = _build_interpretation_artifact(
        document_id="doc-policy-invalid",
        run_id="run-policy-invalid",
        raw_text="Paciente: Luna",
    )

    assert "confidence_policy" not in payload["data"]
    assert any(
        "confidence_policy omitted from interpretation payload "
        "reason=policy_invalid" in record.message
        for record in caplog.records
    )


def test_structured_fields_include_field_mapping_confidence_signal() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-mapping-confidence",
        run_id="run-mapping-confidence",
        raw_text="Paciente: Luna",
    )

    pet_name_field = next(
        field
        for field in payload["data"]["fields"]
        if isinstance(field, dict) and field.get("key") == "pet_name"
    )
    assert "field_candidate_confidence" in pet_name_field
    assert "field_mapping_confidence" in pet_name_field
    assert "text_extraction_reliability" in pet_name_field
    assert "field_review_history_adjustment" in pet_name_field
    assert "confidence" not in pet_name_field
    assert isinstance(pet_name_field["field_candidate_confidence"], float)
    assert 0.0 <= pet_name_field["field_candidate_confidence"] <= 1.0
    expected_mapping = pet_name_field["field_candidate_confidence"] + (
        pet_name_field["field_review_history_adjustment"] / 100.0
    )
    expected_mapping = min(max(expected_mapping, 0.0), 1.0)
    assert pet_name_field["field_mapping_confidence"] == expected_mapping
    assert pet_name_field["text_extraction_reliability"] is None
    assert pet_name_field["field_review_history_adjustment"] == 0


def test_mvp_coverage_debug_includes_line_number_for_accepted_value() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-line-debug",
        run_id="run-line-debug",
        raw_text="Microchip: 941000024967769\nPaciente: Luna",
    )

    summary = payload["data"]["summary"]
    mvp_debug = summary["mvp_coverage_debug"]
    microchip_debug = mvp_debug["microchip_id"]
    assert microchip_debug["status"] == "accepted"
    assert microchip_debug["top1"] == "941000024967769"
    assert microchip_debug["confidence"] == 0.66
    assert microchip_debug["line_number"] == 1


def test_visit_date_is_populated_from_labeled_input() -> None:
    payload = _build_interpretation_artifact(
        document_id="doc-no-overwrite",
        run_id="run-no-overwrite",
        raw_text="Fecha de visita: 03/01/2026",
    )

    schema = payload["data"]["global_schema"]
    assert schema["visit_date"] == "03/01/2026"


def test_frontend_and_backend_global_schema_keys_and_types_are_in_sync() -> None:
    frontend_schema = _parse_frontend_global_schema()

    assert set(frontend_schema.keys()) == set(GLOBAL_SCHEMA_KEYS)

    for key in GLOBAL_SCHEMA_KEYS:
        assert frontend_schema[key] == VALUE_TYPE_BY_KEY[key]
