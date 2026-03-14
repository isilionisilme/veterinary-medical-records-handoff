import type { ReactNode } from "react";

import { Button } from "../ui/button";

type RawTextTabProps = {
  viewerModeToolbarIcons: ReactNode;
  viewerDownloadIcon: ReactNode;
  activeId: string | null;
  isActiveDocumentProcessing: boolean;
  reprocessPending: boolean;
  reprocessingDocumentId: string | null;
  hasObservedProcessingAfterReprocess: boolean;
  onOpenRetryModal: () => void;
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
};

export function RawTextTab({
  viewerModeToolbarIcons,
  viewerDownloadIcon,
  activeId,
  isActiveDocumentProcessing,
  reprocessPending,
  reprocessingDocumentId,
  hasObservedProcessingAfterReprocess,
  onOpenRetryModal,
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
}: RawTextTabProps) {
  return (
    <div className="flex h-full flex-col rounded-card border border-borderSubtle bg-surface p-4">
      <div className="rounded-control border border-borderSubtle bg-surface px-2 py-2">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1">{viewerModeToolbarIcons}</div>
          <div className="flex items-center gap-1">{viewerDownloadIcon}</div>
        </div>
      </div>
      <div className="rounded-card border border-borderSubtle bg-surface p-3">
        <div className="flex flex-col gap-2 text-xs text-ink">
          <span className="text-textSecondary">
            ¿El texto no es correcto? Puedes reprocesarlo para regenerar la extracción.
          </span>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              disabled={!activeId || isActiveDocumentProcessing || reprocessPending}
              onClick={onOpenRetryModal}
            >
              {reprocessPending ||
              (Boolean(activeId) &&
                reprocessingDocumentId === activeId &&
                (!hasObservedProcessingAfterReprocess || isActiveDocumentProcessing))
                ? "Reprocesando..."
                : isActiveDocumentProcessing
                  ? "Procesando..."
                  : "Reprocesar"}
            </Button>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <input
          data-testid="raw-text-search-input"
          className="w-full rounded-control border border-borderSubtle bg-surface px-3 py-2 text-xs text-text outline-none placeholder:text-textSecondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent sm:w-64"
          placeholder="Buscar en el texto"
          value={rawSearch}
          disabled={!canSearchRawText}
          onChange={(event) => setRawSearch(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              onRawSearch();
            }
          }}
        />
        <Button type="button" disabled={!canSearchRawText} onClick={onRawSearch}>
          Buscar
        </Button>
        <Button
          data-testid="raw-text-copy"
          type="button"
          disabled={!canCopyRawText || isCopyingRawText}
          onClick={() => {
            void onCopyRawText();
          }}
        >
          {isCopyingRawText
            ? "Copiando..."
            : copyFeedback === "Texto copiado."
              ? "Copiado"
              : "Copiar todo"}
        </Button>
        <Button
          data-testid="raw-text-download"
          type="button"
          disabled={!rawTextContent}
          onClick={onDownloadRawText}
        >
          Descargar texto (.txt)
        </Button>
      </div>
      {copyFeedback && (
        <p className="mt-2 text-xs text-textSecondary" role="status" aria-live="polite">
          {copyFeedback}
        </p>
      )}
      {hasRawText && rawSearchNotice && (
        <p className="mt-2 text-xs text-textSecondary">{rawSearchNotice}</p>
      )}
      {isRawTextLoading && (
        <p className="mt-2 text-xs text-textSecondary">Cargando texto extraído...</p>
      )}
      {rawTextErrorMessage && (
        <p className="mt-2 text-xs text-statusError">{rawTextErrorMessage}</p>
      )}
      <div className="mt-3 flex-1 overflow-y-auto rounded-card border border-borderSubtle bg-surface p-3 font-mono text-xs text-textSecondary">
        {rawTextContent ? <pre>{rawTextContent}</pre> : "Sin texto extraído."}
      </div>
    </div>
  );
}
