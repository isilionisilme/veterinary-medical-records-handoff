import type { DragEvent, KeyboardEvent, MouseEvent } from "react";
import { Upload } from "lucide-react";

type UploadDropzoneProps = {
  isDragOver: boolean;
  onActivate: (event: MouseEvent<HTMLDivElement> | KeyboardEvent<HTMLDivElement>) => void;
  onDragEnter: (event: DragEvent<HTMLDivElement>) => void;
  onDragOver: (event: DragEvent<HTMLDivElement>) => void;
  onDragLeave: (event: DragEvent<HTMLDivElement>) => void;
  onDrop: (event: DragEvent<HTMLDivElement>) => void;
  showDropOverlay?: boolean;
  className?: string;
  title?: string;
  subtitle?: string;
  compact?: boolean;
  ariaLabel?: string;
};

export function UploadDropzone({
  isDragOver,
  onActivate,
  onDragEnter,
  onDragOver,
  onDragLeave,
  onDrop,
  showDropOverlay = false,
  className = "",
  title = "Arrastra un PDF aquí",
  subtitle = "o haz clic para cargar",
  compact = false,
  ariaLabel,
}: UploadDropzoneProps) {
  const resolvedAriaLabel =
    ariaLabel ?? (compact ? "Cargar documento" : `${title} ${subtitle}`.trim());
  const isOverlayActive = showDropOverlay && isDragOver;

  return (
    <div
      data-testid="upload-dropzone"
      className={`relative flex cursor-pointer flex-col items-center justify-center rounded-card text-center transition ${
        isDragOver
          ? isOverlayActive
            ? "border-2 border-dashed border-transparent bg-surface"
            : "border-2 border-dashed border-statusSuccess bg-statusSuccess/10"
          : "border-2 border-dashed border-borderSubtle bg-surface hover:border-textSecondary/40"
      } ${compact ? "h-12 w-12 rounded-control px-1.5 py-1.5" : "px-4 py-5"} ${className}`}
      role="button"
      aria-label={resolvedAriaLabel}
      tabIndex={0}
      onClick={onActivate}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onActivate(event);
        }
      }}
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {showDropOverlay && isDragOver && (
        <div className="pointer-events-none absolute inset-2 z-10 flex flex-col items-center justify-center gap-2 rounded-control border-2 border-dashed border-statusSuccess bg-surface/75 backdrop-blur-[1px]">
          <Upload size={18} className="text-statusSuccess" aria-hidden="true" />
          <p className="text-sm font-semibold text-ink">Suelta el PDF para subirlo</p>
        </div>
      )}
      <Upload
        size={compact ? 16 : 18}
        className="pointer-events-none text-ink"
        aria-hidden="true"
      />
      {!compact && (
        <>
          <p className="mt-2 text-sm font-semibold text-ink">{title}</p>
          <p className="text-xs text-muted">{subtitle}</p>
        </>
      )}
    </div>
  );
}
