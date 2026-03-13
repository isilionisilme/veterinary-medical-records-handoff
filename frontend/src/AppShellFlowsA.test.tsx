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

  it("uses polished structured header actions without Documento original button", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const activeViewerTool = await screen.findByTestId("viewer-tab-document");
    expect(activeViewerTool).toHaveAttribute("aria-pressed", "true");
    expect(activeViewerTool).toHaveAttribute("aria-current", "page");

    expect(screen.getByRole("heading", { name: /Datos extraídos/i })).toBeInTheDocument();
    expect(
      screen.queryByText(/La confianza guia la atencion, no bloquea decisiones\./i),
    ).toBeNull();
    expect(screen.queryByRole("button", { name: /Abrir texto/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /Documento original/i })).toBeNull();
  }, 15000);

  it("shows only connectivity toast when preview download fails (no global red banner)", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-ready",
                original_filename: "ready.pdf",
                created_at: "2026-02-09T10:00:00Z",
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

      if (url.includes("/documents/doc-ready/download") && method === "GET") {
        throw new TypeError("Failed to fetch");
      }

      if (url.endsWith("/documents/doc-ready") && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-ready",
            original_filename: "ready.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-09T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: "COMPLETED",
            status_message: "Completed.",
            failure_type: null,
            latest_run: { run_id: "run-doc-ready", state: "COMPLETED", failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/documents/doc-ready/review") && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-ready",
            latest_completed_run: {
              run_id: "run-doc-ready",
              state: "COMPLETED",
              completed_at: "2026-02-10T10:00:00Z",
              failure_type: null,
            },
            active_interpretation: {
              interpretation_id: "interp-doc-ready",
              version_number: 1,
              data: {
                document_id: "doc-ready",
                processing_run_id: "run-doc-ready",
                created_at: "2026-02-10T10:00:00Z",
                fields: [],
                confidence_policy: {
                  policy_version: "v1",
                  band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
                },
              },
            },
            raw_text_artifact: {
              run_id: "run-doc-ready",
              available: false,
            },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-ready", runs: [] }), {
          status: 200,
        });
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    expect(await screen.findByText(/No se pudo conectar con el servidor\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Sin conexión/i)).toBeNull();
    expect(screen.queryByText(/No se pudo cargar la vista previa del documento\./i)).toBeNull();
  });

  it("deduplicates connectivity toasts when preview and review fail in the same attempt", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-ready",
                original_filename: "ready.pdf",
                created_at: "2026-02-09T10:00:00Z",
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

      if (url.endsWith("/documents/doc-ready") && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-ready",
            original_filename: "ready.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-09T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: "COMPLETED",
            status_message: "Completed.",
            failure_type: null,
            latest_run: { run_id: "run-doc-ready", state: "COMPLETED", failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/documents/doc-ready/download") && method === "GET") {
        throw new TypeError("Failed to fetch");
      }

      if (url.includes("/documents/doc-ready/review") && method === "GET") {
        throw new TypeError("Failed to fetch");
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-ready", runs: [] }), {
          status: 200,
        });
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/No se pudo conectar con el servidor\./i)).toHaveLength(1);
    });
  });

  it("copies the full extracted text with Copy all", async () => {
    const rawText = "Linea uno\nLinea dos\nLinea tres";
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-ready",
                original_filename: "ready.pdf",
                created_at: "2026-02-09T10:00:00Z",
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

      if (url.includes("/documents/doc-ready/download") && method === "GET") {
        return new Response(new Blob(["pdf"], { type: "application/pdf" }), { status: 200 });
      }

      if (url.match(/\/documents\/doc-ready$/) && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-ready",
            original_filename: "ready.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-09T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: "COMPLETED",
            status_message: "Completed",
            failure_type: null,
            latest_run: { run_id: "run-doc-ready", state: "COMPLETED", failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-ready", runs: [] }), {
          status: 200,
        });
      }

      if (url.includes("/runs/run-doc-ready/artifacts/raw-text") && method === "GET") {
        return new Response(
          JSON.stringify({
            run_id: "run-doc-ready",
            artifact_type: "RAW_TEXT",
            content_type: "text/plain",
            text: rawText,
          }),
          { status: 200 },
        );
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    const writeText = vi.fn(async () => undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    fireEvent.click(screen.getByRole("button", { name: /Texto extraído/i }));

    await screen.findByText(/Linea uno/i);
    fireEvent.click(screen.getByRole("button", { name: /Copiar todo/i }));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(rawText);
    });
    expect(screen.getByText(/Texto copiado\./i)).toBeInTheDocument();
  });

  it("refreshes extracted text after reprocess without switching tabs", async () => {
    let phase: "initial" | "processing" | "completed" = "initial";
    let processingPollCount = 0;
    const oldText = "Texto antiguo";
    const newText = "Texto actualizado";

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-ready",
                original_filename: "ready.pdf",
                created_at: "2026-02-09T10:00:00Z",
                status: phase === "processing" ? "PROCESSING" : "COMPLETED",
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

      if (url.includes("/documents/doc-ready/download") && method === "GET") {
        return new Response(new Blob(["pdf"], { type: "application/pdf" }), {
          status: 200,
          headers: { "content-disposition": 'inline; filename="ready.pdf"' },
        });
      }

      if (url.endsWith("/documents/doc-ready") && method === "GET") {
        let latestState = "COMPLETED";
        let status = "COMPLETED";
        if (phase === "processing") {
          processingPollCount += 1;
          latestState = "RUNNING";
          status = "PROCESSING";
          if (processingPollCount >= 2) {
            phase = "completed";
            latestState = "COMPLETED";
            status = "COMPLETED";
          }
        }
        return new Response(
          JSON.stringify({
            document_id: "doc-ready",
            original_filename: "ready.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-09T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status,
            status_message: "state",
            failure_type: null,
            latest_run: { run_id: "run-doc-ready", state: latestState, failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-ready", runs: [] }), {
          status: 200,
        });
      }

      if (url.includes("/documents/doc-ready/reprocess") && method === "POST") {
        phase = "processing";
        processingPollCount = 0;
        return new Response(
          JSON.stringify({
            run_id: "run-doc-ready",
            state: "QUEUED",
            created_at: "2026-02-10T10:00:00Z",
          }),
          { status: 201 },
        );
      }

      if (url.includes("/runs/run-doc-ready/artifacts/raw-text") && method === "GET") {
        if (phase === "processing") {
          return new Response(
            JSON.stringify({
              error_code: "ARTIFACT_NOT_READY",
              message: "Not ready",
              details: { reason: "RAW_TEXT_NOT_READY" },
            }),
            { status: 409 },
          );
        }
        return new Response(
          JSON.stringify({
            run_id: "run-doc-ready",
            artifact_type: "RAW_TEXT",
            content_type: "text/plain",
            text: phase === "initial" ? oldText : newText,
          }),
          { status: 200 },
        );
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    fireEvent.click(screen.getByRole("button", { name: /Texto extraído/i }));
    expect(
      screen.getByText(
        /¿El texto no es correcto\? Puedes reprocesarlo para regenerar la extracción\./i,
      ),
    ).toBeInTheDocument();

    await screen.findByText(oldText);

    fireEvent.click(screen.getByRole("button", { name: /^Reprocesar$/i }));
    const reprocessDialog = await screen.findByRole("dialog", { name: /Reprocesar documento/i });
    fireEvent.click(within(reprocessDialog).getByRole("button", { name: /^Reprocesar$/i }));

    expect(await screen.findByText(/Reprocesamiento iniciado\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Procesamiento reiniciado/i)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Reprocesando\.\.\./i })).toBeDisabled();
    expect(
      within(screen.getByRole("button", { name: /ready\.pdf/i })).getByText("Procesando"),
    ).toBeInTheDocument();

    await waitFor(
      () => {
        expect(screen.getByText(newText)).toBeInTheDocument();
        expect(
          within(screen.getByRole("button", { name: /ready\.pdf/i })).getByText("Listo"),
        ).toBeInTheDocument();
      },
      { timeout: 10000 },
    );
  }, 12000);
});
