import { type Dispatch, type MutableRefObject, type SetStateAction } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { fetchDocuments, uploadDocument } from "../api/documentApi";
import { type UploadFeedback } from "../components/toast/toast-types";
import { getTechnicalDetails, getUserErrorMessage } from "../lib/appWorkspaceUtils";
import { type DocumentListResponse } from "../types/appWorkspace";

type UseDocumentUploadParams = {
  requestPdfLoad: (documentId: string) => void;
  pendingAutoOpenDocumentIdRef: MutableRefObject<string | null>;
  onUploadFeedback: Dispatch<SetStateAction<UploadFeedback | null>>;
  onSetActiveId: Dispatch<SetStateAction<string | null>>;
  onSetActiveViewerTab: Dispatch<SetStateAction<"document" | "raw_text" | "technical">>;
};

export function useDocumentUpload({
  requestPdfLoad,
  pendingAutoOpenDocumentIdRef,
  onUploadFeedback,
  onSetActiveId,
  onSetActiveViewerTab,
}: UseDocumentUploadParams) {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => uploadDocument(file),
    onSuccess: async (result, file) => {
      const createdAt = result.created_at || new Date().toISOString();
      queryClient.setQueryData<DocumentListResponse | undefined>(
        ["documents", "list"],
        (current) => {
          if (!current) {
            return current;
          }
          const exists = current.items.some((item) => item.document_id === result.document_id);
          const items = exists
            ? current.items
            : [
                {
                  document_id: result.document_id,
                  original_filename: file.name,
                  created_at: createdAt,
                  status: result.status,
                  status_label: result.status,
                  failure_type: null,
                },
                ...current.items,
              ];
          return { ...current, items, total: exists ? current.total : current.total + 1 };
        },
      );
      onSetActiveViewerTab("document");
      pendingAutoOpenDocumentIdRef.current = result.document_id;
      onSetActiveId(result.document_id);
      onUploadFeedback({
        kind: "success",
        message: "Documento subido correctamente.",
        documentId: result.document_id,
        showOpenAction: false,
      });
      requestPdfLoad(result.document_id);
      queryClient.invalidateQueries({ queryKey: ["documents", "list"] });
      try {
        await queryClient.fetchQuery({
          queryKey: ["documents", "list"],
          queryFn: fetchDocuments,
        });
      } catch {
        // Keep optimistic list item and fallback open action when refetch fails.
      }
      queryClient.invalidateQueries({ queryKey: ["documents", "detail", result.document_id] });
      queryClient.invalidateQueries({ queryKey: ["documents", "history", result.document_id] });
      queryClient.invalidateQueries({ queryKey: ["documents", "review", result.document_id] });
    },
    onError: (error) => {
      onUploadFeedback({
        kind: "error",
        message: getUserErrorMessage(error, "No se pudo subir el documento."),
        technicalDetails: getTechnicalDetails(error),
      });
    },
  });

  return { uploadMutation };
}
