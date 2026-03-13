type ConsoleMethod = "error" | "warn";

function consoleArgsMatchPattern(args: unknown[], pattern?: string | RegExp): boolean {
  if (!pattern) {
    return true;
  }

  const text = args
    .map((arg) => {
      if (typeof arg === "string") {
        return arg;
      }
      try {
        return JSON.stringify(arg);
      } catch {
        return String(arg);
      }
    })
    .join(" ");

  if (typeof pattern === "string") {
    return text.includes(pattern);
  }

  return pattern.test(text);
}

type ConsoleSuppression = {
  id: symbol;
  pattern?: string | RegExp;
};

const consoleSuppressions: Record<ConsoleMethod, ConsoleSuppression[]> = {
  error: [],
  warn: [],
};

export function isConsoleOutputSuppressed(method: ConsoleMethod, args: unknown[]): boolean {
  return consoleSuppressions[method].some(({ pattern }) => consoleArgsMatchPattern(args, pattern));
}

export function clearConsoleSuppressions() {
  consoleSuppressions.error = [];
  consoleSuppressions.warn = [];
}

export function registerConsoleSuppression(
  method: ConsoleMethod,
  pattern?: string | RegExp,
): () => void {
  const suppression: ConsoleSuppression = {
    id: Symbol(`console-${method}-suppression`),
    pattern,
  };

  consoleSuppressions[method].push(suppression);

  return () => {
    consoleSuppressions[method] = consoleSuppressions[method].filter(
      ({ id }) => id !== suppression.id,
    );
  };
}
