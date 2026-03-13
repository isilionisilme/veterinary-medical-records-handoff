import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { suppressConsoleError, suppressExpectedWindowError } from "../test/helpers";
import { ErrorBoundary } from "./ErrorBoundary";

function ThrowingChild() {
  throw new Error("boom");
}

describe("ErrorBoundary", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <div>content ok</div>
      </ErrorBoundary>,
    );

    expect(screen.getByText("content ok")).toBeInTheDocument();
  });

  it("renders fallback UI when a child throws", () => {
    const restoreConsole = suppressConsoleError();
    const restoreWindowError = suppressExpectedWindowError("boom");

    render(
      <ErrorBoundary>
        <ThrowingChild />
      </ErrorBoundary>,
    );

    expect(screen.getByRole("heading", { name: "Algo salió mal" })).toBeInTheDocument();
    expect(screen.getByText("Detalles técnicos")).toBeInTheDocument();
    expect(screen.getByText(/boom/i)).toBeInTheDocument();

    restoreWindowError();
    restoreConsole();
  });

  it("reload button calls window.location.reload", () => {
    const reloadSpy = vi.fn();
    vi.stubGlobal("location", { ...window.location, reload: reloadSpy });
    const restoreConsole = suppressConsoleError();
    const restoreWindowError = suppressExpectedWindowError("boom");

    render(
      <ErrorBoundary>
        <ThrowingChild />
      </ErrorBoundary>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Recargar página" }));
    expect(reloadSpy).toHaveBeenCalledTimes(1);

    restoreWindowError();
    restoreConsole();
    vi.unstubAllGlobals();
  });
});
