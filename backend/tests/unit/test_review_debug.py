from __future__ import annotations

from backend.app.api.review_debug import build_visit_debug_sections, build_visit_scoping_metrics


def test_build_visit_debug_sections_trims_each_section_at_next_visit_boundary() -> None:
    visits = [
        {"visit_id": "visit-1", "visit_date": "2024-06-17", "fields": []},
        {"visit_id": "visit-2", "visit_date": "2024-06-18", "fields": []},
    ]
    raw_text = "\n".join(
        [
            "VISITA CONSULTA GENERAL DEL DÍA 17/06/2024 EN EL CENTRO",
            "Observaciones de la primera visita.",
            "VISITA ADMINISTRATIVA DEL DÍA 18/06/2024 EN EL CENTRO",
            "Observaciones de la segunda visita.",
        ]
    )

    sections = build_visit_debug_sections(visits=visits, raw_text=raw_text)

    assert len(sections) == 2
    assert "Observaciones de la primera visita." in sections[0]["raw_context"]
    assert "18/06/2024" not in sections[0]["raw_context"]
    assert "Observaciones de la segunda visita." in sections[1]["raw_context"]


def test_build_visit_debug_sections_reports_missing_offsets_for_all_sections() -> None:
    visits = [
        {"visit_id": "visit-1", "visit_date": "2024-06-17", "fields": []},
        {"visit_id": "visit-2", "visit_date": "2024-06-18", "fields": []},
    ]

    sections = build_visit_debug_sections(
        visits=visits,
        raw_text="Texto sin contexto de visita ni fechas detectables.",
    )

    assert len(sections) == 2
    assert all(
        section["raw_context"] == "No se pudieron inferir offsets de contexto en raw text."
        for section in sections
    )


def test_build_visit_scoping_metrics_marks_unanchored_visits_and_counts_unassigned_fields() -> None:
    visits = [
        {
            "visit_id": "visit-1",
            "visit_date": "2024-06-17",
            "fields": [{"name": "temperature"}],
        },
        {
            "visit_id": "visit-2",
            "visit_date": "2024-06-18",
            "fields": [{"name": "weight"}],
        },
        {
            "visit_id": "unassigned",
            "fields": [{"name": "owner_name"}, {"name": "species"}],
        },
    ]
    raw_text = "\n".join(
        [
            "VISITA CONSULTA GENERAL DEL DÍA 17/06/2024 EN EL CENTRO",
            "Observaciones de la primera visita.",
        ]
    )

    metrics = build_visit_scoping_metrics(visits=visits, raw_text=raw_text)

    assert metrics["summary"] == {
        "total_visits": 3,
        "assigned_visits": 2,
        "anchored_visits": 1,
        "unassigned_field_count": 2,
        "raw_text_available": True,
    }
    assert metrics["visits"][0]["anchored_in_raw_text"] is True
    assert metrics["visits"][0]["raw_context_chars"] > 0
    assert metrics["visits"][1]["anchored_in_raw_text"] is False
    assert metrics["visits"][1]["raw_context_chars"] == 0


def test_build_visit_scoping_metrics_handles_missing_raw_text_without_anchors() -> None:
    visits = [
        {
            "visit_id": "visit-1",
            "visit_date": "2024-06-17",
            "fields": [{"name": "temperature"}, {"name": "weight"}],
        }
    ]

    metrics = build_visit_scoping_metrics(visits=visits, raw_text=None)

    assert metrics["summary"] == {
        "total_visits": 1,
        "assigned_visits": 1,
        "anchored_visits": 0,
        "unassigned_field_count": 0,
        "raw_text_available": False,
    }
    assert metrics["visits"] == [
        {
            "visit_index": 1,
            "visit_id": "visit-1",
            "visit_date": "2024-06-17",
            "field_count": 2,
            "anchored_in_raw_text": False,
            "raw_context_chars": 0,
        }
    ]
