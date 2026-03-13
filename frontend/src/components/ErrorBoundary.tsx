import React, { type ErrorInfo, type ReactNode } from "react";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  error?: Error;
  stack?: string;
};

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      stack: errorInfo.componentStack || error.stack,
    });
  }

  private readonly handleReload = () => {
    window.location.reload();
  };

  override render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6">
        <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-slate-900/80 p-8 text-slate-100 shadow-2xl">
          <p className="mb-3 text-2xl" role="img" aria-label="error icon">
            ⚠️
          </p>
          <h1 className="text-2xl font-semibold">Algo salió mal</h1>
          <p className="mt-3 text-sm text-slate-300">
            Se produjo un error inesperado. Intenta recargar la página.
          </p>
          <button
            type="button"
            className="mt-6 inline-flex items-center rounded-md bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            onClick={this.handleReload}
          >
            Recargar página
          </button>
          <details className="mt-6 rounded-md border border-white/10 bg-slate-950/60 p-3 text-xs text-slate-300">
            <summary className="cursor-pointer select-none font-medium text-slate-200">
              Detalles técnicos
            </summary>
            <pre className="mt-3 overflow-x-auto whitespace-pre-wrap break-words text-[11px] leading-relaxed">
              {this.state.error?.message}
              {this.state.stack ? `\n\n${this.state.stack}` : ""}
            </pre>
          </details>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
