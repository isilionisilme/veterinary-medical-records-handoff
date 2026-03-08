import { useEffect, useState, type RefObject } from "react";
import * as pdfjsLib from "pdfjs-dist";

type UsePdfDocumentParams = {
  fileUrl: string | ArrayBuffer | null;
  scrollRef: RefObject<HTMLDivElement | null>;
  cancelAllRenderTasks: () => void;
};

export function usePdfDocument({ fileUrl, scrollRef, cancelAllRenderTasks }: UsePdfDocumentParams) {
  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let loadingTask: pdfjsLib.PDFDocumentLoadingTask | null = null;
    const maxAttempts = 3;

    const delay = (ms: number) =>
      new Promise<void>((resolve) => {
        window.setTimeout(resolve, ms);
      });

    async function loadPdf() {
      if (!fileUrl) {
        setPdfDoc(null);
        setTotalPages(0);
        setError(null);
        setLoading(false);
        return;
      }

      cancelAllRenderTasks();
      setPdfDoc(null);
      setTotalPages(0);

      setLoading(true);
      setError(null);
      try {
        let loadedDoc: pdfjsLib.PDFDocumentProxy | null = null;
        let lastError: unknown = null;

        for (let attempt = 0; attempt < maxAttempts && !cancelled; attempt += 1) {
          try {
            let arrayBuffer: ArrayBuffer;
            if (typeof fileUrl === "string") {
              const response = await fetch(fileUrl, { cache: "no-store" });
              if (!response.ok) {
                throw new Error("Failed to fetch PDF data.");
              }
              arrayBuffer = await response.arrayBuffer();
            } else {
              arrayBuffer = fileUrl;
            }

            // Use a fresh copy for each attempt to avoid edge cases with reused buffers.
            const pdfBytes = new Uint8Array(arrayBuffer.slice(0));
            loadingTask = pdfjsLib.getDocument({
              data: pdfBytes,
              isEvalSupported: false,
            });
            loadedDoc = await loadingTask.promise;
            break;
          } catch (attemptError) {
            lastError = attemptError;
            if (attempt < maxAttempts - 1) {
              await delay(250);
            }
          }
        }

        if (!loadedDoc) {
          throw lastError ?? new Error("Failed to load PDF.");
        }
        if (cancelled) {
          void loadedDoc.destroy();
          return;
        }

        setPdfDoc(loadedDoc);
        setTotalPages(loadedDoc.numPages);
      } catch (loadError) {
        if (!cancelled) {
          if (import.meta.env.DEV) {
            console.error("[PdfViewer] loadPdf failed:", loadError);
          }
          setError("No pudimos cargar el PDF.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadPdf();

    return () => {
      cancelled = true;
      cancelAllRenderTasks();
      if (loadingTask && typeof (loadingTask as { destroy?: unknown }).destroy === "function") {
        void (loadingTask as { destroy: () => Promise<void> | void }).destroy();
      }
    };
  }, [fileUrl, cancelAllRenderTasks]);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) {
      return;
    }
    if (typeof container.scrollTo === "function") {
      container.scrollTo({ top: 0, behavior: "auto" });
      return;
    }
    container.scrollTop = 0;
  }, [fileUrl, scrollRef]);

  useEffect(() => {
    if (!pdfDoc) {
      return undefined;
    }

    return () => {
      cancelAllRenderTasks();
      if (typeof (pdfDoc as { destroy?: unknown }).destroy === "function") {
        void (pdfDoc as { destroy: () => Promise<void> | void }).destroy();
      }
    };
  }, [pdfDoc, cancelAllRenderTasks]);

  return { pdfDoc, totalPages, loading, error };
}
