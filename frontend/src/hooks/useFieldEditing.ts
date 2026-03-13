import { useCallback, useMemo, useState } from "react";
import { type ActionFeedback } from "../components/toast/toast-types";
import { resolveCandidateSuggestionSections } from "../extraction/candidateSuggestions";
import { getControlledVocabOptionValues, validateFieldValue } from "../extraction/fieldValidators";
import {
  type InterpretationChangePayload,
  type ReviewSelectableField,
} from "../types/appWorkspace";
type UseFieldEditingParams = {
  onSubmitInterpretationChanges: (
    changes: InterpretationChangePayload[],
    successMessage: string,
  ) => void;
  onActionFeedback: (feedback: ActionFeedback) => void;
};
const isDateFieldKey = (fieldKey: string) =>
  fieldKey === "document_date" ||
  fieldKey === "visit_date" ||
  fieldKey === "admission_date" ||
  fieldKey === "discharge_date" ||
  fieldKey === "dob" ||
  fieldKey.startsWith("fecha_");
export function useFieldEditing({
  onSubmitInterpretationChanges,
  onActionFeedback,
}: UseFieldEditingParams) {
  const [editingField, setEditingField] = useState<ReviewSelectableField | null>(null);
  const [editingFieldDraftValue, setEditingFieldDraftValue] = useState("");
  const [isAddFieldDialogOpen, setIsAddFieldDialogOpen] = useState(false);
  const [addFieldKeyDraft, setAddFieldKeyDraft] = useState("");
  const [addFieldValueDraft, setAddFieldValueDraft] = useState("");
  const closeAddFieldDialog = useCallback(() => {
    setIsAddFieldDialogOpen(false);
    setAddFieldKeyDraft("");
    setAddFieldValueDraft("");
  }, []);
  const saveAddFieldDialog = useCallback(() => {
    const key = addFieldKeyDraft.trim();
    if (!key) {
      onActionFeedback({ kind: "error", message: "La clave del campo no puede estar vacía." });
      return;
    }
    const value = addFieldValueDraft.trim();
    onSubmitInterpretationChanges(
      [{ op: "ADD", key, value: value.length > 0 ? value : null, value_type: "string" }],
      "Campo añadido.",
    );
    closeAddFieldDialog();
  }, [
    addFieldKeyDraft,
    addFieldValueDraft,
    closeAddFieldDialog,
    onActionFeedback,
    onSubmitInterpretationChanges,
  ]);
  const openFieldEditDialog = useCallback((item: ReviewSelectableField) => {
    const rawCurrentValue = item.rawField?.value;
    setEditingField(item);
    setEditingFieldDraftValue(
      rawCurrentValue === null || rawCurrentValue === undefined ? "" : String(rawCurrentValue),
    );
  }, []);
  const closeFieldEditDialog = useCallback(() => {
    setEditingField(null);
    setEditingFieldDraftValue("");
  }, []);
  const canonicalSexOptions = useMemo(
    () => new Set(getControlledVocabOptionValues("sex").map((value) => value.toLowerCase())),
    [],
  );
  const canonicalSpeciesOptions = useMemo(
    () => new Set(getControlledVocabOptionValues("species").map((value) => value.toLowerCase())),
    [],
  );
  const isEditingMicrochipField = editingField?.key === "microchip_id";
  const isEditingWeightField = editingField?.key === "weight";
  const isEditingAgeField = editingField?.key === "age";
  const isEditingDateField = editingField?.key ? isDateFieldKey(editingField.key) : false;
  const isEditingSexField = editingField?.key === "sex";
  const isEditingSpeciesField = editingField?.key === "species";
  const isEditingMicrochipInvalid =
    isEditingMicrochipField && !validateFieldValue("microchip_id", editingFieldDraftValue).ok;
  const isEditingWeightInvalid =
    isEditingWeightField && !validateFieldValue("weight", editingFieldDraftValue).ok;
  const isEditingAgeInvalid =
    isEditingAgeField && !validateFieldValue("age", editingFieldDraftValue).ok;
  const isEditingDateInvalid =
    isEditingDateField &&
    !!editingField?.key &&
    !validateFieldValue(editingField.key, editingFieldDraftValue).ok;
  const isEditingSexInvalid =
    isEditingSexField && !canonicalSexOptions.has(editingFieldDraftValue.trim().toLowerCase());
  const isEditingSpeciesInvalid =
    isEditingSpeciesField &&
    !canonicalSpeciesOptions.has(editingFieldDraftValue.trim().toLowerCase());
  const editingFieldCandidateSections = useMemo(
    () =>
      editingField?.key
        ? resolveCandidateSuggestionSections(
            editingField.key,
            editingField.rawField?.candidate_suggestions,
          )
        : { applicableSuggestions: [], detectedCandidates: [] },
    [editingField?.key, editingField?.rawField?.candidate_suggestions],
  );
  const saveFieldEditDialog = useCallback(() => {
    if (!editingField) return;
    if (isEditingMicrochipInvalid || isEditingWeightInvalid || isEditingAgeInvalid) return;
    if (isEditingDateField && isEditingDateInvalid) return;
    if (isEditingSexField && (editingFieldDraftValue.trim().length === 0 || isEditingSexInvalid))
      return;
    if (isEditingSpeciesField && isEditingSpeciesInvalid) return;
    const nextValue = editingFieldDraftValue.trim();
    const nextPayloadValue = nextValue.length > 0 ? nextValue : null;
    const previousRawValue = editingField.rawField?.value;
    const previousValue =
      previousRawValue === null || previousRawValue === undefined
        ? null
        : String(previousRawValue).trim();
    const previousPayloadValue = previousValue && previousValue.length > 0 ? previousValue : null;
    const valueType = editingField.rawField?.value_type ?? editingField.valueType ?? "string";
    if (
      (editingField.rawField && previousPayloadValue === nextPayloadValue) ||
      (!editingField.rawField && nextPayloadValue === null)
    ) {
      onActionFeedback({ kind: "info", message: "No se han realizado cambios." });
      closeFieldEditDialog();
      return;
    }
    const changes: InterpretationChangePayload[] = editingField.rawField
      ? [
          {
            op: "UPDATE",
            field_id: editingField.rawField.field_id,
            value: nextPayloadValue,
            value_type: valueType,
          },
        ]
      : [{ op: "ADD", key: editingField.key, value: nextPayloadValue, value_type: valueType }];
    onSubmitInterpretationChanges(changes, "Valor actualizado correctamente.");
    closeFieldEditDialog();
  }, [
    closeFieldEditDialog,
    editingField,
    editingFieldDraftValue,
    isEditingAgeInvalid,
    isEditingDateField,
    isEditingDateInvalid,
    isEditingMicrochipInvalid,
    isEditingSexField,
    isEditingSexInvalid,
    isEditingSpeciesField,
    isEditingSpeciesInvalid,
    isEditingWeightInvalid,
    onActionFeedback,
    onSubmitInterpretationChanges,
  ]);
  return {
    editingField,
    editingFieldDraftValue,
    setEditingFieldDraftValue,
    isAddFieldDialogOpen,
    setIsAddFieldDialogOpen,
    addFieldKeyDraft,
    setAddFieldKeyDraft,
    addFieldValueDraft,
    setAddFieldValueDraft,
    openFieldEditDialog,
    closeFieldEditDialog,
    saveFieldEditDialog,
    closeAddFieldDialog,
    saveAddFieldDialog,
    editingFieldCandidateSections,
    isEditingMicrochipField,
    isEditingMicrochipInvalid,
    isEditingWeightField,
    isEditingWeightInvalid,
    isEditingAgeField,
    isEditingAgeInvalid,
    isEditingDateField,
    isEditingDateInvalid,
    isEditingSexField,
    isEditingSexInvalid,
    isEditingSpeciesField,
    isEditingSpeciesInvalid,
  };
}
