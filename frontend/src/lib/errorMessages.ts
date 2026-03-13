type ErrorPattern = {
  pattern: RegExp;
  message: string;
};

const errorPatterns: ErrorPattern[] = [
  {
    pattern: /rate.?limit|too many/i,
    message: "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
  },
  {
    pattern: /file.*too large|size.*exceed/i,
    message: "El archivo es demasiado grande. El límite es 50 MB.",
  },
  {
    pattern: /invalid.*uuid|not.*valid.*id/i,
    message: "Identificador de documento inválido.",
  },
  { pattern: /not found|404/i, message: "Documento no encontrado." },
  {
    pattern: /unsupported.*type|invalid.*file/i,
    message: "Tipo de archivo no soportado. Solo se aceptan PDFs.",
  },
  {
    pattern: /processing.*failed|extraction.*error/i,
    message: "Error durante el procesamiento. Intenta reprocesar el documento.",
  },
  {
    pattern: /network|fetch|aborted|timeout/i,
    message: "Error de conexión. Verifica tu conexión a internet.",
  },
  {
    pattern: /server.*error|500|internal/i,
    message: "Error del servidor. Intenta de nuevo más tarde.",
  },
];

export function getUserFriendlyError(rawError: string): string {
  for (const { pattern, message } of errorPatterns) {
    if (pattern.test(rawError)) {
      return message;
    }
  }
  return "Ocurrió un error inesperado. Intenta de nuevo.";
}
