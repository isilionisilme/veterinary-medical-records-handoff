import { lazy, Suspense, type CSSProperties, type DragEventHandler, type ReactNode } from "react";

import { Button } from "../ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { type ProcessingHistoryRun } from "../../types";
import { type VisitScopingMetricsResponse } from "../../types";
import { RawTextTab } from "./RawTextTab";
import { TechnicalTab } from "./TechnicalTab";
import { UploadPanel } from "./UploadPanel";

const PdfViewer = lazy(() =>
  import("../PdfViewer").then((module) => ({ default: module.PdfViewer })),
);

type PdfViewerPanelProps = {
  activeViewerTab: "document" | "raw_text" | "technical";
  activeId: string | null;
  fileUrl: string | ArrayBuffer | null;
  filename: string | null;
  isDragOverViewer: boolean;
  onViewerDragEnter: DragEventHandler<HTMLDivElement>;
  onViewerDragOver: DragEventHandler<HTMLDivElement>;
  onViewerDragLeave: DragEventHandler<HTMLDivElement>;
  onViewerDrop: DragEventHandler<HTMLDivElement>;
  onOpenUploadArea: () => void;
  isDocumentListError: boolean;
  shouldShowLoadPdfErrorBanner: boolean;
  loadPdfErrorMessage: string;
  reviewSplitLayoutStyle: CSSProperties;
  onReviewSplitGridRef: (node: HTMLDivElement | null) => void;
  onStartReviewSplitDragging: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onResetReviewSplitRatio: () => void;
  onHandleReviewSplitKeyboard: (event: React.KeyboardEvent<HTMLButtonElement>) => void;
  effectiveViewMode: string;
  selectedReviewFieldEvidencePage: number | null;
  selectedReviewFieldEvidenceSnippet: string | null;
  fieldNavigationRequestId: number;
  viewerModeToolbarIcons: ReactNode;
  viewerDownloadIcon: ReactNode;
  structuredDataPanel: ReactNode;
  isPinnedSourcePanelVisible: boolean;
  sourcePanelContent: ReactNode;
  isSourceOpen: boolean;
  isSourcePinned: boolean;
  isDesktopForPin: boolean;
  isReviewMode: boolean;
  onCloseSourceOverlay: () => void;
  rawSearch: string;
  setRawSearch: (value: string) => void;
  canSearchRawText: boolean;
  hasRawText: boolean;
  rawSearchNotice: string | null;
  isRawTextLoading: boolean;
  rawTextErrorMessage: string | null;
  rawTextContent: string;
  onRawSearch: () => void;
  canCopyRawText: boolean;
  isCopyingRawText: boolean;
  copyFeedback: string | null;
  onCopyRawText: () => Promise<void>;
  onDownloadRawText: () => void;
  isActiveDocumentProcessing: boolean;
  reprocessPending: boolean;
  reprocessingDocumentId: string | null;
  hasObservedProcessingAfterReprocess: boolean;
  onOpenRetryModal: () => void;
  showRetryModal: boolean;
  onShowRetryModalChange: (open: boolean) => void;
  onConfirmRetry: () => void;
  processingHistoryIsLoading: boolean;
  processingHistoryIsError: boolean;
  processingHistoryErrorMessage: string;
  processingHistoryRuns: ProcessingHistoryRun[];
  visitScopingMetrics: VisitScopingMetricsResponse | null;
  visitScopingIsLoading: boolean;
  visitScopingIsError: boolean;
  visitScopingErrorMessage: string;
  expandedSteps: Record<string, boolean>;
  onToggleStepDetails: (stepKey: string) => void;
  formatRunHeader: (run: ProcessingHistoryRun) => string;
};

export function PdfViewerPanel({
  activeViewerTab,
  activeId,
  fileUrl,
  filename,
  isDragOverViewer,
  onViewerDragEnter,
  onViewerDragOver,
  onViewerDragLeave,
  onViewerDrop,
  onOpenUploadArea,
  isDocumentListError,
  shouldShowLoadPdfErrorBanner,
  loadPdfErrorMessage,
  reviewSplitLayoutStyle,
  onReviewSplitGridRef,
  onStartReviewSplitDragging,
  onResetReviewSplitRatio,
  onHandleReviewSplitKeyboard,
  effectiveViewMode,
  selectedReviewFieldEvidencePage,
  selectedReviewFieldEvidenceSnippet,
  fieldNavigationRequestId,
  viewerModeToolbarIcons,
  viewerDownloadIcon,
  structuredDataPanel,
  isPinnedSourcePanelVisible,
  sourcePanelContent,
  isSourceOpen,
  isSourcePinned,
  isDesktopForPin,
  isReviewMode,
  onCloseSourceOverlay,
  rawSearch,
  setRawSearch,
  canSearchRawText,
  hasRawText,
  rawSearchNotice,
  isRawTextLoading,
  rawTextErrorMessage,
  rawTextContent,
  onRawSearch,
  canCopyRawText,
  isCopyingRawText,
  copyFeedback,
  onCopyRawText,
  onDownloadRawText,
  isActiveDocumentProcessing,
  reprocessPending,
  reprocessingDocumentId,
  hasObservedProcessingAfterReprocess,
  onOpenRetryModal,
  showRetryModal,
  onShowRetryModalChange,
  onConfirmRetry,
  processingHistoryIsLoading,
  processingHistoryIsError,
  processingHistoryErrorMessage,
  processingHistoryRuns,
  visitScopingMetrics,
  visitScopingIsLoading,
  visitScopingIsError,
  visitScopingErrorMessage,
  expandedSteps,
  onToggleStepDetails,
  formatRunHeader,
}: PdfViewerPanelProps) {
  return (
    <>
      {shouldShowLoadPdfErrorBanner && (
        <div className="rounded-card border border-statusError bg-surface px-4 py-3 text-sm text-text">
          {loadPdfErrorMessage}
        </div>
      )}
      <div className="flex min-h-0 flex-1 flex-col">
        <div className="min-h-0 flex-1">
          {activeViewerTab === "document" && (
            <div
              data-testid="viewer-dropzone"
              className="h-full min-h-0"
              onDragEnter={onViewerDragEnter}
              onDragOver={onViewerDragOver}
              onDragLeave={onViewerDragLeave}
              onDrop={onViewerDrop}
            >
              {!activeId ? (
                <UploadPanel
                  isDocumentListError={isDocumentListError}
                  isDragOverViewer={isDragOverViewer}
                  onOpenUploadArea={onOpenUploadArea}
                  onViewerDragEnter={onViewerDragEnter}
                  onViewerDragOver={onViewerDragOver}
                  onViewerDragLeave={onViewerDragLeave}
                  onViewerDrop={onViewerDrop}
                />
              ) : (
                <div className="h-full min-h-0">
                  <div
                    data-testid="document-layout-grid"
                    className={`h-full min-h-0 overflow-x-auto ${
                      isPinnedSourcePanelVisible
                        ? "grid grid-cols-[minmax(0,1fr)_minmax(320px,400px)] gap-4"
                        : ""
                    }`}
                  >
                    <div
                      ref={onReviewSplitGridRef}
                      data-testid="review-split-grid"
                      className="grid h-full min-h-0 overflow-x-auto"
                      style={reviewSplitLayoutStyle}
                    >
                      <aside
                        data-testid="center-panel-scroll"
                        className="panel-shell-muted flex h-full min-h-0 min-w-[560px] flex-col gap-[var(--canvas-gap)] p-[var(--canvas-gap)]"
                      >
                        <div>
                          <h3 className="text-lg font-semibold text-textSecondary">Informe</h3>
                          <p className="mt-0.5 text-xs text-textSecondary">
                            Consulta el documento y navega por la evidencia asociada.
                          </p>
                        </div>
                        {fileUrl ? (
                          <Suspense
                            fallback={
                              <div className="flex h-full min-h-0 items-center justify-center text-sm text-textSecondary">
                                Cargando visor PDF...
                              </div>
                            }
                          >
                            <PdfViewer
                              key={`${effectiveViewMode}-${activeId ?? "empty"}`}
                              documentId={activeId}
                              fileUrl={fileUrl}
                              filename={filename}
                              isDragOver={isDragOverViewer}
                              focusPage={selectedReviewFieldEvidencePage}
                              highlightSnippet={selectedReviewFieldEvidenceSnippet}
                              focusRequestId={fieldNavigationRequestId}
                              toolbarLeftContent={viewerModeToolbarIcons}
                              toolbarRightExtra={viewerDownloadIcon}
                            />
                          </Suspense>
                        ) : (
                          <div className="flex h-full min-h-0 flex-col">
                            <div className="relative z-20 flex items-center justify-between gap-4 pb-3">
                              <div className="flex items-center gap-1">
                                {viewerModeToolbarIcons}
                              </div>
                              <div className="flex items-center gap-1">{viewerDownloadIcon}</div>
                            </div>
                            <div className="flex flex-1 items-center justify-center text-sm text-textSecondary">
                              No hay PDF disponible para este documento.
                            </div>
                          </div>
                        )}
                      </aside>
                      <div className="relative flex h-full min-h-0 items-stretch justify-center">
                        <button
                          type="button"
                          data-testid="review-split-handle"
                          aria-label="Redimensionar paneles de revisión"
                          title="Redimensionar paneles de revisión"
                          onMouseDown={onStartReviewSplitDragging}
                          onDoubleClick={onResetReviewSplitRatio}
                          onKeyDown={onHandleReviewSplitKeyboard}
                          className="group flex h-full w-full cursor-col-resize items-center justify-center rounded-full bg-transparent transition hover:bg-surfaceMuted focus-visible:bg-surfaceMuted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-accent"
                        >
                          <span
                            aria-hidden="true"
                            className="h-24 w-[2px] rounded-full bg-borderSubtle transition group-hover:bg-border"
                          />
                        </button>
                      </div>
                      {structuredDataPanel}
                    </div>
                    {isPinnedSourcePanelVisible && (
                      <aside data-testid="source-pinned-panel" className="min-h-0">
                        {sourcePanelContent}
                      </aside>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
          {activeViewerTab === "document" &&
            isSourceOpen &&
            (isReviewMode || !isSourcePinned || !isDesktopForPin) && (
              <>
                <button
                  type="button"
                  data-testid="source-drawer-backdrop"
                  className="fixed inset-0 z-40 bg-text/20"
                  aria-label="Cerrar fuente"
                  onClick={onCloseSourceOverlay}
                />
                <div
                  data-testid="source-drawer"
                  className="fixed inset-y-0 right-0 z-50 w-full max-w-xl p-4"
                  role="dialog"
                  aria-modal="true"
                  aria-label="Fuente"
                >
                  {sourcePanelContent}
                </div>
              </>
            )}
          {activeViewerTab === "raw_text" && (
            <RawTextTab
              viewerModeToolbarIcons={viewerModeToolbarIcons}
              viewerDownloadIcon={viewerDownloadIcon}
              activeId={activeId}
              isActiveDocumentProcessing={isActiveDocumentProcessing}
              reprocessPending={reprocessPending}
              reprocessingDocumentId={reprocessingDocumentId}
              hasObservedProcessingAfterReprocess={hasObservedProcessingAfterReprocess}
              onOpenRetryModal={onOpenRetryModal}
              rawSearch={rawSearch}
              setRawSearch={setRawSearch}
              canSearchRawText={canSearchRawText}
              hasRawText={hasRawText}
              rawSearchNotice={rawSearchNotice}
              isRawTextLoading={isRawTextLoading}
              rawTextErrorMessage={rawTextErrorMessage}
              rawTextContent={rawTextContent}
              onRawSearch={onRawSearch}
              canCopyRawText={canCopyRawText}
              isCopyingRawText={isCopyingRawText}
              copyFeedback={copyFeedback}
              onCopyRawText={onCopyRawText}
              onDownloadRawText={onDownloadRawText}
            />
          )}
          {activeViewerTab === "technical" && (
            <TechnicalTab
              viewerModeToolbarIcons={viewerModeToolbarIcons}
              viewerDownloadIcon={viewerDownloadIcon}
              activeId={activeId}
              isActiveDocumentProcessing={isActiveDocumentProcessing}
              reprocessPending={reprocessPending}
              onOpenRetryModal={onOpenRetryModal}
              processingHistoryIsLoading={processingHistoryIsLoading}
              processingHistoryIsError={processingHistoryIsError}
              processingHistoryErrorMessage={processingHistoryErrorMessage}
              processingHistoryRuns={processingHistoryRuns}
              expandedSteps={expandedSteps}
              onToggleStepDetails={onToggleStepDetails}
              formatRunHeader={formatRunHeader}
              visitScopingMetrics={visitScopingMetrics}
              visitScopingIsLoading={visitScopingIsLoading}
              visitScopingIsError={visitScopingIsError}
              visitScopingErrorMessage={visitScopingErrorMessage}
            />
          )}
        </div>
      </div>
      <Dialog open={showRetryModal} onOpenChange={onShowRetryModalChange}>
        <DialogContent data-testid="reprocess-confirm-modal" className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Reprocesar documento</DialogTitle>
            <DialogDescription className="text-xs">
              Esto volverá a ejecutar extracción e interpretación y puede cambiar los resultados.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="ghost" disabled={reprocessPending}>
                Cancelar
              </Button>
            </DialogClose>
            <Button
              data-testid="reprocess-confirm-btn"
              type="button"
              onClick={onConfirmRetry}
              disabled={reprocessPending}
            >
              {reprocessPending ? "Reprocesando..." : "Reprocesar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
