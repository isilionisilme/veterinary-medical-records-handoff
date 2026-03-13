import { AddFieldDialog } from "../structured/AddFieldDialog";
import { FieldEditDialog } from "../structured/FieldEditDialog";
import { type CandidateSuggestionSections } from "../../extraction/candidateSuggestions";
import { type ReviewSelectableField } from "../../types/appWorkspace";

type WorkspaceDialogsProps = {
  isInterpretationEditPending: boolean;
  isAddFieldDialogOpen: boolean;
  addFieldKeyDraft: string;
  addFieldValueDraft: string;
  onFieldKeyChange: (value: string) => void;
  onFieldValueChange: (value: string) => void;
  onCloseAddFieldDialog: () => void;
  onSaveAddFieldDialog: () => void;
  editingField: ReviewSelectableField | null;
  editingFieldDraftValue: string;
  onEditingFieldDraftValueChange: (value: string) => void;
  editingFieldCandidateSections: CandidateSuggestionSections;
  isEditingMicrochipField: boolean;
  isEditingMicrochipInvalid: boolean;
  isEditingWeightField: boolean;
  isEditingWeightInvalid: boolean;
  isEditingAgeField: boolean;
  isEditingAgeInvalid: boolean;
  isEditingDateField: boolean;
  isEditingDateInvalid: boolean;
  isEditingSexField: boolean;
  isEditingSexInvalid: boolean;
  isEditingSpeciesField: boolean;
  isEditingSpeciesInvalid: boolean;
  onCloseFieldEditDialog: () => void;
  onSaveFieldEditDialog: () => void;
};

export function WorkspaceDialogs(props: WorkspaceDialogsProps) {
  return (
    <>
      <AddFieldDialog
        open={props.isAddFieldDialogOpen}
        isSaving={props.isInterpretationEditPending}
        fieldKey={props.addFieldKeyDraft}
        fieldValue={props.addFieldValueDraft}
        onFieldKeyChange={props.onFieldKeyChange}
        onFieldValueChange={props.onFieldValueChange}
        onOpenChange={(open) => {
          if (!open) props.onCloseAddFieldDialog();
        }}
        onSave={props.onSaveAddFieldDialog}
      />
      <FieldEditDialog
        open={props.editingField !== null}
        fieldKey={props.editingField?.key ?? null}
        fieldOrigin={props.editingField?.rawField?.origin}
        fieldLabel={props.editingField?.label ?? ""}
        value={props.editingFieldDraftValue}
        candidateSuggestions={props.editingFieldCandidateSections.applicableSuggestions}
        detectedCandidates={props.editingFieldCandidateSections.detectedCandidates}
        isSaving={props.isInterpretationEditPending}
        isSaveDisabled={
          props.isEditingMicrochipInvalid ||
          props.isEditingWeightInvalid ||
          props.isEditingAgeInvalid ||
          props.isEditingDateInvalid ||
          props.isEditingSexInvalid ||
          props.isEditingSpeciesInvalid
        }
        microchipErrorMessage={
          props.isEditingMicrochipField && props.isEditingMicrochipInvalid
            ? "Introduce entre 9 y 15 dígitos."
            : null
        }
        weightErrorMessage={
          props.isEditingWeightField && props.isEditingWeightInvalid
            ? "Introduce un peso entre 0,5 y 120 kg."
            : null
        }
        ageErrorMessage={
          props.isEditingAgeField && props.isEditingAgeInvalid
            ? "Introduce una edad entre 0-999 años"
            : null
        }
        dateErrorMessage={
          props.isEditingDateField && props.isEditingDateInvalid
            ? "Formato no válido. Usa dd/mm/aaaa o aaaa-mm-dd."
            : null
        }
        sexErrorMessage={
          props.isEditingSexField &&
          props.editingFieldDraftValue.trim().length > 0 &&
          props.isEditingSexInvalid
            ? "Valor no válido. Usa “macho” o “hembra”."
            : null
        }
        speciesErrorMessage={
          props.isEditingSpeciesField &&
          props.editingFieldDraftValue.trim().length > 0 &&
          props.isEditingSpeciesInvalid
            ? "Valor no válido. Usa “canino” o “felino”."
            : null
        }
        onValueChange={props.onEditingFieldDraftValueChange}
        onOpenChange={(open) => {
          if (!open) props.onCloseFieldEditDialog();
        }}
        onSave={props.onSaveFieldEditDialog}
      />
    </>
  );
}
