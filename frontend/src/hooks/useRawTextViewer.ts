import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { fetchRawText } from "../api/documentApi";
import { getUserErrorMessage } from "../lib/appWorkspaceUtils";
import { ApiResponseError } from "../types/appWorkspace";
import { useRawTextActions } from "./useRawTextActions";

type UseRawTextViewerParams = {
  rawTextRunId: string | null;
  activeViewerTab: "document" | "raw_text" | "technical";
};

export function useRawTextViewer({ rawTextRunId, activeViewerTab }: UseRawTextViewerParams) {
  const [rawSearch, setRawSearch] = useState("");
  const [rawSearchNotice, setRawSearchNotice] = useState<string | null>(null);

  const rawTextQuery = useQuery({
    queryKey: ["runs", "raw-text", rawTextRunId],
    queryFn: () => fetchRawText(rawTextRunId ?? ""),
    enabled: activeViewerTab === "raw_text" && Boolean(rawTextRunId),
    retry: false,
  });

  const rawTextContent = rawTextQuery.data?.text ?? null;
  const hasRawText = Boolean(rawTextContent && rawTextContent.length > 0);
  const canCopyRawText = hasRawText && !rawTextQuery.isLoading && !rawTextQuery.isError;
  const isRawTextLoading = rawTextQuery.isLoading || rawTextQuery.isFetching;
  const canSearchRawText = hasRawText && !isRawTextLoading && !rawTextQuery.isError;

  const handleRawSearch = () => {
    if (!rawTextContent || !rawSearch.trim()) {
      setRawSearchNotice(null);
      return;
    }
    const match = rawTextContent.toLowerCase().includes(rawSearch.trim().toLowerCase());
    setRawSearchNotice(match ? "Coincidencia encontrada." : "No se encontraron coincidencias.");
  };

  const rawTextErrorMessage = (() => {
    if (!rawTextQuery.isError) {
      return null;
    }
    if (rawTextQuery.error instanceof ApiResponseError) {
      if (rawTextQuery.error.reason === "RAW_TEXT_NOT_READY") {
        return null;
      }
      if (rawTextQuery.error.reason === "RAW_TEXT_NOT_AVAILABLE") {
        return null;
      }
      if (rawTextQuery.error.reason === "RAW_TEXT_NOT_USABLE") {
        return null;
      }
      if (rawTextQuery.error.errorCode === "ARTIFACT_MISSING") {
        return null;
      }
      return rawTextQuery.error.userMessage;
    }
    return getUserErrorMessage(rawTextQuery.error, "No se pudo cargar el texto extraído.");
  })();

  const { copyFeedback, isCopyingRawText, handleDownloadRawText, handleCopyRawText } =
    useRawTextActions({ rawTextContent: rawTextContent ?? undefined, getUserErrorMessage });

  return {
    rawSearch,
    setRawSearch,
    rawSearchNotice,
    rawTextContent,
    hasRawText,
    canCopyRawText,
    isRawTextLoading,
    canSearchRawText,
    rawTextErrorMessage,
    handleRawSearch,
    copyFeedback,
    isCopyingRawText,
    handleDownloadRawText,
    handleCopyRawText,
  };
}
