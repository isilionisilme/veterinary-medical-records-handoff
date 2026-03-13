import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SourcePanel } from "./SourcePanel";

describe("SourcePanel", () => {
  it("toggles pin action when desktop pinning is enabled", () => {
    const onTogglePin = vi.fn();

    render(
      <SourcePanel
        sourcePage={4}
        sourceSnippet="Detalle de evidencia"
        isSourcePinned={false}
        isDesktopForPin={true}
        onTogglePin={onTogglePin}
        onClose={vi.fn()}
        content={<div>Contenido</div>}
      />,
    );

    const pinButton = screen.getByRole("button", { name: /Fijar fuente/i });
    expect(pinButton).toBeEnabled();
    fireEvent.click(pinButton);
    expect(onTogglePin).toHaveBeenCalledTimes(1);
  });

  it("calls close callback from close icon button", () => {
    const onClose = vi.fn();

    render(
      <SourcePanel
        sourcePage={1}
        sourceSnippet="Snippet"
        isSourcePinned={true}
        isDesktopForPin={true}
        onTogglePin={vi.fn()}
        onClose={onClose}
        content={<div>Contenido</div>}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /Cerrar panel de fuente/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("shows fallback evidence text and no-page label", () => {
    render(
      <SourcePanel
        sourcePage={null}
        sourceSnippet={null}
        isSourcePinned={false}
        isDesktopForPin={false}
        onTogglePin={vi.fn()}
        onClose={vi.fn()}
        content={<div>Contenido</div>}
      />,
    );

    expect(screen.getByText(/Sin página seleccionada/i)).toBeInTheDocument();
    expect(screen.getByText(/Sin evidencia disponible/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Fijar fuente/i })).toBeDisabled();
  });

  it("renders pinned state and custom content", () => {
    render(
      <SourcePanel
        sourcePage={2}
        sourceSnippet="Prueba"
        isSourcePinned={true}
        isDesktopForPin={true}
        onTogglePin={vi.fn()}
        onClose={vi.fn()}
        content={<div>Panel interno</div>}
      />,
    );

    expect(screen.getByRole("button", { name: /Desfijar fuente/i })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByText("Panel interno")).toBeInTheDocument();
    expect(screen.getByTestId("source-panel-scroll")).toBeInTheDocument();
  });

  it("does not trigger pin callback when pin button is disabled", () => {
    const onTogglePin = vi.fn();

    render(
      <SourcePanel
        sourcePage={null}
        sourceSnippet={null}
        isSourcePinned={false}
        isDesktopForPin={false}
        onTogglePin={onTogglePin}
        onClose={vi.fn()}
        content={<div>Contenido</div>}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /Fijar fuente/i }));
    expect(onTogglePin).not.toHaveBeenCalled();
  });
});
