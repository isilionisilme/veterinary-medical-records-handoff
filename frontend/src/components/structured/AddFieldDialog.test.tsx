import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { AddFieldDialog } from "./AddFieldDialog";

vi.mock("../ui/dialog", () => {
  type DialogProps = {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children?: ReactNode;
  };
  type DialogContentProps = {
    onEscapeKeyDown?: (event: { preventDefault: () => void }) => void;
    onInteractOutside?: (event: { preventDefault: () => void }) => void;
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
    DialogContent: ({ onEscapeKeyDown, onInteractOutside, children }: DialogContentProps) => (
      <div>
        <button
          type="button"
          onClick={() => {
            const event = { preventDefault: vi.fn() };
            onEscapeKeyDown?.(event);
            (globalThis as { __escapePrevented?: number }).__escapePrevented =
              event.preventDefault.mock.calls.length;
          }}
        >
          mock-escape
        </button>
        <button
          type="button"
          onClick={() => {
            const event = { preventDefault: vi.fn() };
            onInteractOutside?.(event);
            (globalThis as { __outsidePrevented?: number }).__outsidePrevented =
              event.preventDefault.mock.calls.length;
          }}
        >
          mock-outside
        </button>
        {children}
      </div>
    ),
    DialogClose: ({ children }: { children?: ReactNode }) => <>{children}</>,
    DialogDescription: ({ children }: { children?: ReactNode }) => <p>{children}</p>,
    DialogFooter: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    DialogHeader: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    DialogTitle: ({ children }: { children?: ReactNode }) => <h2>{children}</h2>,
  };
});

type AddFieldDialogProps = Parameters<typeof AddFieldDialog>[0];

function renderDialog(overrides?: Partial<AddFieldDialogProps>) {
  const props: AddFieldDialogProps = {
    open: true,
    isSaving: false,
    fieldKey: "",
    fieldValue: "",
    onFieldKeyChange: vi.fn(),
    onFieldValueChange: vi.fn(),
    onOpenChange: vi.fn(),
    onSave: vi.fn(),
    ...overrides,
  };

  render(<AddFieldDialog {...props} />);
  return props;
}

describe("AddFieldDialog", () => {
  it("renders title, description and field values", () => {
    renderDialog({ fieldKey: "weight", fieldValue: "12.5" });

    expect(screen.getByText("Añadir campo")).toBeInTheDocument();
    expect(
      screen.getByText("Define una clave nueva y su valor inicial para este documento."),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Clave")).toHaveValue("weight");
    expect(screen.getByLabelText("Valor")).toHaveValue("12.5");
  });

  it("forwards key and value input changes", () => {
    const props = renderDialog();

    fireEvent.change(screen.getByLabelText("Clave"), { target: { value: "owner_name" } });
    fireEvent.change(screen.getByLabelText("Valor"), { target: { value: "Lucía" } });

    expect(props.onFieldKeyChange).toHaveBeenCalledWith("owner_name");
    expect(props.onFieldValueChange).toHaveBeenCalledWith("Lucía");
  });

  it("calls save handler when clicking Guardar", () => {
    const props = renderDialog();

    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    expect(props.onSave).toHaveBeenCalledTimes(1);
  });

  it("forwards open/close requests through handleOpenChange when not saving", () => {
    const props = renderDialog({ isSaving: false });

    fireEvent.click(screen.getByRole("button", { name: "mock-request-close" }));
    fireEvent.click(screen.getByRole("button", { name: "mock-request-open" }));

    expect(props.onOpenChange).toHaveBeenNthCalledWith(1, false);
    expect(props.onOpenChange).toHaveBeenNthCalledWith(2, true);
  });

  it("disables actions while saving", () => {
    const props = renderDialog({ isSaving: true });

    const saveButton = screen.getByRole("button", { name: "Guardar" });
    const cancelButton = screen.getByRole("button", { name: "Cancelar" });

    expect(saveButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();

    fireEvent.click(saveButton);
    fireEvent.click(cancelButton);
    fireEvent.click(screen.getByRole("button", { name: "mock-request-close" }));
    fireEvent.click(screen.getByRole("button", { name: "mock-request-open" }));
    expect(props.onSave).not.toHaveBeenCalled();
    expect(props.onOpenChange).toHaveBeenCalledTimes(1);
    expect(props.onOpenChange).toHaveBeenCalledWith(true);
  });

  it("prevents escape and outside close interactions while saving", () => {
    renderDialog({ isSaving: true });

    fireEvent.click(screen.getByRole("button", { name: "mock-escape" }));
    fireEvent.click(screen.getByRole("button", { name: "mock-outside" }));

    expect((globalThis as { __escapePrevented?: number }).__escapePrevented).toBe(1);
    expect((globalThis as { __outsidePrevented?: number }).__outsidePrevented).toBe(1);
  });

  it("does not prevent escape and outside interactions when not saving", () => {
    renderDialog({ isSaving: false });

    fireEvent.click(screen.getByRole("button", { name: "mock-escape" }));
    fireEvent.click(screen.getByRole("button", { name: "mock-outside" }));

    expect((globalThis as { __escapePrevented?: number }).__escapePrevented).toBe(0);
    expect((globalThis as { __outsidePrevented?: number }).__outsidePrevented).toBe(0);
  });

  it("focuses key input when the dialog opens", async () => {
    renderDialog({ open: true });

    await waitFor(() => {
      expect(screen.getByLabelText("Clave")).toHaveFocus();
    });
  });
});
