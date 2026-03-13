import { type KeyboardEvent, useEffect, useMemo, useRef } from "react";

import { Button } from "../ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { CANONICAL_SEX_OPTIONS, CANONICAL_SPECIES_OPTIONS } from "../../extraction/fieldValidators";

type CandidateSuggestion = {
  value: string;
  confidence: number;
};

type DetectedCandidate = {
  value: string;
  confidence?: number;
};

type FieldEditDialogProps = {
  open: boolean;
  fieldKey: string | null;
  fieldOrigin?: "machine" | "human" | "derived";
  fieldLabel: string;
  value: string;
  candidateSuggestions?: CandidateSuggestion[];
  detectedCandidates?: DetectedCandidate[];
  isSaving: boolean;
  isSaveDisabled?: boolean;
  microchipErrorMessage?: string | null;
  weightErrorMessage?: string | null;
  ageErrorMessage?: string | null;
  dateErrorMessage?: string | null;
  sexErrorMessage?: string | null;
  speciesErrorMessage?: string | null;
  onValueChange: (value: string) => void;
  onOpenChange: (open: boolean) => void;
  onSave: () => void;
};

export function FieldEditDialog({
  open,
  fieldKey,
  fieldOrigin,
  fieldLabel,
  value,
  candidateSuggestions = [],
  detectedCandidates = [],
  isSaving,
  isSaveDisabled = false,
  microchipErrorMessage = null,
  weightErrorMessage = null,
  ageErrorMessage = null,
  dateErrorMessage = null,
  sexErrorMessage = null,
  speciesErrorMessage = null,
  onValueChange,
  onOpenChange,
  onSave,
}: FieldEditDialogProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const selectRef = useRef<HTMLSelectElement | null>(null);
  const isSexField = fieldKey === "sex";
  const isSpeciesField = fieldKey === "species";
  const shouldUseTextarea = useMemo(
    () => !isSexField && !isSpeciesField && (value.includes("\n") || value.length > 60),
    [isSexField, isSpeciesField, value],
  );

  useEffect(() => {
    if (!open) {
      return;
    }
    const focusTimer = window.setTimeout(() => {
      if (isSexField || isSpeciesField) {
        selectRef.current?.focus();
        return;
      }
      if (shouldUseTextarea) {
        textareaRef.current?.focus();
        return;
      }
      inputRef.current?.focus();
    }, 0);

    return () => window.clearTimeout(focusTimer);
  }, [isSexField, isSpeciesField, open, shouldUseTextarea]);

  const handleSingleLineEnter = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    if (!isSaving && !isSaveDisabled) {
      onSave();
    }
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen && isSaving) {
      return;
    }
    onOpenChange(nextOpen);
  };

  const titleText = fieldLabel.trim().length > 0 ? `Editar "${fieldLabel}"` : "Editar campo";
  const isMicrochipField = fieldKey === "microchip_id";
  const isWeightField = fieldKey === "weight";
  const isAgeField = fieldKey === "age";
  const isDateField =
    fieldKey === "document_date" ||
    fieldKey === "visit_date" ||
    fieldKey === "admission_date" ||
    fieldKey === "discharge_date" ||
    fieldKey === "dob" ||
    Boolean(fieldKey?.startsWith("fecha_"));
  const microchipHintText = "Solo números (9–15 dígitos).";
  const weightHintText = "Ej.: 12,5 kg (0,5–120).";
  const ageHintText = "Introduce una edad entre 0-999 años";
  const dateHintText = "Formatos: dd/mm/aaaa o aaaa-mm-dd.";
  const sexHintText = "Selecciona macho o hembra.";
  const speciesHintText = "Selecciona canino o felino.";
  const normalizedSexValue = value.trim().toLowerCase();
  const isKnownSexValue = normalizedSexValue === "macho" || normalizedSexValue === "hembra";
  const normalizedSpeciesValue = value.trim().toLowerCase();
  const isKnownSpeciesValue = CANONICAL_SPECIES_OPTIONS.some(
    (option) => option.value === normalizedSpeciesValue,
  );
  const visibleCandidateSuggestions = useMemo(() => {
    const normalizedCurrentValue = value.trim();
    const normalizedSuggestions = candidateSuggestions
      .filter((suggestion) => suggestion.value.trim().length > 0)
      .slice(0, 5);
    const hasAlternative = normalizedSuggestions.some(
      (suggestion) => suggestion.value.trim() !== normalizedCurrentValue,
    );
    return hasAlternative ? normalizedSuggestions : [];
  }, [candidateSuggestions, value]);
  const visibleDetectedCandidates = useMemo(
    () => detectedCandidates.filter((candidate) => candidate.value.trim().length > 0).slice(0, 3),
    [detectedCandidates],
  );
  const invalidCurrentControlledValue = useMemo(() => {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    if (isSexField && !isKnownSexValue) {
      return trimmed;
    }
    if (isSpeciesField && !isKnownSpeciesValue) {
      return trimmed;
    }
    return null;
  }, [isKnownSexValue, isKnownSpeciesValue, isSexField, isSpeciesField, value]);
  const controlledSelectValue =
    invalidCurrentControlledValue ??
    (isSexField
      ? isKnownSexValue
        ? normalizedSexValue
        : ""
      : isKnownSpeciesValue
        ? normalizedSpeciesValue
        : "");
  const handleValueChange = (nextValue: string) => {
    if (isMicrochipField) {
      const sanitized = nextValue.replace(/\D/g, "");
      onValueChange(sanitized);
      return;
    }
    if (isWeightField) {
      const sanitized = nextValue.replace(/[^0-9,.\skg]/gi, "");
      onValueChange(sanitized);
      return;
    }
    if (isAgeField) {
      const sanitized = nextValue.replace(/\D/g, "").slice(0, 3);
      onValueChange(sanitized);
      return;
    }
    if (isDateField) {
      const sanitized = nextValue.replace(/[^0-9/-]/g, "");
      onValueChange(sanitized);
      return;
    }
    if (isSexField) {
      onValueChange(nextValue);
      return;
    }
    if (isSpeciesField) {
      onValueChange(nextValue);
      return;
    }
    onValueChange(nextValue);
  };
  const shouldHighlightError =
    (isMicrochipField && microchipErrorMessage) ||
    (isWeightField && weightErrorMessage) ||
    (isAgeField && ageErrorMessage) ||
    (isDateField && dateErrorMessage) ||
    (isSexField && sexErrorMessage) ||
    (isSpeciesField && speciesErrorMessage);

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        data-testid="field-edit-dialog"
        onEscapeKeyDown={(event) => {
          if (!isSaving) {
            return;
          }
          event.preventDefault();
        }}
        onInteractOutside={(event) => {
          if (!isSaving) {
            return;
          }
          event.preventDefault();
        }}
      >
        <DialogHeader>
          <DialogTitle>{titleText}</DialogTitle>
          <DialogDescription className="text-xs">
            Revisa el valor sugerido, corrígelo si hace falta y guarda los cambios.
          </DialogDescription>
        </DialogHeader>

        {isSexField ? (
          <select
            data-testid="field-edit-input"
            ref={selectRef}
            aria-label={`Valor del campo ${fieldLabel || "editable"}`}
            value={controlledSelectValue}
            onChange={(event) => handleValueChange(event.target.value)}
            className={`w-full rounded-control border bg-surface px-3 py-2 text-sm text-text outline-none transition focus-visible:bg-surfaceMuted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
              shouldHighlightError
                ? "border-[var(--status-error)] focus-visible:outline-[var(--status-error)]"
                : "border-borderSubtle focus-visible:border-borderSubtle focus-visible:outline-none"
            }`}
          >
            <option value="">Selecciona una opción</option>
            {CANONICAL_SEX_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
            {invalidCurrentControlledValue ? (
              <option value={invalidCurrentControlledValue} disabled>
                {`Valor detectado (no coincide con las opciones): ${invalidCurrentControlledValue}`}
              </option>
            ) : null}
          </select>
        ) : isSpeciesField ? (
          <select
            data-testid="field-edit-input"
            ref={selectRef}
            aria-label={`Valor del campo ${fieldLabel || "editable"}`}
            value={controlledSelectValue}
            onChange={(event) => handleValueChange(event.target.value)}
            className={`w-full rounded-control border bg-surface px-3 py-2 text-sm text-text outline-none transition focus-visible:bg-surfaceMuted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
              shouldHighlightError
                ? "border-[var(--status-error)] focus-visible:outline-[var(--status-error)]"
                : "border-borderSubtle focus-visible:border-borderSubtle focus-visible:outline-none"
            }`}
          >
            <option value="">Selecciona una opción</option>
            {CANONICAL_SPECIES_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
            {invalidCurrentControlledValue ? (
              <option value={invalidCurrentControlledValue} disabled>
                {`Valor detectado (no coincide con las opciones): ${invalidCurrentControlledValue}`}
              </option>
            ) : null}
          </select>
        ) : shouldUseTextarea ? (
          <textarea
            data-testid="field-edit-input"
            ref={textareaRef}
            aria-label={`Valor del campo ${fieldLabel || "editable"}`}
            value={value}
            onChange={(event) => handleValueChange(event.target.value)}
            rows={6}
            className={`min-h-28 w-full resize-y rounded-control border bg-surface px-3 py-2 text-sm text-text outline-none transition focus-visible:bg-surfaceMuted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
              shouldHighlightError
                ? "border-[var(--status-error)] focus-visible:outline-[var(--status-error)]"
                : "border-borderSubtle focus-visible:border-borderSubtle focus-visible:outline-none"
            }`}
          />
        ) : (
          <Input
            data-testid="field-edit-input"
            ref={inputRef}
            aria-label={`Valor del campo ${fieldLabel || "editable"}`}
            value={value}
            onChange={(event) => handleValueChange(event.target.value)}
            onKeyDown={handleSingleLineEnter}
            className={
              isMicrochipField || isWeightField || isDateField
                ? `rounded-control border bg-surface px-3 py-1 text-sm text-text ${
                    shouldHighlightError
                      ? "border-[var(--status-error)] focus-visible:outline-[var(--status-error)]"
                      : "border-borderSubtle focus-visible:border-borderSubtle focus-visible:outline-none"
                  }`
                : undefined
            }
          />
        )}
        {visibleCandidateSuggestions.length > 0 ? (
          <div className="mt-2 space-y-1.5 rounded-control border border-borderSubtle bg-surface px-3 py-2">
            <p className="text-xs font-semibold text-text">
              Sugerencias ({visibleCandidateSuggestions.length})
            </p>
            <p className="text-xs text-muted">
              Selecciona una sugerencia o escribe tu propia corrección.
            </p>
            <div className="space-y-1">
              {visibleCandidateSuggestions.map((suggestion, index) => (
                <button
                  key={`${suggestion.value}-${index}`}
                  type="button"
                  aria-label={`Aplicar sugerencia ${suggestion.value}`}
                  className="flex w-full items-center justify-between rounded-control border border-borderSubtle bg-surface px-2 py-1 text-left text-xs text-text transition hover:bg-surfaceMuted"
                  onClick={() => handleValueChange(suggestion.value)}
                >
                  <span className="truncate">{suggestion.value}</span>
                  {index === 0 ? (
                    <span className="ml-2 shrink-0 rounded-full bg-accent/15 px-1.5 py-0.5 text-[10px] font-semibold text-accent">
                      Sugerido
                    </span>
                  ) : null}
                </button>
              ))}
            </div>
          </div>
        ) : null}
        {visibleDetectedCandidates.length > 0 ? (
          <div className="mt-2 space-y-1.5 rounded-control border border-borderSubtle bg-surface px-3 py-2">
            <p className="text-xs font-semibold text-text">Detectado en el documento</p>
            <div className="space-y-1">
              {visibleDetectedCandidates.map((candidate, index) => (
                <div
                  key={`${candidate.value}-${index}`}
                  className="rounded-control border border-borderSubtle bg-surface px-2 py-1 text-xs"
                >
                  <p className="truncate text-text">{candidate.value}</p>
                  <p className="text-muted">No coincide con las opciones de este campo</p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        {isMicrochipField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                microchipErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {microchipErrorMessage ?? microchipHintText}
            </p>
          </div>
        ) : isWeightField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                weightErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {weightErrorMessage ?? weightHintText}
            </p>
          </div>
        ) : isAgeField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                ageErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {ageErrorMessage ?? ageHintText}
            </p>
            {fieldOrigin === "derived" ? (
              <p className="text-xs text-blue-500">Edad calculada desde fecha de nacimiento</p>
            ) : null}
          </div>
        ) : isDateField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                dateErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {dateErrorMessage ?? dateHintText}
            </p>
          </div>
        ) : isSexField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                sexErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {sexErrorMessage ?? sexHintText}
            </p>
          </div>
        ) : isSpeciesField ? (
          <div className="mt-1 space-y-1">
            <p
              className={
                speciesErrorMessage ? "text-xs text-[var(--status-error)]" : "text-xs text-muted"
              }
            >
              {speciesErrorMessage ?? speciesHintText}
            </p>
          </div>
        ) : null}

        <DialogFooter>
          <DialogClose asChild>
            <Button
              data-testid="field-edit-cancel"
              type="button"
              variant="ghost"
              className="border border-border bg-surface text-text hover:bg-surfaceMuted"
              disabled={isSaving}
            >
              Cancelar
            </Button>
          </DialogClose>
          <Button
            data-testid="field-edit-save"
            type="button"
            onClick={onSave}
            disabled={isSaving || isSaveDisabled}
          >
            Guardar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
