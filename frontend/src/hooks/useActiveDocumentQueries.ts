import { useCallback, useEffect, useRef, type MutableRefObject } from "react";
import { QueryClient, useQuery } from "@tanstack/react-query";

import {
  fetchDocumentDetails,
  fetchDocumentReview,
  fetchProcessingHistory,
  fetchVisitScopingMetrics,
} from "../api/documentApi";
import { type DocumentListResponse } from "../types/appWorkspace";

type DocumentListQueryLike = {
  refetch: () => unknown;
  isFetching: boolean;
  isLoading: boolean;
  data: DocumentListResponse | undefined;
};

type UseActiveDocumentQueriesParams = {
  activeId: string | null;
  shouldFetchVisitScopingMetrics: boolean;
  documentList: DocumentListQueryLike;
  showRefreshFeedback: boolean;
  setShowRefreshFeedback: (value: boolean) => void;
  refreshFeedbackTimerRef: MutableRefObject<number | null>;
  queryClient: QueryClient;
};

export function useActiveDocumentQueries({
  activeId,
  shouldFetchVisitScopingMetrics,
  documentList,
  showRefreshFeedback,
  setShowRefreshFeedback,
  refreshFeedbackTimerRef,
  queryClient,
}: UseActiveDocumentQueriesParams) {
  const latestRawTextRefreshRef = useRef<string | null>(null);
  const clearRawTextRefreshKey = useCallback(() => {
    latestRawTextRefreshRef.current = null;
  }, []);
  const documentDetails = useQuery({
    queryKey: ["documents", "detail", activeId],
    queryFn: () => fetchDocumentDetails(activeId ?? ""),
    enabled: Boolean(activeId),
  });
  const processingHistory = useQuery({
    queryKey: ["documents", "history", activeId],
    queryFn: () => fetchProcessingHistory(activeId ?? ""),
    enabled: Boolean(activeId),
  });
  const documentReview = useQuery({
    queryKey: ["documents", "review", activeId],
    queryFn: () => fetchDocumentReview(activeId ?? ""),
    enabled: Boolean(activeId),
    retry: false,
  });
  const visitScopingMetrics = useQuery({
    queryKey: ["documents", "review", "visit-scoping", activeId],
    queryFn: () => fetchVisitScopingMetrics(activeId ?? ""),
    enabled: Boolean(activeId) && shouldFetchVisitScopingMetrics,
    retry: false,
  });
  const rawTextRunId = documentDetails.data?.latest_run?.run_id ?? null;
  const latestState = documentDetails.data?.latest_run?.state;
  const latestRunId = documentDetails.data?.latest_run?.run_id;
  const isProcessing =
    documentDetails.data?.status === "PROCESSING" ||
    latestState === "QUEUED" ||
    latestState === "RUNNING";

  useEffect(() => {
    if (!activeId || !documentDetails.data) {
      return;
    }
    const shouldPoll =
      documentDetails.data.status === "PROCESSING" ||
      latestState === "QUEUED" ||
      latestState === "RUNNING";
    if (!shouldPoll) {
      return;
    }
    const intervalId = window.setInterval(() => {
      documentDetails.refetch();
      processingHistory.refetch();
      documentReview.refetch();
    }, 1500);
    return () => window.clearInterval(intervalId);
  }, [
    activeId,
    documentDetails,
    documentDetails.data,
    latestState,
    processingHistory,
    documentReview,
  ]);

  const handleRefresh = useCallback(() => {
    setShowRefreshFeedback(true);
    if (refreshFeedbackTimerRef.current) {
      window.clearTimeout(refreshFeedbackTimerRef.current);
    }
    refreshFeedbackTimerRef.current = window.setTimeout(() => {
      setShowRefreshFeedback(false);
      refreshFeedbackTimerRef.current = null;
    }, 350);
    documentList.refetch();
    if (activeId) {
      documentDetails.refetch();
      processingHistory.refetch();
      documentReview.refetch();
    }
  }, [
    activeId,
    documentDetails,
    documentList,
    documentReview,
    processingHistory,
    refreshFeedbackTimerRef,
    setShowRefreshFeedback,
  ]);

  const isListRefreshing =
    (documentList.isFetching || showRefreshFeedback) && !documentList.isLoading;

  useEffect(() => {
    if (!latestRunId || !latestState) {
      return;
    }
    const shouldRefreshRawText =
      latestState === "COMPLETED" || latestState === "FAILED" || latestState === "TIMED_OUT";
    if (!shouldRefreshRawText) {
      return;
    }
    const refreshKey = `${latestRunId}:${latestState}`;
    if (latestRawTextRefreshRef.current === refreshKey) {
      return;
    }
    latestRawTextRefreshRef.current = refreshKey;
    queryClient.invalidateQueries({ queryKey: ["runs", "raw-text", latestRunId] });
  }, [latestRunId, latestState, queryClient]);

  return {
    documentDetails,
    processingHistory,
    documentReview,
    visitScopingMetrics,
    rawTextRunId,
    latestState,
    latestRunId,
    isProcessing,
    handleRefresh,
    isListRefreshing,
    clearRawTextRefreshKey,
  };
}
