import {
  type Dispatch,
  type SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useMutation } from "@tanstack/react-query";

import { fetchOriginalPdf } from "../api/documentApi";
import { type UploadFeedback } from "../components/toast/toast-types";

type UseDocumentLoaderParams = {
  onUploadFeedback: Dispatch<SetStateAction<UploadFeedback | null>>;
};

export function useDocumentLoader({ onUploadFeedback }: UseDocumentLoaderParams) {
  const [fileUrl, setFileUrl] = useState<string | ArrayBuffer | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const latestLoadRequestIdRef = useRef<string | null>(null);
  const loadRetryCountRef = useRef<Record<string, number>>({});
  const pendingAutoOpenDocumentIdRef = useRef<string | null>(null);
  const autoOpenRetryCountRef = useRef<Record<string, number>>({});
  const autoOpenRetryTimerRef = useRef<number | null>(null);
  const loadRetryTimerRef = useRef<number | null>(null);

  const loadPdf = useMutation({
    mutationFn: async (docId: string) => fetchOriginalPdf(docId),
    onSuccess: (result, docId) => {
      if (latestLoadRequestIdRef.current !== docId) {
        return;
      }
      if (pendingAutoOpenDocumentIdRef.current === docId) {
        pendingAutoOpenDocumentIdRef.current = null;
        delete autoOpenRetryCountRef.current[docId];
        if (autoOpenRetryTimerRef.current) {
          window.clearTimeout(autoOpenRetryTimerRef.current);
          autoOpenRetryTimerRef.current = null;
        }
        onUploadFeedback((current) => {
          if (current?.kind !== "success" || current.documentId !== docId) {
            return current;
          }
          return { ...current, showOpenAction: false };
        });
      }
      delete loadRetryCountRef.current[docId];
      if (loadRetryTimerRef.current) {
        window.clearTimeout(loadRetryTimerRef.current);
        loadRetryTimerRef.current = null;
      }
      setFileUrl(result.data);
      setFilename(result.filename);
    },
    onError: (_, docId) => {
      if (latestLoadRequestIdRef.current !== docId) {
        return;
      }
      if (pendingAutoOpenDocumentIdRef.current === docId) {
        const retries = autoOpenRetryCountRef.current[docId] ?? 0;
        if (retries < 1) {
          autoOpenRetryCountRef.current[docId] = retries + 1;
          autoOpenRetryTimerRef.current = window.setTimeout(() => {
            latestLoadRequestIdRef.current = docId;
            requestPdfLoad(docId);
          }, 1000);
          return;
        }
        pendingAutoOpenDocumentIdRef.current = null;
        delete autoOpenRetryCountRef.current[docId];
        onUploadFeedback({
          kind: "success",
          message: "Documento subido correctamente.",
          documentId: docId,
          showOpenAction: true,
        });
        delete loadRetryCountRef.current[docId];
        return;
      }

      const retries = loadRetryCountRef.current[docId] ?? 0;
      if (retries < 2) {
        loadRetryCountRef.current[docId] = retries + 1;
        if (loadRetryTimerRef.current) {
          window.clearTimeout(loadRetryTimerRef.current);
        }
        loadRetryTimerRef.current = window.setTimeout(() => {
          latestLoadRequestIdRef.current = docId;
          requestPdfLoad(docId);
        }, 1000);
      }
    },
  });
  const mutateLoadPdf = loadPdf.mutate;

  const requestPdfLoad = useCallback(
    (docId: string) => {
      latestLoadRequestIdRef.current = docId;
      mutateLoadPdf(docId);
    },
    [mutateLoadPdf],
  );

  useEffect(() => {
    return () => {
      if (autoOpenRetryTimerRef.current) {
        window.clearTimeout(autoOpenRetryTimerRef.current);
      }
      if (loadRetryTimerRef.current) {
        window.clearTimeout(loadRetryTimerRef.current);
      }
    };
  }, []);

  return {
    fileUrl,
    filename,
    setFileUrl,
    setFilename,
    requestPdfLoad,
    loadPdf,
    pendingAutoOpenDocumentIdRef,
  };
}
