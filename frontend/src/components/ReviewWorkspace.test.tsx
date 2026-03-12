import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  MIN_PDF_PANEL_WIDTH_PX,
  REVIEW_SPLIT_MIN_WIDTH_PX,
  SPLITTER_COLUMN_WIDTH_PX,
} from "../App";
import {
  clickPetNameField,
  createDataTransfer,
  getPetNameFieldButton,
  installDefaultAppFetchMock,
  installReviewedModeFetchMock,
  openReadyDocumentAndGetPanel,
  openReviewedDocument,
  renderApp,
  resetAppTestEnvironment,
  waitForStructuredDataReady,
  withDesktopHoverMatchMedia,
} from "../test/helpers";

vi.mock("./PdfViewer");

describe("App upload and list flow", () => {
  beforeEach(() => {
    resetAppTestEnvironment();
    installDefaultAppFetchMock();
  });

  it("renders review split grid with draggable handle", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const layoutGrid = await screen.findByTestId("document-layout-grid");
    expect(layoutGrid).toBeInTheDocument();
    expect(await screen.findByTestId("review-split-grid")).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /Redimensionar paneles de revisión/i }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Restablecer ancho de paneles/i })).toBeNull();
  }, 15000);

  it("updates split ratio on drag and persists snapped value", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const splitGrid = screen.getByTestId("review-split-grid") as HTMLDivElement;
    vi.spyOn(splitGrid, "getBoundingClientRect").mockReturnValue({
      width: 1200,
      height: 800,
      top: 0,
      left: 0,
      right: 1200,
      bottom: 800,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    } as DOMRect);

    const handle = screen.getByTestId("review-split-handle");
    fireEvent.mouseDown(handle, { clientX: 620 });
    fireEvent.mouseMove(window, { clientX: 740 });
    fireEvent.mouseUp(window);

    await waitFor(() => {
      const storedRatio = Number(window.localStorage.getItem("reviewSplitRatio"));
      expect(storedRatio).toBeGreaterThan(0.64);
      expect(storedRatio).toBeLessThan(0.65);
      expect(splitGrid.style.gridTemplateColumns).toContain(`${storedRatio}fr`);
    });
  });

  it("clamps split drag to current container width when sidebar is collapsed", async () => {
    const INITIAL_GRID_WIDTH_PX = 1380;
    const NARROW_GRID_WIDTH_PX = 1030;
    await withDesktopHoverMatchMedia(async () => {
      renderApp();

      const sidebar = await screen.findByTestId("documents-sidebar");
      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      const splitGrid = screen.getByTestId("review-split-grid") as HTMLDivElement;
      let simulatedWidth = INITIAL_GRID_WIDTH_PX;
      vi.spyOn(splitGrid, "getBoundingClientRect").mockImplementation(
        () =>
          ({
            width: simulatedWidth,
            height: 800,
            top: 0,
            left: 0,
            right: simulatedWidth,
            bottom: 800,
            x: 0,
            y: 0,
            toJSON: () => ({}),
          }) as DOMRect,
      );

      const handle = screen.getByTestId("review-split-handle");
      fireEvent.mouseDown(handle, { clientX: 640 });

      fireEvent.mouseEnter(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");
      simulatedWidth = NARROW_GRID_WIDTH_PX;

      fireEvent.mouseMove(window, { clientX: 10 });
      fireEvent.mouseUp(window);

      const expectedMinRatio = MIN_PDF_PANEL_WIDTH_PX / (simulatedWidth - SPLITTER_COLUMN_WIDTH_PX);
      await waitFor(() => {
        const storedRatio = Number(window.localStorage.getItem("reviewSplitRatio"));
        expect(storedRatio).toBeGreaterThanOrEqual(expectedMinRatio - 0.001);
      });
    });
  });

  it("re-clamps split ratio after expanding sidebar when splitter was dragged to minimum", async () => {
    const COLLAPSED_GRID_WIDTH_PX = 1380;
    const EXPANDED_GRID_WIDTH_PX = 1030;
    await withDesktopHoverMatchMedia(async () => {
      renderApp();

      const sidebar = await screen.findByTestId("documents-sidebar");
      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      const splitGrid = screen.getByTestId("review-split-grid") as HTMLDivElement;
      let simulatedWidth = COLLAPSED_GRID_WIDTH_PX;
      vi.spyOn(splitGrid, "getBoundingClientRect").mockImplementation(
        () =>
          ({
            width: simulatedWidth,
            height: 800,
            top: 0,
            left: 0,
            right: simulatedWidth,
            bottom: 800,
            x: 0,
            y: 0,
            toJSON: () => ({}),
          }) as DOMRect,
      );

      const handle = screen.getByTestId("review-split-handle");
      fireEvent.mouseDown(handle, { clientX: 640 });
      fireEvent.mouseMove(window, { clientX: 10 });
      fireEvent.mouseUp(window);

      simulatedWidth = EXPANDED_GRID_WIDTH_PX;
      fireEvent.mouseEnter(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      const expectedExpandedMinRatio =
        MIN_PDF_PANEL_WIDTH_PX / (simulatedWidth - SPLITTER_COLUMN_WIDTH_PX);
      await waitFor(() => {
        const storedRatio = Number(window.localStorage.getItem("reviewSplitRatio"));
        expect(storedRatio).toBeGreaterThanOrEqual(expectedExpandedMinRatio - 0.001);
      });
    });
  });

  it("keeps stable split bounds when expanded width is narrower than the split min width", async () => {
    const COLLAPSED_GRID_WIDTH_PX = 1380;
    const EXPANDED_GRID_WIDTH_PX = 900;
    await withDesktopHoverMatchMedia(async () => {
      renderApp();

      const sidebar = await screen.findByTestId("documents-sidebar");
      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      const splitGrid = screen.getByTestId("review-split-grid") as HTMLDivElement;
      let simulatedWidth = COLLAPSED_GRID_WIDTH_PX;
      vi.spyOn(splitGrid, "getBoundingClientRect").mockImplementation(
        () =>
          ({
            width: simulatedWidth,
            height: 800,
            top: 0,
            left: 0,
            right: simulatedWidth,
            bottom: 800,
            x: 0,
            y: 0,
            toJSON: () => ({}),
          }) as DOMRect,
      );
      Object.defineProperty(splitGrid, "scrollWidth", {
        configurable: true,
        get: () => REVIEW_SPLIT_MIN_WIDTH_PX,
      });

      const handle = screen.getByTestId("review-split-handle");
      fireEvent.mouseDown(handle, { clientX: 640 });
      fireEvent.mouseMove(window, { clientX: 10 });
      fireEvent.mouseUp(window);

      simulatedWidth = EXPANDED_GRID_WIDTH_PX;
      fireEvent.mouseEnter(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      await waitFor(() => {
        const storedRatio = Number(window.localStorage.getItem("reviewSplitRatio"));
        const expectedMinRatio =
          MIN_PDF_PANEL_WIDTH_PX / (REVIEW_SPLIT_MIN_WIDTH_PX - SPLITTER_COLUMN_WIDTH_PX);
        expect(storedRatio).toBeGreaterThanOrEqual(expectedMinRatio - 0.001);
      });
      expect(splitGrid.style.minWidth).toBe(`${REVIEW_SPLIT_MIN_WIDTH_PX}px`);
    });
  });

  it("restores default split ratio on handle double-click", async () => {
    window.localStorage.setItem("reviewSplitRatio", "0.5");
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const splitGrid = screen.getByTestId("review-split-grid") as HTMLDivElement;
    vi.spyOn(splitGrid, "getBoundingClientRect").mockReturnValue({
      width: 1200,
      height: 800,
      top: 0,
      left: 0,
      right: 1200,
      bottom: 800,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    } as DOMRect);

    const handle = screen.getByTestId("review-split-handle");
    expect(splitGrid.style.gridTemplateColumns).toContain("0.5fr");
    fireEvent.doubleClick(handle);

    await waitFor(() => {
      expect(splitGrid.style.gridTemplateColumns).toContain("0.62fr");
      expect(window.localStorage.getItem("reviewSplitRatio")).toBe("0.62");
    });
  });

  it("navigates PDF from row click without opening source drawer", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const hasInlinePdf = Boolean(screen.queryByTestId("center-panel-scroll"));
    clickPetNameField();

    expect(screen.queryByTestId("source-drawer")).toBeNull();
    const viewer = screen.getByTestId("pdf-viewer");
    expect(viewer).toHaveAttribute("data-focus-page", "1");
    expect(viewer).toHaveAttribute("data-highlight-snippet", "Paciente: Luna");
    if (hasInlinePdf) {
      expect(screen.getByTestId("center-panel-scroll")).toBeInTheDocument();
    }
  });

  it("keeps independent scroll containers and preserves right panel scroll on row clicks", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const leftPanelScroll = screen.getByTestId("left-panel-scroll");
    const centerPanelScroll = screen.getByTestId("center-panel-scroll");
    const rightPanelScroll = screen.getByTestId("right-panel-scroll");
    expect(leftPanelScroll).toBeInTheDocument();
    expect(centerPanelScroll).toBeInTheDocument();
    expect(rightPanelScroll).toBeInTheDocument();

    rightPanelScroll.scrollTop = 140;
    fireEvent.scroll(rightPanelScroll);

    clickPetNameField();

    expect(screen.getByTestId("right-panel-scroll")).toBe(rightPanelScroll);
    expect(rightPanelScroll.scrollTop).toBe(140);
  });

  it("keeps evidence behavior deterministic with tooltip fallback and row navigation", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const confidenceIndicator = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(confidenceIndicator).toHaveAttribute("aria-label", expect.stringMatching(/Página 1/i));
    expect(confidenceIndicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*\+7%/i),
    );

    clickPetNameField();
    const viewer = screen.getAllByTestId("pdf-viewer")[0];
    expect(viewer).toHaveAttribute("data-focus-page", "1");
    expect(viewer).toHaveAttribute("data-highlight-snippet", "Paciente: Luna");
    expect(screen.queryByTestId("source-drawer")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /Especie/i }));
    expect(screen.queryByText(/Sin evidencia disponible para este campo\./i)).toBeNull();
    expect(screen.queryByTestId("source-drawer")).toBeNull();
  });

  it("hides inline Fuente rows and keeps evidence details in confidence tooltip", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    expect(screen.queryByText(/^Fuente:/i)).toBeNull();
    const withEvidence = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(withEvidence).toHaveAttribute("aria-label", expect.stringMatching(/Página 1/i));
    expect(withEvidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Fiabilidad del candidato:\s*65%/i),
    );

    const withoutEvidence = screen.getByTestId("confidence-indicator-core:owner_name");
    expect(withoutEvidence).toHaveAttribute("aria-label", expect.not.stringMatching(/Página/i));
    expect(withoutEvidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*0%/i),
    );
    expect(withoutEvidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Fiabilidad del candidato:\s*No disponible/i),
    );
    const fieldTrigger = screen.getByTestId("field-trigger-core:pet_name");
    fireEvent.focus(fieldTrigger);
    await waitFor(() => {
      expect(
        Array.from(document.body.querySelectorAll("p")).some((node) =>
          /Fiabilidad del candidato:\s*65%/i.test(node.textContent ?? ""),
        ),
      ).toBe(true);
    });
    fireEvent.blur(fieldTrigger);
    expect(screen.queryByTestId("source-drawer")).toBeNull();
  });

  it("hands off tooltip visibility between field row and critical badge hover", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const fieldTrigger = screen.getByTestId("field-trigger-core:pet_name");
    const criticalIndicator = screen.getByTestId("critical-indicator-pet_name");
    const hasFieldTooltipContent = () =>
      Array.from(document.body.querySelectorAll("p")).some((node) =>
        /Fiabilidad del candidato:/i.test(node.textContent ?? ""),
      );
    const hasCriticalTooltip = () =>
      Array.from(document.body.querySelectorAll('[role="tooltip"]')).some((node) =>
        /CRÍTICO/i.test(node.textContent ?? ""),
      );

    fireEvent.mouseEnter(fieldTrigger);
    await waitFor(() => {
      expect(hasFieldTooltipContent()).toBe(true);
    });
    expect(hasCriticalTooltip()).toBe(false);

    fireEvent.mouseEnter(criticalIndicator);
    await waitFor(() => {
      expect(hasCriticalTooltip()).toBe(true);
    });
    expect(hasFieldTooltipContent()).toBe(false);

    fireEvent.mouseLeave(criticalIndicator);
    fireEvent.mouseEnter(fieldTrigger);
    await waitFor(() => {
      expect(hasFieldTooltipContent()).toBe(true);
    });
    expect(hasCriticalTooltip()).toBe(false);

    fireEvent.mouseLeave(fieldTrigger);
    await waitFor(() => {
      expect(hasFieldTooltipContent()).toBe(false);
    });
  });

  it("applies semantic styling for positive, negative and neutral adjustment values in tooltip", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();
    const findAdjustmentLine = async (pattern: RegExp): Promise<HTMLElement> => {
      let line: HTMLElement | undefined;
      await waitFor(() => {
        line = Array.from(document.body.querySelectorAll("p")).find((node) =>
          pattern.test(node.textContent ?? ""),
        ) as HTMLElement | undefined;
        expect(line).toBeDefined();
      });
      return line!;
    };
    const resolveTriggerFromIndicator = (indicator: HTMLElement): HTMLElement => {
      const fieldCard = indicator.closest("article");
      expect(fieldCard).not.toBeNull();
      const trigger = (fieldCard as HTMLElement).querySelector('[role="button"]');
      expect(trigger).not.toBeNull();
      return trigger as HTMLElement;
    };

    const positiveIndicator = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(positiveIndicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*\+7%/i),
    );
    const positive = resolveTriggerFromIndicator(positiveIndicator);
    fireEvent.focus(positive);
    const positiveLine = await findAdjustmentLine(/Ajuste por histórico de revisiones:\s*\+7%/i);
    const positiveValue = positiveLine.querySelector("span");
    expect(positiveValue).not.toBeNull();
    expect(positiveValue).toHaveClass("text-[var(--status-success)]");
    fireEvent.blur(positive);

    const negativeIndicator = screen
      .getAllByTestId(/confidence-indicator-/)
      .find((element) =>
        element.getAttribute("aria-label")?.includes("Ajuste por histórico de revisiones: -4%"),
      );
    expect(negativeIndicator).toBeDefined();
    if (!negativeIndicator) {
      throw new Error("Expected negative adjustment indicator to exist.");
    }
    expect(negativeIndicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*-4%/i),
    );
    const negative = resolveTriggerFromIndicator(negativeIndicator);
    fireEvent.focus(negative);
    const negativeLine = await findAdjustmentLine(/Ajuste por histórico de revisiones:\s*-4%/i);
    const negativeValue = negativeLine.querySelector("span");
    expect(negativeValue).not.toBeNull();
    expect(negativeValue).toHaveClass("text-[var(--status-error)]");
    fireEvent.blur(negative);

    const neutralIndicator = screen.getByTestId("confidence-indicator-core:owner_name");
    expect(neutralIndicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*0%/i),
    );
    const neutral = resolveTriggerFromIndicator(neutralIndicator);
    fireEvent.focus(neutral);
    const neutralLine = await findAdjustmentLine(/Ajuste por histórico de revisiones:\s*0%/i);
    const neutralValue = neutralLine.querySelector("span");
    expect(neutralValue).not.toBeNull();
    expect(neutralValue).toHaveClass("text-muted");
  });

  it("synchronizes selected field with viewer context repeatedly, including repeated same-field clicks", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    fireEvent.click(screen.getByRole("button", { name: /Gastroenteritis/i }));
    let viewer = screen.getByTestId("pdf-viewer");
    expect(viewer).toHaveAttribute("data-focus-page", "2");
    expect(viewer).toHaveAttribute("data-highlight-snippet", "Diagnostico: Gastroenteritis");
    const firstRequestId = Number(viewer.getAttribute("data-focus-request-id"));

    clickPetNameField();
    viewer = screen.getByTestId("pdf-viewer");
    expect(viewer).toHaveAttribute("data-focus-page", "1");
    expect(viewer).toHaveAttribute("data-highlight-snippet", "Paciente: Luna");
    const secondRequestId = Number(viewer.getAttribute("data-focus-request-id"));
    expect(secondRequestId).toBeGreaterThan(firstRequestId);

    clickPetNameField();
    viewer = screen.getByTestId("pdf-viewer");
    const thirdRequestId = Number(viewer.getAttribute("data-focus-request-id"));
    expect(thirdRequestId).toBeGreaterThan(secondRequestId);
    expect(screen.queryByTestId("source-drawer")).toBeNull();
  });

  it("keeps source drawer closed on plain field click", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    clickPetNameField();
    expect(screen.queryByTestId("source-drawer")).toBeNull();
  });

  it("shows destructive blocked-edit toast on first reviewed-mode click", async () => {
    installReviewedModeFetchMock();
    renderApp();

    await openReviewedDocument();
    fireEvent.click(screen.getByRole("button", { name: /Marcar revisado/i }));
    await screen.findByRole("button", { name: /^Reabrir$/i });
    expect(getPetNameFieldButton()).toHaveAttribute("aria-disabled", "true");

    fireEvent.mouseUp(getPetNameFieldButton(), { button: 0 });

    const status = await screen.findByRole("alert");
    expect(status).toHaveTextContent("Documento revisado: edición bloqueada.");
    expect(status).toHaveClass("border-statusError", "text-statusError");
  });

  it("does not show blocked-edit toast while selecting text in reviewed mode", async () => {
    installReviewedModeFetchMock();
    const getSelectionSpy = vi
      .spyOn(window, "getSelection")
      .mockReturnValue({ toString: () => "Luna" } as unknown as Selection);

    renderApp();
    await openReviewedDocument();

    fireEvent.click(screen.getByRole("button", { name: /Marcar revisado/i }));
    await screen.findByRole("button", { name: /^Reabrir$/i });
    fireEvent.click(screen.getByLabelText(/Cerrar notificación de acción/i));

    fireEvent.mouseUp(getPetNameFieldButton(), { button: 0 });

    expect(screen.queryByText(/Documento revisado: edición bloqueada\./i)).toBeNull();
    getSelectionSpy.mockRestore();
  });

  it("renders reviewed warning banner with amber border styling", async () => {
    installReviewedModeFetchMock();
    renderApp();

    await openReviewedDocument();
    fireEvent.click(screen.getByRole("button", { name: /Marcar revisado/i }));

    const bannerText = await screen.findByText(/Los datos están en modo de solo lectura\./i);
    const banner = bannerText.closest("p");
    expect(banner).not.toBeNull();
    expect(banner).toHaveClass("border", "border-statusWarn", "bg-surface", "text-text");
  });

  it("toggles reviewed action visual state and supports keyboard blocked-edit feedback", async () => {
    installReviewedModeFetchMock();
    renderApp();

    await openReviewedDocument();

    const markButton = screen.getByRole("button", { name: /Marcar revisado/i });
    expect(markButton).toHaveClass("bg-accent", "text-accentForeground");
    fireEvent.click(markButton);

    const reopenButton = await screen.findByRole("button", { name: /^Reabrir$/i });
    expect(reopenButton).toHaveClass("border", "bg-surface", "text-text");

    fireEvent.keyDown(getPetNameFieldButton(), { key: "Enter" });
    await screen.findByText(/Documento revisado: edición bloqueada\./i);

    fireEvent.click(reopenButton);
    await screen.findByRole("button", { name: /Marcar revisado/i });
  });
});
