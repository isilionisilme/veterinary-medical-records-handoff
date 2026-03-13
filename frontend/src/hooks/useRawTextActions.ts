import { useEffect, useRef, useState } from "react";

import { copyTextToClipboard } from "../api/documentApi";

type UseRawTextActionsParams = {
  rawTextContent: string | undefined;
  getUserErrorMessage: (error: unknown, fallback: string) => string;
};

export function useRawTextActions({
  rawTextContent,
  getUserErrorMessage,
}: UseRawTextActionsParams) {
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const [isCopyingRawText, setIsCopyingRawText] = useState(false);
  const copyFeedbackTimerRef = useRef<number | null>(null);

  useEffect(
    () => () => {
      if (copyFeedbackTimerRef.current) {
        window.clearTimeout(copyFeedbackTimerRef.current);
      }
    },
    [],
  );

  const setCopyFeedbackWithTimeout = (message: string) => {
    setCopyFeedback(message);
    if (copyFeedbackTimerRef.current) {
      window.clearTimeout(copyFeedbackTimerRef.current);
    }
    copyFeedbackTimerRef.current = window.setTimeout(() => {
      setCopyFeedback(null);
      copyFeedbackTimerRef.current = null;
    }, 2500);
  };

  const handleDownloadRawText = () => {
    if (!rawTextContent) {
      return;
    }
    const blob = new Blob([rawTextContent], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "texto-extraido.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopyRawText = async () => {
    if (!rawTextContent) {
      setCopyFeedbackWithTimeout("No hay texto extraído para copiar.");
      return;
    }
    setIsCopyingRawText(true);
    try {
      await copyTextToClipboard(rawTextContent);
      setCopyFeedbackWithTimeout("Texto copiado.");
    } catch (error) {
      setCopyFeedbackWithTimeout(getUserErrorMessage(error, "No se pudo copiar el texto."));
    } finally {
      setIsCopyingRawText(false);
    }
  };

  return { copyFeedback, isCopyingRawText, handleDownloadRawText, handleCopyRawText };
}
