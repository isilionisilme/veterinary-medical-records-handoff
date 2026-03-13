from __future__ import annotations

from backend.app.application.processing.extractors.common import CandidateCollector, MiningContext


def _collector(raw_text: str) -> CandidateCollector:
    return CandidateCollector(MiningContext.from_raw_text(raw_text))


def test_add_candidate_deduplicates_values_case_insensitively() -> None:
    collector = _collector("Mascota: Luna")

    collector.add_candidate(key="pet_name", value="Luna", confidence=0.7, snippet="Mascota: Luna")
    collector.add_candidate(key="pet_name", value="luna", confidence=0.9, snippet="Mascota: luna")

    built = collector.build()
    assert len(built["pet_name"]) == 1
    assert built["pet_name"][0]["value"] == "Luna"


def test_add_candidate_rejects_microchip_when_snippet_does_not_contain_digits() -> None:
    collector = _collector("Sin identificacion electronica")

    collector.add_candidate(
        key="microchip_id",
        value="941000024967769",
        confidence=0.7,
        snippet="Sin identificacion electronica",
    )

    assert collector.build().get("microchip_id") is None


def test_add_candidate_accepts_microchip_with_spaced_or_dashed_snippet() -> None:
    collector = _collector("Microchip: 941 0000-2496 7769")

    collector.add_candidate(
        key="microchip_id",
        value="941000024967769",
        confidence=0.7,
        snippet="Microchip: 941 0000-2496 7769",
    )

    built = collector.build()
    assert built["microchip_id"][0]["value"] == "941000024967769"


def test_add_candidate_rejects_weight_in_medication_context_without_explicit_weight_label() -> None:
    collector = _collector("Tratamiento: amoxicilina 2 mg/kg")

    collector.add_candidate(
        key="weight",
        value="2",
        confidence=0.7,
        snippet="Tratamiento: amoxicilina 2 mg/kg",
    )

    assert collector.build().get("weight") is None


def test_add_candidate_accepts_weight_with_explicit_context_and_dosage() -> None:
    collector = _collector("Peso: 2 kg. Dosis de mantenimiento 2 mg/kg")

    collector.add_candidate(
        key="weight",
        value="2 kg",
        confidence=0.7,
        snippet="Peso: 2 kg. Dosis de mantenimiento 2 mg/kg",
    )

    built = collector.build()
    assert built["weight"][0]["value"] == "2 kg"


def test_classify_address_context_owner_and_clinic() -> None:
    owner_collector = _collector(
        "\n".join(
            [
                "Datos del cliente",
                "Propietario: Ana Perez",
                "Direccion: Calle Sol 9",
            ]
        )
    )
    clinic_collector = _collector(
        "\n".join(
            [
                "Clinica Veterinaria Centro",
                "Direccion: Avenida Norte 15",
            ]
        )
    )

    owner_line = owner_collector.line_index_for_snippet("Direccion: Calle Sol 9")
    clinic_line = clinic_collector.line_index_for_snippet("Direccion: Avenida Norte 15")

    assert owner_line is not None
    assert clinic_line is not None
    assert owner_collector.classify_address_context(owner_line) == "owner"
    assert clinic_collector.classify_address_context(clinic_line) == "clinic"
