export type ExtractionDebugEvent = {
  field: string;
  status: "missing" | "rejected" | "accepted";
  raw?: string;
  normalized?: string;
  reason?: string;
  docId?: string;
  page?: number;
};

declare global {
  interface Window {
    __extractionDebugEvents?: ExtractionDebugEvent[];
  }
}

export function isExtractionDebugEnabled(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const params = new URLSearchParams(window.location.search);
  return params.get("extractionDebug") === "1";
}

export function logExtractionDebugEvent(event: ExtractionDebugEvent): void {
  if (!isExtractionDebugEnabled() || typeof window === "undefined") {
    return;
  }

  const debugWindow = window as Window;
  const store = debugWindow.__extractionDebugEvents ?? [];
  store.push(event);
  debugWindow.__extractionDebugEvents = store;
  console.debug("[extraction-debug]", event);
}
