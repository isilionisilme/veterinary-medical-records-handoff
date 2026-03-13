type ClassValue = string | false | null | undefined;

export function cn(...classes: ClassValue[]): string {
  return classes.filter(Boolean).join(" ");
}

export type ApiError = {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
  status: number;
};

const DEFAULT_ERROR_MESSAGE = "Ocurrio un error inesperado.";

export const isApiErrorPayload = (value: unknown): value is Omit<ApiError, "status"> => {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as { error_code?: unknown; message?: unknown };
  return typeof payload.error_code === "string" && typeof payload.message === "string";
};

const parseError = async (response: Response): Promise<ApiError> => {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    try {
      const payload = await response.json();
      if (isApiErrorPayload(payload)) {
        return {
          error_code: payload.error_code,
          message: payload.message,
          details: payload.details as Record<string, unknown> | undefined,
          status: response.status,
        };
      }
    } catch {
      // Fall through to default error.
    }
  }
  return {
    error_code: "INTERNAL_ERROR",
    message: DEFAULT_ERROR_MESSAGE,
    status: response.status,
  };
};

export const apiFetchJson = async <T>(input: RequestInfo, init?: RequestInit): Promise<T> => {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json() as Promise<T>;
};

export const apiFetchBlob = async (
  input: RequestInfo,
  init?: RequestInit,
): Promise<{ blob: Blob; headers: Headers }> => {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw await parseError(response);
  }
  return { blob: await response.blob(), headers: response.headers };
};
