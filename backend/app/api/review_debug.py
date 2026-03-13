from __future__ import annotations

import html
import re

from backend.app.application.documents import _locate_visit_date_occurrences_from_raw_text

VisitSection = dict[str, str]
VisitWindow = tuple[int, int]
VisitWithOffset = tuple[VisitSection, int | None]

_NEXT_VISIT_BOUNDARY_PATTERN = re.compile(
    r"(?:\s*)?visita\s+(?:consulta\s+general|administrativa)\s+del\s+d[ií]a",
    re.IGNORECASE,
)
_NON_ANCHORED_RAW_CONTEXT_SENTINELS = {
    "Raw text no disponible para este run.",
    "No se pudieron inferir offsets de contexto en raw text.",
    "Sin ancla de fecha para recortar contexto.",
    "Sin ventana de contexto disponible.",
}


def render_visit_debug_html(*, document_id: str, visit_sections: list[VisitSection]) -> str:
    cards_html = "".join(_render_visit_card(section) for section in visit_sections)
    if not cards_html:
        cards_html = "<p>No hay visitas disponibles.</p>"

    escaped_document_id = html.escape(document_id)
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8' />"
        f"<title>Visit Debug - {escaped_document_id}</title>"
        "</head><body style='font-family:Segoe UI,Arial,sans-serif;background:#f3f4f6;"
        "margin:0;padding:20px;color:#111827;'>"
        f"<h1 style='margin:0 0 12px 0;'>Debug de visitas - {escaped_document_id}</h1>"
        "<p style='margin:0 0 18px 0;color:#374151;'>"
        "Vista temporal de diagnóstico. Muestra el texto crudo asociado a cada visita."
        "</p>"
        f"{cards_html}"
        "</body></html>"
    )


def build_visit_debug_sections(*, visits: object, raw_text: str | None) -> list[VisitSection]:
    assigned_visits = _get_assigned_visits(visits)
    if not assigned_visits:
        return []

    if not isinstance(raw_text, str) or not raw_text.strip():
        return [
            _build_unanchored_section(index, visit) for index, visit in enumerate(assigned_visits)
        ]

    sections_with_offsets = _build_sections_with_offsets(assigned_visits, raw_text)
    offset_windows = _build_offset_windows(sections_with_offsets, len(raw_text))
    return _hydrate_sections_with_raw_context(sections_with_offsets, offset_windows, raw_text)


def build_visit_scoping_metrics(*, visits: object, raw_text: str | None) -> dict[str, object]:
    if not isinstance(visits, list):
        return _empty_visit_scoping_metrics(raw_text=raw_text)

    assigned_visits = _get_assigned_visits(visits)
    raw_text_available = bool(isinstance(raw_text, str) and raw_text.strip())
    debug_sections = build_visit_debug_sections(visits=visits, raw_text=raw_text)
    metrics_rows = [
        _build_visit_metrics_row(
            index=index,
            visit=visit,
            debug_section=debug_sections[index] if index < len(debug_sections) else None,
            raw_text_available=raw_text_available,
        )
        for index, visit in enumerate(assigned_visits)
    ]
    anchored_visits = sum(
        1 for visit_metrics in metrics_rows if visit_metrics["anchored_in_raw_text"] is True
    )

    return {
        "summary": {
            "total_visits": len(visits),
            "assigned_visits": len(assigned_visits),
            "anchored_visits": anchored_visits,
            "unassigned_field_count": _count_unassigned_fields(visits),
            "raw_text_available": raw_text_available,
        },
        "visits": metrics_rows,
    }


def _render_visit_card(section: VisitSection) -> str:
    title = html.escape(section["title"])
    subtitle = html.escape(section["subtitle"])
    raw_context = html.escape(section["raw_context"])
    return (
        "<section style='border:1px solid #d8dee6;border-radius:10px;padding:12px;"
        "margin:12px 0;background:#fff;'>"
        f"<h3 style='margin:0 0 6px 0;font-size:16px;color:#1f2937;'>{title}</h3>"
        f"<p style='margin:0 0 10px 0;color:#4b5563;font-size:13px;'>{subtitle}</p>"
        "<pre style='white-space:pre-wrap;word-break:break-word;background:#f8fafc;"
        "border:1px solid #e5e7eb;border-radius:8px;padding:10px;font-size:13px;"
        "line-height:1.45;max-height:360px;overflow:auto;'>"
        f"{raw_context}"
        "</pre>"
        "</section>"
    )


def _get_assigned_visits(visits: object) -> list[dict[str, object]]:
    if not isinstance(visits, list):
        return []
    return [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]


def _build_unanchored_section(index: int, visit: dict[str, object]) -> VisitSection:
    return {
        "title": f"Visita {index + 1} ({visit.get('visit_date') or 'sin fecha'})",
        "subtitle": f"visit_id={visit.get('visit_id') or 'n/a'}",
        "raw_context": "Raw text no disponible para este run.",
    }


def _build_sections_with_offsets(
    assigned_visits: list[dict[str, object]], raw_text: str
) -> list[VisitWithOffset]:
    offsets_by_date = _group_offsets_by_date(raw_text)
    consumed_by_date: dict[str, int] = {}
    return [
        _build_section_with_offset(
            index=index,
            visit=visit,
            offsets_by_date=offsets_by_date,
            consumed_by_date=consumed_by_date,
        )
        for index, visit in enumerate(assigned_visits)
    ]


def _group_offsets_by_date(raw_text: str) -> dict[str, list[int]]:
    offsets_by_date: dict[str, list[int]] = {}
    for normalized_date, offset in _locate_visit_date_occurrences_from_raw_text(raw_text=raw_text):
        offsets_by_date.setdefault(normalized_date, []).append(offset)
    return offsets_by_date


def _build_section_with_offset(
    *,
    index: int,
    visit: dict[str, object],
    offsets_by_date: dict[str, list[int]],
    consumed_by_date: dict[str, int],
) -> VisitWithOffset:
    normalized_date = visit.get("visit_date") if isinstance(visit.get("visit_date"), str) else None
    anchor_offset = _consume_anchor_offset(
        normalized_date=normalized_date,
        offsets_by_date=offsets_by_date,
        consumed_by_date=consumed_by_date,
    )
    section = {
        "title": f"Visita {index + 1} ({normalized_date or 'sin fecha'})",
        "subtitle": f"visit_id={visit.get('visit_id') or 'n/a'}",
        "raw_context": "",
    }
    return section, anchor_offset


def _consume_anchor_offset(
    *,
    normalized_date: str | None,
    offsets_by_date: dict[str, list[int]],
    consumed_by_date: dict[str, int],
) -> int | None:
    if normalized_date is None:
        return None

    offsets = offsets_by_date.get(normalized_date, [])
    consumed = consumed_by_date.get(normalized_date, 0)
    if consumed >= len(offsets):
        return None

    consumed_by_date[normalized_date] = consumed + 1
    return offsets[consumed]


def _build_offset_windows(
    sections_with_offsets: list[VisitWithOffset], raw_text_length: int
) -> dict[int, VisitWindow]:
    sorted_anchors = sorted(
        [
            (idx, offset)
            for idx, (_, offset) in enumerate(sections_with_offsets)
            if offset is not None
        ],
        key=lambda item: item[1],
    )
    return {
        section_index: (
            start_offset,
            sorted_anchors[anchor_index + 1][1]
            if anchor_index + 1 < len(sorted_anchors)
            else raw_text_length,
        )
        for anchor_index, (section_index, start_offset) in enumerate(sorted_anchors)
    }


def _hydrate_sections_with_raw_context(
    sections_with_offsets: list[VisitWithOffset],
    offset_windows: dict[int, VisitWindow],
    raw_text: str,
) -> list[VisitSection]:
    if not offset_windows:
        return [
            _with_raw_context(
                section,
                "No se pudieron inferir offsets de contexto en raw text.",
            )
            for section, _ in sections_with_offsets
        ]

    return [
        _with_raw_context(
            section,
            _resolve_section_raw_context(index, offset, offset_windows, raw_text),
        )
        for index, (section, offset) in enumerate(sections_with_offsets)
    ]


def _resolve_section_raw_context(
    section_index: int,
    offset: int | None,
    offset_windows: dict[int, VisitWindow],
    raw_text: str,
) -> str:
    if offset is None:
        return "Sin ancla de fecha para recortar contexto."

    window = offset_windows.get(section_index)
    if window is None:
        return "Sin ventana de contexto disponible."

    start_offset, end_offset = _trim_window_to_boundary(offset_windows[section_index], raw_text)
    return raw_text[start_offset:end_offset].strip() or "(vacío)"


def _trim_window_to_boundary(window: VisitWindow, raw_text: str) -> VisitWindow:
    start_offset, end_offset = window
    window_text = raw_text[start_offset:end_offset]
    boundary_match = _NEXT_VISIT_BOUNDARY_PATTERN.search(window_text)
    if boundary_match is not None and boundary_match.start() > 0:
        return start_offset, start_offset + boundary_match.start()
    return window


def _with_raw_context(section: VisitSection, raw_context: str) -> VisitSection:
    hydrated_section = dict(section)
    hydrated_section["raw_context"] = raw_context
    return hydrated_section


def _empty_visit_scoping_metrics(*, raw_text: str | None) -> dict[str, object]:
    return {
        "summary": {
            "total_visits": 0,
            "assigned_visits": 0,
            "anchored_visits": 0,
            "unassigned_field_count": 0,
            "raw_text_available": bool(raw_text and raw_text.strip()),
        },
        "visits": [],
    }


def _build_visit_metrics_row(
    *,
    index: int,
    visit: dict[str, object],
    debug_section: VisitSection | None,
    raw_text_available: bool,
) -> dict[str, object]:
    raw_context = debug_section["raw_context"] if debug_section is not None else ""
    anchored = _is_anchored_raw_context(
        raw_context=raw_context,
        raw_text_available=raw_text_available,
    )
    return {
        "visit_index": index + 1,
        "visit_id": visit.get("visit_id"),
        "visit_date": visit.get("visit_date"),
        "field_count": _count_fields(visit.get("fields")),
        "anchored_in_raw_text": anchored,
        "raw_context_chars": len(raw_context) if anchored else 0,
    }


def _is_anchored_raw_context(*, raw_context: str, raw_text_available: bool) -> bool:
    return bool(
        raw_text_available
        and raw_context
        and raw_context not in _NON_ANCHORED_RAW_CONTEXT_SENTINELS
    )


def _count_fields(fields: object) -> int:
    if not isinstance(fields, list):
        return 0
    return len([field for field in fields if isinstance(field, dict)])


def _count_unassigned_fields(visits: list[object]) -> int:
    unassigned_field_count = 0
    for visit in visits:
        if not isinstance(visit, dict) or visit.get("visit_id") != "unassigned":
            continue
        unassigned_field_count += _count_fields(visit.get("fields"))
    return unassigned_field_count
