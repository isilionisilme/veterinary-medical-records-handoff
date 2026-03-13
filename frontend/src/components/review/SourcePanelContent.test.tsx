import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SourcePanelContent } from "./SourcePanelContent";

vi.mock("../PdfViewer");

type SourcePanelContentProps = Parameters<typeof SourcePanelContent>[0];

function renderComponent(overrides?: Partial<SourcePanelContentProps>) {
  const props: SourcePanelContentProps = {
    sourcePage: 2,
    sourceSnippet: "Hemograma completo",
    isSourcePinned: false,
    isDesktopForPin: true,
    onTogglePin: vi.fn(),
    onClose: vi.fn(),
    fileUrl: "blob:http://localhost/doc.pdf",
    activeId: "doc-1",
    filename: "doc.pdf",
    focusRequestId: 4,
    ...overrides,
  };

  render(<SourcePanelContent {...props} />);
  return props;
}

describe("SourcePanelContent", () => {
  it("renders SourcePanel metadata and forwards PdfViewer props when file is available", async () => {
    renderComponent();

    expect(screen.getByText("Página 2")).toBeInTheDocument();
    expect(screen.getByText("Hemograma completo")).toBeInTheDocument();

    const viewer = await screen.findByTestId("mock-pdf-viewer", {}, { timeout: 5000 });
    expect(viewer).toHaveAttribute("data-document-id", "doc-1");
    expect(viewer).toHaveAttribute("data-file-url", "blob:http://localhost/doc.pdf");
    expect(viewer).toHaveAttribute("data-filename", "doc.pdf");
    expect(viewer).toHaveAttribute("data-focus-page", "2");
    expect(viewer).toHaveAttribute("data-highlight-snippet", "Hemograma completo");
    expect(viewer).toHaveAttribute("data-focus-request-id", "4");
  });

  it("renders fallback content when PDF file is not available", () => {
    renderComponent({ fileUrl: null });

    expect(screen.queryByTestId("mock-pdf-viewer")).toBeNull();
    expect(screen.getByText("No hay PDF disponible para este documento.")).toBeInTheDocument();
  });

  it("shows default evidence and selected page fallback labels", () => {
    renderComponent({ sourceSnippet: null, sourcePage: null });

    expect(screen.getByText("Sin evidencia disponible")).toBeInTheDocument();
    expect(screen.getByText("Sin página seleccionada")).toBeInTheDocument();
  });

  it("triggers panel actions and disables pin button on non-desktop mode", () => {
    const props = renderComponent({ isDesktopForPin: false });

    const pinButton = screen.getByRole("button", { name: "Fijar fuente" });
    expect(pinButton).toBeDisabled();

    const closeButton = screen.getByRole("button", { name: "Cerrar panel de fuente" });
    fireEvent.click(closeButton);
    expect(props.onClose).toHaveBeenCalledTimes(1);
  });

  it("toggles pin when pin action is enabled", () => {
    const props = renderComponent({ isDesktopForPin: true });

    fireEvent.click(screen.getByRole("button", { name: "Fijar fuente" }));
    expect(props.onTogglePin).toHaveBeenCalledTimes(1);
  });
});
