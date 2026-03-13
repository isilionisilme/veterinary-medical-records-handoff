import { useEffect, useRef } from "react";

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

type AddFieldDialogProps = {
  open: boolean;
  isSaving: boolean;
  fieldKey: string;
  fieldValue: string;
  onFieldKeyChange: (value: string) => void;
  onFieldValueChange: (value: string) => void;
  onOpenChange: (open: boolean) => void;
  onSave: () => void;
};

export function AddFieldDialog({
  open,
  isSaving,
  fieldKey,
  fieldValue,
  onFieldKeyChange,
  onFieldValueChange,
  onOpenChange,
  onSave,
}: AddFieldDialogProps) {
  const fieldKeyRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }
    const focusTimer = window.setTimeout(() => {
      fieldKeyRef.current?.focus();
    }, 0);

    return () => window.clearTimeout(focusTimer);
  }, [open]);

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen && isSaving) {
      return;
    }
    onOpenChange(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
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
          <DialogTitle>Añadir campo</DialogTitle>
          <DialogDescription className="text-xs">
            Define una clave nueva y su valor inicial para este documento.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3">
          <label className="space-y-1.5">
            <span className="text-sm font-medium text-text">Clave</span>
            <Input
              ref={fieldKeyRef}
              aria-label="Clave del nuevo campo"
              value={fieldKey}
              onChange={(event) => onFieldKeyChange(event.target.value)}
            />
          </label>
          <label className="space-y-1.5">
            <span className="text-sm font-medium text-text">Valor</span>
            <Input
              aria-label="Valor del nuevo campo"
              value={fieldValue}
              onChange={(event) => onFieldValueChange(event.target.value)}
            />
          </label>
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button
              type="button"
              variant="ghost"
              className="border border-border bg-surface text-text hover:bg-surfaceMuted"
              disabled={isSaving}
            >
              Cancelar
            </Button>
          </DialogClose>
          <Button type="button" onClick={onSave} disabled={isSaving}>
            Guardar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
