import { describe, expect, it } from "vitest";

import { getUserFriendlyError } from "../errorMessages";

describe("getUserFriendlyError", () => {
  it("maps rate limit errors", () => {
    expect(getUserFriendlyError("Too many requests, rate limit exceeded")).toBe(
      "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
    );
  });

  it("maps file size errors", () => {
    expect(getUserFriendlyError("file too large")).toBe(
      "El archivo es demasiado grande. El límite es 50 MB.",
    );
  });

  it("maps invalid id errors", () => {
    expect(getUserFriendlyError("not valid id format")).toBe(
      "Identificador de documento inválido.",
    );
  });

  it("maps not found errors", () => {
    expect(getUserFriendlyError("HTTP 404 not found")).toBe("Documento no encontrado.");
  });

  it("maps unsupported file type errors", () => {
    expect(getUserFriendlyError("unsupported media type")).toBe(
      "Tipo de archivo no soportado. Solo se aceptan PDFs.",
    );
  });

  it("maps processing failures", () => {
    expect(getUserFriendlyError("processing failed during extraction")).toBe(
      "Error durante el procesamiento. Intenta reprocesar el documento.",
    );
  });

  it("maps connectivity errors", () => {
    expect(getUserFriendlyError("fetch timeout")).toBe(
      "Error de conexión. Verifica tu conexión a internet.",
    );
  });

  it("maps server errors", () => {
    expect(getUserFriendlyError("internal server error")).toBe(
      "Error del servidor. Intenta de nuevo más tarde.",
    );
  });

  it("prefers first matching pattern when multiple patterns are present", () => {
    expect(getUserFriendlyError("too many requests 500 internal")).toBe(
      "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
    );
  });

  it("returns fallback message when no pattern matches", () => {
    expect(getUserFriendlyError("unexpected validation branch")).toBe(
      "Ocurrió un error inesperado. Intenta de nuevo.",
    );
  });
});
