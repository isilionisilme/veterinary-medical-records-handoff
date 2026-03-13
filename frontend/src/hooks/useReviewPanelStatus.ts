import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getReviewPanelMessage } from "../lib/appWorkspaceUtils";
import {
  ApiResponseError,
  type DocumentReviewResponse,
  type ReviewPanelState,
} from "../types/appWorkspace";

type UseReviewPanelStatusParams = {
  activeId: string | null;
  documentReview: {
    data: DocumentReviewResponse | undefined;
    isFetching: boolean;
    isError: boolean;
    error: unknown;
    refetch: () => Promise<unknown>;
  };
  isActiveDocumentProcessing: boolean;
  hasActiveStructuredFilters: boolean;
  visibleCoreGroupsLength: number;
};

export function useReviewPanelStatus({
  activeId,
  documentReview,
  isActiveDocumentProcessing,
  hasActiveStructuredFilters,
  visibleCoreGroupsLength,
}: UseReviewPanelStatusParams) {
  const [reviewLoadingDocId, setReviewLoadingDocId] = useState<string | null>(null);
  const [reviewLoadingSinceMs, setReviewLoadingSinceMs] = useState<number | null>(null);
  const [isRetryingInterpretation, setIsRetryingInterpretation] = useState(false);
  const interpretationRetryMinTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!activeId) {
      setReviewLoadingDocId(null);
      setReviewLoadingSinceMs(null);
      setIsRetryingInterpretation(false);
      if (interpretationRetryMinTimerRef.current) {
        window.clearTimeout(interpretationRetryMinTimerRef.current);
        interpretationRetryMinTimerRef.current = null;
      }
      return;
    }
    setReviewLoadingDocId(activeId);
    setReviewLoadingSinceMs(Date.now());
  }, [activeId]);

  useEffect(() => {
    if (!activeId || reviewLoadingDocId !== activeId) {
      return;
    }
    if (documentReview.isFetching) {
      return;
    }
    const minimumVisibleMs = 300;
    const elapsed = reviewLoadingSinceMs ? Date.now() - reviewLoadingSinceMs : minimumVisibleMs;
    if (elapsed >= minimumVisibleMs) {
      setReviewLoadingDocId(null);
      setReviewLoadingSinceMs(null);
      return;
    }
    const timer = window.setTimeout(() => {
      setReviewLoadingDocId(null);
      setReviewLoadingSinceMs(null);
    }, minimumVisibleMs - elapsed);
    return () => window.clearTimeout(timer);
  }, [activeId, documentReview.isFetching, reviewLoadingDocId, reviewLoadingSinceMs]);

  useEffect(() => {
    return () => {
      if (interpretationRetryMinTimerRef.current) {
        window.clearTimeout(interpretationRetryMinTimerRef.current);
      }
    };
  }, []);

  const reviewPanelState: ReviewPanelState = useMemo(() => {
    if (!activeId) {
      return "idle";
    }
    const hasStructuredPayload =
      Boolean(documentReview.data?.active_interpretation?.data) &&
      documentReview.data?.document_id === activeId;
    if (reviewLoadingDocId === activeId) {
      return "loading";
    }
    if (isActiveDocumentProcessing && !hasStructuredPayload) {
      return "loading";
    }
    if (!hasStructuredPayload && !documentReview.isError && documentReview.isFetching) {
      return "loading";
    }
    if (!isRetryingInterpretation && documentReview.isFetching && !documentReview.isError) {
      return "loading";
    }
    if (documentReview.isError) {
      if (
        documentReview.error instanceof ApiResponseError &&
        (documentReview.error.reason === "NO_COMPLETED_RUN" ||
          documentReview.error.reason === "INTERPRETATION_MISSING")
      ) {
        if (isActiveDocumentProcessing) {
          return "loading";
        }
        return "no_completed_run";
      }
      return "error";
    }
    if (!hasStructuredPayload) {
      return "error";
    }
    return "ready";
  }, [
    activeId,
    documentReview.data,
    documentReview.error,
    documentReview.isError,
    documentReview.isFetching,
    isActiveDocumentProcessing,
    isRetryingInterpretation,
    reviewLoadingDocId,
  ]);

  const reviewPanelMessage = getReviewPanelMessage(reviewPanelState);
  const shouldShowReviewEmptyState =
    reviewPanelState !== "loading" && reviewPanelState !== "ready" && Boolean(reviewPanelMessage);
  const hasNoStructuredFilterResults =
    reviewPanelState === "ready" && hasActiveStructuredFilters && visibleCoreGroupsLength === 0;

  const handleRetryInterpretation = useCallback(async () => {
    const retryStartedAt = Date.now();
    setIsRetryingInterpretation(true);
    await documentReview.refetch();
    const minVisibleMs = 250;
    const elapsedMs = Date.now() - retryStartedAt;
    const remainingMs = Math.max(0, minVisibleMs - elapsedMs);
    if (remainingMs === 0) {
      setIsRetryingInterpretation(false);
      return;
    }
    if (interpretationRetryMinTimerRef.current) {
      window.clearTimeout(interpretationRetryMinTimerRef.current);
    }
    interpretationRetryMinTimerRef.current = window.setTimeout(() => {
      interpretationRetryMinTimerRef.current = null;
      setIsRetryingInterpretation(false);
    }, remainingMs);
  }, [documentReview]);

  return {
    reviewPanelState,
    reviewPanelMessage,
    shouldShowReviewEmptyState,
    hasNoStructuredFilterResults,
    isRetryingInterpretation,
    handleRetryInterpretation,
  };
}
