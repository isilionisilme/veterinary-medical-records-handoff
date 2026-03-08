import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { FieldEditDialog } from "./FieldEditDialog";

vi.mock("../ui/dialog", () => {
  type DialogProps = {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children?: ReactNode;
  };

  return {
    Dialog: ({ open, onOpenChange, children }: DialogProps) => (
      <div data-testid="mock-dialog" data-open={String(Boolean(open))}>
        <button type="button" onClick={() => onOpenChange?.(false)}>
          mock-request-close
        </button>
        <button type="button" onClick={() => onOpenChange?.(true)}>
          mock-request-open
        </button>
        {children}
      </div>
    ),
    DialogContent: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    DialogClose: ({ children }: { children?: ReactNode }) => <>{children}</>,
    DialogDescription: ({ children }: { children?: ReactNode }) => <p>{children}</p>,
    DialogFooter: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    DialogHeader: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    DialogTitle: ({ children }: { children?: ReactNode }) => <h2>{children}</h2>,
  };
});

function renderSpeciesDialog(options?: {
  value?: string;
  isSaveDisabled?: boolean;
  speciesErrorMessage?: string | null;
  candidateSuggestions?: Array<{ value: string; confidence: number }>;
  detectedCandidates?: Array<{ value: string; confidence?: number }>;
}) {
  const onValueChange = vi.fn();
  const onOpenChange = vi.fn();
  const onSave = vi.fn();

  render(
    <FieldEditDialog
      open
      fieldKey="species"
      fieldLabel="Especie"
      value={options?.value ?? ""}
      candidateSuggestions={options?.candidateSuggestions}
      detectedCandidates={options?.detectedCandidates}
      isSaving={false}
      isSaveDisabled={options?.isSaveDisabled ?? false}
      speciesErrorMessage={options?.speciesErrorMessage ?? null}
      onValueChange={onValueChange}
      onOpenChange={onOpenChange}
      onSave={onSave}
    />,
  );

  return { onValueChange, onOpenChange, onSave };
}

function renderSexDialog(options?: {
  value?: string;
  isSaveDisabled?: boolean;
  sexErrorMessage?: string | null;
  candidateSuggestions?: Array<{ value: string; confidence: number }>;
  detectedCandidates?: Array<{ value: string; confidence?: number }>;
}) {
  const onValueChange = vi.fn();
  const onOpenChange = vi.fn();
  const onSave = vi.fn();

  render(
    <FieldEditDialog
      open
      fieldKey="sex"
      fieldLabel="Sexo"
      value={options?.value ?? ""}
      candidateSuggestions={options?.candidateSuggestions}
      detectedCandidates={options?.detectedCandidates}
      isSaving={false}
      isSaveDisabled={options?.isSaveDisabled ?? false}
      sexErrorMessage={options?.sexErrorMessage ?? null}
      onValueChange={onValueChange}
      onOpenChange={onOpenChange}
      onSave={onSave}
    />,
  );

  return { onValueChange, onOpenChange, onSave };
}

function renderAgeDialog(options?: {
  value?: string;
  isSaveDisabled?: boolean;
  ageErrorMessage?: string | null;
  fieldOrigin?: "machine" | "human" | "derived";
}) {
  const onValueChange = vi.fn();
  const onOpenChange = vi.fn();
  const onSave = vi.fn();

  render(
    <FieldEditDialog
      open
      fieldKey="age"
      fieldOrigin={options?.fieldOrigin}
      fieldLabel="Edad"
      value={options?.value ?? ""}
      isSaving={false}
      isSaveDisabled={options?.isSaveDisabled ?? false}
      ageErrorMessage={options?.ageErrorMessage ?? null}
      onValueChange={onValueChange}
      onOpenChange={onOpenChange}
      onSave={onSave}
    />,
  );

  return { onValueChange, onOpenChange, onSave };
}

describe("FieldEditDialog species", () => {
  it("shows current invalid value as disabled detected option and keeps save blocked", () => {
    const { onSave } = renderSpeciesDialog({
      value: "equino",
      isSaveDisabled: true,
      speciesErrorMessage: "Valor no valido. Usa canino o felino.",
    });

    const select = screen.getByRole("combobox");
    expect(select).toHaveValue("equino");
    const detectedOption = screen.getByRole("option", {
      name: "Valor detectado (no coincide con las opciones): equino",
    });
    expect(detectedOption).toBeDisabled();
    expect(screen.getByText("Valor no valido. Usa canino o felino.")).toBeInTheDocument();
    expect(screen.queryByText("Selecciona canino o felino.")).toBeNull();

    const saveButton = screen.getByRole("button", { name: "Guardar" });
    expect(saveButton).toBeDisabled();
    fireEvent.click(saveButton);
    expect(onSave).not.toHaveBeenCalled();
  });

  it("shows canonical species value and hint when valid", () => {
    renderSpeciesDialog({ value: "canino", isSaveDisabled: false, speciesErrorMessage: null });

    expect(screen.getByRole("combobox")).toHaveValue("canino");
    expect(screen.getByText("Selecciona canino o felino.")).toBeInTheDocument();
  });

  it("emits canonical option value when selecting species", () => {
    const { onValueChange } = renderSpeciesDialog({ value: "" });

    fireEvent.change(screen.getByRole("combobox"), { target: { value: "felino" } });

    expect(onValueChange).toHaveBeenCalledWith("felino");
  });

  it("shows only valid candidates in sugerencias and keeps click behavior", () => {
    const { onValueChange } = renderSpeciesDialog({
      value: "canino",
      candidateSuggestions: [{ value: "felino", confidence: 0.87 }],
      detectedCandidates: [{ value: "lagarto", confidence: 0.4 }],
    });

    expect(screen.getByText("Sugerencias (1)")).toBeInTheDocument();
    expect(screen.getByText("Sugerido")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /felino/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /lagarto/i })).toBeNull();
    expect(screen.getByText("Detectado en el documento")).toBeInTheDocument();
    expect(screen.getByText("lagarto")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /felino/i }));
    expect(onValueChange).toHaveBeenCalledWith("felino");
  });

  it("shows normalized species value as disabled detected option", () => {
    const { onSave } = renderSpeciesDialog({
      value: "canina",
      isSaveDisabled: true,
      speciesErrorMessage: "Valor no valido. Usa canino o felino.",
    });

    const select = screen.getByRole("combobox");
    expect(select).toHaveValue("canina");
    expect(
      screen.getByRole("option", {
        name: "Valor detectado (no coincide con las opciones): canina",
      }),
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: "Guardar" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(onSave).not.toHaveBeenCalled();
  });

  it("does not render suggestions when only current value is present", () => {
    renderSpeciesDialog({
      value: "canino",
      candidateSuggestions: [{ value: "canino", confidence: 0.93 }],
    });

    expect(screen.queryByText(/Sugerencias/i)).toBeNull();
  });
});

describe("FieldEditDialog sex", () => {
  it("shows current invalid value as disabled detected option", () => {
    renderSexDialog({
      value: "desconocido",
      isSaveDisabled: true,
      sexErrorMessage: "Valor no válido. Usa “macho” o “hembra”.",
    });

    const select = screen.getByRole("combobox");
    expect(select).toHaveValue("desconocido");
    const detectedOption = screen.getByRole("option", {
      name: "Valor detectado (no coincide con las opciones): desconocido",
    });
    expect(detectedOption).toBeDisabled();
    expect(screen.getByRole("option", { name: "Macho" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Hembra" })).toBeInTheDocument();
  });

  it("shows normalized sex value as disabled detected option", () => {
    const { onSave } = renderSexDialog({
      value: "female",
      isSaveDisabled: true,
      sexErrorMessage: "Valor no válido. Usa “macho” o “hembra”.",
    });

    const select = screen.getByRole("combobox");
    expect(select).toHaveValue("female");
    expect(
      screen.getByRole("option", {
        name: "Valor detectado (no coincide con las opciones): female",
      }),
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: "Guardar" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(onSave).not.toHaveBeenCalled();
  });

  it("renders non-applicable candidates in detected block as non-clickable rows", () => {
    renderSexDialog({
      value: "",
      candidateSuggestions: [{ value: "hembra", confidence: 0.8 }],
      detectedCandidates: [{ value: "sexo incierto", confidence: 0.4 }],
    });

    expect(screen.getByText("Detectado en el documento")).toBeInTheDocument();
    expect(screen.getByText("sexo incierto")).toBeInTheDocument();
    expect(screen.getByText("No coincide con las opciones de este campo")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /sexo incierto/i })).toBeNull();
  });
});

describe("FieldEditDialog age", () => {
  it("keeps save disabled and shows restriction message when age is invalid", () => {
    const { onSave } = renderAgeDialog({
      value: "",
      isSaveDisabled: true,
      ageErrorMessage: "Introduce una edad entre 0-999 años",
    });

    expect(screen.getByText("Introduce una edad entre 0-999 años")).toBeInTheDocument();
    const saveButton = screen.getByRole("button", { name: "Guardar" });
    expect(saveButton).toBeDisabled();

    fireEvent.click(saveButton);
    expect(onSave).not.toHaveBeenCalled();
  });

  it("sanitizes age input to digits only and max three characters", () => {
    const { onValueChange } = renderAgeDialog({ value: "" });

    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12ab34" } });

    expect(onValueChange).toHaveBeenCalledWith("123");
  });

  it("keeps save enabled for valid upper boundary age 999", () => {
    const { onSave } = renderAgeDialog({
      value: "999",
      isSaveDisabled: false,
      ageErrorMessage: null,
    });

    const saveButton = screen.getByRole("button", { name: "Guardar" });
    expect(saveButton).toBeEnabled();

    fireEvent.click(saveButton);
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it("shows the derived-age hint when origin is derived", () => {
    renderAgeDialog({ value: "7", fieldOrigin: "derived" });

    expect(screen.getByText("Edad calculada desde fecha de nacimiento")).toBeInTheDocument();
  });

  it("does not show the derived-age hint when origin is human", () => {
    renderAgeDialog({ value: "7", fieldOrigin: "human" });

    expect(screen.queryByText("Edad calculada desde fecha de nacimiento")).not.toBeInTheDocument();
  });
});
