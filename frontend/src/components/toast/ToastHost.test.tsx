import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ToastHost } from "./ToastHost";
import type { ActionFeedback, ConnectivityToast, UploadFeedback } from "./toast-types";

function renderToastHost(options?: {
  connectivityToast?: ConnectivityToast | null;
  uploadFeedback?: UploadFeedback | null;
  actionFeedback?: ActionFeedback | null;
}) {
  const onCloseConnectivityToast = vi.fn();
  const onCloseUploadFeedback = vi.fn();
  const onCloseActionFeedback = vi.fn();
  const onOpenUploadedDocument = vi.fn();

  const connectivityToast = options?.connectivityToast ?? null;
  const uploadFeedback = options?.uploadFeedback ?? null;
  const actionFeedback = options?.actionFeedback ?? null;

  render(
    <ToastHost
      connectivityToast={connectivityToast}
      uploadFeedback={uploadFeedback}
      actionFeedback={actionFeedback}
      onCloseConnectivityToast={onCloseConnectivityToast}
      onCloseUploadFeedback={onCloseUploadFeedback}
      onCloseActionFeedback={onCloseActionFeedback}
      onOpenUploadedDocument={onOpenUploadedDocument}
    />,
  );

  return {
    onCloseConnectivityToast,
    onCloseUploadFeedback,
    onCloseActionFeedback,
    onOpenUploadedDocument,
  };
}

describe("ToastHost", () => {
  it("applies semantic border classes and stacked positions when connectivity toast is visible", () => {
    renderToastHost({
      connectivityToast: {},
      uploadFeedback: {
        kind: "success",
        message: "Documento cargado correctamente.",
        documentId: "doc-1",
        showOpenAction: true,
      },
      actionFeedback: {
        kind: "info",
        message: "Documento revisado: usa Reabrir para habilitar edición.",
      },
    });

    const connectivityStatus = screen
      .getByText("No se pudo conectar con el servidor.")
      .closest('[role="alert"]');
    expect(connectivityStatus).toHaveClass("border-statusError");
    expect(connectivityStatus?.parentElement).toHaveClass("top-10");

    const uploadStatus = screen
      .getByText("Documento cargado correctamente.")
      .closest('[role="status"]');
    expect(uploadStatus).toHaveClass("border-statusSuccess");
    expect(uploadStatus?.parentElement).toHaveClass("top-28");

    const actionStatus = screen
      .getByText("Documento revisado: usa Reabrir para habilitar edición.")
      .closest('[role="status"]');
    expect(actionStatus).toHaveClass("border-accent");
    expect(actionStatus?.parentElement).toHaveClass("top-44");
  });

  it("uses fallback stacking without connectivity and keeps semantic error/success borders", () => {
    renderToastHost({
      uploadFeedback: {
        kind: "error",
        message: "El archivo supera el tamaño máximo.",
      },
      actionFeedback: {
        kind: "success",
        message: "Documento reabierto para revisión.",
      },
    });

    const uploadStatus = screen
      .getByText("El archivo supera el tamaño máximo.")
      .closest('[role="alert"]');
    expect(uploadStatus).toHaveClass("border-statusError");
    expect(uploadStatus?.parentElement).toHaveClass("top-10");

    const actionStatus = screen
      .getByText("Documento reabierto para revisión.")
      .closest('[role="status"]');
    expect(actionStatus).toHaveClass("border-statusSuccess");
    expect(actionStatus?.parentElement).toHaveClass("top-28");
  });

  it("keeps upload open action and close handlers wired", () => {
    const handlers = renderToastHost({
      connectivityToast: {},
      uploadFeedback: {
        kind: "success",
        message: "Documento cargado correctamente.",
        documentId: "doc-1",
        showOpenAction: true,
      },
      actionFeedback: {
        kind: "error",
        message: "No se pudo guardar.",
        technicalDetails: "HTTP 500",
      },
    });

    fireEvent.click(screen.getByRole("button", { name: "Cerrar aviso de conexión" }));
    expect(handlers.onCloseConnectivityToast).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Cerrar notificación" }));
    expect(handlers.onCloseUploadFeedback).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Cerrar notificación de acción" }));
    expect(handlers.onCloseActionFeedback).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Ver documento" }));
    expect(handlers.onOpenUploadedDocument).toHaveBeenCalledWith("doc-1");
  });
});
