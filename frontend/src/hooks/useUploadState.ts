import { type ChangeEvent, type DragEvent, useCallback, useRef, useState } from "react";

import { type UploadFeedback } from "../components/toast/toast-types";

type OpenUploadEvent = { preventDefault?: () => void; stopPropagation?: () => void };
type UseUploadStateParams = {
  isUploadPending: boolean;
  maxUploadSizeBytes: number;
  onQueueUpload: (file: File) => void;
  onSetUploadFeedback: (feedback: UploadFeedback | null) => void;
  onSidebarUploadDrop?: () => void;
};

export function useUploadState({
  isUploadPending,
  maxUploadSizeBytes,
  onQueueUpload,
  onSetUploadFeedback,
  onSidebarUploadDrop,
}: UseUploadStateParams) {
  const [isDragOverViewer, setIsDragOverViewer] = useState(false);
  const [isDragOverSidebarUpload, setIsDragOverSidebarUpload] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const uploadPanelRef = useRef<HTMLDivElement | null>(null);
  const viewerDragDepthRef = useRef(0);
  const sidebarUploadDragDepthRef = useRef(0);

  const queueUpload = useCallback(
    (file: File) => {
      if (isUploadPending) return false;
      const hasPdfMime = file.type === "application/pdf";
      const hasPdfExtension = file.name.toLowerCase().endsWith(".pdf");
      if (!hasPdfMime && !hasPdfExtension) {
        onSetUploadFeedback({ kind: "error", message: "Solo se admiten archivos PDF." });
        return false;
      }
      if (file.size > maxUploadSizeBytes) {
        onSetUploadFeedback({
          kind: "error",
          message: "El archivo supera el tamaño máximo (20 MB).",
        });
        return false;
      }
      onSetUploadFeedback(null);
      onQueueUpload(file);
      return true;
    },
    [isUploadPending, maxUploadSizeBytes, onQueueUpload, onSetUploadFeedback],
  );

  const handleViewerDragEnter = useCallback((event: DragEvent<HTMLDivElement>) => {
    if (!event.dataTransfer.types.includes("Files")) return;
    event.preventDefault();
    event.stopPropagation();
    viewerDragDepthRef.current += 1;
    setIsDragOverViewer(true);
  }, []);

  const handleViewerDragOver = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      if (!event.dataTransfer.types.includes("Files")) return;
      event.preventDefault();
      event.stopPropagation();
      if (!isDragOverViewer) setIsDragOverViewer(true);
    },
    [isDragOverViewer],
  );

  const handleViewerDragLeave = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    viewerDragDepthRef.current = Math.max(0, viewerDragDepthRef.current - 1);
    if (viewerDragDepthRef.current === 0) setIsDragOverViewer(false);
  }, []);

  const handleViewerDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      viewerDragDepthRef.current = 0;
      setIsDragOverViewer(false);
      const file = event.dataTransfer.files?.[0];
      if (file) queueUpload(file);
    },
    [queueUpload],
  );

  const handleSidebarUploadDragEnter = useCallback((event: DragEvent<HTMLDivElement>) => {
    if (!event.dataTransfer.types.includes("Files")) return;
    event.preventDefault();
    event.stopPropagation();
    sidebarUploadDragDepthRef.current += 1;
    setIsDragOverSidebarUpload(true);
  }, []);

  const handleSidebarUploadDragOver = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      if (!event.dataTransfer.types.includes("Files")) return;
      event.preventDefault();
      event.stopPropagation();
      if (!isDragOverSidebarUpload) setIsDragOverSidebarUpload(true);
    },
    [isDragOverSidebarUpload],
  );

  const handleSidebarUploadDragLeave = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    sidebarUploadDragDepthRef.current = Math.max(0, sidebarUploadDragDepthRef.current - 1);
    if (sidebarUploadDragDepthRef.current === 0) setIsDragOverSidebarUpload(false);
  }, []);

  const handleSidebarUploadDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      sidebarUploadDragDepthRef.current = 0;
      setIsDragOverSidebarUpload(false);
      onSidebarUploadDrop?.();
      const file = event.dataTransfer.files?.[0];
      if (file) queueUpload(file);
    },
    [onSidebarUploadDrop, queueUpload],
  );

  const handleOpenUploadArea = useCallback(
    (event?: OpenUploadEvent) => {
      event?.stopPropagation?.();
      if (!isUploadPending) fileInputRef.current?.click();
    },
    [isUploadPending],
  );

  const handleSidebarFileInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0] ?? null;
      if (!file) {
        onSetUploadFeedback(null);
        return;
      }
      if (!queueUpload(file)) event.currentTarget.value = "";
    },
    [onSetUploadFeedback, queueUpload],
  );

  return {
    fileInputRef,
    uploadPanelRef,
    isDragOverViewer,
    isDragOverSidebarUpload,
    sidebarUploadDragDepthRef,
    handleViewerDragEnter,
    handleViewerDragOver,
    handleViewerDragLeave,
    handleViewerDrop,
    handleSidebarUploadDragEnter,
    handleSidebarUploadDragOver,
    handleSidebarUploadDragLeave,
    handleSidebarUploadDrop,
    handleOpenUploadArea,
    handleSidebarFileInputChange,
  };
}
