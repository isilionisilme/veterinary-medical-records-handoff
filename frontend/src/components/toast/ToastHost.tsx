import { IconButton } from "../app/IconButton";
import type { ActionFeedback, ConnectivityToast, UploadFeedback } from "./toast-types";

type ToastHostProps = {
  connectivityToast: ConnectivityToast | null;
  uploadFeedback: UploadFeedback | null;
  actionFeedback: ActionFeedback | null;
  onCloseConnectivityToast: () => void;
  onCloseUploadFeedback: () => void;
  onCloseActionFeedback: () => void;
  onOpenUploadedDocument: (documentId: string) => void;
};

const TOAST_CONTAINER_BASE_CLASS =
  "fixed left-1/2 z-[60] w-full max-w-lg -translate-x-1/2 px-4 sm:w-[32rem]";
const TOAST_BASE_CLASS = "rounded-2xl border px-5 py-4 shadow-subtle";

function getToastKindClass(kind: "success" | "info" | "error"): string {
  if (kind === "success") {
    return "border-statusSuccess text-text";
  }
  if (kind === "info") {
    return "border-accent text-text";
  }
  return "border-statusError text-statusError";
}

function getToastKindBackground(kind: "success" | "info" | "error"): React.CSSProperties {
  if (kind === "success") {
    return { backgroundColor: "var(--status-success-bg)" };
  }
  if (kind === "info") {
    return { backgroundColor: "var(--status-info-bg)" };
  }
  return { backgroundColor: "var(--status-error-bg)" };
}

function getUploadToastTopClass(hasConnectivityToast: boolean): string {
  return hasConnectivityToast ? "top-28" : "top-10";
}

function getActionToastTopClass(hasConnectivityToast: boolean): string {
  return hasConnectivityToast ? "top-44" : "top-28";
}

export function ToastHost({
  connectivityToast,
  uploadFeedback,
  actionFeedback,
  onCloseConnectivityToast,
  onCloseUploadFeedback,
  onCloseActionFeedback,
  onOpenUploadedDocument,
}: ToastHostProps) {
  const uploadToastKind = uploadFeedback?.kind ?? "success";
  const actionToastKind = actionFeedback?.kind ?? "info";

  return (
    <div data-testid="toast-host">
      {connectivityToast && (
        <div
          data-testid="toast-connectivity"
          className="fixed left-1/2 top-10 z-[65] w-full max-w-lg -translate-x-1/2 px-4 sm:w-[32rem]"
        >
          <div
            className={`${TOAST_BASE_CLASS} ${getToastKindClass("error")}`}
            style={getToastKindBackground("error")}
            role="alert"
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm">No se pudo conectar con el servidor.</p>
              <IconButton
                label="Cerrar aviso de conexión"
                onClick={onCloseConnectivityToast}
                className="text-lg font-semibold leading-none"
              >
                &times;
              </IconButton>
            </div>
          </div>
        </div>
      )}
      {uploadFeedback && (
        <div
          data-testid={`toast-${uploadToastKind}`}
          className={`${TOAST_CONTAINER_BASE_CLASS} ${getUploadToastTopClass(Boolean(connectivityToast))}`}
        >
          <div
            className={`${TOAST_BASE_CLASS} text-base ${getToastKindClass(
              uploadFeedback.kind === "success" ? "success" : "error",
            )}`}
            style={getToastKindBackground(uploadFeedback.kind === "success" ? "success" : "error")}
            role={uploadFeedback.kind === "error" ? "alert" : "status"}
          >
            <div className="flex items-center justify-between gap-3">
              <span>{uploadFeedback.message}</span>
              <IconButton
                label="Cerrar notificación"
                onClick={onCloseUploadFeedback}
                className="text-lg font-semibold leading-none text-ink"
              >
                &times;
              </IconButton>
            </div>
            {uploadFeedback.kind === "success" &&
              uploadFeedback.documentId &&
              uploadFeedback.showOpenAction && (
                <button
                  type="button"
                  className="mt-2 text-xs font-semibold text-ink underline"
                  onClick={() => onOpenUploadedDocument(uploadFeedback.documentId!)}
                >
                  Ver documento
                </button>
              )}
            {uploadFeedback.kind === "error" && (
              <div className="mt-2 flex items-center gap-3">
                {uploadFeedback.technicalDetails && (
                  <details className="text-xs text-muted">
                    <summary className="cursor-pointer">Ver detalles técnicos</summary>
                    <p className="mt-1">{uploadFeedback.technicalDetails}</p>
                  </details>
                )}
              </div>
            )}
          </div>
        </div>
      )}
      {actionFeedback && (
        <div
          data-testid={`toast-${actionToastKind}`}
          className={`${TOAST_CONTAINER_BASE_CLASS} ${getActionToastTopClass(Boolean(connectivityToast))}`}
        >
          <div
            className={`${TOAST_BASE_CLASS} text-base ${getToastKindClass(
              actionFeedback.kind === "success"
                ? "success"
                : actionFeedback.kind === "info"
                  ? "info"
                  : "error",
            )}`}
            style={getToastKindBackground(
              actionFeedback.kind === "success"
                ? "success"
                : actionFeedback.kind === "info"
                  ? "info"
                  : "error",
            )}
            role={actionFeedback.kind === "error" ? "alert" : "status"}
          >
            <div className="flex items-center justify-between gap-3">
              <span>{actionFeedback.message}</span>
              <IconButton
                label="Cerrar notificación de acción"
                onClick={onCloseActionFeedback}
                className="text-lg font-semibold leading-none text-ink"
              >
                &times;
              </IconButton>
            </div>
            {actionFeedback.kind === "error" && actionFeedback.technicalDetails && (
              <div className="mt-2 flex items-center gap-3">
                <details className="text-xs text-muted">
                  <summary className="cursor-pointer">Ver detalles técnicos</summary>
                  <p className="mt-1">{actionFeedback.technicalDetails}</p>
                </details>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
