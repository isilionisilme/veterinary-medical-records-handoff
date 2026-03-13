import { lazy, Suspense } from "react";

import { SourcePanel } from "../SourcePanel";

const PdfViewer = lazy(() =>
  import("../PdfViewer").then((module) => ({ default: module.PdfViewer })),
);

type SourcePanelContentProps = {
  sourcePage: number | null;
  sourceSnippet: string | null;
  isSourcePinned: boolean;
  isDesktopForPin: boolean;
  onTogglePin: () => void;
  onClose: () => void;
  fileUrl: string | ArrayBuffer | null;
  activeId: string | null;
  filename: string | null;
  focusRequestId: number;
};

export function SourcePanelContent({
  sourcePage,
  sourceSnippet,
  isSourcePinned,
  isDesktopForPin,
  onTogglePin,
  onClose,
  fileUrl,
  activeId,
  filename,
  focusRequestId,
}: SourcePanelContentProps) {
  return (
    <SourcePanel
      sourcePage={sourcePage}
      sourceSnippet={sourceSnippet}
      isSourcePinned={isSourcePinned}
      isDesktopForPin={isDesktopForPin}
      onTogglePin={onTogglePin}
      onClose={onClose}
      content={
        fileUrl ? (
          <Suspense
            fallback={
              <div className="flex h-40 items-center justify-center text-sm text-muted">
                Cargando visor PDF...
              </div>
            }
          >
            <PdfViewer
              key={`source-${activeId ?? "empty"}`}
              documentId={activeId}
              fileUrl={fileUrl}
              filename={filename}
              isDragOver={false}
              focusPage={sourcePage}
              highlightSnippet={sourceSnippet}
              focusRequestId={focusRequestId}
            />
          </Suspense>
        ) : (
          <div className="flex h-40 items-center justify-center text-sm text-muted">
            No hay PDF disponible para este documento.
          </div>
        )
      }
    />
  );
}
