import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  installDefaultAppFetchMock,
  renderApp,
  resetAppTestEnvironment,
  waitForStructuredDataReady,
} from "./test/helpers";

vi.mock("./components/PdfViewer");

describe("App upload and list flow", () => {
  beforeEach(() => {
    resetAppTestEnvironment();
    installDefaultAppFetchMock();
  });

  it("removes the old no-document error block and exposes list control in viewer header", () => {
    renderApp();
    expect(screen.queryByText(/Documento no encontrado o falta ID/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /Volver a la lista/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /Documentos cargados/i })).toBeNull();
    expect(
      screen.getByText(/Selecciona un documento en la barra lateral o carga uno nuevo\./i),
    ).toBeInTheDocument();
    expect(screen.getAllByText(/Arrastra un PDF aquí/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/o haz clic para cargar/i).length).toBeGreaterThan(0);
    expect(screen.queryByText(/Formatos permitidos: PDF\./i)).toBeNull();
    expect(screen.queryByText(/\(\.pdf \/ application\/pdf\)/i)).toBeNull();
    expect(screen.queryByText(/Tamaño máximo: 20 MB\./i)).toBeNull();
    expect(screen.getByLabelText(/Información de formatos y tamaño/i)).toBeInTheDocument();
    expect(screen.queryByText(/Selecciona un PDF/i)).toBeNull();
  });

  it("keeps browse defaults when there are no documents and opens upload from CTA", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(JSON.stringify({ items: [], limit: 50, offset: 0, total: 0 }), {
          status: 200,
        });
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    expect(await screen.findByText(/Aún no hay documentos cargados\./i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Cargar documento/i })).toBeInTheDocument();
    expect(
      screen.getByText(/Selecciona un documento en la barra lateral o carga uno nuevo\./i),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("view-mode-toggle")).toBeNull();
    expect(screen.queryByTestId("review-docs-handle")).toBeNull();

    const emptyViewer = screen.getByTestId("viewer-empty-state");
    fireEvent.click(emptyViewer);

    await waitFor(() => {
      expect(screen.getByTestId("viewer-empty-state")).toBeInTheDocument();
    });
  });

  it("does not show select-or-upload empty state when document list fetch fails", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        throw new TypeError("Failed to fetch");
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    await screen.findByText(/No se pudo conectar con el servidor\./i);
    expect(screen.getByText(/No se pudo conectar con el servidor\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Sin conexión/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /Reintentar/i })).toBeNull();
    expect(
      screen.getByText(/Revisa la lista lateral para reintentar la carga de documentos\./i),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Selecciona un documento en la barra lateral o carga uno nuevo\./i),
    ).toBeNull();
    expect(screen.queryByText(/Failed to fetch/i)).toBeNull();
    expect(screen.queryByText(/No se pudieron cargar los documentos\./i)).toBeNull();
  });

  it("keeps browse mode with docs, pdf, and structured columns after selecting a document", async () => {
    renderApp();

    await screen.findByRole("button", { name: /ready\.pdf/i });
    fireEvent.click(screen.getByRole("button", { name: /ready\.pdf/i }));

    await waitFor(() => {
      expect(screen.getByTestId("left-panel-scroll")).toBeInTheDocument();
      expect(screen.getByTestId("center-panel-scroll")).toBeInTheDocument();
      expect(screen.getByTestId("right-panel-scroll")).toBeInTheDocument();
      expect(screen.queryByTestId("view-mode-toggle")).toBeNull();
      expect(screen.queryByText(/Vista Docs · PDF · Datos/i)).toBeNull();
    });
  });

  it("uses a unified layout without mode controls or breadcrumb", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    expect(screen.getByTestId("canvas-wrapper")).toHaveClass("p-[var(--canvas-gap)]");
    expect(screen.getByTestId("main-canvas-layout")).toHaveClass("gap-[var(--canvas-gap)]");
    expect(screen.getByTestId("docs-column-stack")).toHaveClass("gap-[var(--canvas-gap)]");
    expect(screen.getByTestId("docs-column-stack")).toHaveClass("p-[var(--canvas-gap)]");
    expect(screen.getByTestId("center-panel-scroll")).toHaveClass("gap-[var(--canvas-gap)]");
    expect(screen.getByTestId("center-panel-scroll")).toHaveClass("p-[var(--canvas-gap)]");
    expect(screen.getByTestId("structured-column-stack")).toHaveClass("gap-[var(--canvas-gap)]");
    expect(screen.getByTestId("structured-column-stack")).toHaveClass("p-[var(--canvas-gap)]");
    const leftScroll = screen.getByTestId("left-panel-scroll");
    expect(leftScroll).toBeInTheDocument();
    expect(screen.getByTestId("center-panel-scroll")).toBeInTheDocument();
    expect(screen.getByTestId("right-panel-scroll")).toBeInTheDocument();
    expect(screen.getByTestId("documents-sidebar").firstElementChild).toHaveClass(
      "panel-shell-muted",
    );
    expect(screen.getByTestId("center-panel-scroll")).toHaveClass("panel-shell-muted");
    expect(screen.getByRole("heading", { name: /Datos extraídos/i }).closest("aside")).toHaveClass(
      "panel-shell-muted",
    );
    expect(screen.getByTestId("structured-search-shell")).toHaveClass("panel-shell");
    const firstDocumentRow = screen.getByTestId("doc-row-doc-ready");
    expect(firstDocumentRow).toHaveClass("bg-surfaceMuted");
    expect(firstDocumentRow).toHaveClass("rounded-card");
    expect(firstDocumentRow).toHaveClass("shadow-subtle");
    const hoverableDocumentRow = screen.getByTestId("doc-row-doc-processing");
    expect(hoverableDocumentRow).toHaveClass("hover:bg-surfaceMuted");
    const searchInput = screen.getByRole("textbox", { name: /Buscar en datos extraídos/i });
    expect(searchInput).toHaveClass("border");
    expect(searchInput).toHaveClass("bg-surface");
    expect(screen.queryByTestId("view-mode-toggle")).toBeNull();
    expect(screen.queryByText(/Modo exploración/i)).toBeNull();
    expect(screen.queryByText(/Modo revisión/i)).toBeNull();
    expect(screen.queryByText(/Vista Docs · PDF · Datos/i)).toBeNull();
  });

  it("keeps docs sidebar available in unified layout", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    expect(screen.getByTestId("documents-sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("left-panel-scroll")).toBeInTheDocument();
    expect(screen.getByTestId("right-panel-scroll")).toBeInTheDocument();
    expect(screen.getByTestId("center-panel-scroll")).toBeInTheDocument();
  });
});
