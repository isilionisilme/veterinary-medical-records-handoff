from __future__ import annotations

from backend.app.application.documents.review_service import (
    _split_segment_into_observations_actions,
)


def test_split_segment_into_observations_actions_mixed_text() -> None:
    segment_text = "\n".join(
        [
            "Consulta 11/02/2026: dolor de oido y prurito auricular.",
            "Se diagnostica otitis externa y se realiza limpieza de oido.",
            "Se indica medicacion: gotas oticas 4 gotas cada 12 horas por 7 dias.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations == "dolor de oido y prurito auricular"
    assert actions is not None
    assert "Se diagnostica otitis externa y se realiza limpieza de oido" in actions
    assert "Se indica medicacion: gotas oticas 4 gotas cada 12 horas por 7 dias" in actions


def test_split_segment_into_observations_actions_observations_only() -> None:
    segment_text = "\n".join(
        [
            "Consulta 11/02/2026: apetito conservado y buen estado general.",
            "Temperatura normal y sin dolor a la palpacion.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "apetito conservado y buen estado general" in observations
    assert "Temperatura normal y sin dolor a la palpacion" in observations
    assert actions is None


def test_split_segment_into_observations_actions_actions_only() -> None:
    segment_text = "\n".join(
        [
            "Se administra antiinflamatorio intramuscular.",
            "Tratamiento: continuar medicacion oral por 5 dias.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is None
    assert actions is not None
    assert "Se administra antiinflamatorio intramuscular" in actions
    assert "Tratamiento: continuar medicacion oral por 5 dias" in actions


def test_split_segment_into_observations_actions_empty_text() -> None:
    observations, actions = _split_segment_into_observations_actions(segment_text=" \n \n")

    assert observations is None
    assert actions is None
