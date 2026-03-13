import type { DragEventHandler } from "react";

import { UploadDropzone } from "../UploadDropzone";

type UploadPanelProps = {
  isDocumentListError: boolean;
  isDragOverViewer: boolean;
  onOpenUploadArea: () => void;
  onViewerDragEnter: DragEventHandler<HTMLDivElement>;
  onViewerDragOver: DragEventHandler<HTMLDivElement>;
  onViewerDragLeave: DragEventHandler<HTMLDivElement>;
  onViewerDrop: DragEventHandler<HTMLDivElement>;
};

export function UploadPanel({
  isDocumentListError,
  isDragOverViewer,
  onOpenUploadArea,
  onViewerDragEnter,
  onViewerDragOver,
  onViewerDragLeave,
  onViewerDrop,
}: UploadPanelProps) {
  if (isDocumentListError) {
    return (
      <div className="flex h-full flex-col rounded-card bg-surface p-6">
        <div className="flex flex-1 items-center justify-center text-center">
          <p className="text-sm text-muted">
            Revisa la lista lateral para reintentar la carga de documentos.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="viewer-empty-state"
      className="relative flex h-full flex-col rounded-card bg-surfaceMuted p-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      role="button"
      aria-label="Cargar documento"
      tabIndex={0}
      onClick={onOpenUploadArea}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onOpenUploadArea();
        }
      }}
    >
      <div className="flex flex-1 flex-col items-center justify-center text-center">
        <p className="text-sm text-muted">
          Selecciona un documento en la barra lateral o carga uno nuevo.
        </p>
        <UploadDropzone
          className="mt-4 w-full max-w-sm"
          isDragOver={isDragOverViewer}
          onActivate={onOpenUploadArea}
          onDragEnter={onViewerDragEnter}
          onDragOver={onViewerDragOver}
          onDragLeave={onViewerDragLeave}
          onDrop={onViewerDrop}
          showDropOverlay
        />
      </div>
    </div>
  );
}
