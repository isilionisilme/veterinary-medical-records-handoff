import { API_BASE_URL } from "../constants/appWorkspace";
import { isNetworkFetchError, parseFilename } from "../lib/appWorkspaceUtils";
import { getUserFriendlyError } from "../lib/errorMessages";
import {
  ApiResponseError,
  type DocumentDetailResponse,
  type DocumentListResponse,
  type DocumentReviewResponse,
  type DocumentUploadResponse,
  type InterpretationChangePayload,
  type InterpretationEditResponse,
  type LatestRun,
  type LoadResult,
  type ProcessingHistoryResponse,
  type RawTextArtifactResponse,
  type ReviewToggleResponse,
  type VisitScopingMetricsResponse,
  UiError,
} from "../types/appWorkspace";

function resolveFriendlyPayloadMessage(payloadMessage: unknown, fallback: string): string {
  if (typeof payloadMessage === "string" && payloadMessage.trim().length > 0) {
    return getUserFriendlyError(payloadMessage);
  }
  return fallback;
}

// --- Internal fetch wrapper ---

type ResponseType = "json" | "blob" | "text" | "raw";

const NETWORK_ERROR_DEFAULT = "No se pudo conectar con el servidor.";

interface ApiFetchConfig<T> {
  fetchOptions?: RequestInit;
  responseType?: ResponseType;
  friendlyMessage: string;
  networkMessage?: string;
  onResponseError?: (response: Response) => Promise<T>;
}

async function apiFetch<T>(endpoint: string, config: ApiFetchConfig<T>): Promise<T> {
  const {
    fetchOptions,
    responseType = "json",
    friendlyMessage,
    networkMessage = NETWORK_ERROR_DEFAULT,
    onResponseError,
  } = config;

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      throw new UiError(networkMessage, `Network error calling ${API_BASE_URL}${endpoint}`);
    }
    throw error;
  }

  if (!response.ok) {
    if (onResponseError) {
      return onResponseError(response);
    }
    let errorMessage = friendlyMessage;
    try {
      const payload = await response.json();
      errorMessage = resolveFriendlyPayloadMessage(payload?.message, errorMessage);
    } catch {
      // Ignore JSON parse errors for non-JSON responses.
    }
    throw new UiError(errorMessage, `HTTP ${response.status} calling ${API_BASE_URL}${endpoint}`);
  }

  switch (responseType) {
    case "blob":
      return (await response.blob()) as T;
    case "text":
      return (await response.text()) as T;
    case "raw":
      return response as unknown as T;
    default:
      return (await response.json()) as T;
  }
}

async function throwApiResponseError(
  response: Response,
  endpoint: string,
  friendlyMessage: string,
): Promise<never> {
  let errorMessage = friendlyMessage;
  let errorCode: string | undefined;
  let reason: string | undefined;
  try {
    const payload = await response.json();
    errorMessage = resolveFriendlyPayloadMessage(payload?.message, errorMessage);
    if (typeof payload?.error_code === "string") {
      errorCode = payload.error_code;
    }
    if (typeof payload?.details?.reason === "string") {
      reason = payload.details.reason;
    }
  } catch {
    // Ignore JSON parse errors for non-JSON responses.
  }
  throw new ApiResponseError(
    errorMessage,
    `HTTP ${response.status} calling ${API_BASE_URL}${endpoint}`,
    errorCode,
    reason,
  );
}

export async function fetchOriginalPdf(documentId: string): Promise<LoadResult> {
  const endpoint = `/documents/${documentId}/download`;
  const response = await apiFetch<Response>(endpoint, {
    responseType: "raw",
    friendlyMessage: "No pudimos cargar el documento.",
  });
  const data = await response.arrayBuffer();
  const filename = parseFilename(response.headers.get("content-disposition"));
  return { data, filename };
}

export async function fetchDocuments(): Promise<DocumentListResponse> {
  return apiFetch<DocumentListResponse>("/documents?limit=50&offset=0", {
    friendlyMessage: "No se pudieron cargar los documentos.",
    networkMessage: "No se pudieron cargar los documentos.",
    onResponseError: async (response) => {
      if (response.status === 404) {
        return { items: [], limit: 50, offset: 0, total: 0 };
      }
      let errorMessage = "No se pudieron cargar los documentos.";
      try {
        const payload = await response.json();
        errorMessage = resolveFriendlyPayloadMessage(payload?.message, errorMessage);
      } catch {
        // Ignore JSON parse errors for non-JSON responses.
      }
      throw new UiError(errorMessage, `HTTP ${response.status} calling ${API_BASE_URL}/documents`);
    },
  });
}

export async function fetchDocumentDetails(documentId: string): Promise<DocumentDetailResponse> {
  return apiFetch<DocumentDetailResponse>(`/documents/${documentId}`, {
    friendlyMessage: "No pudimos cargar el estado del documento.",
  });
}

export async function fetchDocumentReview(documentId: string): Promise<DocumentReviewResponse> {
  const endpoint = `/documents/${documentId}/review`;
  return apiFetch<DocumentReviewResponse>(endpoint, {
    friendlyMessage: "No se pudo cargar la revisión del documento.",
    onResponseError: (response) =>
      throwApiResponseError(response, endpoint, "No se pudo cargar la revisión del documento."),
  });
}

export async function fetchProcessingHistory(
  documentId: string,
): Promise<ProcessingHistoryResponse> {
  return apiFetch<ProcessingHistoryResponse>(`/documents/${documentId}/processing-history`, {
    friendlyMessage: "No pudimos cargar el historial de procesamiento.",
  });
}

export async function fetchVisitScopingMetrics(
  documentId: string,
): Promise<VisitScopingMetricsResponse> {
  return apiFetch<VisitScopingMetricsResponse>(
    `/documents/${documentId}/review/debug/visit-scoping`,
    {
      friendlyMessage: "No pudimos cargar la observabilidad de visitas.",
    },
  );
}

export async function triggerReprocess(documentId: string): Promise<LatestRun> {
  const endpoint = `/documents/${documentId}/reprocess`;
  return apiFetch<LatestRun>(endpoint, {
    fetchOptions: { method: "POST" },
    friendlyMessage: "No pudimos reprocesar el documento.",
    onResponseError: async (response) => {
      let errorMessage = "No pudimos reprocesar el documento.";
      try {
        const payload = await response.json();
        errorMessage = resolveFriendlyPayloadMessage(payload?.message, errorMessage);
      } catch {
        // Ignore JSON parse errors for non-JSON responses.
      }
      throw new Error(errorMessage);
    },
  });
}

export async function markDocumentReviewed(documentId: string): Promise<ReviewToggleResponse> {
  return apiFetch<ReviewToggleResponse>(`/documents/${documentId}/reviewed`, {
    fetchOptions: { method: "POST" },
    friendlyMessage: "No se pudo marcar como revisado.",
  });
}

export async function reopenDocumentReview(documentId: string): Promise<ReviewToggleResponse> {
  return apiFetch<ReviewToggleResponse>(`/documents/${documentId}/reviewed`, {
    fetchOptions: { method: "DELETE" },
    friendlyMessage: "No se pudo reabrir el documento.",
  });
}

export async function editRunInterpretation(
  runId: string,
  payload: {
    base_version_number: number;
    changes: InterpretationChangePayload[];
  },
): Promise<InterpretationEditResponse> {
  const endpoint = `/runs/${runId}/interpretations`;
  return apiFetch<InterpretationEditResponse>(endpoint, {
    fetchOptions: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    friendlyMessage: "No se pudo guardar la edición.",
    onResponseError: (response) =>
      throwApiResponseError(response, endpoint, "No se pudo guardar la edición."),
  });
}

export async function fetchRawText(runId: string): Promise<RawTextArtifactResponse> {
  const endpoint = `/runs/${runId}/artifacts/raw-text`;
  return apiFetch<RawTextArtifactResponse>(endpoint, {
    friendlyMessage: "No se pudo cargar el texto extraído.",
    onResponseError: (response) =>
      throwApiResponseError(response, endpoint, "No se pudo cargar el texto extraído."),
  });
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const endpoint = "/documents/upload";
  return apiFetch<DocumentUploadResponse>(endpoint, {
    fetchOptions: { method: "POST", body: formData },
    friendlyMessage: "No pudimos subir el documento.",
    networkMessage: "No se pudo subir el documento.",
    onResponseError: async (response) => {
      let errorMessage = "No pudimos subir el documento.";
      try {
        const payload = await response.json();
        if (payload?.error_code === "UNSUPPORTED_MEDIA_TYPE") {
          errorMessage = "Solo se admiten archivos PDF.";
        } else if (payload?.error_code === "FILE_TOO_LARGE") {
          errorMessage = "El PDF supera el tamaño máximo permitido de 20 MB.";
        } else if (payload?.error_code === "INVALID_REQUEST") {
          errorMessage = "El archivo no es válido. Selecciona un PDF e inténtalo otra vez.";
        } else {
          errorMessage = resolveFriendlyPayloadMessage(payload?.message, errorMessage);
        }
      } catch {
        // Ignore JSON parse errors for non-JSON responses.
      }
      throw new UiError(errorMessage, `HTTP ${response.status} calling ${API_BASE_URL}${endpoint}`);
    },
  });
}

export async function copyTextToClipboard(text: string): Promise<void> {
  if (!text) {
    throw new UiError("No hay texto disponible para copiar.");
  }

  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  if (typeof document !== "undefined") {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    textarea.style.pointerEvents = "none";
    textarea.style.left = "-9999px";
    textarea.style.top = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);

    try {
      const copied = document.execCommand("copy");
      if (!copied) {
        throw new UiError("No se pudo copiar el texto al portapapeles.");
      }
      return;
    } finally {
      document.body.removeChild(textarea);
    }
  }

  throw new UiError("No se pudo copiar el texto al portapapeles.");
}

// --- Clinic address lookup ---

export type ClinicAddressLookupResponse = {
  found: boolean;
  address: string | null;
  source: string;
};

export async function lookupClinicAddress(
  clinicName: string,
): Promise<ClinicAddressLookupResponse> {
  return apiFetch<ClinicAddressLookupResponse>("/clinics/lookup-address", {
    fetchOptions: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clinic_name: clinicName }),
    },
    friendlyMessage: "No se pudo buscar la dirección de la clínica.",
    networkMessage: "No se pudo conectar con el servidor para buscar la dirección.",
  });
}
