export type DocumentStatusTone = "success" | "warn" | "error";

export type DocumentStatusClusterModel = {
  label: string;
  tone: DocumentStatusTone;
  hint?: string;
  tooltip: string;
  icon?: "dot" | "check";
};

export function mapDocumentStatus(item: {
  status: string;
  failure_type: string | null | undefined;
  review_status?: string;
}): DocumentStatusClusterModel {
  const isReviewed = item.review_status === "REVIEWED";

  if (item.status === "FAILED" || item.status === "TIMED_OUT" || item.failure_type) {
    return {
      label: "Error",
      tone: "error",
      tooltip: "El documento tuvo un error durante el procesamiento.",
      icon: "dot",
    };
  }

  if (isReviewed) {
    return {
      label: "Revisado",
      tone: "success",
      tooltip: "Documento revisado. Usa Reabrir para volver a editar.",
      icon: "check",
    };
  }

  if (item.status === "COMPLETED") {
    return {
      label: "Listo",
      tone: "success",
      tooltip: "El documento está procesado y listo.",
      icon: "dot",
    };
  }

  return {
    label: "Procesando",
    tone: "warn",
    tooltip: "El documento sigue en procesamiento. Los datos pueden cambiar.",
    icon: "dot",
  };
}
