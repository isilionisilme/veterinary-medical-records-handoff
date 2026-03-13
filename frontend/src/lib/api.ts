import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  DocumentDetailResponse,
  DocumentListResponse,
  DocumentReviewResponse,
  DocumentUploadResponse,
  ProcessingHistoryResponse,
  RawTextArtifactResponse,
} from "../types";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(body || `HTTP ${response.status} ${url}`);
  }
  return (await response.json()) as T;
}

export async function fetchDocumentList(): Promise<DocumentListResponse> {
  return fetchJson<DocumentListResponse>(`${API_BASE}/documents?limit=50&offset=0`);
}

export async function fetchDocumentDetails(documentId: string): Promise<DocumentDetailResponse> {
  return fetchJson<DocumentDetailResponse>(`${API_BASE}/documents/${documentId}`);
}

export async function fetchProcessingHistory(
  documentId: string,
): Promise<ProcessingHistoryResponse> {
  return fetchJson<ProcessingHistoryResponse>(
    `${API_BASE}/documents/${documentId}/processing-history`,
  );
}

export async function fetchDocumentReview(documentId: string): Promise<DocumentReviewResponse> {
  return fetchJson<DocumentReviewResponse>(`${API_BASE}/documents/${documentId}/review`);
}

export async function fetchRawText(
  documentId: string,
  runId: string,
): Promise<RawTextArtifactResponse> {
  return fetchJson<RawTextArtifactResponse>(
    `${API_BASE}/documents/${documentId}/artifacts/${runId}/raw-text`,
  );
}

export function useDocumentList() {
  return useQuery({ queryKey: ["documentList"], queryFn: fetchDocumentList });
}

export function useDocumentDetails(documentId: string | null) {
  return useQuery({
    queryKey: ["documentDetails", documentId],
    queryFn: () => fetchDocumentDetails(documentId as string),
    enabled: Boolean(documentId),
  });
}

export function useProcessingHistory(documentId: string | null) {
  return useQuery({
    queryKey: ["processingHistory", documentId],
    queryFn: () => fetchProcessingHistory(documentId as string),
    enabled: Boolean(documentId),
  });
}

export function useDocumentReview(documentId: string | null) {
  return useQuery({
    queryKey: ["documentReview", documentId],
    queryFn: () => fetchDocumentReview(documentId as string),
    enabled: Boolean(documentId),
  });
}

export function useRawTextQuery(documentId: string | null, runId: string | null) {
  return useQuery({
    queryKey: ["rawText", documentId, runId],
    queryFn: () => fetchRawText(documentId as string, runId as string),
    enabled: Boolean(documentId && runId),
  });
}

export function useLoadPdfMutation() {
  return useMutation({
    mutationFn: async (documentId: string) => {
      const response = await fetch(`${API_BASE}/documents/${documentId}/download`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const filename =
        /filename="?([^";]+)"?/i.exec(response.headers.get("content-disposition") ?? "")?.[1] ??
        null;
      return { url: URL.createObjectURL(blob), filename };
    },
  });
}

export function useUploadMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return fetchJson<DocumentUploadResponse>(`${API_BASE}/documents/upload`, {
        method: "POST",
        body: form,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documentList"] });
    },
  });
}

export function useReprocessMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      fetchJson<{ run_id: string }>(`${API_BASE}/documents/${documentId}/reprocess`, {
        method: "POST",
      }),
    onSuccess: async (_value, documentId) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["documentDetails", documentId] }),
        queryClient.invalidateQueries({ queryKey: ["processingHistory", documentId] }),
        queryClient.invalidateQueries({ queryKey: ["documentReview", documentId] }),
      ]);
    },
  });
}

export function useReviewToggleMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: { documentId: string; review_status: "IN_REVIEW" | "REVIEWED" }) =>
      fetchJson(`${API_BASE}/documents/${params.documentId}/review`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review_status: params.review_status }),
      }),
    onSuccess: async (_value, params) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["documentList"] }),
        queryClient.invalidateQueries({ queryKey: ["documentDetails", params.documentId] }),
        queryClient.invalidateQueries({ queryKey: ["documentReview", params.documentId] }),
      ]);
    },
  });
}

export function useInterpretationEditMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: {
      documentId: string;
      payload: {
        interpretation_id: string;
        operations: Array<Record<string, unknown>>;
      };
    }) =>
      fetchJson(`${API_BASE}/documents/${params.documentId}/interpretation/edits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params.payload),
      }),
    onSuccess: async (_value, params) => {
      await queryClient.invalidateQueries({ queryKey: ["documentReview", params.documentId] });
    },
  });
}
