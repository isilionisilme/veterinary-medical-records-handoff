"""Age normalization and display formatting."""

from __future__ import annotations

from backend.app.application.field_normalizers import (
    derive_age_from_dob,
    normalize_canonical_fields,
)


def _normalize_age_from_review_projection(data: dict[str, object]) -> dict[str, object]:
    global_schema = data.get("global_schema")
    if not isinstance(global_schema, dict):
        return data

    projected = dict(data)
    existing_age_value, age_origin_hint = _resolve_existing_age_field_state(projected.get("fields"))
    global_schema_for_normalization = dict(global_schema)
    if existing_age_value is not None and not _has_non_empty_string(
        global_schema_for_normalization.get("age")
    ):
        global_schema_for_normalization["age"] = existing_age_value

    normalized_global_schema = normalize_canonical_fields(
        global_schema_for_normalization,
    )
    visits = projected.get("visits") if isinstance(projected.get("visits"), list) else None
    normalized_global_schema = derive_age_from_dob(normalized_global_schema, visits=visits)

    if normalized_global_schema.get("age_origin") is None and age_origin_hint == "human":
        age_value = normalized_global_schema.get("age")
        if isinstance(age_value, str) and age_value.strip():
            normalized_global_schema["age_origin"] = "human"

    age_display = _resolve_age_display_from_global_schema(
        global_schema=normalized_global_schema,
        visits=projected.get("visits") if isinstance(projected.get("visits"), list) else None,
        age_origin=(
            normalized_global_schema.get("age_origin")
            if isinstance(normalized_global_schema.get("age_origin"), str)
            else age_origin_hint
        ),
    )
    if age_display is not None:
        normalized_global_schema["age_display"] = age_display
    else:
        normalized_global_schema.pop("age_display", None)

    if normalized_global_schema != global_schema:
        projected["global_schema"] = normalized_global_schema

    age_changed = _upsert_age_field_from_global_schema(
        normalized_data=projected,
        normalized_age=(
            normalized_global_schema.get("age")
            if isinstance(normalized_global_schema.get("age"), str)
            else None
        ),
        age_display=age_display,
        age_origin=(
            normalized_global_schema.get("age_origin")
            if isinstance(normalized_global_schema.get("age_origin"), str)
            else age_origin_hint
        ),
    )
    if age_changed and "global_schema" not in projected:
        projected["global_schema"] = normalized_global_schema

    return projected


def _resolve_existing_age_field_state(fields: object) -> tuple[str | None, str | None]:
    if not isinstance(fields, list):
        return None, None

    for field in fields:
        if not isinstance(field, dict) or field.get("key") != "age":
            continue
        value = field.get("value")
        origin = field.get("origin")
        resolved_value = value.strip() if isinstance(value, str) and value.strip() else None
        resolved_origin = str(origin) if origin in {"human", "machine", "derived"} else None
        return resolved_value, resolved_origin
    return None, None


def _upsert_age_field_from_global_schema(
    *,
    normalized_data: dict[str, object],
    normalized_age: str | None,
    age_display: str | None,
    age_origin: str | None,
) -> bool:
    if not isinstance(normalized_age, str) or not normalized_age.strip():
        return False

    raw_fields = normalized_data.get("fields")
    fields: list[object]
    if isinstance(raw_fields, list):
        fields = list(raw_fields)
    else:
        fields = []

    age_field_index: int | None = None
    for index, item in enumerate(fields):
        if isinstance(item, dict) and item.get("key") == "age":
            age_field_index = index
            break

    target_origin = age_origin if age_origin in {"human", "derived"} else "machine"

    if age_field_index is None:
        fields.append(
            {
                "field_id": "backfill-age",
                "key": "age",
                "value": normalized_age,
                "value_type": "string",
                "scope": "document",
                "section": "patient",
                "classification": "medical_record",
                "domain": "clinical",
                "is_critical": True,
                "origin": target_origin,
                "display_value": age_display,
                "evidence": {"page": 1, "snippet": normalized_age},
            }
        )
        normalized_data["fields"] = fields
        return True

    existing_field = fields[age_field_index]
    if not isinstance(existing_field, dict):
        return False

    existing_value = existing_field.get("value")
    existing_compact = str(existing_value).strip() if isinstance(existing_value, str) else ""
    existing_origin = (
        existing_field.get("origin") if isinstance(existing_field.get("origin"), str) else None
    )
    existing_display = (
        existing_field.get("display_value")
        if isinstance(existing_field.get("display_value"), str)
        else None
    )
    if (
        existing_compact == normalized_age
        and existing_origin == target_origin
        and existing_display == age_display
    ):
        return False

    patched_field = dict(existing_field)
    patched_field["value"] = normalized_age
    patched_field["value_type"] = "string"
    patched_field.setdefault("scope", "document")
    patched_field.setdefault("section", "patient")
    patched_field.setdefault("classification", "medical_record")
    patched_field.setdefault("domain", "clinical")
    patched_field.setdefault("is_critical", True)
    patched_field["origin"] = target_origin
    if age_display is not None:
        patched_field["display_value"] = age_display
    else:
        patched_field.pop("display_value", None)
    patched_field.setdefault("evidence", {"page": 1, "snippet": normalized_age})
    fields[age_field_index] = patched_field
    normalized_data["fields"] = fields
    return True


def _resolve_age_display_from_global_schema(
    *,
    global_schema: dict[str, object],
    visits: list[object] | None,
    age_origin: str | None,
) -> str | None:
    raw_age = global_schema.get("age")
    if not isinstance(raw_age, str) or not raw_age.strip():
        return None

    if age_origin == "derived":
        dob_value = global_schema.get("dob")
        if isinstance(dob_value, str) and dob_value.strip():
            from backend.app.application.age_derivation import (
                calculate_age_presentation,
                resolve_reference_date,
            )

            reference_date = resolve_reference_date(
                [visit for visit in visits or () if isinstance(visit, dict)],
                global_schema.get("document_date")
                if isinstance(global_schema.get("document_date"), str)
                else None,
            )
            if isinstance(reference_date, str):
                presentation = calculate_age_presentation(dob_value, reference_date)
                if presentation is not None and str(presentation.years) == raw_age.strip():
                    return presentation.display_value

    return _format_age_display_from_years(raw_age)


def _format_age_display_from_years(raw_age: str) -> str | None:
    compact = raw_age.strip()
    if not compact.isdigit():
        return None
    years = int(compact)
    unit = "año" if years == 1 else "años"
    return f"{years} {unit}"


def _has_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
