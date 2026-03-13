import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { type ReviewSelectableField } from "../types/appWorkspace";
import { useFieldEditing } from "./useFieldEditing";

function buildSelectableField(
  overrides: Partial<ReviewSelectableField> = {},
): ReviewSelectableField {
  return {
    id: "field-1",
    key: "pet_name",
    label: "Pet name",
    section: "Paciente",
    order: 0,
    valueType: "string",
    displayValue: "Luna",
    isMissing: false,
    hasMappingConfidence: true,
    confidence: 0.9,
    confidenceBand: "high",
    source: "core",
    repeatable: false,
    ...overrides,
  };
}

describe("useFieldEditing", () => {
  it("exposes initial state defaults", () => {
    const { result } = renderHook(() =>
      useFieldEditing({
        onSubmitInterpretationChanges: vi.fn(),
        onActionFeedback: vi.fn(),
      }),
    );

    expect(result.current.editingField).toBeNull();
    expect(result.current.editingFieldDraftValue).toBe("");
    expect(result.current.isAddFieldDialogOpen).toBe(false);
    expect(result.current.addFieldKeyDraft).toBe("");
    expect(result.current.addFieldValueDraft).toBe("");
  });

  it("opens edit dialog with raw field value as draft", () => {
    const { result } = renderHook(() =>
      useFieldEditing({
        onSubmitInterpretationChanges: vi.fn(),
        onActionFeedback: vi.fn(),
      }),
    );
    const field = buildSelectableField({
      rawField: {
        field_id: "raw-1",
        key: "pet_name",
        value: "Milo",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    });

    act(() => {
      result.current.openFieldEditDialog(field);
    });

    expect(result.current.editingField?.id).toBe("field-1");
    expect(result.current.editingFieldDraftValue).toBe("Milo");
  });

  it("submits UPDATE change and closes dialog on valid edit", () => {
    const onSubmitInterpretationChanges = vi.fn();
    const onActionFeedback = vi.fn();
    const { result } = renderHook(() =>
      useFieldEditing({
        onSubmitInterpretationChanges,
        onActionFeedback,
      }),
    );
    const field = buildSelectableField({
      rawField: {
        field_id: "raw-2",
        key: "pet_name",
        value: "Luna",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    });

    act(() => {
      result.current.openFieldEditDialog(field);
    });
    act(() => {
      result.current.setEditingFieldDraftValue("Nina");
    });
    act(() => {
      result.current.saveFieldEditDialog();
    });

    expect(onSubmitInterpretationChanges).toHaveBeenCalledWith(
      [{ op: "UPDATE", field_id: "raw-2", value: "Nina", value_type: "string" }],
      "Valor actualizado correctamente.",
    );
    expect(onActionFeedback).not.toHaveBeenCalled();
    expect(result.current.editingField).toBeNull();
    expect(result.current.editingFieldDraftValue).toBe("");
  });

  it("reports no changes when edited value is unchanged", () => {
    const onSubmitInterpretationChanges = vi.fn();
    const onActionFeedback = vi.fn();
    const { result } = renderHook(() =>
      useFieldEditing({
        onSubmitInterpretationChanges,
        onActionFeedback,
      }),
    );
    const field = buildSelectableField({
      rawField: {
        field_id: "raw-3",
        key: "pet_name",
        value: "Same value",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    });

    act(() => {
      result.current.openFieldEditDialog(field);
    });
    act(() => {
      result.current.setEditingFieldDraftValue(" Same value ");
    });
    act(() => {
      result.current.saveFieldEditDialog();
    });

    expect(onSubmitInterpretationChanges).not.toHaveBeenCalled();
    expect(onActionFeedback).toHaveBeenCalledWith({
      kind: "info",
      message: "No se han realizado cambios.",
    });
    expect(result.current.editingField).toBeNull();
  });

  it("validates add-field key before submit", () => {
    const onSubmitInterpretationChanges = vi.fn();
    const onActionFeedback = vi.fn();
    const { result } = renderHook(() =>
      useFieldEditing({
        onSubmitInterpretationChanges,
        onActionFeedback,
      }),
    );

    act(() => {
      result.current.setAddFieldKeyDraft("  ");
      result.current.setAddFieldValueDraft("value");
      result.current.saveAddFieldDialog();
    });

    expect(onSubmitInterpretationChanges).not.toHaveBeenCalled();
    expect(onActionFeedback).toHaveBeenCalledWith({
      kind: "error",
      message: "La clave del campo no puede estar vacía.",
    });
  });
});
