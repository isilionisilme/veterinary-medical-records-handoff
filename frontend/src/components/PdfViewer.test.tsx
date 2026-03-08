import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { waitFor } from "@testing-library/react";
import * as pdfjsLib from "pdfjs-dist";

import { PdfViewer } from "./PdfViewer";

vi.mock("pdfjs-dist/build/pdf.worker.mjs?url", () => ({
  default: "pdf-worker",
}));

let mockDoc: {
  numPages: number;
  getPage: (pageNumber: number) => Promise<{
    getViewport: ({ scale }: { scale: number }) => { width: number; height: number };
    render: () => { promise: Promise<void> };
    getTextContent: () => Promise<{ items: Array<{ str: string }> }>;
  }>;
};

vi.mock("pdfjs-dist", () => {
  return {
    GlobalWorkerOptions: { workerSrc: "" },
    getDocument: vi.fn(() => ({
      promise: Promise.resolve(mockDoc),
    })),
  };
});

let lastObserver: MockIntersectionObserver | null = null;

class MockIntersectionObserver {
  private readonly callback: IntersectionObserverCallback;
  private readonly elements: Element[] = [];

  constructor(callback: IntersectionObserverCallback) {
    this.callback = callback;
    lastObserver = this;
  }

  observe(target: Element) {
    this.elements.push(target);
  }

  unobserve() {}

  disconnect() {}

  trigger(entries: IntersectionObserverEntry[]) {
    this.callback(entries, this as unknown as IntersectionObserver);
  }
}

describe("PdfViewer", () => {
  beforeEach(() => {
    window.localStorage.clear();
    const renderCallsByPage = new Map<number, number>();

    mockDoc = {
      numPages: 3,
      getPage: vi.fn(async (pageNumber: number) => ({
        getViewport: () => ({ width: 600, height: 800 }),
        render: () => {
          renderCallsByPage.set(pageNumber, (renderCallsByPage.get(pageNumber) ?? 0) + 1);
          return { promise: Promise.resolve() };
        },
        getTextContent: async () => ({ items: [{ str: `Pagina ${pageNumber}` }] }),
      })),
    };
    lastObserver = null;
    globalThis.IntersectionObserver =
      MockIntersectionObserver as unknown as typeof IntersectionObserver;
    Object.defineProperty(HTMLElement.prototype, "scrollTo", {
      configurable: true,
      writable: true,
      value: vi.fn(),
    });
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      arrayBuffer: async () => new Uint8Array([0x25, 0x50, 0x44, 0x46]).buffer,
    } as Response);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sets GlobalWorkerOptions.workerSrc at module level", () => {
    // pdfjs-dist v4 requires workerSrc before any getDocument() call.
    // Without it, PDFWorker.workerSrc getter throws synchronously and
    // the PDF silently fails to render. This guard catches regressions
    // if the import or assignment is accidentally removed.
    expect(pdfjsLib.GlobalWorkerOptions.workerSrc).toBeTruthy();
  });

  it("renders all pages in a continuous scroll", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    const pages = await screen.findAllByTestId("pdf-page");
    expect(screen.getByTestId("pdf-toolbar-shell")).toHaveClass("panel-shell");
    expect(pages).toHaveLength(3);
    await waitFor(() => {
      expect(mockDoc.getPage).toHaveBeenCalledWith(2);
    });
  });

  it("scrolls to next and previous pages on button click", async () => {
    const windowScrollSpy = vi.spyOn(window, "scrollTo").mockImplementation(() => undefined);

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    const pages = await screen.findAllByTestId("pdf-page");
    const container = screen.getByTestId("pdf-scroll-container");
    const containerScrollTo = vi.fn();
    (container as HTMLElement & { scrollTo: typeof container.scrollTo }).scrollTo =
      containerScrollTo;
    Object.defineProperty(container, "scrollTop", { value: 10, writable: true });
    vi.spyOn(container, "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 100,
      top: 100,
      left: 0,
      right: 600,
      bottom: 800,
      width: 600,
      height: 700,
      toJSON: () => "",
    });
    vi.spyOn(pages[1], "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 500,
      top: 500,
      left: 0,
      right: 600,
      bottom: 1300,
      width: 600,
      height: 800,
      toJSON: () => "",
    });

    const [nextButton] = screen.getAllByRole("button", { name: /Página siguiente/i });
    await waitFor(() => {
      expect(nextButton).not.toBeDisabled();
    });
    fireEvent.click(nextButton);

    expect(containerScrollTo).toHaveBeenCalledWith({ top: 410, behavior: "smooth" });
    expect(windowScrollSpy).not.toHaveBeenCalled();
    expect(screen.getByText("2/3")).toBeInTheDocument();

    const [prevButton] = screen.getAllByRole("button", { name: /Página anterior/i });
    await waitFor(() => {
      expect(prevButton).not.toBeDisabled();
    });
    fireEvent.click(prevButton);
    expect(containerScrollTo).toHaveBeenCalledTimes(2);
    expect(windowScrollSpy).not.toHaveBeenCalled();
    expect(screen.getByText("1/3")).toBeInTheDocument();
  });

  it("updates the active page based on scroll position", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    const pages = await screen.findAllByTestId("pdf-page");
    expect(lastObserver).not.toBeNull();

    act(() => {
      lastObserver?.trigger([
        {
          target: pages[2],
          intersectionRatio: 0.8,
          isIntersecting: true,
        } as unknown as IntersectionObserverEntry,
      ]);
    });

    expect(screen.getByText("3/3")).toBeInTheDocument();
  });

  it("disables Next on the last page (bounds)", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    const pages = await screen.findAllByTestId("pdf-page");
    expect(lastObserver).not.toBeNull();

    act(() => {
      lastObserver?.trigger([
        {
          target: pages[2],
          intersectionRatio: 0.9,
          isIntersecting: true,
        } as unknown as IntersectionObserverEntry,
      ]);
    });

    await waitFor(() => {
      expect(screen.getByText("3/3")).toBeInTheDocument();
    });

    const [nextButton] = screen.getAllByRole("button", { name: /Página siguiente/i });
    expect(nextButton).toBeDisabled();
  });

  it("hides page navigation when no document is selected", () => {
    render(<PdfViewer fileUrl={null} filename={null} />);

    expect(screen.queryByRole("button", { name: /Página siguiente/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /Página anterior/i })).toBeNull();
  });

  it("shows zoom controls next to pagination and updates zoom indicator", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    await screen.findAllByTestId("pdf-page");

    const zoomOut = screen.getByRole("button", { name: /Alejar/i });
    const zoomIn = screen.getByRole("button", { name: /Acercar/i });
    const fitWidth = screen.getByRole("button", { name: /Ajustar al ancho/i });
    const indicator = screen.getByTestId("pdf-zoom-indicator");

    expect(zoomOut).toBeInTheDocument();
    expect(zoomIn).toBeInTheDocument();
    expect(fitWidth).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Restablecer zoom/i })).toBeNull();
    expect(indicator).toHaveTextContent("100%");

    fireEvent.mouseEnter(zoomIn);
    expect(screen.getByRole("tooltip")).toHaveTextContent("Acercar");
    fireEvent.mouseLeave(zoomIn);

    fireEvent.click(zoomIn);
    expect(indicator).toHaveTextContent("110%");
    expect(window.localStorage.getItem("pdfViewerZoomLevel")).toBe("1.1");

    fireEvent.click(zoomOut);
    expect(indicator).toHaveTextContent("100%");

    fireEvent.click(zoomIn);
    expect(indicator).toHaveTextContent("110%");
    fireEvent.click(fitWidth);
    expect(indicator).toHaveTextContent("100%");
  });

  it("applies Ctrl+wheel zoom only inside viewer", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    await screen.findAllByTestId("pdf-page");
    const container = screen.getByTestId("pdf-scroll-container");
    const indicator = screen.getByTestId("pdf-zoom-indicator");

    const plainWheel = new WheelEvent("wheel", {
      deltaY: -120,
      ctrlKey: false,
      cancelable: true,
      bubbles: true,
    });
    act(() => {
      container.dispatchEvent(plainWheel);
    });
    expect(plainWheel.defaultPrevented).toBe(false);
    expect(indicator).toHaveTextContent("100%");

    const ctrlWheelIn = new WheelEvent("wheel", {
      deltaY: -120,
      ctrlKey: true,
      cancelable: true,
      bubbles: true,
    });
    act(() => {
      container.dispatchEvent(ctrlWheelIn);
    });
    expect(ctrlWheelIn.defaultPrevented).toBe(true);
    await waitFor(() => {
      expect(indicator).toHaveTextContent("110%");
    });

    const ctrlWheelOut = new WheelEvent("wheel", {
      deltaY: 120,
      ctrlKey: true,
      cancelable: true,
      bubbles: true,
    });
    act(() => {
      container.dispatchEvent(ctrlWheelOut);
    });
    expect(ctrlWheelOut.defaultPrevented).toBe(true);
    await waitFor(() => {
      expect(indicator).toHaveTextContent("100%");
    });
  });

  it("restores persisted zoom level", async () => {
    window.localStorage.setItem("pdfViewerZoomLevel", "1.3");
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    await screen.findAllByTestId("pdf-page");
    expect(screen.getByTestId("pdf-zoom-indicator")).toHaveTextContent("130%");
  });

  it("loads PDF from fetched data source with eval disabled", async () => {
    const getDocumentMock = vi.mocked(pdfjsLib.getDocument);
    getDocumentMock.mockReset();
    getDocumentMock.mockImplementationOnce(() => ({
      promise: Promise.resolve(mockDoc),
    }));

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    await screen.findAllByTestId("pdf-page");

    expect(globalThis.fetch).toHaveBeenCalledWith("blob://sample", { cache: "no-store" });
    const firstCall = getDocumentMock.mock.calls[0]?.[0] as { data?: Uint8Array };
    expect(firstCall).toMatchObject({
      isEvalSupported: false,
    });
    expect(firstCall).not.toHaveProperty("disableWorker");
    expect(firstCall.data).toBeInstanceOf(Uint8Array);
    expect(screen.queryByText("No pudimos cargar el PDF.")).toBeNull();
  });

  it("loads PDF directly from ArrayBuffer without fetching", async () => {
    const getDocumentMock = vi.mocked(pdfjsLib.getDocument);
    getDocumentMock.mockReset();
    getDocumentMock.mockImplementationOnce(() => ({
      promise: Promise.resolve(mockDoc),
    }));
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const pdfBytes = new Uint8Array([0x25, 0x50, 0x44, 0x46]).buffer;

    render(<PdfViewer fileUrl={pdfBytes} filename="record.pdf" />);

    await screen.findAllByTestId("pdf-page");

    expect(fetchSpy).not.toHaveBeenCalled();
    const firstCall = getDocumentMock.mock.calls[0]?.[0] as { data?: Uint8Array };
    expect(firstCall).toMatchObject({
      isEvalSupported: false,
    });
    expect(firstCall).not.toHaveProperty("disableWorker");
    expect(firstCall.data).toBeInstanceOf(Uint8Array);
    expect(firstCall.data?.byteLength).toBe(4);
  });

  it("shows loading state while document promise is pending", async () => {
    const getDocumentMock = vi.mocked(pdfjsLib.getDocument);
    getDocumentMock.mockReset();

    let resolveDoc: ((value: typeof mockDoc) => void) | null = null;
    const pendingPromise = new Promise<typeof mockDoc>((resolve) => {
      resolveDoc = resolve;
    });

    getDocumentMock.mockImplementation(() => ({
      promise: pendingPromise,
    }));

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    expect(screen.getByText("Cargando PDF...")).toBeInTheDocument();

    resolveDoc?.(mockDoc);
    await screen.findAllByTestId("pdf-page");
    expect(screen.queryByText("Cargando PDF...")).toBeNull();
  });

  it("shows error state when data-source load fails", async () => {
    const getDocumentMock = vi.mocked(pdfjsLib.getDocument);
    getDocumentMock.mockReset();
    getDocumentMock.mockImplementation(() => ({
      promise: Promise.reject(new Error("data load failed")),
    }));

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    expect(await screen.findByText("No pudimos cargar el PDF.")).toBeInTheDocument();
  });

  it("shows error state when blob fetch fails", async () => {
    const getDocumentMock = vi.mocked(pdfjsLib.getDocument);
    getDocumentMock.mockReset();
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      arrayBuffer: async () => new ArrayBuffer(0),
    } as Response);

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    expect(await screen.findByText("No pudimos cargar el PDF.")).toBeInTheDocument();
    expect(getDocumentMock).not.toHaveBeenCalled();
  });

  it("renders drag overlay when upload drag state is active", async () => {
    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" isDragOver />);

    await screen.findAllByTestId("pdf-page");
    expect(screen.getByText("Suelta el PDF para subirlo")).toBeInTheDocument();
  });

  it("applies focus page targeting when focus request changes", async () => {
    render(
      <PdfViewer
        fileUrl="blob://sample"
        filename="record.pdf"
        focusPage={2}
        focusRequestId={1}
        highlightSnippet="Pagina 2"
      />,
    );

    const pages = await screen.findAllByTestId("pdf-page");
    const container = screen.getByTestId("pdf-scroll-container");
    Object.defineProperty(container, "scrollTop", { value: 30, writable: true });
    vi.spyOn(container, "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 100,
      top: 100,
      left: 0,
      right: 600,
      bottom: 800,
      width: 600,
      height: 700,
      toJSON: () => "",
    });
    vi.spyOn(pages[1], "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 500,
      top: 500,
      left: 0,
      right: 600,
      bottom: 1300,
      width: 600,
      height: 800,
      toJSON: () => "",
    });

    await waitFor(() => {
      expect(screen.getByText("2/3")).toBeInTheDocument();
    });
  });

  it("enables debug mode from storage flag", async () => {
    vi.stubEnv("VITE_DEBUG_PDF_VIEWER", "true");
    window.localStorage.setItem("pdfDebug", "1");

    render(<PdfViewer fileUrl="blob://sample" filename="record.pdf" />);

    await screen.findByTestId("pdf-scroll-container");
    expect(
      screen.getByTestId("pdf-scroll-container").closest("[data-pdf-debug='on']"),
    ).toBeTruthy();

    vi.unstubAllEnvs();
  });
});
