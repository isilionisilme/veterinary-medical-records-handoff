import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
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

  it("shows required list status labels", async () => {
    renderApp();
    expect(await screen.findByText("Procesando")).toBeInTheDocument();
    expect(screen.getByText("Listo")).toBeInTheDocument();
    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Tardando más de lo esperado")).toBeInTheDocument();
  });

  it("updates PROCESSING to Listo after refresh", async () => {
    const fetchMock = globalThis.fetch as unknown as ReturnType<typeof vi.fn>;
    const processingDoc = {
      document_id: "doc-transition",
      original_filename: "transition.pdf",
      created_at: "2026-02-10T10:00:00Z",
      status: "PROCESSING",
      status_label: "Processing",
      failure_type: null,
    };

    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({ items: [processingDoc], limit: 50, offset: 0, total: 1 }),
          { status: 200 },
        );
      }
      if (url.includes("/download")) {
        return new Response(new Blob(["pdf"], { type: "application/pdf" }), { status: 200 });
      }
      if (url.match(/\/documents\/[^/]+$/) && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-transition",
            original_filename: "transition.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-10T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: processingDoc.status,
            status_message: "state",
            failure_type: null,
            latest_run: {
              run_id: "run-transition",
              state: processingDoc.status,
              failure_type: null,
            },
          }),
          { status: 200 },
        );
      }
      if (url.includes("/processing-history")) {
        return new Response(JSON.stringify({ document_id: "doc-transition", runs: [] }), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    });

    renderApp();
    await screen.findByText("Procesando");

    expect(
      within(screen.getByRole("button", { name: /transition\.pdf/i })).getByText("Procesando"),
    ).toBeInTheDocument();

    processingDoc.status = "COMPLETED";
    fireEvent.click(screen.getByRole("button", { name: /Actualizar/i }));

    await waitFor(() => {
      expect(
        within(screen.getByRole("button", { name: /transition\.pdf/i })).getByText("Listo"),
      ).toBeInTheDocument();
    });
  });

  it("shows branding and actions inside expanded sidebar and no global brand header", async () => {
    renderApp();

    const sidebar = await screen.findByTestId("documents-sidebar");
    expect(sidebar).toHaveAttribute("data-expanded", "true");
    expect(screen.getByText("Barkibu")).toBeInTheDocument();
    expect(screen.getByText("Revisión de reembolsos")).toBeInTheDocument();
    expect(screen.queryByTestId("header-cluster-row")).toBeNull();

    const actionsCluster = screen.getByTestId("sidebar-actions-cluster");
    const refreshButton = within(actionsCluster).getByRole("button", { name: /Actualizar/i });
    expect(refreshButton).toBeInTheDocument();
    expect(refreshButton).toHaveClass("border");
    expect(refreshButton).toHaveClass("bg-surface");
    const pinButton = within(actionsCluster).getByRole("button", {
      name: /(Fijar|Fijada)/i,
    });
    expect(pinButton).toBeInTheDocument();
    expect(pinButton).toHaveClass("border");
    expect(pinButton).toHaveClass("bg-surface");
  });

  it("auto-collapses docs sidebar on desktop after selecting a document and expands on hover", async () => {
    await withDesktopHoverMatchMedia(async () => {
      renderApp();

      const sidebar = await screen.findByTestId("documents-sidebar");
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();

      expect(sidebar).toHaveAttribute("data-expanded", "false");
      expect(sidebar.className).toContain("w-16");
      expect(screen.queryByRole("button", { name: /Actualizar/i })).toBeNull();
      expect(screen.getByTestId("sidebar-collapsed-brand-mark")).toBeInTheDocument();
      const leftRailScroll = screen.getByTestId("left-panel-scroll");
      expect(leftRailScroll.className).toContain("[scrollbar-width:none]");

      fireEvent.mouseEnter(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");
      expect(screen.getByRole("button", { name: /Actualizar/i })).toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: /processing\.pdf/i }));
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      fireEvent.click(screen.getByRole("button", { name: /failed\.pdf/i }));
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      fireEvent.mouseLeave(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      const collapsedReadyItem = screen.getByRole("button", {
        name: /ready\.pdf\s*\(Listo\)/i,
      });
      expect(collapsedReadyItem).toBeInTheDocument();
      expect(collapsedReadyItem).toHaveAttribute("data-testid", "doc-row-doc-ready");
      const collapsedSelectedItem = screen
        .getAllByRole("button", { name: /\.pdf/i })
        .find((button) => button.getAttribute("aria-pressed") === "true");
      expect(collapsedSelectedItem).toBeTruthy();
      const collapsedIcon = collapsedSelectedItem?.querySelector("svg");
      expect(collapsedIcon?.parentElement).toHaveClass("rounded-full");
      expect(collapsedIcon?.parentElement).toHaveClass("bg-surface");
      expect(collapsedIcon?.parentElement).toHaveClass("border");
      expect(collapsedIcon?.parentElement).toHaveClass("border-transparent");
      expect(collapsedIcon?.parentElement).toHaveClass("ring-1");
      expect(collapsedIcon?.parentElement).toHaveClass("ring-borderSubtle");
      const statusDot = collapsedReadyItem.querySelector('span[aria-hidden="true"]');
      expect(statusDot).toBeTruthy();
      expect(statusDot?.className).toContain("ring-2");

      fireEvent.click(collapsedReadyItem);
      expect(sidebar).toHaveAttribute("data-expanded", "false");
    });
  }, 10000);

  it("keeps sidebar open on mouse leave when pinned, and collapses again after unpin", async () => {
    await withDesktopHoverMatchMedia(async () => {
      renderApp();
      const sidebar = await screen.findByTestId("documents-sidebar");

      fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
      await waitForStructuredDataReady();
      expect(sidebar).toHaveAttribute("data-expanded", "false");

      fireEvent.mouseEnter(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      fireEvent.click(screen.getByRole("button", { name: /Fijar/i }));
      fireEvent.mouseLeave(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "true");

      fireEvent.mouseEnter(sidebar);
      fireEvent.click(screen.getByRole("button", { name: /Fijada/i }));
      expect(sidebar).toHaveAttribute("data-expanded", "true");
      fireEvent.mouseLeave(sidebar);
      expect(sidebar).toHaveAttribute("data-expanded", "false");
    });
  });

  it("shows clear search control and keeps focus after clearing", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const searchInput = screen.getByRole("textbox", { name: /Buscar en datos extraídos/i });
    expect(screen.queryByRole("button", { name: /Limpiar búsqueda/i })).toBeNull();

    fireEvent.change(searchInput, { target: { value: "Luna" } });
    const clearButton = screen.getByRole("button", { name: /Limpiar búsqueda/i });
    expect(clearButton).toBeInTheDocument();

    fireEvent.click(clearButton);
    expect(searchInput).toHaveValue("");
    expect(searchInput).toHaveFocus();
    expect(screen.queryByRole("button", { name: /Limpiar búsqueda/i })).toBeNull();
  });
});
