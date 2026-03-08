import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchRawText } from "../../api/documentApi";
import type { ProcessingHistoryRun } from "../../types/appWorkspace";
import { ProcessingHistorySection } from "./ProcessingHistorySection";

vi.mock("../../api/documentApi", () => ({
  fetchRawText: vi.fn(),
}));

const fetchRawTextMock = vi.mocked(fetchRawText);

const baseProps = {
  activeId: "doc-1",
  isActiveDocumentProcessing: false,
  reprocessPending: false,
  onOpenRetryModal: vi.fn(),
  processingHistoryIsLoading: false,
  processingHistoryIsError: false,
  processingHistoryErrorMessage: "",
  expandedSteps: {},
  onToggleStepDetails: vi.fn(),
  formatRunHeader: (run: ProcessingHistoryRun) => `Run ${run.run_id}`,
};

function renderSection(runs: ProcessingHistoryRun[]) {
  return render(<ProcessingHistorySection {...baseProps} processingHistoryRuns={runs} />);
}

describe("ProcessingHistorySection", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders empty state with no runs", () => {
    renderSection([]);
    expect(screen.getByText(/No hay ejecuciones registradas/i)).toBeInTheDocument();
  });

  it("renders one run with state badge and total duration", () => {
    renderSection([
      {
        run_id: "run-1",
        state: "COMPLETED",
        failure_type: null,
        started_at: "2026-03-01T10:00:00.000Z",
        completed_at: "2026-03-01T10:00:05.000Z",
        steps: [],
      },
    ]);

    expect(screen.getByText("Run run-1")).toBeInTheDocument();
    expect(screen.getByText("Completado")).toBeInTheDocument();
    expect(screen.getByText("Última")).toBeInTheDocument();
    expect(screen.getByText("Duración total: 5s")).toBeInTheDocument();
  });

  it("renders multiple runs in reverse order and maps state labels", () => {
    renderSection([
      {
        run_id: "run-1",
        state: "FAILED",
        failure_type: "OCR_FAILURE",
        started_at: "2026-03-01T10:00:00.000Z",
        completed_at: "2026-03-01T10:00:02.000Z",
        steps: [],
      },
      {
        run_id: "run-2",
        state: "TIMED_OUT",
        failure_type: "TIMEOUT",
        started_at: "2026-03-01T10:01:00.000Z",
        completed_at: "2026-03-01T10:01:05.000Z",
        steps: [],
      },
    ]);

    const runHeaders = screen.getAllByText(/Run run-/);
    expect(runHeaders[0]).toHaveTextContent("Run run-2");
    expect(screen.getByText("Timeout")).toBeInTheDocument();
    expect(screen.getByText("Fallido")).toBeInTheDocument();
  });

  it("loads and displays raw text for completed runs", async () => {
    fetchRawTextMock.mockResolvedValueOnce({
      run_id: "run-1",
      artifact_type: "RAW_TEXT",
      content_type: "text/plain",
      text: "texto de prueba",
    });

    renderSection([
      {
        run_id: "run-1",
        state: "COMPLETED",
        failure_type: null,
        started_at: "2026-03-01T10:00:00.000Z",
        completed_at: "2026-03-01T10:00:05.000Z",
        steps: [],
      },
    ]);

    fireEvent.click(screen.getByRole("button", { name: /Ver texto extraído/i }));

    await waitFor(() => {
      expect(fetchRawTextMock).toHaveBeenCalledWith("run-1");
      expect(screen.getByText("texto de prueba")).toBeInTheDocument();
    });
  });
});
