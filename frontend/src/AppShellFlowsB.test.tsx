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

  it("rolls back optimistic processing state when reprocess fails", async () => {
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

      if (url.includes("/documents/doc-ready/reprocess") && method === "POST") {
        return new Response(JSON.stringify({ message: "reprocess failed" }), { status: 500 });
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    fireEvent.click(screen.getByRole("button", { name: /Texto extraído/i }));
    fireEvent.click(screen.getByRole("button", { name: /^Reprocesar$/i }));
    const reprocessDialog = await screen.findByRole("dialog", { name: /Reprocesar documento/i });
    fireEvent.click(within(reprocessDialog).getByRole("button", { name: /^Reprocesar$/i }));

    expect(
      (await screen.findAllByText(/Ocurrió un error inesperado\. Intenta de nuevo\./i)).length,
    ).toBeGreaterThan(0);
    await waitFor(() => {
      expect(
        within(screen.getByRole("button", { name: /ready\.pdf/i })).getByText("Listo"),
      ).toBeInTheDocument();
    });
  });

  it("does not show stale empty-search warning when there is no text", async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents?") && method === "GET") {
        return new Response(
          JSON.stringify({
            items: [
              {
                document_id: "doc-empty",
                original_filename: "empty.pdf",
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

      if (url.endsWith("/documents/doc-empty") && method === "GET") {
        return new Response(
          JSON.stringify({
            document_id: "doc-empty",
            original_filename: "empty.pdf",
            content_type: "application/pdf",
            file_size: 10,
            created_at: "2026-02-09T10:00:00Z",
            updated_at: "2026-02-10T10:00:00Z",
            status: "COMPLETED",
            status_message: "Completed",
            failure_type: null,
            latest_run: { run_id: "run-empty", state: "COMPLETED", failure_type: null },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/documents/doc-empty/download") && method === "GET") {
        return new Response(new Blob(["pdf"], { type: "application/pdf" }), {
          status: 200,
          headers: { "content-disposition": 'inline; filename="empty.pdf"' },
        });
      }

      if (url.includes("/processing-history") && method === "GET") {
        return new Response(JSON.stringify({ document_id: "doc-empty", runs: [] }), {
          status: 200,
        });
      }

      if (url.includes("/runs/run-empty/artifacts/raw-text") && method === "GET") {
        return new Response(
          JSON.stringify({
            error_code: "ARTIFACT_NOT_AVAILABLE",
            message: "Not available",
            details: { reason: "RAW_TEXT_NOT_AVAILABLE" },
          }),
          { status: 404 },
        );
      }

      return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /empty\.pdf/i }));
    fireEvent.click(screen.getByRole("button", { name: /Texto extraído/i }));

    expect(screen.getByPlaceholderText(/Buscar en el texto/i)).toBeDisabled();
    expect(screen.getByRole("button", { name: /^Buscar$/i })).toBeDisabled();
    expect(screen.getByText(/Sin texto extraído\./i)).toBeInTheDocument();
    expect(screen.queryByText(/No hay texto disponible para buscar/i)).not.toBeInTheDocument();
    expect(
      screen.queryByText(/El texto extraído no está disponible para este run\./i),
    ).not.toBeInTheDocument();
  });

  it("does not post extraction snapshots from the UI", async () => {
    const baseFetch = globalThis.fetch as typeof fetch;
    let snapshotPostAttempts = 0;

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();
      if (url.endsWith("/debug/extraction-runs") && method === "POST") {
        snapshotPostAttempts += 1;
      }
      return baseFetch(input, init);
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    fireEvent.click(screen.getByRole("button", { name: /Actualizar/i }));
    await waitForStructuredDataReady();

    await waitFor(() => {
      expect(snapshotPostAttempts).toBe(0);
    });
  });

  it("keeps right panel mounted and shows skeleton while loading interpretation", async () => {
    const baseFetch = globalThis.fetch as typeof fetch;
    let releaseReviewRequest!: () => void;

    globalThis.fetch = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/documents/doc-ready/review") && method === "GET") {
        return new Promise<Response>((resolve) => {
          releaseReviewRequest = () => {
            void baseFetch(input, init).then(resolve);
          };
        });
      }

      return baseFetch(input, init);
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    expect(await screen.findByText("Cargando interpretación estructurada...")).toBeInTheDocument();
    expect(screen.getByTestId("right-panel-scroll")).toBeInTheDocument();
    expect(screen.getByTestId("review-core-skeleton")).toBeInTheDocument();
    expect(within(screen.getByTestId("right-panel-scroll")).queryByText("—")).toBeNull();

    expect(typeof releaseReviewRequest).toBe("function");
    await act(async () => {
      releaseReviewRequest();
    });

    expect(await screen.findByRole("heading", { name: /Datos extraídos/i })).toBeInTheDocument();
  });

  it("shows centered interpretation empty state, retries with loading button, and recovers on success", async () => {
    let reviewAttempts = 0;
    let resolveRetryReview!: () => void;
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
        reviewAttempts += 1;
        if (reviewAttempts === 1) {
          throw new TypeError("Failed to fetch");
        }
        return new Promise<Response>((resolve) => {
          resolveRetryReview = () =>
            resolve(
              new Response(
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
                      fields: [
                        {
                          field_id: "field-pet-name-doc-ready",
                          key: "pet_name",
                          value: "Luna",
                          value_type: "string",
                          field_candidate_confidence: 0.82,
                          field_mapping_confidence: 0.82,
                          is_critical: false,
                          origin: "machine",
                          evidence: { page: 1, snippet: "Paciente: Luna" },
                        },
                      ],
                      confidence_policy: {
                        policy_version: "v1",
                        band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
                      },
                    },
                  },
                  raw_text_artifact: {
                    run_id: "run-doc-ready",
                    available: true,
                  },
                }),
                { status: 200 },
              ),
            );
        });
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

    const unavailableTitle = await screen.findByText("Interpretación no disponible");
    const unavailableCard = unavailableTitle.closest("section");
    expect(unavailableCard).not.toBeNull();
    expect(
      within(unavailableCard as HTMLElement).getByText(
        /No se pudo cargar la interpretación\. Comprueba tu conexión y vuelve a intentarlo\./i,
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Error loading interpretation/i)).toBeNull();
    expect(screen.queryByText(/No completed run found/i)).toBeNull();

    const panelRetryButton = within(unavailableCard as HTMLElement).getByRole("button", {
      name: /Reintentar/i,
    });
    const attemptsBeforeRetry = reviewAttempts;
    fireEvent.click(panelRetryButton);
    await waitFor(() => {
      expect(reviewAttempts).toBeGreaterThan(attemptsBeforeRetry);
    });
    await waitFor(() => {
      expect(
        screen.queryByRole("button", { name: /Reintentando\.\.\./i }) ??
          screen.queryByText(/Cargando interpretación estructurada\.\.\./i),
      ).toBeTruthy();
    });
    expect(screen.queryByRole("button", { name: /Ver detalles técnicos/i })).toBeNull();

    expect(typeof resolveRetryReview).toBe("function");
    resolveRetryReview();
    expect(await screen.findByRole("heading", { name: /Datos extraídos/i })).toBeInTheDocument();
    expect(screen.getByText(/No se pudo conectar con el servidor\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Sin conexión/i)).toBeNull();
  });
});
