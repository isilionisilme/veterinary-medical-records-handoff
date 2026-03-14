import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RawTextTab } from "./RawTextTab";

function createProps(overrides?: Partial<React.ComponentProps<typeof RawTextTab>>) {
  return {
    viewerModeToolbarIcons: <span data-testid="toolbar-icons">icons</span>,
    viewerDownloadIcon: <span data-testid="download-icon">download</span>,
    activeId: "doc-1",
    isActiveDocumentProcessing: false,
    reprocessPending: false,
    reprocessingDocumentId: null,
    hasObservedProcessingAfterReprocess: true,
    onOpenRetryModal: vi.fn(),
    rawSearch: "",
    setRawSearch: vi.fn(),
    canSearchRawText: true,
    hasRawText: true,
    rawSearchNotice: null,
    isRawTextLoading: false,
    rawTextErrorMessage: null,
    rawTextContent: "texto de prueba",
    onRawSearch: vi.fn(),
    canCopyRawText: true,
    isCopyingRawText: false,
    copyFeedback: null,
    onCopyRawText: vi.fn(async () => {}),
    onDownloadRawText: vi.fn(),
    ...overrides,
  };
}

describe("RawTextTab", () => {
  it("triggers search on Enter and search button", () => {
    const props = createProps();
    render(<RawTextTab {...props} />);

    fireEvent.keyDown(screen.getByTestId("raw-text-search-input"), { key: "Enter" });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));

    expect(props.onRawSearch).toHaveBeenCalledTimes(2);
  });

  it("renders copy button dynamic label and disabled state", () => {
    const props = createProps({ isCopyingRawText: true, canCopyRawText: true });
    render(<RawTextTab {...props} />);

    const copyButton = screen.getByTestId("raw-text-copy");
    expect(copyButton).toBeDisabled();
    expect(copyButton).toHaveTextContent("Copiando...");
  });

  it("disables reprocess action when no active document", () => {
    const props = createProps({ activeId: null });
    render(<RawTextTab {...props} />);

    expect(screen.getByRole("button", { name: "Reprocesar" })).toBeDisabled();
  });
});
