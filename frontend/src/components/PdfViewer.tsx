import { type ReactNode, useCallback, useEffect, useMemo, useRef } from "react";
import { Upload } from "lucide-react";
import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorkerUrl from "pdfjs-dist/build/pdf.worker.mjs?url";
import { usePdfDocument } from "../hooks/usePdfDocument";
import { usePdfNavigation } from "../hooks/usePdfNavigation";
import { usePdfRenderer } from "../hooks/usePdfRenderer";
import { createDebugFlags } from "../lib/pdfDebug";
import { usePdfZoom } from "../hooks/usePdfZoom";
import { PdfViewerToolbar } from "./PdfViewerToolbar";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorkerUrl;

type PdfViewerProps = {
  documentId?: string | null;
  fileUrl: string | ArrayBuffer | null;
  filename?: string | null;
  isDragOver?: boolean;
  focusPage?: number | null;
  highlightSnippet?: string | null;
  focusRequestId?: number;
  toolbarLeftContent?: ReactNode;
  toolbarRightExtra?: ReactNode;
};

export function PdfViewer({
  documentId = null,
  fileUrl,
  filename,
  isDragOver = false,
  focusPage = null,
  highlightSnippet = null,
  focusRequestId = 0,
  toolbarLeftContent,
  toolbarRightExtra,
}: PdfViewerProps) {
  const debugFlags = useMemo(() => createDebugFlags(), []);

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const contentRef = useRef<HTMLDivElement | null>(null);
  const pageNumberRef = useRef(1);
  const cancelAllRenderTasksRef = useRef<() => void>(() => {});
  const {
    zoomLevel,
    canZoomIn,
    canZoomOut,
    zoomPercent,
    handleZoomIn,
    handleZoomOut,
    handleZoomFit,
  } = usePdfZoom({ scrollRef });
  const handleCancelAllRenderTasks = useCallback(() => {
    cancelAllRenderTasksRef.current();
  }, []);

  const { pdfDoc, totalPages, loading, error } = usePdfDocument({
    fileUrl,
    scrollRef,
    cancelAllRenderTasks: handleCancelAllRenderTasks,
  });

  const { canvasRefs, pageRefs, pageTextByIndex, cancelAllRenderTasks } = usePdfRenderer({
    pdfDoc,
    totalPages,
    zoomLevel,
    documentId,
    contentRef,
    debugFlags,
    fileUrl,
    filename,
    pageNumberRef,
  });
  cancelAllRenderTasksRef.current = cancelAllRenderTasks;

  const {
    pageNumber,
    canGoBack,
    canGoForward,
    showPageNavigation,
    isSnippetLocated,
    scrollToPage,
  } = usePdfNavigation({
    pdfDoc,
    totalPages,
    loading,
    error,
    fileUrl,
    focusPage,
    highlightSnippet,
    focusRequestId,
    scrollRef,
    pageRefs,
    pageTextByIndex,
  });
  pageNumberRef.current = pageNumber;

  useEffect(() => {
    if (!debugFlags.enabled || !debugFlags.noMotion || typeof document === "undefined") {
      return;
    }
    document.body.classList.add("pdf-debug-no-motion");
    return () => {
      document.body.classList.remove("pdf-debug-no-motion");
    };
  }, [debugFlags.enabled, debugFlags.noMotion]);

  const pages = useMemo(
    () => Array.from({ length: totalPages }, (_, index) => index + 1),
    [totalPages],
  );
  const navDisabled = loading || !pdfDoc;

  return (
    <div
      className={`flex h-full min-h-0 flex-col gap-[var(--canvas-gap)] ${
        debugFlags.enabled && debugFlags.noTransformSubtree ? "pdf-debug-no-transform-subtree" : ""
      }`}
      data-pdf-debug={debugFlags.enabled ? "on" : "off"}
    >
      {showPageNavigation && (
        <PdfViewerToolbar
          toolbarLeftContent={toolbarLeftContent}
          toolbarRightExtra={toolbarRightExtra}
          canZoomIn={canZoomIn}
          canZoomOut={canZoomOut}
          zoomPercent={zoomPercent}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onZoomFit={handleZoomFit}
          navDisabled={navDisabled}
          canGoBack={canGoBack}
          canGoForward={canGoForward}
          pageNumber={pageNumber}
          totalPages={totalPages}
          onPrevPage={() => scrollToPage(Math.max(1, pageNumber - 1))}
          onNextPage={() => scrollToPage(Math.min(totalPages, pageNumber + 1))}
        />
      )}
      <div className="relative min-h-0 flex-1">
        <div
          ref={scrollRef}
          data-testid="pdf-scroll-container"
          className="panel-shell h-full min-h-0 overflow-y-auto p-[var(--canvas-gap)]"
        >
          <div ref={contentRef} className="mx-auto w-full">
            {loading && (
              <div className="flex h-72 items-center justify-center text-sm text-muted">
                Cargando PDF...
              </div>
            )}
            {error && (
              <div className="flex h-72 items-center justify-center text-sm text-statusError">
                {error}
              </div>
            )}
            {!loading &&
              !error &&
              fileUrl &&
              pages.map((page) => (
                <div
                  key={
                    debugFlags.enabled && debugFlags.hardRemountCanvas
                      ? `${documentId ?? fileUrl ?? "unknown"}:${page}:${zoomLevel}:0`
                      : `${documentId ?? fileUrl ?? "unknown"}:${page}`
                  }
                  ref={(node) => {
                    pageRefs.current[page - 1] = node;
                  }}
                  data-page-index={page}
                  data-testid="pdf-page"
                  className={`mb-6 last:mb-0 ${
                    focusPage === page && isSnippetLocated ? "rounded-card bg-accent/10 p-1" : ""
                  }`}
                >
                  <canvas
                    ref={(node) => {
                      canvasRefs.current[page - 1] = node;
                    }}
                    className="mx-auto rounded-card bg-surface"
                  />
                </div>
              ))}
            {!fileUrl && !loading && (
              <div className="flex h-72 items-center justify-center text-sm text-muted">
                Selecciona un documento para iniciar la vista previa.
              </div>
            )}
          </div>
        </div>
        {isDragOver && (
          <div className="pointer-events-none absolute inset-3 z-10 flex flex-col items-center justify-center gap-2 rounded-card border-2 border-dashed border-statusSuccess bg-surface/75 backdrop-blur-[1px]">
            <Upload size={20} className="text-statusSuccess" aria-hidden="true" />
            <p className="text-sm font-semibold text-ink">Suelta el PDF para subirlo</p>
          </div>
        )}
      </div>
    </div>
  );
}
