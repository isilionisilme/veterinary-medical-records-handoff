from __future__ import annotations

from backend.app.application.documents._shared import _detect_visit_dates_from_raw_text


def test_detect_visit_dates_from_raw_text_supports_timeline_style_entries() -> None:
    raw_text = "\n".join(
        [
            "HISTORIAL COMPLETO DE MARLEY DESDE LA PRIMERA VISITA A NUESTRO CENTRO",
            "- 08/12/19 - 16:12 -",
            "- 10/12/19 - 10:25 -",
            "- 13/12/19 - 10:20 -",
        ]
    )

    detected = _detect_visit_dates_from_raw_text(raw_text=raw_text)

    assert {"2019-12-08", "2019-12-10", "2019-12-13"}.issubset(set(detected))


def test_detect_visit_dates_from_raw_text_ignores_lab_dates_near_visit_blocks() -> None:
    raw_text = "\n".join(
        [
            "VISITA CONSULTA GENERAL DEL DÍA 17/06/2024 EN EL CENTRO",
            "Analisis de Heces 12/07/2024 0:51:03",
            "Laboratorio externo 19/07/2024 22:45:03",
            "VISITA ADMINISTRATIVA DEL DÍA 11/07/2024 16:30:00 EN EL CENTRO",
        ]
    )

    detected = _detect_visit_dates_from_raw_text(raw_text=raw_text)

    assert "2024-06-17" in detected
    assert "2024-07-11" in detected
    assert "2024-07-12" not in detected
    assert "2024-07-19" not in detected


def test_detect_visit_dates_from_raw_text_supports_visit_header_on_previous_line() -> None:
    raw_text = "\n".join(
        [
            "VISITA VACUNACION/DESPARASITACION DEL",
            "DIA 17/07/2024 19:23:12 EN EL CENTRO",
        ]
    )

    detected = _detect_visit_dates_from_raw_text(raw_text=raw_text)

    assert "2024-07-17" in detected


def test_detect_visit_dates_from_raw_text_supports_timeline_suffix_text() -> None:
    raw_text = "- 03/09/20 - 16:36 - LLAMADA"

    detected = _detect_visit_dates_from_raw_text(raw_text=raw_text)

    assert detected == ["2020-09-03"]


def test_detect_visit_dates_from_raw_text_keeps_repeated_same_day_occurrences() -> None:
    raw_text = "\n".join(
        [
            "- 19/09/20 - 12:10 -",
            "- 19/09/20 - 18:45 -",
        ]
    )

    detected = _detect_visit_dates_from_raw_text(raw_text=raw_text)

    assert detected == ["2020-09-19", "2020-09-19"]
