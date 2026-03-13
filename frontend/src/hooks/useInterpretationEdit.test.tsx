import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { editRunInterpretation } from "../api/documentApi";
import { type DocumentReviewResponse } from "../types/appWorkspace";
import { useInterpretationEdit } from "./useInterpretationEdit";

vi.mock("../api/documentApi", () => ({
  editRunInterpretation: vi.fn(),
}));

const mockedEditRunInterpretation = vi.mocked(editRunInterpretation);

function createHarness() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { queryClient, wrapper };
}

describe("useInterpretationEdit", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("submits interpretation edits and emits success feedback", async () => {
    mockedEditRunInterpretation.mockResolvedValueOnce({
      interpretation_id: "interp-2",
      version_number: 2,
      data: {
        document_id: "doc-1",
        processing_run_id: "run-1",
        created_at: "2026-02-28T12:00:00Z",
        fields: [],
      },
    });

    const { queryClient, wrapper } = createHarness();
    const reviewPayload: DocumentReviewResponse = {
      document_id: "doc-1",
      latest_completed_run: {
        run_id: "run-1",
        state: "COMPLETED",
        completed_at: "2026-02-28T11:59:00Z",
        failure_type: null,
      },
      active_interpretation: {
        interpretation_id: "interp-1",
        version_number: 1,
        data: {
          document_id: "doc-1",
          processing_run_id: "run-1",
          created_at: "2026-02-28T11:00:00Z",
          fields: [],
        },
      },
      raw_text_artifact: {
        run_id: "run-1",
        available: true,
      },
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
    };
    queryClient.setQueryData(["documents", "review", "doc-1"], reviewPayload);
    const onActionFeedback = vi.fn();

    const { result } = renderHook(
      () =>
        useInterpretationEdit({
          activeId: "doc-1",
          reviewPayload,
          onActionFeedback,
        }),
      { wrapper },
    );

    act(() => {
      result.current.submitInterpretationChanges(
        [{ op: "set", path: "/fields/0/value", value: "nuevo" }],
        "Guardado.",
      );
    });

    await waitFor(() => {
      expect(mockedEditRunInterpretation).toHaveBeenCalledWith("run-1", {
        base_version_number: 1,
        changes: [{ op: "set", path: "/fields/0/value", value: "nuevo" }],
      });
    });
    await waitFor(() => {
      expect(onActionFeedback).toHaveBeenCalledWith({
        kind: "success",
        message: "Guardado.",
      });
    });
  });

  it("does not submit when active document context is missing", () => {
    const { wrapper } = createHarness();
    const { result } = renderHook(
      () =>
        useInterpretationEdit({
          activeId: null,
          reviewPayload: undefined,
          onActionFeedback: vi.fn(),
        }),
      { wrapper },
    );

    act(() => {
      result.current.submitInterpretationChanges(
        [{ op: "set", path: "/fields/0/value", value: "nuevo" }],
        "Guardado.",
      );
    });

    expect(mockedEditRunInterpretation).not.toHaveBeenCalled();
  });
});
