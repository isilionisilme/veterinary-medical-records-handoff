import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  createDataTransfer,
  installDefaultAppFetchMock,
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

  afterEach(() => {
    vi.useRealTimers();
  });

  it("uploads a document, shows toast and auto-opens the uploaded document", async () => {
    renderApp();

    const input = screen.getByLabelText(/Archivo PDF/i);
    const file = new File(["pdf"], "nuevo.pdf", { type: "application/pdf" });
    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    expect(await screen.findByText(/Documento subido correctamente/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Ver documento/i })).toBeNull();

    await waitFor(() => {
      const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
      expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(true);
      expect(calls.some(([url]) => String(url).includes("/documents/doc-new/download"))).toBe(true);
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /nuevo\.pdf/i })).toHaveAttribute(
        "aria-pressed",
        "true",
      );
    });
  });

  it("shows fallback open action only when auto-open fails", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-new",
                original_filename: "nuevo.pdf",
                created_at: "2026-02-10T10:00:00Z",
                status: "COMPLETED",
                status_label: "Completed",
                failure_type: null,
              },
            ],
            limit: 50,
            offset: 0,
            total: 1,
          }),
          { status: 200 },
        );
      }

      if (url.endsWith("/documents/upload") && method === "POST") {
        return new Response(
          JSON.stringify({
            document_id: "doc-new",
            status: "COMPLETED",
            created_at: "2026-02-10T10:00:00Z",
          }),
          { status: 201 },
        );
      }

      if (url.includes("/documents/doc-new/download") && method === "GET") {
        return new Response(JSON.stringify({ message: "Not ready" }), { status: 404 });
      }

      if (url.match(/\/documents\/[^/]+$/) && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-new",
            original_filename: "nuevo.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-10T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: "COMPLETED",
            status_message: "Completed",
            failure_type: null,
            latest_run: { run_id: "run-doc-new", state: "COMPLETED", failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-new", runs: [] }), { status: 200 });
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    const input = screen.getByLabelText(/Archivo PDF/i);
    const file = new File(["pdf"], "nuevo.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(await screen.findByText(/Documento subido correctamente/i)).toBeInTheDocument();

    await waitFor(
      () => {
        expect(screen.getByRole("button", { name: /Ver documento/i })).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  it("auto-dismisses upload toast", async () => {
    vi.useFakeTimers();
    renderApp();

    const input = screen.getByLabelText(/Archivo PDF/i);
    const file = new File(["pdf"], "nuevo.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [file] } });

    await act(async () => {
      await vi.runOnlyPendingTimersAsync();
    });
    expect(screen.getByText(/Documento subido correctamente/i)).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(3600);
      await vi.runOnlyPendingTimersAsync();
    });
    expect(screen.queryByText(/Documento subido correctamente/i)).toBeNull();
  });

  it("shows a clear error when selected file exceeds 20 MB", async () => {
    vi.useFakeTimers();
    renderApp();

    const input = screen.getByLabelText(/Archivo PDF/i);
    const oversizedFile = new File([new Uint8Array(20 * 1024 * 1024 + 1)], "grande.pdf", {
      type: "application/pdf",
    });
    fireEvent.change(input, { target: { files: [oversizedFile] } });

    expect(screen.getByText(/El archivo supera el tamaño máximo \(20 MB\)\./i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Reintentar/i })).toBeNull();

    await act(async () => {
      vi.advanceTimersByTime(5200);
      await vi.runOnlyPendingTimersAsync();
    });
    expect(screen.queryByText(/El archivo supera el tamaño máximo \(20 MB\)\./i)).toBeNull();
  });

  it("uploads from collapsed sidebar dropzone without auto-expanding", async () => {
    await withDesktopHoverMatchMedia(async () => {
      renderApp();
      const sidebar = await screen.findByTestId("documents-sidebar");

      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      const dropzoneContainer = screen.getByTestId("sidebar-collapsed-dropzone");
      const dropzone = within(dropzoneContainer).getByRole("button");
      const file = new File(["pdf"], "rail-upload.pdf", { type: "application/pdf" });
      const dataTransfer = createDataTransfer(file);

      fireEvent.dragEnter(dropzone, { dataTransfer });
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      fireEvent.drop(dropzone, { dataTransfer });
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      await waitFor(() => {
        const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
        expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(true);
      });
    });
  });

  it("supports drag and drop upload from the viewer empty state", async () => {
    renderApp();

    const emptyState = screen.getByTestId("viewer-empty-state");
    const file = new File(["pdf"], "dragged.pdf", { type: "application/pdf" });
    const dataTransfer = createDataTransfer(file);

    fireEvent.dragEnter(emptyState, { dataTransfer });
    expect(screen.getByText(/Suelta el PDF para subirlo/i)).toBeInTheDocument();

    fireEvent.drop(emptyState, { dataTransfer });

    expect(await screen.findByText(/Documento subido correctamente/i)).toBeInTheDocument();

    await waitFor(() => {
      const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
      expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(true);
      expect(calls.some(([url]) => String(url).includes("/documents/doc-new/download"))).toBe(true);
    });
  });

  it("opens the file picker when clicking anywhere in empty viewer", async () => {
    renderApp();

    const input = screen.getByLabelText(/Archivo PDF/i) as HTMLInputElement;
    const clickSpy = vi.spyOn(input, "click");

    fireEvent.click(screen.getByTestId("viewer-empty-state"));

    expect(clickSpy).toHaveBeenCalledTimes(1);
  });

  it("supports drag and drop upload when a document is already open", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitFor(() => {
      expect(screen.getByTestId("center-panel-scroll")).toBeInTheDocument();
    });

    const dropzone = screen.getByTestId("viewer-dropzone");
    const file = new File(["pdf"], "dragged-open.pdf", { type: "application/pdf" });
    const dataTransfer = createDataTransfer(file);

    fireEvent.dragEnter(dropzone, { dataTransfer });
    fireEvent.drop(dropzone, { dataTransfer });
    expect(await screen.findByText(/Documento subido correctamente/i)).toBeInTheDocument();

    await waitFor(() => {
      const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
      expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(true);
      expect(calls.some(([url]) => String(url).includes("/documents/doc-new/download"))).toBe(true);
    });
  });

  it("shows validation error when dropping a non-PDF file", async () => {
    renderApp();

    const emptyState = screen.getByTestId("viewer-empty-state");
    const file = new File(["text"], "notes.txt", { type: "text/plain" });
    const dataTransfer = createDataTransfer(file);

    fireEvent.drop(emptyState, { dataTransfer });

    expect(await screen.findByText(/Solo se admiten archivos PDF\./i)).toBeInTheDocument();

    const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
    expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(false);
  });

  it("shows size validation error when dropping a PDF over 20 MB", async () => {
    renderApp();

    const emptyState = screen.getByTestId("viewer-empty-state");
    const file = new File([new Uint8Array(20 * 1024 * 1024 + 1)], "huge.pdf", {
      type: "application/pdf",
    });
    const dataTransfer = createDataTransfer(file);

    fireEvent.drop(emptyState, { dataTransfer });

    expect(
      await screen.findByText(/El archivo supera el tamaño máximo \(20 MB\)\./i),
    ).toBeInTheDocument();

    const calls = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls;
    expect(calls.some(([url]) => String(url).includes("/documents/upload"))).toBe(false);
  });
});
