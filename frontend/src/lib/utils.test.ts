import { afterEach, describe, expect, it, vi } from "vitest";

import { apiFetchBlob, apiFetchJson, cn, isApiErrorPayload } from "./utils";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("cn", () => {
  it("merges class names and drops falsy values", () => {
    expect(cn("base", false, undefined, null, "active", "")).toBe("base active");
  });
});

describe("isApiErrorPayload", () => {
  it("returns true for valid payload shape", () => {
    expect(
      isApiErrorPayload({
        error_code: "VALIDATION_ERROR",
        message: "Payload inválido",
        details: {},
      }),
    ).toBe(true);
  });

  it("returns false for missing fields and non-object values", () => {
    expect(isApiErrorPayload({ message: "Missing code" })).toBe(false);
    expect(isApiErrorPayload({ error_code: "ONLY_CODE" })).toBe(false);
    expect(isApiErrorPayload(null)).toBe(false);
    expect(isApiErrorPayload("oops")).toBe(false);
  });
});

describe("apiFetchJson", () => {
  it("throws fallback ApiError for non-json error responses", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response("plain-text", {
        status: 500,
        headers: { "content-type": "text/plain" },
      }),
    ) as typeof fetch;

    await expect(apiFetchJson("/documents")).rejects.toMatchObject({
      error_code: "INTERNAL_ERROR",
      message: "Ocurrio un error inesperado.",
      status: 500,
    });
  });

  it("falls back when json body is malformed despite json content type", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response("{not-valid-json", {
        status: 400,
        headers: { "content-type": "application/json" },
      }),
    ) as typeof fetch;

    await expect(apiFetchJson("/documents")).rejects.toMatchObject({
      error_code: "INTERNAL_ERROR",
      status: 400,
    });
  });

  it("falls back when json content type payload does not match error shape", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          code: "VALIDATION_ERROR",
          detail: "Payload inválido",
        }),
        {
          status: 422,
          headers: { "content-type": "application/json" },
        },
      ),
    ) as typeof fetch;

    await expect(apiFetchJson("/documents")).rejects.toMatchObject({
      error_code: "INTERNAL_ERROR",
      message: "Ocurrio un error inesperado.",
      status: 422,
    });
  });

  it("surfaces api payload errors when shape is valid", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error_code: "VALIDATION_ERROR",
          message: "Payload inválido",
          details: { field: "name" },
        }),
        {
          status: 422,
          headers: { "content-type": "application/json" },
        },
      ),
    ) as typeof fetch;

    await expect(apiFetchJson("/documents")).rejects.toMatchObject({
      error_code: "VALIDATION_ERROR",
      message: "Payload inválido",
      status: 422,
    });
  });

  it("propagates network errors", async () => {
    const networkError = new Error("network down");
    globalThis.fetch = vi.fn().mockRejectedValue(networkError) as typeof fetch;

    await expect(apiFetchJson("/documents")).rejects.toBe(networkError);
  });
});

describe("apiFetchBlob", () => {
  it("throws parsed error payload for non-ok responses", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error_code: "NOT_FOUND",
          message: "Documento no encontrado",
        }),
        {
          status: 404,
          headers: { "content-type": "application/json" },
        },
      ),
    ) as typeof fetch;

    await expect(apiFetchBlob("/documents/1/download")).rejects.toMatchObject({
      error_code: "NOT_FOUND",
      status: 404,
    });
  });

  it("falls back for non-json blob error responses", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response("failed", {
        status: 503,
        headers: { "content-type": "text/plain" },
      }),
    ) as typeof fetch;

    await expect(apiFetchBlob("/documents/1/download")).rejects.toMatchObject({
      error_code: "INTERNAL_ERROR",
      message: "Ocurrio un error inesperado.",
      status: 503,
    });
  });

  it("falls back when blob error json body is malformed", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response("{broken", {
        status: 400,
        headers: { "content-type": "application/json" },
      }),
    ) as typeof fetch;

    await expect(apiFetchBlob("/documents/1/download")).rejects.toMatchObject({
      error_code: "INTERNAL_ERROR",
      message: "Ocurrio un error inesperado.",
      status: 400,
    });
  });
});
