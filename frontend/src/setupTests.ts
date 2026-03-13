import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";
import { clearConsoleSuppressions, isConsoleOutputSuppressed } from "./test/consoleSuppressions";

afterEach(() => {
  cleanup();
});

let originalConsoleError: typeof console.error | undefined;
let originalConsoleWarn: typeof console.warn | undefined;

beforeEach(() => {
  clearConsoleSuppressions();

  originalConsoleError = console.error;
  originalConsoleWarn = console.warn;

  console.error = vi.fn((...args: unknown[]) => {
    if (isConsoleOutputSuppressed("error", args)) {
      return;
    }

    throw new Error(
      `Unexpected console.error (1 call). ` +
        `Call: ${JSON.stringify(args)}. ` +
        `Use suppressConsoleError() from test/helpers to allow expected errors.`,
    );
  }) as typeof console.error;

  console.warn = vi.fn((...args: unknown[]) => {
    if (isConsoleOutputSuppressed("warn", args)) {
      return;
    }

    throw new Error(
      `Unexpected console.warn (1 call). ` +
        `Call: ${JSON.stringify(args)}. ` +
        `Use suppressConsoleWarn() from test/helpers to allow expected warnings.`,
    );
  }) as typeof console.warn;
});

afterEach(() => {
  if (originalConsoleError) {
    console.error = originalConsoleError;
  }
  if (originalConsoleWarn) {
    console.warn = originalConsoleWarn;
  }
  clearConsoleSuppressions();
});

if (!Object.getOwnPropertyDescriptor(HTMLElement.prototype, "clientWidth")?.get) {
  Object.defineProperty(HTMLElement.prototype, "clientWidth", {
    configurable: true,
    get() {
      return 800;
    },
  });
}

if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = class ResizeObserver {
    constructor(private readonly callback: ResizeObserverCallback) {}

    observe() {
      this.callback([], this as unknown as ResizeObserver);
    }

    unobserve() {}

    disconnect() {}
  };
}

if (!HTMLCanvasElement.prototype.getContext) {
  // no-op
}

HTMLCanvasElement.prototype.getContext = (() =>
  ({}) as CanvasRenderingContext2D) as unknown as HTMLCanvasElement["getContext"];

HTMLElement.prototype.scrollIntoView = () => {};
