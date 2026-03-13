import { type MouseEvent, type ReactNode } from "react";
import { ChevronLeft, ChevronRight, ScanLine, ZoomIn, ZoomOut } from "lucide-react";
import { IconButton } from "./app/IconButton";
import { Tooltip } from "./ui/tooltip";

type PdfViewerToolbarProps = {
  toolbarLeftContent?: ReactNode;
  toolbarRightExtra?: ReactNode;
  canZoomIn: boolean;
  canZoomOut: boolean;
  zoomPercent: number;
  onZoomIn: (event?: MouseEvent<HTMLButtonElement>) => void;
  onZoomOut: (event?: MouseEvent<HTMLButtonElement>) => void;
  onZoomFit: (event?: MouseEvent<HTMLButtonElement>) => void;
  navDisabled: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
  pageNumber: number;
  totalPages: number;
  onPrevPage: () => void;
  onNextPage: () => void;
};

export function PdfViewerToolbar({
  toolbarLeftContent,
  toolbarRightExtra,
  canZoomIn,
  canZoomOut,
  zoomPercent,
  onZoomIn,
  onZoomOut,
  onZoomFit,
  navDisabled,
  canGoBack,
  canGoForward,
  pageNumber,
  totalPages,
  onPrevPage,
  onNextPage,
}: PdfViewerToolbarProps) {
  return (
    <div
      data-testid="pdf-toolbar-shell"
      className="panel-shell relative z-20 flex items-center justify-between gap-4 px-2 py-2"
    >
      <div className="flex min-w-0 items-center gap-1">{toolbarLeftContent}</div>

      <div className="flex items-center gap-1">
        <IconButton
          label="Alejar"
          tooltip="Alejar"
          data-testid="pdf-zoom-out"
          disabled={!canZoomOut}
          onClick={onZoomOut}
        >
          <ZoomOut size={17} className="h-[17px] w-[17px] shrink-0" />
        </IconButton>

        <Tooltip content="Nivel de zoom">
          <p
            className="min-w-14 text-center text-sm font-semibold text-textSecondary"
            aria-label="Nivel de zoom"
            data-testid="pdf-zoom-indicator"
          >
            {zoomPercent}%
          </p>
        </Tooltip>

        <IconButton
          label="Acercar"
          tooltip="Acercar"
          data-testid="pdf-zoom-in"
          disabled={!canZoomIn}
          onClick={onZoomIn}
        >
          <ZoomIn size={17} className="h-[17px] w-[17px] shrink-0" />
        </IconButton>

        <IconButton
          label="Ajustar al ancho"
          tooltip="Ajustar al ancho"
          data-testid="pdf-zoom-fit"
          onClick={onZoomFit}
        >
          <ScanLine size={17} className="h-[17px] w-[17px] shrink-0" />
        </IconButton>
      </div>

      <span aria-hidden="true" className="h-5 w-px bg-page" />

      <div className="flex items-center gap-1">
        <IconButton
          label="Página anterior"
          tooltip="Página anterior"
          data-testid="pdf-page-prev"
          disabled={navDisabled || !canGoBack}
          onClick={onPrevPage}
        >
          <ChevronLeft size={18} className="h-[18px] w-[18px] shrink-0" />
        </IconButton>
        <p
          className="min-w-12 text-center text-sm font-semibold text-textSecondary"
          data-testid="pdf-page-indicator"
        >
          {pageNumber}/{totalPages}
        </p>
        <IconButton
          label="Página siguiente"
          tooltip="Página siguiente"
          data-testid="pdf-page-next"
          disabled={navDisabled || !canGoForward}
          onClick={onNextPage}
        >
          <ChevronRight size={18} className="h-[18px] w-[18px] shrink-0" />
        </IconButton>
      </div>

      {toolbarRightExtra ? (
        <>
          <span aria-hidden="true" className="h-5 w-px bg-page" />
          <div className="flex items-center gap-1">{toolbarRightExtra}</div>
        </>
      ) : null}
    </div>
  );
}
