import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TechnicalTab } from "./TechnicalTab";

vi.mock("./ProcessingHistorySection", () => ({
  ProcessingHistorySection: () => <div data-testid="processing-history-stub">history</div>,
}));

function createProps(overrides?: Partial<React.ComponentProps<typeof TechnicalTab>>) {
  return {
    viewerModeToolbarIcons: <span>icons</span>,
    viewerDownloadIcon: <span>download</span>,
    activeId: null,
    isActiveDocumentProcessing: false,
    reprocessPending: false,
    onOpenRetryModal: vi.fn(),
    processingHistoryIsLoading: false,
    processingHistoryIsError: false,
    processingHistoryErrorMessage: "",
    processingHistoryRuns: [],
    expandedSteps: {},
    onToggleStepDetails: vi.fn(),
    formatRunHeader: vi.fn((run) => run.run_id),
    visitScopingMetrics: null,
    visitScopingIsLoading: false,
    visitScopingIsError: false,
    visitScopingErrorMessage: "",
    ...overrides,
  };
}

describe("TechnicalTab", () => {
  it("shows empty-state prompt when there is no active document", () => {
    render(<TechnicalTab {...createProps({ activeId: null })} />);

    expect(
      screen.getByText("Selecciona un documento para ver métricas de visit-scoping."),
    ).toBeInTheDocument();
  });

  it("shows loading state when visit scoping is loading", () => {
    render(<TechnicalTab {...createProps({ activeId: "doc-1", visitScopingIsLoading: true })} />);

    expect(screen.getByText("Cargando métricas de visit-scoping...")).toBeInTheDocument();
  });

  it("renders visit scoping metrics summary when available", () => {
    render(
      <TechnicalTab
        {...createProps({
          activeId: "doc-1",
          visitScopingMetrics: {
            document_id: "doc-1",
            run_id: "run-1",
            summary: {
              total_visits: 2,
              assigned_visits: 2,
              anchored_visits: 1,
              unassigned_field_count: 0,
              raw_text_available: true,
            },
            visits: [
              {
                visit_index: 1,
                visit_id: "visit-1",
                visit_date: "2026-03-10",
                field_count: 3,
                anchored_in_raw_text: true,
                raw_context_chars: 120,
              },
            ],
          },
        })}
      />,
    );

    expect(screen.getByText("Document ID:")).toBeInTheDocument();
    expect(screen.getByText("Visitas totales")).toBeInTheDocument();
    expect(screen.getByText("Visitas asignadas")).toBeInTheDocument();
    expect(screen.getByText("visit-1")).toBeInTheDocument();
  });
});
