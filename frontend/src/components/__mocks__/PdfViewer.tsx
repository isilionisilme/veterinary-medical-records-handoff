import type { ReactNode } from "react";
import { vi } from "vitest";

type MockPdfViewerProps = {
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

export const PdfViewer = vi.fn((props: MockPdfViewerProps) => (
  <>
    <div data-testid="pdf-viewer-toolbar-left">{props.toolbarLeftContent ?? null}</div>
    <div data-testid="pdf-viewer-toolbar-right">{props.toolbarRightExtra ?? null}</div>
    <div
      data-testid="pdf-viewer"
      data-document-id={props.documentId ?? ""}
      data-file-url={typeof props.fileUrl === "string" ? props.fileUrl : ""}
      data-filename={props.filename ?? ""}
      data-focus-page={String(props.focusPage ?? "")}
      data-highlight-snippet={props.highlightSnippet ?? ""}
      data-focus-request-id={String(props.focusRequestId ?? 0)}
    />
    <div
      data-testid="mock-pdf-viewer"
      data-document-id={props.documentId ?? ""}
      data-file-url={typeof props.fileUrl === "string" ? props.fileUrl : ""}
      data-filename={props.filename ?? ""}
      data-focus-page={String(props.focusPage ?? "")}
      data-highlight-snippet={props.highlightSnippet ?? ""}
      data-focus-request-id={String(props.focusRequestId ?? "")}
    />
  </>
));

export default PdfViewer;
