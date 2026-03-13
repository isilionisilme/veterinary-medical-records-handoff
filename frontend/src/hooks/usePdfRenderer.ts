import { useEffect, useRef, useState, type MutableRefObject, type RefObject } from "react";
import type * as pdfjsLib from "pdfjs-dist";
import { captureDebugSnapshot, type DebugFlags } from "../lib/pdfDebug";

type UsePdfRendererParams = {
  pdfDoc: pdfjsLib.PDFDocumentProxy | null;
  totalPages: number;
  zoomLevel: number;
  documentId: string | null;
  contentRef: RefObject<HTMLDivElement | null>;
  debugFlags: DebugFlags;
  fileUrl: string | ArrayBuffer | null;
  filename?: string | null;
  pageNumberRef: MutableRefObject<number>;
};

export function usePdfRenderer({
  pdfDoc,
  totalPages,
  zoomLevel,
  documentId,
  contentRef,
  debugFlags,
  fileUrl,
  filename,
  pageNumberRef,
}: UsePdfRendererParams) {
  const nodeIdentityMapRef = useRef<WeakMap<Element, string>>(new WeakMap());
  const nodeIdentityCounterRef = useRef(0);
  const lastCanvasNodeByPageRef = useRef<Map<number, string>>(new Map());
  const renderTaskStatusRef = useRef<Map<number, string>>(new Map());
  const renderTasksByPageRef = useRef<Map<number, pdfjsLib.RenderTask>>(new Map());
  const currentDocumentIdRef = useRef<string | null>(documentId);
  const pageRefs = useRef<Array<HTMLDivElement | null>>([]);
  const canvasRefs = useRef<Array<HTMLCanvasElement | null>>([]);
  const renderedPages = useRef<Set<number>>(new Set());
  const renderingPages = useRef<Set<number>>(new Set());
  const renderSessionRef = useRef(0);
  const [containerWidth, setContainerWidth] = useState(0);
  const [pageTextByIndex, setPageTextByIndex] = useState<Record<number, string>>({});

  function cancelAllRenderTasks() {
    for (const task of renderTasksByPageRef.current.values()) {
      try {
        task.cancel();
      } catch {
        // ignore cancellation errors
      }
    }
    renderTasksByPageRef.current.clear();
  }

  useEffect(() => {
    currentDocumentIdRef.current = documentId;
  }, [documentId]);

  useEffect(() => {
    renderSessionRef.current += 1;
    cancelAllRenderTasks();
    renderedPages.current = new Set();
    renderingPages.current = new Set();
    pageRefs.current = [];
    canvasRefs.current = [];
    lastCanvasNodeByPageRef.current = new Map();
    renderTaskStatusRef.current = new Map();
    setPageTextByIndex({});
  }, [documentId]);

  useEffect(() => {
    renderSessionRef.current += 1;
    cancelAllRenderTasks();
  }, [zoomLevel]);

  useEffect(() => {
    if (!contentRef.current) {
      return undefined;
    }

    const updateWidth = () => {
      setContainerWidth(contentRef.current?.clientWidth ?? 0);
    };
    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(contentRef.current);

    return () => {
      observer.disconnect();
    };
  }, [contentRef]);

  useEffect(() => {
    renderedPages.current = new Set();
    renderingPages.current = new Set();
  }, [zoomLevel, containerWidth, pdfDoc]);

  useEffect(() => {
    const renderSession = ++renderSessionRef.current;
    const sessionDocumentId = documentId;
    let cancelled = false;
    let retryCount = 0;
    let retryTimer: number | null = null;
    const MAX_CANVAS_RETRIES = 30;

    async function renderAllPages() {
      if (!pdfDoc || containerWidth <= 0 || totalPages <= 0) {
        return;
      }

      let missingCanvas = false;
      for (let pageIndex = 1; pageIndex <= pdfDoc.numPages; pageIndex += 1) {
        if (cancelled || renderSession !== renderSessionRef.current) {
          return;
        }

        const canvas = canvasRefs.current[pageIndex - 1];
        if (!canvas) {
          missingCanvas = true;
          continue;
        }
        if (renderedPages.current.has(pageIndex) || renderingPages.current.has(pageIndex)) {
          continue;
        }

        renderingPages.current.add(pageIndex);
        try {
          const page = await pdfDoc.getPage(pageIndex);
          if (cancelled || renderSession !== renderSessionRef.current) {
            return;
          }

          const viewport = page.getViewport({ scale: 1 });
          const fitWidthScale = containerWidth / viewport.width;
          const scale = Math.max(0.1, fitWidthScale * zoomLevel);
          const scaledViewport = page.getViewport({ scale });
          const expectedPage = pageIndex;
          const context = canvas.getContext("2d");
          if (!context) {
            continue;
          }

          const preRenderTransform =
            typeof context.getTransform === "function"
              ? context.getTransform().toString()
              : "unavailable";

          canvas.width = Math.max(1, Math.floor(scaledViewport.width));
          canvas.height = Math.max(1, Math.floor(scaledViewport.height));
          context.setTransform(1, 0, 0, 1, 0, 0);
          context.clearRect(0, 0, canvas.width, canvas.height);

          const existingTask = renderTasksByPageRef.current.get(pageIndex);
          if (existingTask) {
            try {
              existingTask.cancel();
            } catch {
              // ignore cancellation errors
            }
          }

          const renderTask = page.render({ canvasContext: context, viewport: scaledViewport });
          renderTasksByPageRef.current.set(pageIndex, renderTask);
          renderTaskStatusRef.current.set(pageIndex, "started");
          await renderTask.promise;
          renderTasksByPageRef.current.delete(pageIndex);
          renderTaskStatusRef.current.set(pageIndex, "completed");
          if (cancelled || renderSession !== renderSessionRef.current) {
            if (debugFlags.enabled) {
              console.debug("[PdfViewerDebug] stale-render-ignored", {
                reason: "session-mismatch",
                sessionAtStart: renderSession,
                sessionCurrent: renderSessionRef.current,
                documentIdAtStart: sessionDocumentId,
                documentIdCurrent: currentDocumentIdRef.current,
                pageIndex,
              });
            }
            return;
          }

          if (sessionDocumentId !== currentDocumentIdRef.current) {
            if (debugFlags.enabled) {
              console.debug("[PdfViewerDebug] stale-render-ignored", {
                reason: "document-mismatch",
                sessionAtStart: renderSession,
                sessionCurrent: renderSessionRef.current,
                documentIdAtStart: sessionDocumentId,
                documentIdCurrent: currentDocumentIdRef.current,
                pageIndex,
              });
            }
            return;
          }

          if (expectedPage !== pageIndex) {
            if (debugFlags.enabled) {
              console.debug("[PdfViewerDebug] stale-render-ignored", {
                reason: "page-mismatch",
                expectedPage,
                pageIndex,
                sessionAtStart: renderSession,
                sessionCurrent: renderSessionRef.current,
                documentIdAtStart: sessionDocumentId,
                documentIdCurrent: currentDocumentIdRef.current,
              });
            }
            return;
          }

          const postRenderTransform =
            typeof context.getTransform === "function"
              ? context.getTransform().toString()
              : "unavailable";

          if (debugFlags.enabled) {
            console.debug("[PdfViewerDebug] context-transform", {
              documentId,
              pageIndex,
              preRenderTransform,
              postRenderTransform,
              renderTaskStatus: renderTaskStatusRef.current.get(pageIndex),
            });
          }

          captureDebugSnapshot({
            reason: "page-render-finished",
            pageIndex,
            canvas,
            viewportScale: scale,
            viewportRotation: scaledViewport.rotation,
            renderTaskStatus: renderTaskStatusRef.current.get(pageIndex) ?? "unknown",
            debugFlags,
            nodeIdentityMap: nodeIdentityMapRef.current,
            nodeIdentityCounterRef,
            lastCanvasNodeByPage: lastCanvasNodeByPageRef.current,
            documentId,
            fileUrl,
            filename,
            pageNumber: pageNumberRef.current,
            zoomLevel,
            renderSession: renderSessionRef.current,
          });

          const latestSnapshots = (
            window as Window & {
              __pdfBugSnapshots?: Array<{ chainHasFlip?: boolean }>;
            }
          ).__pdfBugSnapshots;
          const latestSnapshot = latestSnapshots?.[latestSnapshots.length - 1];
          if (latestSnapshot?.chainHasFlip) {
            captureDebugSnapshot({
              reason: "flip-detected-transform-chain",
              pageIndex,
              canvas,
              viewportScale: scale,
              viewportRotation: scaledViewport.rotation,
              renderTaskStatus: renderTaskStatusRef.current.get(pageIndex) ?? "unknown",
              debugFlags,
              nodeIdentityMap: nodeIdentityMapRef.current,
              nodeIdentityCounterRef,
              lastCanvasNodeByPage: lastCanvasNodeByPageRef.current,
              documentId,
              fileUrl,
              filename,
              pageNumber: pageNumberRef.current,
              zoomLevel,
              renderSession: renderSessionRef.current,
            });
          }

          const textContent = await page.getTextContent();
          if (cancelled || renderSession !== renderSessionRef.current) {
            return;
          }
          const pageText = textContent.items
            .map((item) => {
              if (typeof item !== "object" || !("str" in item)) {
                return "";
              }
              const value = item.str;
              return typeof value === "string" ? value : "";
            })
            .join(" ")
            .replace(/\s+/g, " ")
            .trim();
          setPageTextByIndex((current) => ({ ...current, [pageIndex]: pageText }));
          renderedPages.current.add(pageIndex);
        } catch (error) {
          renderTasksByPageRef.current.delete(pageIndex);
          const errorName =
            typeof error === "object" && error && "name" in error
              ? String((error as { name?: unknown }).name)
              : "UnknownError";
          if (errorName === "RenderingCancelledException") {
            renderTaskStatusRef.current.set(pageIndex, "cancelled");
          } else {
            renderTaskStatusRef.current.set(pageIndex, "failed");
          }
          continue;
        } finally {
          renderingPages.current.delete(pageIndex);
        }
      }

      const allPagesRendered = renderedPages.current.size >= pdfDoc.numPages;
      if (
        !allPagesRendered &&
        missingCanvas &&
        retryCount < MAX_CANVAS_RETRIES &&
        !cancelled &&
        renderSession === renderSessionRef.current
      ) {
        retryCount += 1;
        retryTimer = window.setTimeout(() => {
          void renderAllPages();
        }, 50);
      }
    }

    void renderAllPages();

    return () => {
      cancelled = true;
      cancelAllRenderTasks();
      if (retryTimer) {
        window.clearTimeout(retryTimer);
      }
    };
  }, [
    pdfDoc,
    containerWidth,
    totalPages,
    zoomLevel,
    documentId,
    debugFlags.enabled,
    debugFlags,
    fileUrl,
    filename,
    pageNumberRef,
  ]);

  return {
    canvasRefs,
    pageRefs,
    pageTextByIndex,
    containerWidth,
    renderSessionRef,
    cancelAllRenderTasks,
  };
}
