import { UploadDropzone } from "./UploadDropzone";

type UploadPanelProps = {
  isDragOver: boolean;
  isPending: boolean;
  onActivate: () => void;
  onDragEnter: React.DragEventHandler<HTMLDivElement>;
  onDragOver: React.DragEventHandler<HTMLDivElement>;
  onDragLeave: React.DragEventHandler<HTMLDivElement>;
  onDrop: React.DragEventHandler<HTMLDivElement>;
};

export function UploadPanel({
  isDragOver,
  isPending,
  onActivate,
  onDragEnter,
  onDragOver,
  onDragLeave,
  onDrop,
}: UploadPanelProps) {
  return (
    <div className="w-full" data-testid="upload-panel">
      <UploadDropzone
        isDragOver={isDragOver}
        onActivate={(event) => {
          event.preventDefault();
          onActivate();
        }}
        onDragEnter={onDragEnter}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      />
      {isPending ? <p className="mt-2 text-xs text-textSecondary">Subiendo...</p> : null}
    </div>
  );
}
